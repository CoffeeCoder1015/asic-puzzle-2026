from pathlib import Path

import klayout.db as kdb


GDS_FILE = "warmup/04_final.gds"


gds_path = Path(GDS_FILE)
layout = kdb.Layout()
layout.read(str(gds_path))

print(f"FILE: {gds_path}")
print(f"DATABASE UNIT: {layout.dbu} microns")
print("TOP CELLS:", ", ".join(cell.name for cell in layout.top_cells()))

def describe_shape(shape: kdb.Shape) -> str:
    if shape.is_text():
        text = shape.text
        return f"TEXT value={text.string!r} position={text.trans.disp}"

    if shape.is_box():
        return f"BOX geometry={shape.box}"

    if shape.is_path():
        return f"PATH geometry={shape.path}"

    if shape.is_polygon():
        return f"POLYGON geometry={shape.polygon}"

    return f"UNKNOWN geometry={shape}"

for cell in layout.each_cell():
    print()
    print(f"CELL: {cell.name}")
    print(f"BOUNDING BOX: {cell.bbox()}")

    print("  References:",len(list( cell.each_inst() )))

    for layer_index in layout.layer_indexes():
        shapes = cell.shapes(layer_index)

        if shapes.is_empty():
            continue

        layer = layout.get_info(layer_index)
        shapes_list = list( shapes.each() )
        print("     layer",layer,"instances:",len(shapes_list))
        for shape in shapes_list:
            if shape.is_text() or shape.is_path():
                print("     ",describe_shape(shape))
