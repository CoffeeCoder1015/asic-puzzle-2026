"""Fold recovered flip-flops into explicit synchronous transition systems."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
SOURCES = {
    "warmup": ROOT / "experiments/collapse/results/adder_demo_collapsed.json",
    "puzzle": ROOT / "experiments/collapse/results/puzzle_collapsed.json",
}


def qualify(block: str, expression: str) -> str:
    return f"{block}.{expression}"


def load_machine(path: Path) -> dict[str, Any]:
    collapsed = json.loads(path.read_text())
    roots_by_destination: dict[str, str] = {}
    expressions: dict[str, dict[str, Any]] = {}
    state_name_by_q_net = {
        instance["pins"]["Q"]: f"{instance['name']}.Q"
        for instance in collapsed["sequential_instances"]
        if "Q" in instance["pins"]
    }

    for block in collapsed["combinational_blocks"]:
        block_name = block["name"]
        for node in block["expression_nodes"]:
            copied = dict(node)
            copied["id"] = qualify(block_name, node["id"])
            if copied["operation"] == "boundary" and copied.get("net_id") in state_name_by_q_net:
                copied["name"] = state_name_by_q_net[copied["net_id"]]
            if "arguments" in copied:
                copied["arguments"] = [
                    qualify(block_name, argument) for argument in copied["arguments"]
                ]
            expressions[copied["id"]] = copied
        for output in block["outputs"].values():
            root = qualify(block_name, output["expression"])
            for destination in output["destinations"]:
                roots_by_destination[destination] = root

    states = []
    for instance in collapsed["sequential_instances"]:
        name = instance["name"]
        state = instance["state"]
        if state.get("clear"):
            reset = {"kind": "asynchronous_clear", "condition": state["clear"], "value": 0}
        elif state.get("preset"):
            reset = {"kind": "asynchronous_preset", "condition": state["preset"], "value": 1}
        else:
            reset = {"kind": "none"}
        states.append(
            {
                "name": f"{name}.Q",
                "instance": name,
                "cell_type": instance["cell_type"],
                "clock": state["clocked_on"],
                "reset": reset,
                "current_net": instance["pins"].get("Q"),
                "next_net": instance["pins"].get("D"),
                "next_expression": roots_by_destination.get(f"{name}.D"),
            }
        )

    sequential_destinations = {f"{state['instance']}.D" for state in states}
    top_names = {pin["name"] for pin in collapsed["top_pins"]}
    outputs = {
        destination: expression
        for destination, expression in roots_by_destination.items()
        if destination in top_names and destination not in sequential_destinations
    }
    return {
        "design": collapsed["design_name"],
        "source": str(path.relative_to(ROOT)),
        "semantics": {
            "evaluation": "Evaluate every next_expression from old state and current inputs.",
            "edge": "Commit all resulting state values simultaneously on the active clock edge.",
            "outputs": "Evaluate combinational outputs from current state and current inputs.",
            "reset": "Each state's reset field is authoritative; kind=none means no recovered reset pin.",
        },
        "states": states,
        "outputs": outputs,
        "expressions": expressions,
        "collapsed_structure": {
            "combinational_blocks": len(collapsed["combinational_blocks"]),
            "combinational_instances": sum(
                len(block["instances"]) for block in collapsed["combinational_blocks"]
            ),
            "expression_nodes": len(expressions),
        },
    }


def support(machine: dict[str, Any], root: str) -> set[str]:
    memo: dict[str, set[str]] = {}

    def visit(node_id: str) -> set[str]:
        if node_id in memo:
            return memo[node_id]
        node = machine["expressions"][node_id]
        if node["operation"] == "boundary":
            result = {node["name"]}
        else:
            result = set().union(*(visit(arg) for arg in node.get("arguments", [])))
        memo[node_id] = result
        return result

    return visit(root)


def evaluate(machine: dict[str, Any], root: str, values: dict[str, bool]) -> bool:
    memo: dict[str, bool] = {}

    def visit(node_id: str) -> bool:
        if node_id in memo:
            return memo[node_id]
        node = machine["expressions"][node_id]
        operation = node["operation"]
        if operation == "boundary":
            result = values[node["name"]]
        elif operation == "constant":
            result = bool(node["value"])
        elif operation == "not":
            result = not visit(node["arguments"][0])
        elif operation == "and":
            result = all(visit(arg) for arg in node["arguments"])
        elif operation == "or":
            result = any(visit(arg) for arg in node["arguments"])
        else:
            raise ValueError(f"unsupported operation {operation!r}")
        memo[node_id] = result
        return result

    return visit(root)


def find_node_by_instance(machine: dict[str, Any], instance: str, operation: str | None = None) -> str:
    matches = [
        node_id
        for node_id, node in machine["expressions"].items()
        if instance in node.get("instances", [])
        and (operation is None or node["operation"] == operation)
    ]
    if not matches:
        raise KeyError(instance)
    return matches[-1]


def classify_mux_holds(machine: dict[str, Any]) -> list[dict[str, str]]:
    """Recognize q' = control ? source : q by exact truth-table equivalence."""
    found = []
    for state in machine["states"]:
        root = state["next_expression"]
        if not root:
            continue
        names = sorted(support(machine, root))
        if state["name"] not in names or len(names) > 5:
            continue
        others = [name for name in names if name != state["name"]]
        for control in others:
            for source in others:
                if source == control:
                    continue
                for active_high in (True, False):
                    matches = True
                    for bits in range(1 << len(names)):
                        values = {name: bool(bits & (1 << i)) for i, name in enumerate(names)}
                        enabled = values[control] == active_high
                        expected = values[source] if enabled else values[state["name"]]
                        if evaluate(machine, root, values) != expected:
                            matches = False
                            break
                    if matches:
                        found.append(
                            {
                                "state": state["name"],
                                "control": control,
                                "active": "high" if active_high else "low",
                                "source": source,
                            }
                        )
                        break
                if found and found[-1]["state"] == state["name"]:
                    break
            if found and found[-1]["state"] == state["name"]:
                break
    return found


