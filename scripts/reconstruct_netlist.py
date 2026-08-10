"""Recover a synthetic standard-cell netlist from the puzzle GDS routing."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path
import re
import sys

import klayout.db as kdb


# Each pair below is (GDS layer number, GDS datatype), not an (x, y) point.
# Datatype 20 contains drawn conductor geometry. Datatype 5 contains labels.
CONDUCTOR_LAYERS = (
    ("li1", (67, 20)),
    ("met1", (68, 20)),
    ("met2", (69, 20)),
    ("met3", (70, 20)),
    ("met4", (71, 20)),
    ("met5", (72, 20)),
)

LABEL_LAYERS = (
    ((67, 5), "li1"),
    ((68, 5), "met1"),
    ((69, 5), "met2"),
    ((70, 5), "met3"),
    ((71, 5), "met4"),
    ((72, 5), "met5"),
)

# A cut on each layer electrically bridges the named conductors.
VIA_CUT_LAYERS = (
    ((67, 44), "li1", "met1"),
    ((68, 44), "met1", "met2"),
    ((69, 44), "met2", "met3"),
    ((70, 44), "met3", "met4"),
    ((71, 44), "met4", "met5"),
)

POWER_PIN_NETS = {
    "VGND": "VGND",
    "VNB": "VGND",
    "VPWR": "VPWR",
    "VPB": "VPWR",
}

# The bucket width only limits polygon comparisons. It cannot alter whether
# two polygons connect because every candidate is checked with Polygon.touches.
SPATIAL_BUCKET_WIDTH_DBU = 2_000


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flood-fill SKY130 routing and emit a synthetic Verilog netlist."
    )
    parser.add_argument("gds", type=Path)
    args = parser.parse_args()

    if not args.gds.is_file():
        raise SystemExit(f"GDS file does not exist: {args.gds}")

    layout = kdb.Layout()
    layout.read(str(args.gds))

    top_cells = list(layout.top_cells())
    if len(top_cells) != 1:
        names = ", ".join(sorted(cell.name for cell in top_cells))
        raise SystemExit(
            f"expected exactly one top-level cell, found {len(top_cells)}: {names}"
        )
    top = top_cells[0]

    # Merge touching geometry independently on each planar conductor layer.
    # The remaining nodes are continuous two-dimensional conductor regions.
    planar_nodes: list[tuple[str, kdb.Polygon]] = []
    planar_ids_by_layer: dict[str, list[int]] = defaultdict(list)
    spatial_buckets: dict[tuple[str, int, int], set[int]] = defaultdict(set)

    def covered_tiles(box: kdb.Box):
        for tile_x in range(
            box.left // SPATIAL_BUCKET_WIDTH_DBU,
            box.right // SPATIAL_BUCKET_WIDTH_DBU + 1,
        ):
            for tile_y in range(
                box.bottom // SPATIAL_BUCKET_WIDTH_DBU,
                box.top // SPATIAL_BUCKET_WIDTH_DBU + 1,
            ):
                yield tile_x, tile_y

    for layer_name, (gds_layer, datatype) in CONDUCTOR_LAYERS:
        layer_index = layout.find_layer(gds_layer, datatype)
        if layer_index is None:
            continue

        region = kdb.Region(top.begin_shapes_rec(layer_index)).merged()
        for polygon in region.each():
            planar_id = len(planar_nodes)
            planar_nodes.append((layer_name, polygon))
            planar_ids_by_layer[layer_name].append(planar_id)

            for tile_x, tile_y in covered_tiles(polygon.bbox()):
                spatial_buckets[(layer_name, tile_x, tile_y)].add(planar_id)

    def polygons_touching(layer_name: str, polygon: kdb.Polygon) -> list[int]:
        candidates: set[int] = set()
        for tile_x, tile_y in covered_tiles(polygon.bbox()):
            candidates.update(spatial_buckets[(layer_name, tile_x, tile_y)])

        return [
            planar_id
            for planar_id in candidates
            if planar_nodes[planar_id][1].touches(polygon)
        ]

    # Vias are not retained as graph vertices. Each cut adds an edge between
    # the continuous planar regions immediately below and above it.
    via_adjacency: list[set[int]] = [set() for _ in planar_nodes]
    via_cut_count = 0
    via_anomalies: list[tuple[tuple[int, int], int, int]] = []

    for (gds_layer, datatype), lower_layer, upper_layer in VIA_CUT_LAYERS:
        layer_index = layout.find_layer(gds_layer, datatype)
        if layer_index is None:
            continue

        cut_region = kdb.Region(top.begin_shapes_rec(layer_index))
        for cut_polygon in cut_region.each():
            via_cut_count += 1
            lower_ids = polygons_touching(lower_layer, cut_polygon)
            upper_ids = polygons_touching(upper_layer, cut_polygon)

            if len(lower_ids) != 1 or len(upper_ids) != 1:
                via_anomalies.append(
                    ((gds_layer, datatype), len(lower_ids), len(upper_ids))
                )

            for lower_id in lower_ids:
                for upper_id in upper_ids:
                    via_adjacency[lower_id].add(upper_id)
                    via_adjacency[upper_id].add(lower_id)

    # Flood-fill the via edges. Same-layer connectivity was already collapsed
    # by Region.merged, so each result is one continuous three-dimensional wire.
    wire_by_planar_id = [-1] * len(planar_nodes)
    wire_members: list[list[int]] = []

    for start_id in range(len(planar_nodes)):
        if wire_by_planar_id[start_id] != -1:
            continue

        wire_id = len(wire_members)
        queue = deque([start_id])
        wire_by_planar_id[start_id] = wire_id
        members: list[int] = []

        while queue:
            planar_id = queue.popleft()
            members.append(planar_id)

            for neighbor_id in via_adjacency[planar_id]:
                if wire_by_planar_id[neighbor_id] == -1:
                    wire_by_planar_id[neighbor_id] = wire_id
                    queue.append(neighbor_id)

        wire_members.append(members)

    def wires_at_point(layer_name: str, point: kdb.Point) -> set[int]:
        point_box = kdb.Box(point, point)
        candidates: set[int] = set()

        for tile_x, tile_y in covered_tiles(point_box):
            candidates.update(spatial_buckets[(layer_name, tile_x, tile_y)])

        return {
            wire_by_planar_id[planar_id]
            for planar_id in candidates
            if planar_nodes[planar_id][1].touches(point_box)
        }

    missing_pins: list[tuple[str, str, kdb.Point]] = []
    split_pins: list[tuple[str, str, set[int]]] = []
    instances: list[dict[str, object]] = []

    for reference in top.each_inst():
        if not reference.cell.name.startswith("sky130_fd_sc_"):
            continue

        instance_name = f"u{len(instances):05d}"
        pin_wires: dict[str, set[int]] = defaultdict(set)
        power_pins: set[str] = set()

        for (gds_layer, datatype), layer_name in LABEL_LAYERS:
            layer_index = layout.find_layer(gds_layer, datatype)
            if layer_index is None:
                continue

            for shape in reference.cell.shapes(layer_index).each():
                if not shape.is_text():
                    continue

                pin_name = shape.text.string
                if pin_name in POWER_PIN_NETS:
                    power_pins.add(pin_name)
                    continue

                # A text displacement is a Vector, whose transformation omits
                # translation. Convert it to a Point before applying placement.
                displacement = shape.text.trans.disp
                local_point = kdb.Point(displacement.x, displacement.y)
                placed_point = reference.trans * local_point
                matching_wires = wires_at_point(layer_name, placed_point)

                if not matching_wires:
                    missing_pins.append((instance_name, pin_name, placed_point))
                pin_wires[pin_name].update(matching_wires)

        # Well/substrate labels are not on routing layers, but their standard
        # SKY130 connections are unambiguous supply pins.
        for gds_layer, datatype in ((64, 5), (64, 59)):
            layer_index = layout.find_layer(gds_layer, datatype)
            if layer_index is None:
                continue
            for shape in reference.cell.shapes(layer_index).each():
                if shape.is_text() and shape.text.string in POWER_PIN_NETS:
                    power_pins.add(shape.text.string)

        resolved_pins: dict[str, int | str | None] = {
            pin_name: POWER_PIN_NETS[pin_name]
            for pin_name in power_pins
        }

        for pin_name, matching_wires in pin_wires.items():
            if len(matching_wires) > 1:
                split_pins.append((instance_name, pin_name, matching_wires))
            resolved_pins[pin_name] = (
                min(matching_wires) if matching_wires else None
            )

        instances.append(
            {
                "name": instance_name,
                "cell_type": reference.cell.name,
                "pins": resolved_pins,
            }
        )

    # Direct text in the top cell names the external ports and supply straps.
    port_wires: dict[str, set[int]] = defaultdict(set)
    for (gds_layer, datatype), layer_name in LABEL_LAYERS:
        layer_index = layout.find_layer(gds_layer, datatype)
        if layer_index is None:
            continue

        for shape in top.shapes(layer_index).each():
            if not shape.is_text():
                continue

            displacement = shape.text.trans.disp
            point = kdb.Point(displacement.x, displacement.y)
            port_wires[shape.text.string].update(wires_at_point(layer_name, point))

    split_ports = {
        name: wires
        for name, wires in port_wires.items()
        if name not in POWER_PIN_NETS and len(wires) != 1
    }

    # Prefer recovered top-level names over synthetic internal net names.
    wire_names = {
        wire_id: f"net_{wire_id:05d}"
        for wire_id in range(len(wire_members))
    }

    for port_name, matching_wires in port_wires.items():
        if port_name in POWER_PIN_NETS or len(matching_wires) != 1:
            continue
        wire_names[next(iter(matching_wires))] = port_name

    used_internal_nets: set[str] = set()
    for instance in instances:
        pins = instance["pins"]
        assert isinstance(pins, dict)
        for connection in pins.values():
            if isinstance(connection, int):
                net_name = wire_names[connection]
                if net_name.startswith("net_"):
                    used_internal_nets.add(net_name)

    signal_port_names = sorted(
        name
        for name, matching_wires in port_wires.items()
        if name not in POWER_PIN_NETS and len(matching_wires) == 1
    )

    vector_bits: dict[str, set[int]] = defaultdict(set)
    scalar_ports: list[str] = []
    for port_name in signal_port_names:
        match = re.fullmatch(r"([A-Za-z_$][A-Za-z0-9_$]*)\[(\d+)\]", port_name)
        if match:
            vector_bits[match.group(1)].add(int(match.group(2)))
        else:
            scalar_ports.append(port_name)

    port_declarations = [f"inout wire {name}" for name in scalar_ports]
    for name, bits in sorted(vector_bits.items()):
        port_declarations.append(
            f"inout wire [{max(bits)}:{min(bits)}] {name}"
        )

    print(f"module {top.name} (")
    for index, declaration in enumerate(port_declarations):
        comma = "," if index + 1 < len(port_declarations) else ""
        print(f"    {declaration}{comma}")
    print(");")
    print()
    print("  supply0 VGND;")
    print("  supply1 VPWR;")

    if used_internal_nets:
        print()
        for net_name in sorted(used_internal_nets):
            print(f"  wire {net_name};")

    for instance in instances:
        name = instance["name"]
        cell_type = instance["cell_type"]
        pins = instance["pins"]
        assert isinstance(name, str)
        assert isinstance(cell_type, str)
        assert isinstance(pins, dict)

        print()
        print(f"  {cell_type} {name} (")
        sorted_pins = sorted(pins.items())
        for index, (pin_name, connection) in enumerate(sorted_pins):
            if isinstance(connection, int):
                expression = wire_names[connection]
            elif isinstance(connection, str):
                expression = connection
            else:
                expression = ""

            comma = "," if index + 1 < len(sorted_pins) else ""
            print(f"      .{pin_name}({expression}){comma}")
        print("  );")

    print()
    print("endmodule")

    print(
        f"{top.name}: {len(planar_nodes)} planar conductors, "
        f"{via_cut_count} cuts, {len(wire_members)} wires, "
        f"{len(instances)} standard-cell instances",
        file=sys.stderr,
    )
    if via_anomalies:
        print(
            f"warning: {len(via_anomalies)} via cuts did not touch exactly "
            "one conductor on each side",
            file=sys.stderr,
        )
    if missing_pins:
        print(
            f"warning: {len(missing_pins)} labeled pins did not touch routing",
            file=sys.stderr,
        )
        for instance_name, pin_name, point in missing_pins[:20]:
            print(f"  {instance_name}.{pin_name} at {point}", file=sys.stderr)
    if split_pins:
        print(
            f"warning: {len(split_pins)} labeled pins touched multiple wires",
            file=sys.stderr,
        )
    if split_ports:
        print(f"warning: unresolved top ports: {split_ports}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
