def render_module_preamble(reconstruction):
    port_names = [port["name"] for port in reconstruction["ports"]]
    port_list = ",\n".join(f"    {name}" for name in port_names)

    port_declarations = []

    for port in reconstruction["ports"]:
        width = ""

        if "high" in port:
            width = f" [{port['high']}:{port['low']}]"

        port_declarations.append(
            f"    {port['direction']}{width} {port['name']}"
        )

    declaration_block = ";\n".join(port_declarations)
    top_net_ids = {pin["net_id"] for pin in reconstruction["top_pins"]}
    signal_net_ids = {
        pin["net_id"]
        for instance in reconstruction["instances"]
        for pin in instance["pins"].values()
        if pin["kind"] == "signal"
    }
    internal_net_ids = signal_net_ids - top_net_ids
    wire_block = "\n".join(
        f"    wire net_{net_id};" for net_id in sorted(internal_net_ids)
    )

    return f"""module {reconstruction["design_name"]} (
{port_list}
);

{declaration_block};
{wire_block}

"""


def render_instance(instance, top_pins):
    pin_connections = []

    for pin_name, pin in instance["pins"].items():
        if pin["kind"] == "power":
            continue

        signal_name = top_pins.get(pin["net_id"], f"net_{pin['net_id']}")
        pin_connections.append(f"        .{pin_name}({signal_name})")

    return f"""    {instance["cell_type"]} {instance["name"]} (
{",\n".join(pin_connections)}
);

"""
