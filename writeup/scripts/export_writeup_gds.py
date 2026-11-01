"""Export real GDS polygons and verify the exported geometry.

Run from the repository root with ``uv run python writeup/scripts/export_writeup_gds.py``.
XY coordinates remain integer database units; layer heights are in micrometres.
"""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import klayout.db as kdb


ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_COMMIT = "2969b5e7b4004cc35875738ee53fa3043fd6b415"
UPSTREAM_LAYERS = (
    "https://github.com/TinyTapeout/tinytapeout_gds_viewer/blob/"
    f"{UPSTREAM_COMMIT}/src/pdk_layers.js"
)

# SKY130 physical stack from the upstream viewer, in its original z order.
PHYSICAL_LAYERS = (
    (235, 4, "substrate", -2.0, 0.0),
    (64, 20, "nwell", -2.0, 0.0),
    (65, 20, "diff", -0.5, 0.01),
    (66, 20, "poly", 0.0, 0.18),
    (66, 44, "licon", 0.0, 0.936),
    (67, 20, "li1", 0.936, 1.136),
    (67, 44, "mcon", 1.011, 1.376),
    (68, 20, "met1", 1.376, 1.736),
    (68, 44, "via", 1.73, 2.0),
    (69, 20, "met2", 2.0, 2.36),
    (69, 44, "via2", 2.36, 2.786),
    (70, 20, "met3", 2.786, 3.631),
    (70, 44, "via3", 3.631, 4.0211),
    (71, 20, "met4", 4.0211, 4.8661),
    (71, 44, "via4", 4.8661, 5.371),
    (72, 20, "met5", 5.371, 6.6311),
)


def polygon_record(shape: kdb.Shape) -> dict:
    """Turn a box, path, or polygon into its actual polygon boundary."""
    if not (shape.is_box() or shape.is_path() or shape.is_polygon()):
        raise ValueError(f"Cannot export physical shape: {shape}")
    polygon = shape.polygon
    return {
        "hull": [[point.x, point.y] for point in polygon.each_point_hull()],
        "holes": [
            [[point.x, point.y] for point in polygon.each_point_hole(index)]
            for index in range(polygon.holes())
        ],
    }


def reference_record(instance: kdb.Instance) -> dict:
    """Preserve an individual reference; this fixed layout has no arrays or scaling."""
    transform = instance.cplx_trans
    if instance.is_regular_array() or transform.mag != 1:
        raise ValueError("This exporter requires individual references with magnification 1")
    return {
        "cell": instance.cell.name,
        "x": transform.disp.x,
        "y": transform.disp.y,
        "rotation": transform.angle,
        "mirror": transform.is_mirror(),
    }


def make_polygon(record: dict) -> kdb.Polygon:
    polygon = kdb.Polygon([kdb.Point(*point) for point in record["hull"]])
    for hole in record["holes"]:
        polygon.insert_hole([kdb.Point(*point) for point in hole])
    return polygon


