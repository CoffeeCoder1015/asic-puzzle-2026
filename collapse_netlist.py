import json
from pathlib import Path
import re

import networkx as nx


breakdown_path = Path(__file__).parent / "puzzle" / "reversed_puzzle.json"
cell_classifications = Path(__file__).parent / "cell_classifications.json"

with breakdown_path.open() as file:
    gds_breakdown = json.load(file)

with cell_classifications.open() as file:
    cell_classes = json.load(file)

top_pins = gds_breakdown["top_pins"]
ports = gds_breakdown["ports"]
port_map = {p["name"]:p["direction"] for p in ports}

instances = {
    instance["name"]: instance
    for instance in gds_breakdown["instances"]
}
combinational_cells = set( cell_classes["combinational"] )
sequential_cells = set( cell_classes["sequential"] ) 

def get_cell_family_name(cell_type:str):
    return cell_type.rsplit("_",1)[0]

def tag_cell_class(cell:dict):
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

module_definition_lines = []
asic_setup_lines = []
state_snapshot_lines = []
next_state_update_lines = []

flipflop_initial_values = {
    "dfrtp": False,
    "dfstp": True,
    "dfxtp": False,
}

# Flip flop setup
for instance_name, instance in instances.items():
    if instance["kind"] != "sequential":
        continue

    cell_type = get_cell_family_name(
        instance["cell_type"]
    ).removeprefix("sky130_fd_sc_hd__")
    initial_value = flipflop_initial_values[cell_type]

    module_definition_lines.append(
        f"{instance_name}_next_state = {initial_value}"
    )
    asic_setup_lines.append(
        f"global {instance_name}_next_state"
    )
    state_snapshot_lines.append(
        f"{instance_name} = {instance_name}_next_state"
    )

# Output setup
output_ports = [
    port
    for port in ports
    if port["direction"] == "output"
]
return_values = []

for output_port in output_ports:
    output_name = f"top_{output_port['name']}"
    return_values.append(output_name)

    if "low" in output_port and "high" in output_port:
        output_width = output_port["high"] - output_port["low"] + 1
        asic_setup_lines.append(
            f"{output_name} = [False] * {output_width}"
        )
    else:
        asic_setup_lines.append(
            f"{output_name} = False"
        )

def distinguish_cell_IO(cell_instance:dict):
    pins = cell_instance["pins"]
    signal_pins = dict(filter(lambda x: x[1]["kind"] == "signal",pins.items()))
    input_pins = dict(filter(lambda x: x[1]["direction"] == "input",signal_pins.items()))
    output_pins = dict(filter(lambda x: x[1]["direction"] == "output",signal_pins.items()))
    return ( input_pins,output_pins )

nets = {}
for instance in instances.values():
    inputs,outputs = distinguish_cell_IO(instance)
    for pin_name, pin_info in inputs.items():
        net_id = pin_info["net_id"]
        nets.setdefault(net_id,{})
        nets[net_id].setdefault("sinks",{})
        nets[net_id]["sinks"][instance["name"]] = {
            "kind": instance["kind"],
            "type": instance["cell_type"],
            "pin": pin_name,
        }
    for pin_name, pin_info in outputs.items():
        net_id = pin_info["net_id"]
        nets.setdefault(net_id,{})
        nets[net_id].setdefault("sources",{})
        nets[net_id]["sources"][instance["name"]] = {
            "kind": instance["kind"],
            "type": instance["cell_type"],
            "pin": pin_name,
        }

for pin in top_pins:
    net_id = pin["net_id"]
    pin_name = pin["name"]
    pin_canonical = pin_name.rsplit("[",1)[0]
    direction = port_map.get(pin_canonical)

    pin_category = None
    match direction:
        case "input":
            pin_category = "sources"
        case "output":
            pin_category = "sinks"

    if pin_category is not None:
        nets.setdefault(net_id,{})
        nets[net_id].setdefault(pin_category,{})
        nets[net_id][pin_category]["top"] = {
            "kind": "combinational",
            "type": "top",
            "pin": pin_name,
        }

compute_graph = nx.MultiDiGraph()

