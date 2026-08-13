from pathlib import Path
import argparse
import json
import re


DEFAULT_CATALOG = Path(__file__).with_name("sky130_logic.json")
TOKEN_PATTERN = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*|[01!&|^()]")


def parse_formula(source: str) -> tuple:
    tokens = TOKEN_PATTERN.findall(source)

    if "".join(tokens) != "".join(source.split()):
        raise ValueError(f"unsupported Liberty formula: {source!r}")

    position = 0

    def parse_or() -> tuple:
        nonlocal position
        expression = parse_xor()

        while position < len(tokens) and tokens[position] == "|":
            position += 1
            expression = ("or", expression, parse_xor())

        return expression

    def parse_xor() -> tuple:
        nonlocal position
        expression = parse_and()

        while position < len(tokens) and tokens[position] == "^":
            position += 1
            expression = ("xor", expression, parse_and())

        return expression

    def parse_and() -> tuple:
        nonlocal position
        expression = parse_unary()

        while position < len(tokens) and tokens[position] == "&":
            position += 1
            expression = ("and", expression, parse_unary())

        return expression

    def parse_unary() -> tuple:
        nonlocal position

        if position >= len(tokens):
            raise ValueError(f"unexpected end of formula: {source!r}")

        token = tokens[position]
        position += 1

        if token == "!":
            return ("not", parse_unary())
        if token == "(":
            expression = parse_or()
            if position >= len(tokens) or tokens[position] != ")":
                raise ValueError(f"unclosed parenthesis: {source!r}")
            position += 1
            return expression
        if token in {"0", "1"}:
            return ("constant", int(token))
        if TOKEN_PATTERN.fullmatch(token) and token not in "&|^)!":
            return ("variable", token)

        raise ValueError(f"unexpected token {token!r} in {source!r}")

    result = parse_or()

    if position != len(tokens):
        raise ValueError(
            f"unexpected token {tokens[position]!r} in {source!r}"
        )

    return result


def instantiate_formula(
    expression: tuple,
    variables: dict[str, tuple],
    source_instance: str,
    provenance: dict[tuple, set[str]],
) -> tuple:
    operation = expression[0]

    if operation == "variable":
        try:
            return variables[expression[1]]
        except KeyError as error:
            raise KeyError(
                f"formula refers to unconnected variable {expression[1]}"
            ) from error

    if operation in {"constant", "boundary"}:
        return expression

    instantiated = (
        operation,
        *(
            instantiate_formula(
                argument,
                variables,
                source_instance,
                provenance,
            )
            for argument in expression[1:]
        ),
    )
    provenance.setdefault(instantiated, set()).add(source_instance)
    return instantiated


def serialize_expression_graph(
    outputs: dict[int, tuple],
    provenance: dict[tuple, set[str]],
) -> tuple[list[dict], dict[tuple, str]]:
    ordered_expressions = []
    seen = set()

    def visit(expression: tuple) -> None:
        if expression in seen:
            return

        for argument in expression[1:]:
            if isinstance(argument, tuple):
                visit(argument)

        seen.add(expression)
        ordered_expressions.append(expression)

    for _, expression in sorted(outputs.items()):
        visit(expression)

    expression_ids = {
        expression: f"expr_{index}"
        for index, expression in enumerate(ordered_expressions)
    }
    nodes = []

    for expression in ordered_expressions:
        operation = expression[0]
        node = {
            "id": expression_ids[expression],
            "operation": operation,
        }

        if operation == "boundary":
            node["name"] = expression[1]
            node["net_id"] = expression[2]
        elif operation == "constant":
            node["value"] = expression[1]
        else:
            node["arguments"] = [
                expression_ids[argument] for argument in expression[1:]
            ]
            node["instances"] = sorted(provenance.get(expression, set()))

        nodes.append(node)

    return nodes, expression_ids