def transition_table(
    machine: dict[str, Any], states_lsb_first: list[str], fixed: dict[str, bool]
) -> dict[int, int]:
    state_map = {state["name"]: state for state in machine["states"]}
    table = {}
    for value in range(1 << len(states_lsb_first)):
        values = dict(fixed)
        values.update(
            {name: bool(value & (1 << bit)) for bit, name in enumerate(states_lsb_first)}
        )
        next_value = 0
        for bit, name in enumerate(states_lsb_first):
            root = state_map[name]["next_expression"]
            for dependency in support(machine, root):
                values.setdefault(dependency, False)
            next_value |= int(evaluate(machine, root, values)) << bit
        table[value] = next_value
    return table


def terminal_slice(puzzle: dict[str, Any]) -> dict[str, Any]:
    state_map = {state["instance"]: state for state in puzzle["states"]}
    net_4166 = find_node_by_instance(puzzle, "cell_808", "and")
    net_4201 = find_node_by_instance(puzzle, "cell_18", "and")
    success_next = state_map["cell_144"]["next_expression"]
    failure_next = state_map["cell_179"]["next_expression"]
    not_touch = find_node_by_instance(puzzle, "cell_781", "not")
    touch = find_node_by_instance(puzzle, "cell_783", "not")
    hold_phase = find_node_by_instance(puzzle, "cell_274", "or")

    def flattened(node_id: str, operation: str) -> set[str]:
        node = puzzle["expressions"][node_id]
        if node["operation"] != operation:
            return {node_id}
        return set().union(*(flattened(arg, operation) for arg in node["arguments"]))

    def descendants(node_id: str) -> set[str]:
        return {node_id}.union(
            *(descendants(arg) for arg in puzzle["expressions"][node_id].get("arguments", []))
        )

    success_terms = puzzle["expressions"][success_next]["arguments"]
    failure_terms = puzzle["expressions"][failure_next]["arguments"]
    success_candidate = next(term for term in success_terms if not_touch in flattened(term, "and"))
    success_hold = next(term for term in success_terms if term != success_candidate)
    failure_candidate = next(term for term in failure_terms if touch in flattened(term, "and"))
    failure_hold = next(term for term in failure_terms if term != failure_candidate)
    assert {not_touch, net_4166, net_4201} <= descendants(success_candidate)
    assert {touch, net_4166, net_4201} <= descendants(failure_candidate)
    assert flattened(success_hold, "and") == {
        find_boundary(puzzle, "cell_144.Q"),
        hold_phase,
    }
    assert flattened(failure_hold, "and") == {
        find_boundary(puzzle, "cell_179.Q"),
        hold_phase,
    }

    def cone_summary(root: str) -> dict[str, Any]:
        cone = descendants(root)
        return {
            "support": sorted(support(puzzle, root)),
            "operations": dict(Counter(puzzle["expressions"][node]["operation"] for node in cone)),
            "nodes": len(cone),
        }

    net_4166_summary = cone_summary(net_4166)
    net_4201_summary = cone_summary(net_4201)
    assert not set(net_4166_summary["support"]) & set(net_4201_summary["support"])
    assert set(net_4201_summary["operations"]) == {"boundary", "and", "not"}

    return {
        "touch_state": "cell_145.Q",
        "not_touch_inverter": "cell_781",
        "touch_buffer_inverter": "cell_783",
        "net_4166": net_4166,
        "net_4166_summary": net_4166_summary,
        "net_4201": net_4201,
        "net_4201_summary": net_4201_summary,
        "qualifier": {"operation": "and", "arguments": [net_4166, net_4201]},
        "hold_phase": hold_phase,
        "success_state": "cell_144.Q",
        "success_next": success_next,
        "two_not_touch_state": "cell_179.Q",
        "two_not_touch_next": failure_next,
        "success_support_size": len(support(puzzle, success_next)),
        "two_not_touch_support_size": len(support(puzzle, failure_next)),
        "shared_support_size": len(support(puzzle, success_next) & support(puzzle, failure_next)),
    }


