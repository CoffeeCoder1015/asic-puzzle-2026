from pathlib import Path
import sys

import klayout.db as kdb


GDS_FILE = "warmup/04_final.gds" 
if len(sys.argv) > 1:
    GDS_FILE = sys.argv[1]



gds_path = Path(GDS_FILE)
layout = kdb.Layout()
layout.read(str(gds_path))


top_cell = layout.top_cell()

shape_iterator = kdb.RecursiveShapeIterator(layout, top_cell, [])
layout_to_netlist = kdb.LayoutToNetlist(shape_iterator)


# Most polysilicon is ordinary conductive geometry. However, SKY130 uses
# datatype 15 ("poly.short") to mark a short implemented inside certain
# standard cells, such as conb:
#
#     global VPWR ── conb.VPWR ──[poly.short]── conb.HI ── local signal
#
# Treating the entire raw poly layer as an ordinary wire would cross that
# standard-cell boundary and incorrectly merge the local HI signal into
# the global VPWR net:
#
#     VPWR/HI ──────────────────────── one flattened power net
#
# Remove poly.short markers from the ordinary poly conductor so KLayout
# keeps the two external nets distinct. The standard-cell definition will
# later describe the conb relationship between those terminals.
raw_poly = layout_to_netlist.make_polygon_layer(
    layout.layer(66, 20),
    "raw_poly",
)
poly_short = layout_to_netlist.make_polygon_layer(
    layout.layer(66, 15),
    "poly_short",
)
poly = raw_poly - poly_short


# Polysilicon is the conductor used for transistor gates. A licon1 cut
# connects poly to li1 only where the non-conductive NPC marker overlaps it.
licon1 = layout_to_netlist.make_polygon_layer(layout.layer(66, 44), "licon1")
npc = layout_to_netlist.make_polygon_layer(layout.layer(95, 20), "npc")
poly_contact = licon1 & npc


# Each tuple describes:
#   readable name, GDS layer number, extracted polygon region
#
# Datatype 20 contains the physical conductor geometry.
conductive_layers = [
    ("li1", 67, layout_to_netlist.make_polygon_layer(layout.layer(67, 20), "li1")),
    ("met1", 68, layout_to_netlist.make_polygon_layer(layout.layer(68, 20), "met1")),
    ("met2", 69, layout_to_netlist.make_polygon_layer(layout.layer(69, 20), "met2")),
    ("met3", 70, layout_to_netlist.make_polygon_layer(layout.layer(70, 20), "met3")),
    ("met4", 71, layout_to_netlist.make_polygon_layer(layout.layer(71, 20), "met4")),
    ("met5", 72, layout_to_netlist.make_polygon_layer(layout.layer(72, 20), "met5")),
]

li1 = conductive_layers[0][2]
met1 = conductive_layers[1][2]
met2 = conductive_layers[2][2]
met3 = conductive_layers[3][2]
met4 = conductive_layers[4][2]
met5 = conductive_layers[5][2]


# Datatype 44 contains cuts connecting consecutive conductor layers.
mcon = layout_to_netlist.make_polygon_layer(
    layout.layer(67, 44),
    "mcon_li1_to_met1",
)
via1 = layout_to_netlist.make_polygon_layer(
    layout.layer(68, 44),
    "via_met1_to_met2",
)
via2 = layout_to_netlist.make_polygon_layer(
    layout.layer(69, 44),
    "via_met2_to_met3",
)
via3 = layout_to_netlist.make_polygon_layer(
    layout.layer(70, 44),
    "via_met3_to_met4",
)
via4 = layout_to_netlist.make_polygon_layer(
    layout.layer(71, 44),
    "via_met4_to_met5",
)


# Merge touching shapes within each physical layer.
#
# KLayout converts BOX, PATH, and POLYGON objects into occupied polygon
# regions before calculating connectivity.
for layer in (
    poly,
    poly_contact,
    li1,
    mcon,
    met1,
    via1,
    met2,
    via2,
    met3,
    via3,
    met4,
    via4,
    met5,
):
    layout_to_netlist.connect(layer)


# Join conductor layers only through the appropriate vertical cut layer.
layout_to_netlist.connect(poly, poly_contact)
layout_to_netlist.connect(poly_contact, li1)

layout_to_netlist.connect(li1, mcon)
layout_to_netlist.connect(mcon, met1)

layout_to_netlist.connect(met1, via1)
layout_to_netlist.connect(via1, met2)

layout_to_netlist.connect(met2, via2)
layout_to_netlist.connect(via2, met3)

layout_to_netlist.connect(met3, via3)
layout_to_netlist.connect(via3, met4)

layout_to_netlist.connect(met4, via4)
layout_to_netlist.connect(via4, met5)


# Datatype 5 contains textual net/pin labels. Connecting each text layer
# to its corresponding conductor lets KLayout produce names such as
# A, B, Y, VPWR, and VGND instead of anonymous numeric identifiers.
for conductor_name, gds_layer_number, conductor_region in conductive_layers:
    text_layer_index = layout.find_layer(gds_layer_number, 5)

    if text_layer_index is None:
        continue

    text_layer = layout_to_netlist.make_text_layer(
        text_layer_index,
        f"{conductor_name}_labels",
    )
    layout_to_netlist.connect(conductor_region, text_layer)


layout_to_netlist.extract_netlist()

# print()
# print("EXTRACTED PHYSICAL NETLIST")
# print(layout_to_netlist.netlist())


extracted_netlist = layout_to_netlist.netlist()

# A top-level port may connect to only one standard-cell pin. Convert named
# chip-level nets into explicit circuit pins so they are not mistaken for
# dangling nets merely because no second standard-cell endpoint exists.
extracted_netlist.make_top_level_pins()

top_circuit = extracted_netlist.circuit_by_name(top_cell.name)

instances = []

for subcircuit in top_circuit.each_subcircuit():
    referenced_circuit = subcircuit.circuit_ref()
    cell_type = referenced_circuit.name

    # Vias have already contributed to physical connectivity.
    # Only retain actual SKY130 standard-cell instances.
    if not cell_type.startswith("sky130_fd_sc_"):
        continue

    pins = {}

    for pin in referenced_circuit.each_pin():
        connected_net = subcircuit.net_for_pin(pin.id())

        if connected_net is None:
            continue

        # KLayout creates a net even for an isolated standard-cell pin. Retain
        # the pin only when its net reaches the chip boundary or another
        # standard-cell instance. Via subcircuits may also appear as endpoints,
        # but they describe the physical route rather than another logical
        # component.
        connects_to_top_level = connected_net.pin_count() > 0
        connects_to_another_standard_cell = False

        for endpoint in connected_net.each_subcircuit_pin():
            connected_subcircuit = endpoint.subcircuit()

            if (
                connected_subcircuit.id() != subcircuit.id()
                and connected_subcircuit.circuit_ref().name.startswith(
                    "sky130_fd_sc_"
                )
            ):
                connects_to_another_standard_cell = True
                break

        if connects_to_top_level or connects_to_another_standard_cell:
            pins[pin.name()] = connected_net.cluster_id

    instances.append({
        "cell_type": cell_type,
        "pins": pins,
    })


print("STANDARD-CELL INSTANCES")

for instance in instances:
    print(instance)
