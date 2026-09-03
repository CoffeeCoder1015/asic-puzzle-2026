import ast
import json
from pathlib import Path
import re

import z3


breakdown_path = Path(__file__).parent.parent / "puzzle" / "reversed_puzzle.json"
cell_classifications = Path(__file__).parent.parent / "cell_classifications.json"

with breakdown_path.open() as file:
    gds_breakdown = json.load(file)

with cell_classifications.open() as file:
    cell_classes = json.load(file)

top_pins = gds_breakdown["top_pins"]
ports = gds_breakdown["ports"]
port_map = {p["name"]: p["direction"] for p in ports}

instances = {
    instance["name"]: instance
    for instance in gds_breakdown["instances"]
}
combinational_cells = set(cell_classes["combinational"])
sequential_cells = set(cell_classes["sequential"])


def get_cell_family_name(cell_type: str):
    return cell_type.rsplit("_", 1)[0]


def tag_cell_class(cell: dict):
    family = get_cell_family_name(cell["cell_type"])

    if family in sequential_cells:
        cell["kind"] = "sequential"
    elif family in combinational_cells:
        cell["kind"] = "combinational"
    else:
        cell["kind"] = "ignored"

    return cell


instances = {
    name: tag_cell_class(instance)
    for name, instance in instances.items()
}

def distinguish_cell_IO(cell_instance: dict):
    pins = cell_instance["pins"]
    signal_pins = dict( filter( lambda pin: pin[1]["kind"] == "signal", pins.items(),))
    input_pins = dict( filter( lambda pin: pin[1]["direction"] == "input", signal_pins.items(),))
    output_pins = dict( filter( lambda pin: pin[1]["direction"] == "output", signal_pins.items(),))
    return input_pins, output_pins


nets = {}

for instance in instances.values():
    if instance["kind"] == "ignored":
        continue

    inputs, outputs = distinguish_cell_IO(instance)

    for pin_name, pin_info in inputs.items():
        net_id = pin_info["net_id"]
        nets.setdefault(net_id, {})
        nets[net_id].setdefault("sinks", {})
        nets[net_id]["sinks"][instance["name"]] = {
            "kind": instance["kind"],
            "type": instance["cell_type"],
            "pin": pin_name,
        }

    for pin_name, pin_info in outputs.items():
        net_id = pin_info["net_id"]
        nets.setdefault(net_id, {})
        nets[net_id].setdefault("sources", {})
        nets[net_id]["sources"][instance["name"]] = {
            "kind": instance["kind"],
            "type": instance["cell_type"],
            "pin": pin_name,
        }

for pin in top_pins:
    net_id = pin["net_id"]
    pin_name = pin["name"]
    pin_canonical = pin_name.rsplit("[", 1)[0]
    direction = port_map.get(pin_canonical)

    pin_category = None

    match direction:
        case "input":
            pin_category = "sources"
        case "output":
            pin_category = "sinks"

    if pin_category is not None:
        nets.setdefault(net_id, {})
        nets[net_id].setdefault(pin_category, {})
        nets[net_id][pin_category]["top"] = {
            "kind": "combinational",
            "type": "top",
            "pin": pin_name,
        }

flipflop_initial_values = {
    "dfrtp": False,
    "dfstp": True,
    "dfxtp": False,
}

flipflops = {}

for instance_name, instance in instances.items():
    if instance["kind"] != "sequential":
        continue

    cell_type = get_cell_family_name(
        instance["cell_type"]
    ).removeprefix("sky130_fd_sc_hd__")

    flipflops[instance_name] = flipflop_initial_values[cell_type]


interconnects = {}

for instance_name in flipflops:
    input_net = instances[instance_name]["pins"]["D"]["net_id"]
    source_name, source_type = next(
        iter(nets[input_net]["sources"].items())
    )

    if source_name == "top":
        source_name = f"top_{source_type['pin']}"

    interconnects[instance_name] = source_name


inputs = {}

for pin in top_pins:
    pin_name = pin["name"]
    pin_canonical = pin_name.rsplit("[", 1)[0]

    if port_map.get(pin_canonical) != "input":
        continue

    inputs[f"top_{pin_name}"] = pin["net_id"]


outputs = {}

for pin in top_pins:
    pin_name = pin["name"]
    pin_canonical = pin_name.rsplit("[", 1)[0]

    if port_map.get(pin_canonical) != "output":
        continue

    outputs[f"top_{pin_name}"] = pin["net_id"]