def build_logic_groups(
    outputs: dict[int, tuple],
    expression_ids: dict[tuple, str],
    provenance: dict[tuple, set[str]],
) -> list[dict]:
    calculations = {
        expression
        for expression in expression_ids
        if expression[0] not in {"boundary", "constant"}
    }
    reference_counts = {expression: 0 for expression in calculations}

    for expression in calculations:
        for argument in expression[1:]:
            if argument in reference_counts:
                reference_counts[argument] += 1

    output_roots = set(outputs.values())
    group_roots = output_roots | {
        expression
        for expression, count in reference_counts.items()
        if count > 1
    }
    ordered_roots = sorted(
        group_roots,
        key=lambda expression: int(expression_ids[expression].split("_")[1]),
    )
    group_ids = {
        expression: f"group_{index}"
        for index, expression in enumerate(ordered_roots)
    }
    outputs_by_root: dict[tuple, list[str]] = {}

    for net_id, expression in sorted(outputs.items()):
        outputs_by_root.setdefault(expression, []).append(str(net_id))

    groups = []

    for root in ordered_roots:
        owned_nodes = set()
        boundary_inputs = set()
        children = set()

        def collect(expression: tuple) -> None:
            if expression in owned_nodes:
                return
            if expression[0] in {"boundary", "constant"}:
                boundary_inputs.add(expression_ids[expression])
                return
            if expression != root and expression in group_roots:
                children.add(group_ids[expression])
                return

            owned_nodes.add(expression)

            for argument in expression[1:]:
                collect(argument)

        collect(root)
        instances = set()

        for expression in owned_nodes:
            instances.update(provenance.get(expression, set()))

        groups.append(
            {
                "id": group_ids[root],
                "root": expression_ids[root],
                "output_nets": outputs_by_root.get(root, []),
                "nodes": sorted(
                    (expression_ids[expression] for expression in owned_nodes),
                    key=lambda node_id: int(node_id.split("_")[1]),
                ),
                "inputs": sorted(
                    boundary_inputs,
                    key=lambda node_id: int(node_id.split("_")[1]),
                ),
                "children": sorted(
                    children,
                    key=lambda group_id: int(group_id.split("_")[1]),
                ),
                "instances": sorted(instances),
            }
        )

    return groups


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Collapse connected SKY130 combinational cells into exact "
            "Boolean formulas, stopping at sequential and chip boundaries."
        )
    )
    parser.add_argument("reconstruction", type=Path)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reconstruction = json.loads(
        args.reconstruction.read_text(encoding="utf-8")
    )
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))["cells"]
    output_path = args.output or (
        Path(__file__).with_name("results")
        / f"{reconstruction['design_name']}_collapsed.json"
    )

    instances = {
        instance["name"]: instance
        for instance in reconstruction["instances"]
    }
    cell_definitions = {
        name: catalog.get(
            instance["cell_type"].rsplit("_", 1)[0],
            {"kind": "physical", "outputs": {}},
        )
        for name, instance in instances.items()
    }
    top_pins = {
        pin["net_id"]: pin["name"]
        for pin in reconstruction["top_pins"]
    }

    net_endpoints: dict[int, list[tuple[str, str, str]]] = {}

    for instance_name, instance in instances.items():
        for pin_name, pin in instance["pins"].items():
            if pin["kind"] != "signal":
                continue

            net_endpoints.setdefault(pin["net_id"], []).append(
                (instance_name, pin_name, pin["direction"])
            )

    combinational = {
        name
        for name, definition in cell_definitions.items()
        if definition["kind"] == "combinational"
    }
    sequential = {
        name
        for name, definition in cell_definitions.items()
        if definition["kind"] == "sequential"
    }

    combinational_drivers: dict[int, list[tuple[str, str]]] = {}

    for instance_name in combinational:
        instance = instances[instance_name]
        definition = cell_definitions[instance_name]

        for output_pin in definition["outputs"]:
            pin = instance["pins"].get(output_pin)
            if pin is not None:
                combinational_drivers.setdefault(pin["net_id"], []).append(
                    (instance_name, output_pin)
                )

    for net_id, drivers in combinational_drivers.items():
        if len(drivers) > 1:
            raise RuntimeError(
                f"net {net_id} has multiple combinational drivers: {drivers}"
            )

    adjacency = {name: set() for name in combinational}

    for net_id, drivers in combinational_drivers.items():
        driver_name, _ = drivers[0]

        for destination_name, _, direction in net_endpoints[net_id]:
            if direction == "input" and destination_name in combinational:
                adjacency[driver_name].add(destination_name)
                adjacency[destination_name].add(driver_name)

    components = []
    unseen = set(combinational)

    while unseen:
        start = min(unseen)
        stack = [start]
        component = set()

        while stack:
            instance_name = stack.pop()
            if instance_name in component:
                continue

            component.add(instance_name)
            stack.extend(adjacency[instance_name] - component)

        unseen -= component
        components.append(component)

    def boundary_name(net_id: int, component: set[str]) -> str:
        if net_id in top_pins:
            return top_pins[net_id]

        sources = [
            f"{instance_name}.{pin_name}"
            for instance_name, pin_name, direction in net_endpoints[net_id]
            if direction == "output" and instance_name not in component
        ]

        if len(sources) == 1:
            return sources[0]
        if not sources:
            return f"net_{net_id}"

        raise RuntimeError(f"net {net_id} has multiple boundary sources: {sources}")

    parsed_functions = {
        (family, output_pin): parse_formula(function)
        for family, definition in catalog.items()
        for output_pin, function in definition["outputs"].items()
        if definition["kind"] == "combinational"
    }
    collapsed_blocks = []

    for component_number, component in enumerate(
        sorted(components, key=lambda item: min(item))
    ):
        expressions_by_net: dict[int, tuple] = {}
        provenance: dict[tuple, set[str]] = {}
        active_nets = set()
        boundary_inputs = {}

        def expression_for_net(net_id: int) -> tuple:
            if net_id in expressions_by_net:
                return expressions_by_net[net_id]
            if net_id in active_nets:
                raise RuntimeError(
                    f"combinational cycle encountered through net {net_id}"
                )

            drivers = combinational_drivers.get(net_id, [])

            if not drivers or drivers[0][0] not in component:
                name = boundary_name(net_id, component)
                boundary_inputs[name] = net_id
                expression = ("boundary", name, net_id)
                expressions_by_net[net_id] = expression
                return expression

            active_nets.add(net_id)
            instance_name, output_pin = drivers[0]
            instance = instances[instance_name]
            family = instance["cell_type"].rsplit("_", 1)[0]
            variables = {}

            for pin_name, pin in sorted(instance["pins"].items()):
                if pin["kind"] == "signal" and pin["direction"] == "input":
                    variables[pin_name] = expression_for_net(pin["net_id"])

            expression = instantiate_formula(
                parsed_functions[(family, output_pin)],
                variables,
                instance_name,
                provenance,
            )
            active_nets.remove(net_id)
            expressions_by_net[net_id] = expression
            return expression

        output_details: dict[str, dict[str, object]] = {}
        output_expressions = {}

        for net_id, drivers in sorted(combinational_drivers.items()):
            driver_name, output_pin = drivers[0]
            if driver_name not in component:
                continue

            destinations = []

            if net_id in top_pins:
                destinations.append(top_pins[net_id])

            for destination_name, pin_name, direction in net_endpoints[net_id]:
                if direction != "input" or destination_name in component:
                    continue
                destinations.append(f"{destination_name}.{pin_name}")

            if not destinations:
                continue

            expression = expression_for_net(net_id)
            output_expressions[net_id] = expression
            output_details[str(net_id)] = {
                "destinations": sorted(destinations),
                "source": {
                    "instance": driver_name,
                    "pin": output_pin,
                },
            }

        if output_details:
            nodes, expression_ids = serialize_expression_graph(
                output_expressions,
                provenance,
            )

            for net_id, expression in sorted(output_expressions.items()):
                output_details[str(net_id)]["expression"] = expression_ids[
                    expression
                ]

            collapsed_blocks.append(
                {
                    "name": f"comb_{component_number}",
                    "inputs": dict(sorted(boundary_inputs.items())),
                    "outputs": output_details,
                    "expression_nodes": nodes,
                    "logic_groups": build_logic_groups(
                        output_expressions,
                        expression_ids,
                        provenance,
                    ),
                    "instances": sorted(component),
                }
            )

    sequential_instances = []

    for instance_name in sorted(sequential):
        instance = instances[instance_name]
        definition = cell_definitions[instance_name]
        sequential_instances.append(
            {
                "name": instance_name,
                "cell_type": instance["cell_type"],
                "state": definition["state"],
                "pins": {
                    pin_name: pin["net_id"]
                    for pin_name, pin in instance["pins"].items()
                    if pin["kind"] == "signal"
                },
            }
        )

    collapsed = {
        "design_name": reconstruction["design_name"],
        "source_reconstruction": str(args.reconstruction),
        "top_pins": reconstruction["top_pins"],
        "sequential_instances": sequential_instances,
        "combinational_blocks": collapsed_blocks,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(collapsed, indent=2) + "\n",
        encoding="utf-8",
    )

    collapsed_instances = sum(
        len(block["instances"]) for block in collapsed_blocks
    )
    print(f"wrote {output_path}")
    print(f"sequential instances: {len(sequential_instances)}")
    print(f"combinational blocks: {len(collapsed_blocks)}")
    print(f"combinational instances collapsed: {collapsed_instances}")
    print(
        "block sizes: "
        + ", ".join(
            str(len(block["instances"])) for block in collapsed_blocks
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
