import builtins
from pathlib import Path
import sys

from hal_py import FFComponent, NetlistFactory
from hal_plugins import dataflow


def trace_backwards(start_nets, group_by_gate_id):
    """Walk toward top inputs, stopping whenever another register is reached."""
    top_inputs = builtins.set()
    register_groups = builtins.set()
    combinational_gates = builtins.set()
    pending_nets = list(start_nets)
    visited_net_ids = builtins.set()

    while pending_nets:
        net = pending_nets.pop()

        if net.id in visited_net_ids:
            continue

        visited_net_ids.add(net.id)

        if net.is_global_input_net():
            top_inputs.add(net.name)

        for source in net.sources:
            gate = source.gate
            register_group = group_by_gate_id.get(gate.id)

            if register_group is not None:
                register_groups.add(register_group)
                continue

            combinational_gates.add(gate)
            pending_nets.extend(gate.fan_in_nets)

    return top_inputs, register_groups, combinational_gates


def trace_forwards(start_nets, group_by_gate_id):
    """Walk toward top outputs, stopping whenever another register is reached."""
    top_outputs = builtins.set()
    register_groups = builtins.set()
    combinational_gates = builtins.set()
    pending_nets = list(start_nets)
    visited_net_ids = builtins.set()

    while pending_nets:
        net = pending_nets.pop()

        if net.id in visited_net_ids:
            continue

        visited_net_ids.add(net.id)

        if net.is_global_output_net():
            top_outputs.add(net.name)

        for destination in net.get_destinations():
            gate = destination.gate
            register_group = group_by_gate_id.get(gate.id)

            if register_group is not None:
                register_groups.add(register_group)
                continue

            combinational_gates.add(gate)
            pending_nets.extend(gate.fan_out_nets)

    return top_outputs, register_groups, combinational_gates


def get_control_pin_names(gate, control_pin_types):
    """Read sequential controls from both pin tags and FF behavior."""
    control_pin_names = {
        pin.name for pin in gate.type.input_pins if pin.type in control_pin_types
    }

    # HAL 4.5.0's Python binding requires the otherwise-optional filter.
    for component in gate.type.get_components(lambda _component: True):
        if not FFComponent.is_class_of(component):
            continue

        control_pin_names.update(component.clock_function.variable_names)
        control_pin_names.update(component.async_reset_function.variable_names)
        control_pin_names.update(component.async_set_function.variable_names)

    return control_pin_names


if len(sys.argv) != 3:
    raise RuntimeError(
        "expected three arguments: the netlist, gate library, and output directory"
    )

# HAL places only the `--python-args` values in sys.argv; it does not
# prepend the script name as a normal Python interpreter would.
netlist_path = Path(sys.argv[0])
gate_library_path = Path(sys.argv[1])
output_directory = Path(sys.argv[2])
output_directory.mkdir(parents=True, exist_ok=True)

netlist = NetlistFactory.load_netlist(netlist_path, gate_library_path)

if netlist is None:
    raise RuntimeError("HAL could not load the netlist and gate library")

# The command-line DANA action omits this default configuration, so
# specify that we want HAL to find groups of flip-flops.
configuration = dataflow.Configuration(netlist).with_flip_flops()
result = dataflow.analyze(configuration)

if result is None:
    raise RuntimeError("DANA could not analyze the loaded netlist")

if not result.write_txt(output_directory):
    raise RuntimeError("DANA could not write its text result")

if not result.write_dot(output_directory):
    raise RuntimeError("DANA could not write its DOT result")

groups = result.get_groups()
print(f"DANA_GROUPS {len(groups)}")

for group_id, gates in sorted(groups.items()):
    gate_names = sorted(gate.name for gate in gates)
    print(f"GROUP {group_id} SIZE {len(gate_names)}")
    print("  " + " ".join(gate_names))


# DANA tells us which flip-flops form a register.  These searches describe
# the boundary around each register without crossing through another one.
group_by_gate_id = {
    gate.id: group_id
    for group_id, gates in groups.items()
    for gate in gates
}
control_pin_types = builtins.set(configuration.control_pin_types)
boundaries = {}
boundary_report = []

for group_id, gates in sorted(groups.items()):
    data_input_nets = builtins.set()
    control_input_nets = builtins.set()
    output_nets = builtins.set()

    for gate in gates:
        control_pin_names = get_control_pin_names(gate, control_pin_types)

        for endpoint in gate.fan_in_endpoints:
            if endpoint.get_pin().name in control_pin_names:
                control_input_nets.add(endpoint.get_net())
            else:
                data_input_nets.add(endpoint.get_net())

        output_nets.update(gate.fan_out_nets)

    data_inputs, data_groups, next_state_gates = trace_backwards(
        data_input_nets,
        group_by_gate_id,
    )
    control_inputs, control_groups, control_gates = trace_backwards(
        control_input_nets,
        group_by_gate_id,
    )
    top_outputs, output_groups, downstream_gates = trace_forwards(
        output_nets,
        group_by_gate_id,
    )

    boundaries[group_id] = downstream_gates

    boundary_lines = [
        f"GROUP {group_id}",
        f"  DATA_TOP_INPUTS {' '.join(sorted(data_inputs)) or '-'}",
        f"  DATA_REGISTER_GROUPS {' '.join(map(str, sorted(data_groups))) or '-'}",
        f"  CONTROL_TOP_INPUTS {' '.join(sorted(control_inputs)) or '-'}",
        f"  CONTROL_REGISTER_GROUPS {' '.join(map(str, sorted(control_groups))) or '-'}",
        f"  TOP_OUTPUTS {' '.join(sorted(top_outputs)) or '-'}",
        f"  OUTPUT_REGISTER_GROUPS {' '.join(map(str, sorted(output_groups))) or '-'}",
        "  NEXT_STATE_GATES "
        + (" ".join(sorted(gate.name for gate in next_state_gates)) or "-"),
        "  CONTROL_GATES "
        + (" ".join(sorted(gate.name for gate in control_gates)) or "-"),
        f"  DOWNSTREAM_GATE_COUNT {len(downstream_gates)}",
    ]

    print()
    print("\n".join(boundary_lines))
    boundary_report.extend(boundary_lines + [""])

group_ids = sorted(groups)

for index, first_group_id in enumerate(group_ids):
    for second_group_id in group_ids[index + 1 :]:
        shared_gates = boundaries[first_group_id] & boundaries[second_group_id]
        shared_line = (
            f"SHARED_DOWNSTREAM GROUPS {first_group_id} {second_group_id} "
            f"GATES {len(shared_gates)}"
        )
        print(shared_line)
        boundary_report.append(shared_line)


(output_directory / "boundaries.txt").write_text(
    "\n".join(boundary_report),
    encoding="utf-8",
)
