"""Organize reconstructed structural Verilog using DANA register groups."""

import argparse
import json
from pathlib import Path

from verilog_fragments import render_instance, render_module_preamble


parser = argparse.ArgumentParser(
    description="Render a reconstruction with probable registers grouped together."
)
parser.add_argument("reconstruction", type=Path)
parser.add_argument("register_groups", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()

reconstruction = json.loads(args.reconstruction.read_text(encoding="utf-8"))
register_facts = json.loads(args.register_groups.read_text(encoding="utf-8"))

instances_by_name = {
    instance["name"]: instance
    for instance in reconstruction["instances"]
}
grouped_names = set()
registers = []

for register in sorted(register_facts["registers"], key=lambda item: item["id"]):
    members = []

    for member_name in register["members"]:
        if member_name not in instances_by_name:
            raise RuntimeError(
                f"DANA register {register['id']} references unknown instance "
                f"{member_name!r}"
            )

        if member_name in grouped_names:
            raise RuntimeError(
                f"instance {member_name!r} belongs to more than one DANA register"
            )

        grouped_names.add(member_name)
        members.append(instances_by_name[member_name])

    registers.append({"id": register["id"], "members": members})

top_pins = {
    pin["net_id"]: pin["name"]
    for pin in reconstruction["top_pins"]
}


def has_signal_pin(instance):
    return any(pin["kind"] == "signal" for pin in instance["pins"].values())


verilog = render_module_preamble(reconstruction)

# Preserve every ordinary standard-cell instance first. Grouping changes only
# presentation order; the cell types and pin-to-net connections remain intact.
for instance in reconstruction["instances"]:
    if instance["name"] in grouped_names or not has_signal_pin(instance):
        continue

    verilog += render_instance(instance, top_pins)

for register in registers:
    verilog += f"""    // DANA REGISTER {register["id"]}
    // Width: {len(register["members"])} flip-flops.
    // Member order is not inferred bit order.
"""

    for instance in register["members"]:
        if has_signal_pin(instance):
            verilog += render_instance(instance, top_pins)

verilog += "endmodule\n"

args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(verilog, encoding="utf-8")

print(f"REGISTER_GROUPS {len(registers)}")
print(f"GROUPED_FLIP_FLOPS {len(grouped_names)}")
print(f"WROTE {args.output}")
