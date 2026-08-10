"""Print the semantic contents of a GDS file."""

import argparse
from pathlib import Path

import klayout.db as kdb


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


def describe_instance(instance: kdb.Instance) -> str:
    transform = instance.dcplx_trans
    description = (
        f"REFERENCE cell={instance.cell.name!r} "
        f"origin={instance.trans.disp} "
        f"rotation={transform.angle} "
        f"mirrored={transform.is_mirror()} "
        f"magnification={transform.mag}"
    )

    if instance.is_regular_array():
        description += (
            f" columns={instance.na} rows={instance.nb}"
            f" column_step={instance.a} row_step={instance.b}"
        )

    return description


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print every structure, reference, and shape in a GDS file."
    )
    parser.add_argument("gds", type=Path)
    args = parser.parse_args()

    layout = kdb.Layout()
    layout.read(str(args.gds))

    print(f"FILE {args.gds}")
    print(f"DATABASE_UNIT_MICRONS {layout.dbu}")
    print("TOP_CELLS", *(cell.name for cell in layout.top_cells()))

    for cell in sorted(layout.each_cell(), key=lambda candidate: candidate.name):
        print()
        print(f"CELL {cell.name!r} BBOX {cell.bbox()}")

        for instance in cell.each_inst():
            print(" ", describe_instance(instance))

        for layer_index in layout.layer_indexes():
            layer = layout.get_info(layer_index)

            for shape in cell.shapes(layer_index).each():
                print(
                    f"  LAYER {layer.layer}/{layer.datatype}",
                    describe_shape(shape),
                )


if __name__ == "__main__":
    main()
