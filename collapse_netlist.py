import json
from pathlib import Path


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

print(list( nets.items() )[0])
