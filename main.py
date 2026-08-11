from pathlib import Path

import klayout.db as kdb


GDS_FILE = "warmup/04_final.gds"


gds_path = Path(GDS_FILE)
layout = kdb.Layout()
layout.read(str(gds_path))


top_cell = layout.top_cell()

shape_iterator = kdb.RecursiveShapeIterator(layout, top_cell, [])
layout_to_netlist = kdb.LayoutToNetlist(shape_iterator)


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

print()
print("EXTRACTED PHYSICAL NETLIST")
print(layout_to_netlist.netlist())