cell_formulas = {key.removeprefix("sky130_fd_sc_hd__"):value for key,value in cell_classes["combinational"].items() }

constants = {}
call_funcs = {}

for instance_name, instance in instances.items():
    if instance["kind"] != "combinational":
        continue

    cell_type = get_cell_family_name(
        instance["cell_type"]
    ).removeprefix("sky130_fd_sc_hd__")

    inputs, cell_outputs = distinguish_cell_IO(instance)

    if cell_type == "conb":
        output_pin = next(iter(cell_outputs))
        constants[instance_name] = output_pin == "HI"
        continue

    arguments = []

    for pin_name, pin_info in inputs.items():
        source_name, source_type = next(
            iter(nets[pin_info["net_id"]]["sources"].items())
        )

        if source_name == "top":
            source_name = f"top_{source_type['pin']}"

        arguments.append((pin_name, source_name))

    call_funcs[instance_name] = (cell_type, arguments)

for output_name, net_id in outputs.items():
    source_name, source_type = next(
        iter(nets[net_id]["sources"].items())
    )

    if source_name == "top":
        source_name = f"top_{source_type['pin']}"

    call_funcs[output_name] = ("identity", [("X", source_name)])

# cell_1515, cell_209, and cell_28 each use cell_310 in their calculations,
# so all three are listed under cell_310.
#
# variable_name: [variables that directly depend on it]
# str: list[str]
#
# "cell_310": ["cell_1515", "cell_209", "cell_28"]
#
# cell_310
# ├──> cell_1515
# ├──> cell_209
# └──> cell_28
dependency_graph: dict[str, list[str]] = {}

def inline_calls_and_add_refs(x):
    variable_name = x[0]
    function,args = x[1]
    arg_map = dict(args)

    formula = cell_formulas[function]
    result = list(formula.keys())[0]
    expression = str(
        formula[result]
        .replace("!", "not ")
        .replace("&", " and ")
        .replace("|", " or ")
    )
    pattern =  re.compile(
    "|".join(re.escape(k) for k in sorted(arg_map, key=len, reverse=True))
    )
    expression = pattern.sub(lambda x: arg_map[x.group(0)],expression)

    vars_used = set()
    for _,x in args:
        sub_formula = call_funcs.get(x,[None])[0]
        if sub_formula is None:
            continue
        vars_used.add(x)

    arg_depdencies = [y[1] for y in args]
    referneced_dependencies =  list(filter(lambda x: call_funcs.get(x) != None,arg_depdencies))
    for cell in referneced_dependencies:
        dependency_graph.setdefault(cell,[])
        dependency_graph[cell].append(variable_name)

    call_funcs[variable_name] = expression


cell_formulas["identity"] = {"X":"X"}
for x in call_funcs.items():
    inline_calls_and_add_refs(x)


def get_instance_formula(
    instance_name: str,
    time: int,
) -> z3.BoolRef:
    expression = ast.parse(
        call_funcs[instance_name],
        mode="eval",
    ).body

    def build_expression(node: ast.expr) -> z3.BoolRef:
        if isinstance(node, ast.Name):
            if node.id in constants:
                return z3.BoolVal(constants[node.id])

            return z3.Bool(f"{node.id}_{time}")

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return z3.Not(build_expression(node.operand))

        if isinstance(node, ast.BoolOp):
            arguments = [
                build_expression(argument)
                for argument in node.values
            ]

            if isinstance(node.op, ast.And):
                return z3.And(arguments)

            if isinstance(node.op, ast.Or):
                return z3.Or(arguments)

        raise RuntimeError(
            "unsupported cell expression: "
            f"{ast.dump(node, include_attributes=False)}"
        )

    return (
        z3.Bool(f"{instance_name}_{time}")
        == build_expression(expression)
    )


def get_time_formulas(
    time: int,
) -> list[z3.BoolRef]:
    formulas = []

    for instance_name in call_funcs:
        formulas.append(
            get_instance_formula(instance_name, time)
        )

    return formulas


call_count = 121 + 30
solver = z3.Solver()

for time in range(call_count):
    for flipflop, default_value in flipflops.items():
        if time == 0:
            source_value = z3.BoolVal(default_value)
        else:
            source_name = interconnects[flipflop]
            source_value = z3.Bool(
                f"{source_name}_{time - 1}"
            )

        solver.add(
            z3.Bool(f"{flipflop}_{time}")
            == source_value
        )

    solver.add(
        *get_time_formulas(time)
    )