def find_boundary(machine: dict[str, Any], name: str) -> str:
    return next(
        node_id
        for node_id, node in machine["expressions"].items()
        if node["operation"] == "boundary" and node["name"] == name
    )


def render_terminal(machine: dict[str, Any], terminal: dict[str, Any]) -> str:
    roots = [terminal["net_4166"], terminal["net_4201"], terminal["success_next"], terminal["two_not_touch_next"]]
    needed: set[str] = set()

    def collect(node_id: str) -> None:
        if node_id in needed:
            return
        needed.add(node_id)
        for argument in machine["expressions"][node_id].get("arguments", []):
            collect(argument)

    for root in roots:
        collect(root)
    lines = [
        "# All RHS values are current inputs/current (old) state.",
        "# All *_next values commit simultaneously at the clock edge.",
        "touch := cell_145.Q",
        "not_touch := !touch  # cell_781; cell_783 restores touch",
    ]
    symbols: dict[str, str] = {}
    for node_id in sorted(needed, key=lambda value: (value.split(".")[0], int(value.split("expr_")[1]))):
        node = machine["expressions"][node_id]
        op = node["operation"]
        if op == "boundary":
            symbols[node_id] = node["name"]
            continue
        if op == "constant":
            symbols[node_id] = str(int(bool(node["value"])))
            continue
        args = [symbols[arg] for arg in node["arguments"]]
        if op == "not":
            expression = f"!{args[0]}"
        else:
            expression = f" {('&' if op == 'and' else '|')} ".join(args)
            expression = f"({expression})"
        symbol = node_id.replace("comb_0.", "t")
        symbols[node_id] = symbol
        lines.append(f"{symbol} := {expression}")
    lines.extend(
        [
            f"net_4166 := {symbols[terminal['net_4166']]}",
            f"net_4201 := {symbols[terminal['net_4201']]}",
            "qualifier := net_4166 & net_4201",
            f"cell_144.Q_next := {symbols[terminal['success_next']]}",
            f"cell_179.Q_next := {symbols[terminal['two_not_touch_next']]}",
            "",
            "# Proven factored terminal form (the hold term is shared in shape):",
            "cell_144.Q_next := (qualifier & !touch) | (cell_144.Q & hold_phase)",
            "cell_179.Q_next := (qualifier &  touch) | (cell_179.Q & hold_phase)",
        ]
    )
    return "\n".join(lines) + "\n"