def verify_geometry(layout: kdb.Layout, document: dict) -> list[dict]:
    """Compare serialized hierarchy and renderer placements to the original GDS."""
    rebuilt = kdb.Layout()
    rebuilt.dbu = document["source"]["dbuMicrons"]
    cells = {cell["name"]: rebuilt.create_cell(cell["name"]) for cell in document["cells"]}
    for record in document["cells"]:
        cell = cells[record["name"]]
        for layer in record["layers"]:
            number, datatype = map(int, layer["id"].split("/"))
            layer_index = rebuilt.layer(number, datatype)
            for polygon in layer["polygons"]:
                cell.shapes(layer_index).insert(make_polygon(polygon))
        for reference in record["references"]:
            transform = kdb.ICplxTrans(
                1, reference["rotation"], reference["mirror"], reference["x"], reference["y"]
            )
            cell.insert(kdb.CellInstArray(cells[reference["cell"]].cell_index(), transform))

    comparisons = []
    top_name = document["source"]["topCell"]
    local_polygons = {
        (cell["name"], layer["id"]): [make_polygon(polygon) for polygon in layer["polygons"]]
        for cell in document["cells"] for layer in cell["layers"]
    }
    for layer in document["layers"]:
        source_index = layout.find_layer(layer["number"], layer["datatype"])
        export_index = rebuilt.find_layer(layer["number"], layer["datatype"])
        original = kdb.Region(layout.cell(top_name).begin_shapes_rec(source_index))
        exported = kdb.Region(rebuilt.cell(top_name).begin_shapes_rec(export_index))
        difference = original ^ exported
        if original.size() != exported.size() or original.area() != exported.area() or not difference.is_empty():
            raise ValueError(f"Export differs from source on layer {layer['id']}")
        placed = kdb.Region()
        for placement in document["placements"]:
            transform = kdb.ICplxTrans(
                1, placement["rotation"], placement["mirror"], placement["x"], placement["y"]
            )
            for polygon in local_polygons.get((placement["cell"], layer["id"]), []):
                placed.insert(polygon.transformed(transform))
        placement_difference = original ^ placed
        if original.size() != placed.size() or original.area() != placed.area() or not placement_difference.is_empty():
            raise ValueError(f"Flattened placements differ from source on layer {layer['id']}")
        comparisons.append({
            "id": layer["id"],
            "polygonCount": original.size(),
            "areaDatabaseUnitsSquared": original.area(),
            "xorAreaDatabaseUnitsSquared": difference.area(),
            "placementPolygonCount": placed.size(),
            "placementAreaDatabaseUnitsSquared": placed.area(),
            "placementXorAreaDatabaseUnitsSquared": placement_difference.area(),
        })
    return comparisons


def export_layout(source: Path) -> dict:
    layout = kdb.Layout()
    layout.read(str(source))
    top_cells = list(layout.top_cells())
    if len(top_cells) != 1:
        raise ValueError("Expected exactly one top cell")
    top = top_cells[0]
    bbox = top.bbox()
    layers = []
    for number, datatype, name, z_min, z_max in PHYSICAL_LAYERS:
        if layout.find_layer(number, datatype) is not None:
            layers.append({"id": f"{number}/{datatype}", "name": name,
                           "number": number, "datatype": datatype, "zMin": z_min, "zMax": z_max})

    cells = []
    for cell in sorted(layout.each_cell(), key=lambda candidate: candidate.name):
        cell_layers = []
        for layer in layers:
            index = layout.find_layer(layer["number"], layer["datatype"])
            polygons = [polygon_record(shape) for shape in cell.shapes(index).each() if not shape.is_text()]
            if polygons:
                cell_layers.append({"id": layer["id"], "polygons": polygons})
        cells.append({"name": cell.name, "layers": cell_layers,
                      "references": [reference_record(instance) for instance in cell.each_inst()]})

    # Flatten only placements. Every cell's local polygon coordinates remain shared.
    placements = []
    def collect_placements(cell: kdb.Cell, transform: kdb.ICplxTrans) -> None:
        placements.append({"cell": cell.name, "x": transform.disp.x, "y": transform.disp.y,
                           "rotation": transform.angle, "mirror": transform.is_mirror()})
        for instance in cell.each_inst():
            collect_placements(instance.cell, transform * instance.cplx_trans)
    collect_placements(top, kdb.ICplxTrans())

    document = {
        "schemaVersion": 1,
        "source": {"path": source.relative_to(ROOT).as_posix(),
                   "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                   "bytes": source.stat().st_size, "topCell": top.name, "dbuMicrons": layout.dbu,
                   "bbox": [bbox.left, bbox.bottom, bbox.right, bbox.top]},
        "provenance": {"geometry": "Original GDS polygons exported with KLayout; no invented mask geometry",
                       "layerStack": UPSTREAM_LAYERS, "layerStackLicense": "Apache-2.0",
                       "coordinates": "XY and placements are integer database units; layer Z is micrometres",
                       "omitted": "Nonphysical annotation, pin-label and marker datatypes; text labels"},
        "layers": layers, "cells": cells, "placements": placements,
    }
    comparisons = verify_geometry(layout, document)
    document["statistics"] = {
        "cells": len(cells), "references": sum(len(cell["references"]) for cell in cells),
        "placements": len(placements),
        "uniquePolygons": sum(len(layer["polygons"]) for cell in cells for layer in cell["layers"]),
        "cellTypeCounts": dict(sorted(Counter(placement["cell"] for placement in placements).items())),
        "verification": {"method": "Independently rebuild hierarchy and flattened placements; compare each to GDS counts, area and XOR",
                         "layers": comparisons},
    }
    return document


