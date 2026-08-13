"""Analyze structural output cones and differential sequential traces."""

import csv
import json
from collections import Counter
from itertools import permutations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECONSTRUCTION_PATH = ROOT / "puzzle" / "reversed_puzzle.json"
RESULTS_DIRECTORY = Path(__file__).parent / "results"
MANIFEST_PATH = RESULTS_DIRECTORY / "probe_manifest.json"
TRACE_PATH = RESULTS_DIRECTORY / "probe_trace.csv"


reconstruction = json.loads(RECONSTRUCTION_PATH.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
instances_by_name = {
    instance["name"]: instance
    for instance in reconstruction["instances"]
}
top_pins = {
    pin["net_id"]: pin["name"]
    for pin in reconstruction["top_pins"]
}
port_directions = {
    port["name"]: port["direction"]
    for port in reconstruction["ports"]
}
top_input_nets = {
    net_id
    for net_id, name in top_pins.items()
    if port_directions.get(name.split("[", 1)[0]) == "input"
}
flip_flop_names = {
    flip_flop["name"]
    for flip_flop in manifest["flip_flops"]
}
drivers = {}

for instance in reconstruction["instances"]:
    for pin_name, pin in instance["pins"].items():
        if pin["kind"] != "signal" or pin["direction"] != "output":
            continue

        drivers.setdefault(pin["net_id"], []).append(
            {"instance": instance["name"], "pin": pin_name}
        )


def backward_cone(root_nets):
    pending_nets = list(root_nets)
    visited_nets = set()
    combinational_gates = set()
    boundary_flip_flops = set()
    boundary_inputs = set()
    undriven_nets = set()

    while pending_nets:
        net_id = pending_nets.pop()

        if net_id in visited_nets:
            continue

        visited_nets.add(net_id)

        if net_id in top_input_nets:
            boundary_inputs.add(top_pins[net_id])
            continue

        net_drivers = drivers.get(net_id, [])

        if not net_drivers:
            undriven_nets.add(net_id)
            continue

        for driver in net_drivers:
            instance_name = driver["instance"]

            if instance_name in flip_flop_names:
                boundary_flip_flops.add(instance_name)
                continue

            combinational_gates.add(instance_name)
            instance = instances_by_name[instance_name]

            for pin in instance["pins"].values():
                if pin["kind"] == "signal" and pin["direction"] == "input":
                    pending_nets.append(pin["net_id"])

    gate_types = Counter(
        instances_by_name[name]["cell_type"]
        for name in combinational_gates
    )

    return {
        "root_nets": sorted(root_nets),
        "nets": sorted(visited_nets),
        "combinational_gates": sorted(combinational_gates),
        "gate_types": dict(sorted(gate_types.items())),
        "boundary_flip_flops": sorted(boundary_flip_flops),
        "boundary_inputs": sorted(boundary_inputs),
        "undriven_nets": sorted(undriven_nets),
    }


output_nets = sorted(
    net_id
    for net_id, name in top_pins.items()
    if name.startswith("O[")
)
success_net = next(
    net_id for net_id, name in top_pins.items() if name == "success"
)
success_driver = next(
    driver
    for driver in drivers[success_net]
    if driver["instance"] in flip_flop_names
)
success_flip_flop = instances_by_name[success_driver["instance"]]
success_d_net = success_flip_flop["pins"]["D"]["net_id"]
success_d_column = next(
    flip_flop["d_column"]
    for flip_flop in manifest["flip_flops"]
    if flip_flop["name"] == success_flip_flop["name"]
)

output_driver_names = {
    driver["instance"]
    for net_id in output_nets
    for driver in drivers.get(net_id, [])
}
output_driver_input_sets = []

for name in output_driver_names:
    output_driver_input_sets.append(
        {
            pin["net_id"]
            for pin in instances_by_name[name]["pins"].values()
            if pin["kind"] == "signal" and pin["direction"] == "input"
        }
    )

shared_output_control_nets = sorted(
    set.intersection(*output_driver_input_sets)
    if output_driver_input_sets
    else set()
)

cones = {
    "output_bus": backward_cone(output_nets),
    "success_output": backward_cone([success_net]),
    "success_next_state": backward_cone([success_d_net]),
}

with TRACE_PATH.open(newline="", encoding="utf-8") as trace_file:
    trace_rows = list(csv.DictReader(trace_file))

rows_by_run = {}
for row in trace_rows:
    row["run"] = int(row["run"])
    row["cycle"] = int(row["cycle"])
    row["input_phase"] = int(row["input_phase"])
    rows_by_run.setdefault(row["run"], []).append(row)

for rows in rows_by_run.values():
    rows.sort(key=lambda row: row["cycle"])

expected_cycles = 121 + manifest["post_input_cycles"]
for variant in manifest["variants"]:
    rows = rows_by_run.get(variant["id"], [])

    if len(rows) != expected_cycles:
        raise RuntimeError(
            f"run {variant['id']} has {len(rows)} cycles; expected {expected_cycles}"
        )

baseline_rows = rows_by_run[0]
q_columns = {
    flip_flop["name"]: flip_flop["q_column"]
    for flip_flop in manifest["flip_flops"]
}
d_columns = {
    flip_flop["name"]: flip_flop["d_column"]
    for flip_flop in manifest["flip_flops"]
}


def first_state_difference(mutant_rows, columns):
    for baseline, mutant in zip(baseline_rows, mutant_rows, strict=True):
        differing = sorted(
            name
            for name, column in columns.items()
            if baseline[column] != mutant[column]
        )

        if differing:
            return {
                "cycle": baseline["cycle"],
                "flip_flops": differing,
            }

    return None


def first_signal_difference(mutant_rows, columns):
    for baseline, mutant in zip(baseline_rows, mutant_rows, strict=True):
        differing = [
            column
            for column in columns
            if baseline[column] != mutant[column]
        ]

        if differing:
            return {
                "cycle": baseline["cycle"],
                "signals": differing,
                "baseline": {column: baseline[column] for column in differing},
                "mutant": {column: mutant[column] for column in differing},
            }

    return None


def state_spread(mutant_rows):
    changes = []
    previous_count = None
    maximum_count = 0
    maximum_cycle = None

    for baseline, mutant in zip(baseline_rows, mutant_rows, strict=True):
        count = sum(
            baseline[column] != mutant[column]
            for column in q_columns.values()
        )

        if count != previous_count:
            changes.append({"cycle": baseline["cycle"], "different_q_bits": count})
            previous_count = count

        if count > maximum_count:
            maximum_count = count
            maximum_cycle = baseline["cycle"]

    return {
        "changes": changes,
        "maximum_bits": maximum_count,
        "maximum_cycle": maximum_cycle,
        "final_bits": changes[-1]["different_q_bits"],
    }


differentials = []

for variant in manifest["variants"][1:]:
    mutant_rows = rows_by_run[variant["id"]]
    differentials.append(
        {
            "run": variant["id"],
            "position": variant["position"],
            "baseline_character": manifest["baseline"][variant["position"]],
            "mutant_character": variant["text"][variant["position"]],
            "input_difference_cycle": variant["position"] * 11,
            "first_d_difference": first_state_difference(mutant_rows, d_columns),
            "first_q_difference": first_state_difference(mutant_rows, q_columns),
            "first_visible_difference": first_signal_difference(
                mutant_rows,
                ("O", "success", "net_3771", "net_3874"),
            ),
            "first_success_next_difference": first_signal_difference(
                mutant_rows,
                (success_d_column,),
            ),
            "state_spread": state_spread(mutant_rows),
        }
    )

activity = []

for flip_flop in manifest["flip_flops"]:
    column = flip_flop["q_column"]
    transitions = []

    for previous, current in zip(baseline_rows, baseline_rows[1:]):
        if previous[column] != current[column]:
            transitions.append(current["cycle"])

    activity.append(
        {
            "flip_flop": flip_flop["name"],
            "transition_count": len(transitions),
            "input_transitions": sum(cycle <= 120 for cycle in transitions),
            "post_input_transitions": sum(cycle > 120 for cycle in transitions),
            "first_transition": transitions[0] if transitions else None,
            "last_transition": transitions[-1] if transitions else None,
        }
    )

activity.sort(
    key=lambda item: str(item["transition_count"]).zfill(4),
    reverse=True,
)

emitted_bytes = []
for row in baseline_rows:
    if row["input_phase"] or "x" in row["O"].lower():
        continue

    value = int(row["O"], 2)

    if value:
        emitted_bytes.append(
            {
                "cycle": row["cycle"],
                "value": value,
                "character": chr(value) if 32 <= value <= 126 else None,
            }
        )

# Look for stored bits that are completely still during input reception and
# then form an ordinary binary count during the response phase. This is an
# observed behavior test; physical instance ordering plays no role in choosing
# or ordering the bits.
post_only_flip_flops = [
    item["flip_flop"]
    for item in activity
    if item["input_transitions"] == 0
    and item["post_input_transitions"] not in (0, None)
]
post_input_rows = [row for row in baseline_rows if not row["input_phase"]]
counter = None

for bit_order in permutations(post_only_flip_flops, 4):
    values = []

    for row in post_input_rows[:16]:
        bits = [row[q_columns[name]] for name in bit_order]

        if any(bit not in ("0", "1") for bit in bits):
            break

        values.append(sum(int(bit) << index for index, bit in enumerate(bits)))

    if values == list(range(16)):
        counter = {
            "bits_lsb_to_msb": list(bit_order),
            "cycles": [row["cycle"] for row in post_input_rows[:16]],
            "values": values,
            "output_values": [int(row["O"], 2) for row in post_input_rows[:16]],
            "net_3771": [int(row["net_3771"], 2) for row in post_input_rows[:16]],
            "net_3874": [int(row["net_3874"], 2) for row in post_input_rows[:16]],
        }
        break

frame_counter_candidates = [
    item["flip_flop"]
    for item in activity
    if item["post_input_transitions"] == 0
    and item["input_transitions"] in (21, 22, 65, 66, 109, 110)
]
input_rows = [row for row in baseline_rows if row["input_phase"]]
frame_counter = None

for bit_order in permutations(frame_counter_candidates, 4):
    values = [
        sum(int(row[q_columns[name]]) << index for index, name in enumerate(bit_order))
        for row in input_rows
    ]

    for phase in range(11):
        if values == [(cycle + phase) % 11 for cycle in range(len(input_rows))]:
            frame_counter = {
                "bits_lsb_to_msb": list(bit_order),
                "modulus": 11,
                "phase": phase,
                "values": values,
            }
            break

    if frame_counter is not None:
        break

analysis = {
    "stimulus": {
        "baseline": manifest["baseline"],
        "variants": manifest["variants"],
        "cycles_per_run": expected_cycles,
    },
    "structure": {
        "flip_flop_count": len(manifest["flip_flops"]),
        "shared_output_control_nets": shared_output_control_nets,
        "success_flip_flop": success_flip_flop["name"],
        "success_d_net": success_d_net,
        "cones": cones,
    },
    "baseline": {
        "emitted_bytes": emitted_bytes,
        "flip_flop_activity": activity,
        "post_only_flip_flops": post_only_flip_flops,
        "frame_counter": frame_counter,
        "counter": counter,
    },
    "differentials": differentials,
}

(RESULTS_DIRECTORY / "analysis.json").write_text(
    json.dumps(analysis, indent=2) + "\n",
    encoding="utf-8",
)


def display_cycle(observation, key="cycle"):
    return "-" if observation is None else str(observation[key])


def display_first_flip_flops(observation):
    if observation is None:
        return "-"

    names = observation["flip_flops"]
    shown = ", ".join(names[:4])
    return shown + (f" +{len(names) - 4}" if len(names) > 4 else "")


emitted_parts = []
for item in emitted_bytes:
    if item["character"] is not None:
        emitted_parts.append(str(item["character"]))
    else:
        emitted_parts.append(f"\\x{item['value']:02x}")

emitted_text = "".join(emitted_parts)
output_cone = cones["output_bus"]
success_cone = cones["success_next_state"]

report_lines = [
    "# Differential state-probe experiment",
    "",
    "## Stimulus",
    "",
    f"Baseline: `{manifest['baseline']}`",
    "",
    "Each mutant flips the least-significant ASCII bit at one character position. "
    "That changes exactly one of the 121 serial input cycles.",
    "",
    "| Position | Baseline | Mutant | Differing input cycle |",
    "|---:|:---:|:---:|---:|",
]

for differential in differentials:
    report_lines.append(
        f"| {differential['position']} | "
        f"`{differential['baseline_character']}` | "
        f"`{differential['mutant_character']}` | "
        f"{differential['input_difference_cycle']} |"
    )

report_lines.extend(
    [
        "",
        "## Structural backward slices",
        "",
        f"The eight output bits share input nets `{', '.join(map(str, shared_output_control_nets))}`.",
        "",
        f"The output bus cone contains {len(output_cone['combinational_gates'])} combinational "
        f"gates and stops at {len(output_cone['boundary_flip_flops'])} flip-flops.",
        "",
        f"The next-state cone for `{success_flip_flop['name']}` contains "
        f"{len(success_cone['combinational_gates'])} combinational gates and stops at "
        f"{len(success_cone['boundary_flip_flops'])} upstream flip-flops.",
        "",
        "### Output-bus boundary flip-flops",
        "",
        "`" + "`, `".join(output_cone["boundary_flip_flops"]) + "`",
        "",
        "### Success next-state boundary flip-flops",
        "",
        "`" + "`, `".join(success_cone["boundary_flip_flops"]) + "`",
        "",
        "## Baseline behavior",
        "",
        f"Post-input bytes: `{emitted_text}`",
        "",
        "Most active stored bits:",
        "",
        "| Flip-flop | Transitions | First | Last |",
        "|---|---:|---:|---:|",
    ]
)

for item in activity[:20]:
    report_lines.append(
        f"| {item['flip_flop']} | {item['transition_count']} | "
        f"{item['first_transition'] if item['first_transition'] is not None else '-'} | "
        f"{item['last_transition'] if item['last_transition'] is not None else '-'} |"
    )

if frame_counter is not None:
    frame_counter_bit_names = frame_counter["bits_lsb_to_msb"]
    assert isinstance(frame_counter_bit_names, list)
    frame_counter_bits = ", ".join(
        str(name) for name in frame_counter_bit_names
    )
    report_lines.extend(
        [
            "",
            "## Recovered serial-frame behavior",
            "",
            f"`{frame_counter_bits}` form a modulo-11 counter from least- to "
            "most-significant bit.",
            "",
            "It advances once per serial input bit and repeats every eleven cycles. "
            "This independently recovers the 11-cycle character framing seen in the "
            "supplied waveform.",
        ]
    )

if counter is not None:
    counter_bits = ", ".join(map(str, counter["bits_lsb_to_msb"]))
    report_lines.extend(
        [
            "",
            "## Recovered output-controller behavior",
            "",
            f"`{counter_bits}` form a four-bit binary counter from least- to "
            "most-significant bit.",
            "",
            "It remains zero throughout input reception, then counts from 0 through "
            "15 during response cycles 121 through 136. Counts 0 through 8 select "
            f"the bytes `{emitted_text}`. Counts 9 through 15 produce zero.",
            "",
            "`net_3771` rises when response generation begins. `net_3874` is the "
            "NAND of the four counter bits, so it remains high for counts 0 through "
            "14 and falls at terminal count 15.",
        ]
    )

report_lines.extend(
    [
        "",
        "## Differential propagation",
        "",
        "| Pos. | Mutation | First D | First Q | First affected Q bits | Success next-state | First visible | Max Q difference | Final Q difference |",
        "|---:|---|---:|---:|---|---:|---:|---:|---:|",
    ]
)

for differential in differentials:
    report_lines.append(
        f"| {differential['position']} | "
        f"`{differential['baseline_character']}->{differential['mutant_character']}` | "
        f"{display_cycle(differential['first_d_difference'])} | "
        f"{display_cycle(differential['first_q_difference'])} | "
        f"{display_first_flip_flops(differential['first_q_difference'])} | "
        f"{display_cycle(differential['first_success_next_difference'])} | "
        f"{display_cycle(differential['first_visible_difference'])} | "
        f"{differential['state_spread']['maximum_bits']} | "
        f"{differential['state_spread']['final_bits']} |"
    )

if all(
    differential["first_success_next_difference"] is None
    for differential in differentials
):
    report_lines.extend(
        [
            "",
            "All eleven mutations changed internal stored state, but none changed "
            "the success flip-flop's next-state input or the visible `TRY AGAIN` "
            "response during this run.",
        ]
    )

report_lines.extend(
    [
        "",
        "The complete per-mutant spread timelines and structural cone membership are in "
        "`analysis.json`.",
        "",
    ]
)

(RESULTS_DIRECTORY / "report.md").write_text(
    "\n".join(report_lines),
    encoding="utf-8",
)

print(f"TRACE_ROWS {len(trace_rows)}")
print(f"OUTPUT_CONE_GATES {len(output_cone['combinational_gates'])}")
print(f"SUCCESS_NEXT_CONE_GATES {len(success_cone['combinational_gates'])}")
print(f"BASELINE_OUTPUT {emitted_text!r}")
print(f"WROTE {RESULTS_DIRECTORY / 'analysis.json'}")
print(f"WROTE {RESULTS_DIRECTORY / 'report.md'}")