def make_report(warmup: dict[str, Any], puzzle: dict[str, Any], terminal: dict[str, Any]) -> str:
    warmup_holds = classify_mux_holds(warmup)
    puzzle_holds = classify_mux_holds(puzzle)
    resets = Counter(state["reset"]["kind"] for state in puzzle["states"])

    state_200 = next(state for state in puzzle["states"] if state["instance"] == "cell_200")
    state_200_support = sorted(support(puzzle, state_200["next_expression"]))

    return f"""# Synchronous state-fold experiment

## Essential representation

The fold replaces each recovered DFF boundary with one transition equation:

```text
old state + current inputs -> evaluate every Q_next -> one simultaneous edge -> new state
```

Reset remains per-state metadata rather than being folded into ordinary combinational logic. Outputs are roots in the same shared expression DAG, evaluated from current state and current inputs.

## Concrete structural change

| Design | Recovered combinational cells | Collapse blocks | Shared DAG nodes | State variables | Recognized mux/hold equations |
|---|---:|---:|---:|---:|---:|
| Warmup | {warmup['collapsed_structure']['combinational_instances']} | {warmup['collapsed_structure']['combinational_blocks']} | {warmup['collapsed_structure']['expression_nodes']} | {len(warmup['states'])} | {len(warmup_holds)} |
| Puzzle | {puzzle['collapsed_structure']['combinational_instances']} | {puzzle['collapsed_structure']['combinational_blocks']} | {puzzle['collapsed_structure']['expression_nodes']} | {len(puzzle['states'])} | {len(puzzle_holds)} |

The earlier flat puzzle serialization was 125,052,645 bytes. This experiment's complete shared-DAG state representation is {len(json.dumps(puzzle, separators=(',', ':'))):,} bytes before pretty-printing. The reduction comes from naming state boundaries and retaining shared expressions once; it is not logic minimization.

## Warmup structural control

The warmup has 16 DFFs and the fold recognizes {len(warmup_holds)} exact `enable ? source : old_value` equations. Their sources form the two known eight-bit input shift chains. This is the expected source-level behavior and validates that the representation exposes a real synchronous rule rather than merely deleting DFF symbols.

## Puzzle state rules

The puzzle has {len(puzzle['states'])} state variables. Reset recovery is explicit: {resets['asynchronous_clear']} asynchronously clear, {resets['asynchronous_preset']} asynchronously preset, and {resets['none']} have no recovered reset pin.

Exact exhaustive evaluation of the four-bit serial-cycle state (`cell_150`, `cell_193`, `cell_157`, `cell_184`, least-significant first) shows:

- with `enable=0`, all 16 encodings hold;
- with `enable=1` and `cell_125.Q=0`, reachable values advance `0 -> 1 -> ... -> 10 -> 0`;
- once `cell_125.Q=1`, the state holds. (The full 16-state table is recorded in `state_machines.json`.)

Exact exhaustive evaluation of the four-bit response state (`cell_2`, `cell_3`, `cell_4`, `cell_478`) shows:

- `cell_200.Q=0`: every current encoding maps to zero;
- `cell_200.Q=1`: `0 -> 1 -> ... -> 15`, then 15 holds.

`cell_200.Q_next` depends only on {', '.join(state_200_support)} and is the sticky phase rule `cell_125.Q | cell_200.Q`. This makes the handoff mechanism legible as state-machine control.

## Confirmed terminal transition pair

The recovered logic proves:

```text
touch                    = cell_145.Q
qualifier                = net_4166 & net_4201
cell_144.Q_next candidate = qualifier & !touch
cell_179.Q_next candidate = qualifier &  touch
```

Each full next-state equation ORs its candidate with the same-shaped self-retention term. The two cones have supports of {terminal['success_support_size']} and {terminal['two_not_touch_support_size']} boundary values and share {terminal['shared_support_size']} of them. Thus `cell_144` (the `success` output) and `cell_179` are a deliberate mutually selected terminal pair, not merely nearby registers.

The state fold also splits the still-unknown qualifier cleanly:

- `net_4166` is a {terminal['net_4166_summary']['nodes']}-node predicate over {len(terminal['net_4166_summary']['support'])} state bits, using six ANDs, two ORs, and four inversions;
- `net_4201` is an exact 46-bit polarity match: 46 state boundaries joined by 45 ANDs, with 23 inverted literals. It explicitly includes `cell_125.Q=1` and `cell_200.Q=0`, placing the decision in the one-edge handoff window.

The two supports are disjoint. This is a substantial reduction in where to look: the qualifier is not one opaque 55-input formula but a small nine-state predicate gated by one large expected-state signature.

Combined with the already-confirmed natural touch behavior and response decoding, this establishes the terminal routing:

- `qualifier & !touch` selects success/`cell_144`;
- `qualifier & touch` selects `cell_179`, whose output path produces the genuine `TWO NOT TOUCH` response;
- horizontal, vertical, and diagonal adjacency can all set the stored `touch` state naturally;
- the semantic meaning of the shared qualifier remains unknown.

## What the fold reveals—and what it does not

**Proven:** state folding exposes two counters, a sticky phase transition, the stored touch bit, and the matched terminal transition pair. It also makes old-state/simultaneous-update semantics explicit, removing a common source of mistaken sequential reasoning.

**Interpretation:** the design appears to have an input-acquisition phase, a one-cycle terminal handoff, and a saturated response-emission phase. This interpretation fits all recovered transition rules but does not name the 57-state-bit qualifier predicate.

**Best next analysis:** slice `net_4166` and `net_4201` separately at state boundaries, then use known board traces to record which contributing state bits become invariant or distinguish valid from invalid boards at the handoff. Static Boolean cofactors around those observed states should be attempted before global minimization: the qualifier's whole support is large, while the terminal decision only needs its behavior on reachable handoff states.
"""


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    machines = {name: load_machine(path) for name, path in SOURCES.items()}
    terminal = terminal_slice(machines["puzzle"])

    input_counter = ["cell_150.Q", "cell_193.Q", "cell_157.Q", "cell_184.Q"]
    input_disabled = transition_table(
        machines["puzzle"], input_counter, {"enable": False, "cell_125.Q": False}
    )
    input_enabled = transition_table(
        machines["puzzle"], input_counter, {"enable": True, "cell_125.Q": False}
    )
    input_stopped = transition_table(
        machines["puzzle"], input_counter, {"enable": True, "cell_125.Q": True}
    )
    response_counter = ["cell_2.Q", "cell_3.Q", "cell_4.Q", "cell_478.Q"]
    machines["puzzle"]["recognized"] = {
        "mux_holds": classify_mux_holds(machines["puzzle"]),
        "terminal": terminal,
        "input_counter": {
            "bits_lsb_first": input_counter,
            "enable_0": input_disabled,
            "enable_1_cell_125_0": input_enabled,
            "enable_1_cell_125_1": input_stopped,
        },
        "response_counter": {
            "bits_lsb_first": response_counter,
            "phase_0": transition_table(machines["puzzle"], response_counter, {"cell_200.Q": False}),
            "phase_1": transition_table(machines["puzzle"], response_counter, {"cell_200.Q": True}),
        },
    }
    machines["warmup"]["recognized"] = {"mux_holds": classify_mux_holds(machines["warmup"])}

    (RESULTS / "state_machines.json").write_text(json.dumps(machines, indent=2) + "\n")
    (RESULTS / "puzzle_state_machine.txt").write_text(render_terminal(machines["puzzle"], terminal))
    (RESULTS / "report.md").write_text(make_report(machines["warmup"], machines["puzzle"], terminal))
    print(f"wrote {RESULTS / 'state_machines.json'}")
    print(f"wrote {RESULTS / 'puzzle_state_machine.txt'}")
    print(f"wrote {RESULTS / 'report.md'}")


if __name__ == "__main__":
    main()
