from pathlib import Path

import klayout.db as kdb


GDS_FILE = "warmup/04_final.gds"


gds_path = Path(GDS_FILE)
layout = kdb.Layout()
layout.read(str(gds_path))

print(f"FILE: {gds_path}")
print(f"DATABASE UNIT: {layout.dbu} microns")
print("TOP CELLS:", ", ".join(cell.name for cell in layout.top_cells()))

for cell in layout.each_cell():
    print()
    print(f"CELL: {cell.name}")
    print(f"BOUNDING BOX: {cell.bbox()}")

    print("     References:",len(list( cell.each_inst() )))
    # for reference in cell.each_inst():
    #     print(
    #         "REFERENCE:",
    #         reference.cell.name,
    #         "TRANSFORM:",
    #         reference.trans,
    #     )

    for layer_index in layout.layer_indexes():
        shapes = cell.shapes(layer_index)
        if shapes.is_empty():
            continue

        layer = layout.get_info(layer_index)
        print("     instances:",layer,len(list( shapes.each() )))
        # for shape in shapes.each():
        #     print(f"LAYER: {layer.layer}/{layer.datatype} SHAPE: {shape}")
