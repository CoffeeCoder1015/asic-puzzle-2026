import json
from pathlib import Path

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
sequential_cells = set( cell_classes["sequential"] )

def get_cell_family_name(cell_type:str):
    return cell_type.rsplit("_",1)[0]

def tag_cell_class(cell:dict):
    is_comb = get_cell_family_name(cell["cell_type"]) not in sequential_cells
    cell["kind"] = "combinational" if is_comb else "sequential"
    return cell

instances = {
    name: tag_cell_class(instance)
    for name, instance in instances.items()
}

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


def cell_function_args(cell_in_edges):
    args = []
    for source,sink,_,pin_map  in cell_in_edges:
        arg_name = pin_map["sink_pin"] # function argument which is being filled
        arg_value = f"{source}_{pin_map["source_pin"]}"
        args.append((arg_name,arg_value))
    return args

def format_cell_pin(node_name: str, pin_name: str) -> str:
    cell_type = get_cell_family_name(
        compute_graph.nodes[node_name]["cell_type"]
    ).removeprefix("sky130_fd_sc_hd__")
    node_parts = node_name.rsplit("_", 1)
    cell_id = node_parts[1] if len(node_parts) == 2 else ""

    args = list( compute_graph.in_edges(node_name,data=True,keys=True)   )
    arguments_str = ""
    arguments = cell_function_args(args)
    if arguments:
        arguments_str += "("
        arguments_str += ", ".join(map(lambda x: f"{ x[0] }={x[1]}",arguments))
        arguments_str += ")"
    
    return f"{cell_type}_{pin_name}_{cell_id}{arguments_str}"


def bfs_upstream(start_nodes: list[str]) -> None:
    """Traverse backward from sinks to sources (upstream)."""
    queue = list(start_nodes)
    visited = set(queue)
    while queue:
        current = queue.pop(0)
        neighbors = list(compute_graph.in_edges(current, data=True, keys=True))
        for source, _, _, meta in neighbors:
            source_pin = meta["source_pin"]
            current_pin = meta["sink_pin"]
            print(
                f"{format_cell_pin(current, current_pin)} <- {format_cell_pin(source, source_pin)}"
            )
            if source not in visited:
                visited.add(source)
                queue.append(source)


def bfs_downstream(start_nodes: list[str]) -> None:
    """Traverse forward from sources to sinks (downstream)."""
    queue = list(start_nodes)
    visited = set(queue)
    while queue:
        current = queue.pop(0)
        neighbors = list(compute_graph.out_edges(current, data=True, keys=True))
        for _, sink, _, meta in neighbors:
            source_pin = meta["source_pin"]
            sink_pin = meta["sink_pin"]
            print(
                f"{format_cell_pin(current, source_pin)} -> {format_cell_pin(sink, sink_pin)}"
            )
            if sink not in visited:
                visited.add(sink)
                queue.append(sink)


input_ports = [
        "top_I"
]

print("=== DOWNSTREAM BFS (From Inputs) ===")
bfs_downstream(input_ports)

output_ports = [
    f"top_{pin['name']}"
    for pin in top_pins
    if port_map.get(pin["name"].rsplit("[", 1)[0]) == "output"
]
print("\n=== UPSTREAM BFS (From Outputs) ===")
bfs_upstream(output_ports)



