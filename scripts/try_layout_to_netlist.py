from pathlib import Path

import klayout.db as kdb


GDS_FILE = "../warmup/04_final.gds"
GDS_FILE = "../puzzle.gds"


gds_path = Path(GDS_FILE)
layout = kdb.Layout()
layout.read(str(gds_path))

top_cell = layout.top_cell()

print(f"FILE: {gds_path}")
print(f"DATABASE UNIT: {layout.dbu} microns")
print(f"TOP CELL: {top_cell.name}")


# Keep the original GDS hierarchy while extracting connectivity.
shape_iterator = kdb.RecursiveShapeIterator(layout, top_cell, [])
layout_to_netlist = kdb.LayoutToNetlist(shape_iterator)


# SKY130 conductor and cut layers used by the warmup routing stack.
li1 = layout_to_netlist.make_polygon_layer(layout.layer(67, 20), "li1")
mcon = layout_to_netlist.make_polygon_layer(
    layout.layer(67, 44),
    "mcon_li1_to_met1",
)
met1 = layout_to_netlist.make_polygon_layer(layout.layer(68, 20), "met1")
via1 = layout_to_netlist.make_polygon_layer(
    layout.layer(68, 44),
    "via_met1_to_met2",
)
met2 = layout_to_netlist.make_polygon_layer(layout.layer(69, 20), "met2")
via2 = layout_to_netlist.make_polygon_layer(
    layout.layer(69, 44),
    "via_met2_to_met3",
)
met3 = layout_to_netlist.make_polygon_layer(layout.layer(70, 20), "met3")
via3 = layout_to_netlist.make_polygon_layer(
    layout.layer(70, 44),
    "via_met3_to_met4",
)
met4 = layout_to_netlist.make_polygon_layer(layout.layer(71, 20), "met4")
via4 = layout_to_netlist.make_polygon_layer(
    layout.layer(71, 44),
    "via_met4_to_met5",
)
met5 = layout_to_netlist.make_polygon_layer(layout.layer(72, 20), "met5")


# Touching geometry is conductive within a layer.
for conductive_layer in (
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
    layout_to_netlist.connect(conductive_layer)


# Each cut layer joins only the conductor immediately below and above it.
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


layout_to_netlist.extract_netlist()

print()
print(layout_to_netlist.netlist())