def projection_svg(document: dict, selected_layers: set[str] | None = None) -> str:
    """Render the same physical polygons as a compact, reusable SVG projection."""
    bbox = document["source"]["bbox"]
    x_min, y_min, x_max, y_max = bbox
    palette = ("#1b2520", "#33473a", "#6a9479", "#98bb9e", "#405f4b", "#b7d2bb",
               "#577a63", "#739d86", "#466d55", "#bbd7c4", "#577961", "#8bb99b",
               "#52765e", "#c8e1cf", "#789780", "#9ccfac")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x_min} {y_min} {x_max-x_min} {y_max-y_min}">',
             '<title>ASIC layout, actual physical mask geometry</title>',
             '<desc>Exact original GDS XY polygons. ' +
             ('Selected layers: li1, met1, met2, met3.' if selected_layers else 'All 16 physical layers.') + '</desc>',
             f'<rect x="{x_min}" y="{y_min}" width="{x_max-x_min}" height="{y_max-y_min}" fill="#172019"/>',
             '<defs>']
    identifiers = {}
    for cell_index, cell in enumerate(document["cells"]):
        for layer in cell["layers"]:
            if selected_layers is not None and layer["id"] not in selected_layers:
                continue
            identifier = f'cell-{cell_index}-{layer["id"].replace("/", "-")}'
            identifiers[(cell["name"], layer["id"])] = identifier
            commands = []
            for polygon in layer["polygons"]:
                for ring in [polygon["hull"], *polygon["holes"]]:
                    commands.append("M" + "L".join(f"{x},{y}" for x, y in ring) + "Z")
            parts.append(f'<path id="{identifier}" fill-rule="evenodd" d="{"".join(commands)}"/>')
    parts.extend(['</defs>', f'<g transform="translate(0 {y_min+y_max}) scale(1 -1)">'])
    for index, layer in enumerate(document["layers"]):
        if selected_layers is not None and layer["id"] not in selected_layers:
            continue
        parts.append(f'<g fill="{palette[index]}">')
        for placement in document["placements"]:
            identifier = identifiers.get((placement["cell"], layer["id"]))
            if identifier is None:
                continue
            mirror = -1 if placement["mirror"] else 1
            parts.append(f'<use href="#{identifier}" transform="translate({placement["x"]} {placement["y"]}) '
                         f'rotate({placement["rotation"]}) scale(1 {mirror})"/>')
        parts.append('</g>')
    parts.extend(['</g>', '</svg>'])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "warmup/04_final.gds")
    parser.add_argument("--output", type=Path, default=ROOT / "writeup/public/data/warmup-layout.json")
    parser.add_argument("--projection", type=Path, help="Optional SVG output path")
    args = parser.parse_args()
    document = export_layout(args.source.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, separators=(",", ":")) + "\n", encoding="utf-8")
    if args.projection is not None:
        args.projection.parent.mkdir(parents=True, exist_ok=True)
        args.projection.write_text(projection_svg(document, {"67/20", "68/20", "69/20", "70/20"}), encoding="utf-8")
    stats = document["statistics"]
    print(f"Wrote {args.output}: {stats['cells']} cells, {stats['references']} references, "
          f"{stats['uniquePolygons']} unique polygons; all {len(document['layers'])} physical layers match the GDS")


if __name__ == "__main__":
    main()