for net_id, net_info in nets.items():
    # A logical net has one driving endpoint and any number of receiving
    # endpoints. Fanout therefore becomes multiple graph edges with the same
    # net ID.
    source_name, source_type = next(iter(net_info["sources"].items()))

    if source_name == "top":
        source_name = f"top_{source_type['pin']}"
        compute_graph.add_node(
            source_name,
            cell_type="top",
            kind="top",
            port_direction="input",
            pins={
                source_type["pin"]: {
                    "net_id": net_id,
                    "direction": "output",
                    "kind": "signal",
                    "supply": None,
                }
            },
        )

    source_cell_type = get_cell_family_name(
        source_type["type"]
    ).removeprefix("sky130_fd_sc_hd__")

    if source_cell_type == "conb":
        module_definition_lines.append(
            f"{source_name} = {source_type['pin'] == 'HI'}"
        )

    for sink_name, sink_type in net_info["sinks"].items():
        if sink_name == "top":
            sink_name = f"top_{sink_type['pin']}"
            compute_graph.add_node(
                sink_name,
                cell_type="top",
                kind="top",
                port_direction="output",
                pins={
                    sink_type["pin"]: {
                        "net_id": net_id,
                        "direction": "input",
                        "kind": "signal",
                        "supply": None,
                    }
                },
            )

        if sink_type["kind"] == "ignored":
            continue

        if sink_type["kind"] == "sequential":
            if sink_type["pin"] == "D":
                next_state_update_lines.append(
                    f"{sink_name}_next_state = {source_name}"
                )
            continue

        compute_graph.add_edge(
            source_name,
            sink_name,
            net_id=net_id,
            source_pin=source_type["pin"],
            sink_pin=sink_type["pin"],
        )

for instance_name, instance in instances.items():
    if instance_name not in compute_graph:
        continue

    compute_graph.nodes[instance_name].update(
        cell_type=instance["cell_type"],
        kind=instance["kind"],
        pins=instance["pins"],
    )


def get_cell_args(args):
    arguments = []
    for source,_,_,pin_map  in args:
        arg_name = pin_map["sink_pin"] # function argument which is being filled
        arg_value = f"{source}"
        arguments.append((arg_name,arg_value))
    return arguments

def format_cell_pin(node_name: str, pin_name: str,arguments) -> str:
    cell_type = get_cell_family_name(
        compute_graph.nodes[node_name]["cell_type"]
    ).removeprefix("sky130_fd_sc_hd__")

    arguments_str = ""

    if arguments:
        arguments_str += "("
        arguments_str += ", ".join(map(lambda x: f"{ x[0] }={x[1]}",arguments))
        arguments_str += ")"

    if cell_type == "top":
        if len(arguments) == 0:
            return node_name
        else:
            return f"{node_name}={arguments[0][1]}"
    
    return f"{node_name}={cell_type}{arguments_str}"


cell_formulas = {key.removeprefix("sky130_fd_sc_hd__"):value for key,value in cell_classes["combinational"].items() }
input_ports = [
    f"top_{pin['name']}"
    for pin in top_pins
    if port_map.get(pin["name"].rsplit("[", 1)[0]) == "input"
]

call_funcs = {}

for node_name in nx.topological_sort(compute_graph):
    node = compute_graph.nodes[node_name]

    if node["kind"] == "top":
        if node["port_direction"] == "output":
            arguments = get_cell_args(
                list(
                    compute_graph.in_edges(
                        node_name,
                        data=True,
                        keys=True,
                    )
                )
            )
            call_funcs[node_name] = ("identity",[ ("X",arguments[0][1]) ])
            # call_funcs.append(
            #     format_cell_pin(node_name, "", arguments)
            # )
        continue

    if node["kind"] != "combinational":
        continue

    cell_type = get_cell_family_name(
        node["cell_type"]
    ).removeprefix("sky130_fd_sc_hd__")

    if cell_type == "conb":
        continue

    arguments = get_cell_args(
        list(
            compute_graph.in_edges(
                node_name,
                data=True,
                keys=True,
            )
        )
    )

    call_funcs[node_name] = (cell_type,arguments)
    # call_funcs.append(
    #     format_cell_pin(node_name, "", arguments)
    # )
    # called_functions_and_args[cell_type] = [
    #     argument_name
    #     for argument_name, _ in arguments
    # ]

# def form_cell_function_def(x):
#     name = x[0]
#     args = x[1]

#     if name not in cell_formulas:
#         return ""
    
#     formula = cell_formulas[name]
#     result = list(formula.keys())[0]
#     expression = (
#         formula[result]
#         .replace("!", "not ")
#         .replace("&", " and ")
#         .replace("|", " or ")
#     )

#     function_str =  f"""def {name}({", ".join(args)}):
#     {result} = {expression}
#     return {result}"""

#     return function_str

# lib_functions = "\n".join(map(form_cell_function_def,called_functions_and_args.items()))

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

call_funcs_strs = [f"{key}={value}" for key,value in call_funcs.items()]


body_lines = (
    asic_setup_lines
    + state_snapshot_lines
    + call_funcs_strs
    + next_state_update_lines
    + [f"return {', '.join(return_values)}"]
)

body = f"""def asic({", ".join(input_ports)}):
    {"\n    ".join(body_lines)}
"""
program = "\n".join([
    # lib_functions,
    "\n".join(module_definition_lines),
    body,
])
with open("program.py","w+") as fio:
    fio.write(program)
