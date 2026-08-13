"""Use HAL/DANA to identify probable multi-bit registers.

HAL loads the recovered structural Verilog with the SKY130 Liberty library.
DANA then groups related flip-flops. Only those group memberships cross back
out of the HAL/Nix environment; main.py's reconstruction remains the source of
truth for components, pins, and electrical connectivity.
"""

import json
from pathlib import Path
import sys

from hal_py import NetlistFactory
from hal_plugins import dataflow


# HAL supplies only the values after --python-args in sys.argv.
if len(sys.argv) != 3:
    raise RuntimeError(
        "expected three arguments: the netlist, gate library, and JSON output"
    )

netlist_path = Path(sys.argv[0])
gate_library_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
output_path.parent.mkdir(parents=True, exist_ok=True)

netlist = NetlistFactory.load_netlist(netlist_path, gate_library_path)

if netlist is None:
    raise RuntimeError("HAL could not load the netlist and gate library")

configuration = dataflow.Configuration(netlist).with_flip_flops()
result = dataflow.analyze(configuration)

if result is None:
    raise RuntimeError("DANA could not analyze the loaded netlist")

# A group is a probable register and each member is one flip-flop instance.
# DANA's member ordering is deliberately not exported as inferred bit order.
registers = [
    {
        "id": group_id,
        "members": sorted(gate.name for gate in gates),
    }
    for group_id, gates in sorted(result.get_groups().items())
]

facts = {
    "source_netlist": str(netlist_path),
    "registers": registers,
}

output_path.write_text(
    json.dumps(facts, indent=2) + "\n",
    encoding="utf-8",
)

print(f"REGISTER_GROUPS {len(registers)}")
flip_flop_count = 0
for register in registers:
    flip_flop_count += len(register["members"])

print(f"FLIP_FLOPS {flip_flop_count}")
print(f"WROTE {output_path}")
