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
instances = gds_breakdown["instances"]
sequential_cells = set( cell_classes["sequential"] )

def get_cell_family_name(cell_type:str):
    return cell_type.rsplit("_",1)[0]

def tag_cell_class(cell:dict):
    is_comb = get_cell_family_name(cell["cell_type"]) not in sequential_cells
    cell["kind"] = "combinational" if is_comb else "sequential"
    return cell

instances = list(map(tag_cell_class,instances))

def distinguish_cell_IO(cell_instance:dict):
    pins = cell_instance["pins"]
    signal_pins = dict(filter(lambda x: x[1]["kind"] == "signal",pins.items()))
    input_pins = dict(filter(lambda x: x[1]["direction"] == "input",signal_pins.items()))
    output_pins = dict(filter(lambda x: x[1]["direction"] == "output",signal_pins.items()))
    return ( input_pins,output_pins )

nets = {}
for instance in instances:
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

print(ports)
for pin in top_pins:
    print(pin)
    