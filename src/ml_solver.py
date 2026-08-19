from collections import deque
import json
from pathlib import Path

import networkx as nx


breakdown_path = Path(__file__).parent.parent / "puzzle" / "reversed_puzzle.json"
cell_classifications = Path(__file__).parent.parent / "cell_classifications.json"

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
previous_frame_dependencies: dict[str, str] = {}

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
                previous_frame_dependencies[
                    sink_name
                ] = source_name

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

def trace_static_dependencies(start_variables):
    pending_variables = deque(
        sorted(start_variables)
    )
    visited_variables = set()
    traced_variables = []

    while pending_variables:
        variable_name = pending_variables.popleft()

        if variable_name in visited_variables:
            continue

        visited_variables.add(variable_name)
        traced_variables.append(variable_name)

        pending_variables.extend(
            sorted(
                compute_graph.predecessors(
                    variable_name
                )
            )
        )

    return traced_variables


# Static circuit backtrace

target_variables = sorted(
    variable_name
    for variable_name, variable
    in compute_graph.nodes(data=True)
    if (
        variable["kind"] == "top"
        and variable["port_direction"] == "output"
    )
)

relevant_variables = trace_static_dependencies(
    target_variables
)


# Time-unrolled backtrace

def trace_relevant_frames(
    frame_count: int,
    target_frames: list[int],
) -> list[list[str]]:
    base_variables_by_frame = [
        set()
        for _ in range(frame_count)
    ]

    pending_variables_by_frame = [
        set()
        for _ in range(frame_count)
    ]

    for frame in target_frames:
        base_variables_by_frame[frame].update(
            relevant_variables
        )

    for frame in range(frame_count - 1, -1, -1):
        base_variables_by_frame[frame].update(
            trace_static_dependencies(
                pending_variables_by_frame[frame]
            )
        )

        if frame == 0:
            continue

        for variable_name in base_variables_by_frame[
            frame
        ]:
            previous_variable = (
                previous_frame_dependencies.get(
                    variable_name
                )
            )

            if previous_variable is not None:
                pending_variables_by_frame[
                    frame - 1
                ].add(previous_variable)

    return [
        [
            f"{variable_name}_{frame}"
            for variable_name in sorted(
                base_variables
            )
        ]
        for frame, base_variables
        in enumerate(base_variables_by_frame)
    ]


if __name__ == "__main__":
    print("\n".join(relevant_variables))
