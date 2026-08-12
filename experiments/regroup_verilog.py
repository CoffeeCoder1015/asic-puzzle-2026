"""Emit experimental hierarchy from structural graph communities.

This deliberately preserves every recovered standard-cell instance.  The only
transformation is to place cells from the same functional-graph community into
an inferred submodule and turn crossing nets into module ports.

The result tests whether graph communities resemble source-level module
instances; it does not claim to recover the author's original hierarchy.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).parent))

from fold_netlist_graph import (  # noqa: E402
    build_graphs,
    communities_for,
    fold_at_registers,
    functional_cell_graph,
    is_ff,
    parse_netlist,
)
from scripts.compare_netlists import (  # noqa: E402
    compare_graphs,
    load_catalog_families,
    parse_netlist as parse_comparison_netlist,
)


MODULE_HEADER_RE = re.compile(r"\A\s*(module\s+(\w+)\s*\(.*?\);)", re.DOTALL)
SOURCE_MODULE_RE = re.compile(
    r"\bmodule\s+(\w+)\s*\(.*?\);(.*?)\bendmodule\b",
    re.DOTALL,
)


def signal_sort_key(signal: str):
    match = re.fullmatch(r"(.*?)(?:\[(\d+)\]|_(\d+))?", signal)
    assert match is not None
    prefix, bracket_index, suffix_index = match.groups()
    index = bracket_index if bracket_index is not None else suffix_index
    return prefix, -1 if index is None else int(index)


def local_port_names(nets: set[str]) -> dict[str, str]:
    """Map arbitrary net spelling such as O[3] to unique Verilog identifiers."""
    result = {}
    used = set()
    for net in sorted(nets, key=signal_sort_key):
        base = re.sub(r"\W", "_", net).strip("_") or "signal"
        if base[0].isdigit():
            base = f"signal_{base}"
        candidate = base
        suffix = 2
        while candidate in used:
            candidate = f"{base}_{suffix}"
            suffix += 1
        used.add(candidate)
        result[net] = candidate
    return result


def signal_pins(cell) -> list[tuple[str, str]]:
    pins = []
    for pin, net in cell["pins"].items():
        definition = cell["pin_defs"].get(pin)
        if definition and definition["kind"] == "signal":
            pins.append((pin, net))
    return pins


def render_cell(name: str, cell, rename_net) -> str:
    connections = [
        f"        .{pin}({rename_net(net)})"
        for pin, net in signal_pins(cell)
    ]
    return (
        f"    {cell['type']} {name} (\n"
        + ",\n".join(connections)
        + "\n    );\n"
    )


def is_clock_infrastructure(member_cells: set[str], cells) -> bool:
    """Clock buffers are implementation infrastructure, not source hierarchy."""
    return bool(member_cells) and all(
        cells[name]["type"].split("__", 1)[-1] == "clkbuf"
        for name in member_cells
    )


def infer_blocks(cells, collapsed):
    functional = functional_cell_graph(collapsed, cells)
    communities = communities_for(functional)

    blocks = []
    infrastructure = set()
    for community in communities:
        member_cells = {
            node.removeprefix("cell:")
            for node in community
            if node.startswith("cell:")
        }
        if is_clock_infrastructure(member_cells, cells):
            infrastructure.update(member_cells)
            continue
        if member_cells:
            blocks.append(member_cells)

    assigned = set().union(*blocks) if blocks else set()
    ungrouped = set(cells) - assigned
    return blocks, infrastructure, ungrouped


def detect_hold_shift_chains(cells, cones):
    """Find mux/hold register paths without assuming one exact gate signature."""
    candidates = set()
    for node, cone in cones.items():
        if not node.startswith("cell:") or node not in cone["sources"]:
            continue
        families = Counter(
            cells[name]["type"].split("__", 1)[-1]
            for name in cone["combinational_cells"]
        )
        if families["mux2"] == 1 and len(cone["combinational_cells"]) <= 3:
            candidates.add(node)

    frequency = Counter(
        source
        for node in candidates
        for source in cones[node]["sources"]
        if source != node
    )
    common_controls = {source for source, count in frequency.items() if count >= 3}

    graph = nx.DiGraph()
    graph.add_nodes_from(candidates)
    serial_source = {}
    for target in candidates:
        data_sources = (
            set(cones[target]["sources"])
            - {target}
            - common_controls
        )
        if len(data_sources) != 1:
            continue
        source = data_sources.pop()
        if source in candidates:
            graph.add_edge(source, target)
        else:
            serial_source[target] = source

    chains = []
    for component in nx.weakly_connected_components(graph):
        subgraph = graph.subgraph(component)
        if len(component) < 3 or not nx.is_directed_acyclic_graph(subgraph):
            continue
        if not all(
            subgraph.in_degree(node) <= 1 and subgraph.out_degree(node) <= 1
            for node in component
        ):
            continue
        order = list(nx.topological_sort(subgraph))
        start_sources = sorted(
            set(cones[order[0]]["sources"])
            - {order[0]}
            - common_controls
        )
        chains.append(
            {
                "members": order,
                "serial_sources": start_sources,
                "common_controls": sorted(
                    set.intersection(*(set(cones[node]["sources"]) for node in order))
                    - set(order)
                ),
            }
        )
    return sorted(chains, key=lambda chain: len(chain["members"]), reverse=True)


def net_endpoints(ports, net_drivers, net_loads):
    endpoints = {}
    for net in set(net_drivers) | set(net_loads) | set(ports):
        endpoints[net] = {
            endpoint
            for endpoint, _pin in net_drivers.get(net, []) + net_loads.get(net, [])
        }
    return endpoints


def describe_block(
    index: int,
    members: set[str],
    cells,
    ports,
    endpoints,
    net_drivers,
    group_for_cell,
):
    used_nets = {
        net
        for name in members
        for _pin, net in signal_pins(cells[name])
    }
    boundary_nets = set()
    for net in used_nets:
        for endpoint in endpoints.get(net, set()):
            if endpoint.startswith("port:"):
                boundary_nets.add(net)
                break
            other_cell = endpoint.removeprefix("cell:")
            if group_for_cell.get(other_cell) != index:
                boundary_nets.add(net)
                break

    internal_nets = used_nets - boundary_nets
    directions = {}
    for net in boundary_nets:
        driven_inside = any(
            endpoint.startswith("cell:")
            and endpoint.removeprefix("cell:") in members
            for endpoint, _pin in net_drivers.get(net, [])
        )
        directions[net] = "output" if driven_inside else "input"

    return {
        "index": index,
        "members": members,
        "boundary_nets": boundary_nets,
        "internal_nets": internal_nets,
        "directions": directions,
        "top_ports": sorted(boundary_nets & set(ports), key=signal_sort_key),
    }


def emit_regrouped_verilog(
    netlist_path: Path,
    output_path: Path,
    cells,
    ports,
    blocks,
    ungrouped,
    net_drivers,
    net_loads,
):
    original = netlist_path.read_text()
    header_match = MODULE_HEADER_RE.search(original)
    if header_match is None:
        raise ValueError(f"could not parse module header from {netlist_path}")
    original_header, top_name = header_match.groups()

    group_for_cell = {
        name: index
        for index, members in enumerate(blocks)
        for name in members
    }
    endpoints = net_endpoints(ports, net_drivers, net_loads)
    descriptions = [
        describe_block(
            index,
            members,
            cells,
            ports,
            endpoints,
            net_drivers,
            group_for_cell,
        )
        for index, members in enumerate(blocks)
    ]

    lines = [
        "// Experimental hierarchy inferred from graph communities.",
        "// Standard-cell logic is unchanged; module boundaries are hypotheses.",
        "",
    ]

    for block in descriptions:
        index = block["index"]
        module_name = f"{top_name}__inferred_block_{index}"
        names = local_port_names(block["boundary_nets"])
        declarations = [
            f"    {block['directions'][net]} wire {names[net]}"
            for net in sorted(block["boundary_nets"], key=signal_sort_key)
        ]
        lines.append(f"module {module_name} (")
        lines.append(",\n".join(declarations))
        lines.append(");")
        for net in sorted(block["internal_nets"], key=signal_sort_key):
            lines.append(f"    wire {net};")
        if block["internal_nets"]:
            lines.append("")
        for name in sorted(block["members"], key=lambda value: int(value.split("_")[-1])):
            lines.append(
                render_cell(
                    name,
                    cells[name],
                    lambda net, names=names: names.get(net, net),
                ).rstrip()
            )
            lines.append("")
        lines.extend(["endmodule", ""])

    internal_in_modules = set().union(
        *(block["internal_nets"] for block in descriptions)
    ) if descriptions else set()
    all_signal_nets = {
        net
        for cell in cells.values()
        for _pin, net in signal_pins(cell)
    }
    top_internal_nets = all_signal_nets - set(ports) - internal_in_modules

    lines.extend([original_header, ""])
    for net in sorted(top_internal_nets, key=signal_sort_key):
        lines.append(f"    wire {net};")
    if top_internal_nets:
        lines.append("")

    for block in descriptions:
        index = block["index"]
        module_name = f"{top_name}__inferred_block_{index}"
        names = local_port_names(block["boundary_nets"])
        connections = [
            f"        .{names[net]}({net})"
            for net in sorted(block["boundary_nets"], key=signal_sort_key)
        ]
        lines.append(f"    {module_name} inferred_block_{index} (")
        lines.append(",\n".join(connections))
        lines.extend(["    );", ""])

    for name in sorted(ungrouped, key=lambda value: int(value.split("_")[-1])):
        lines.append(render_cell(name, cells[name], lambda net: net).rstrip())
        lines.append("")

    lines.append("endmodule")
    output_path.write_text("\n".join(lines) + "\n")
    return descriptions


def reference_hierarchy(source_path: Path | None, top_name: str):
    if source_path is None:
        return None
    source = source_path.read_text()
    modules = {name: body for name, body in SOURCE_MODULE_RE.findall(source)}
    known_modules = set(modules)
    top_body = modules.get(top_name, "")
    children = []
    for module_name in known_modules:
        for instance_name in re.findall(
            rf"\b{re.escape(module_name)}\s+(\w+)\s*\(", top_body
        ):
            children.append((module_name, instance_name))
    return {
        "definitions": sorted(modules),
        "top_children": sorted(children),
    }


def reference_cell_owners(
    reference_netlist: Path | None,
    recovered_netlist: Path,
    catalog: Path,
):
    """Map anonymous recovered cells back to warmup hierarchy by isomorphism."""
    if reference_netlist is None:
        return None
    catalog_families = load_catalog_families(catalog)
    _ports, reference_instances, reference_graph = parse_comparison_netlist(
        reference_netlist,
        catalog_families,
    )
    _ports, recovered_instances, recovered_graph = parse_comparison_netlist(
        recovered_netlist,
        catalog_families,
    )
    mapping = compare_graphs(reference_graph, recovered_graph)
    if mapping is None:
        return None

    owners = {}
    for reference_node, recovered_node in mapping.items():
        if reference_node[0] != "instance":
            continue
        reference_index = reference_node[1]
        recovered_index = recovered_node[1]
        if not isinstance(reference_index, int) or not isinstance(recovered_index, int):
            continue
        reference_name = reference_instances[reference_index][1]
        recovered_name = recovered_instances[recovered_index][1]
        owner = reference_name.strip().removeprefix("\\").split("/", 1)[0]
        owners[recovered_name] = owner
    return owners


def write_report(
    path: Path,
    netlist_path: Path,
    cells,
    blocks,
    infrastructure,
    ungrouped,
    descriptions,
    chains,
    reference,
    owners,
):
    group_for_cell = {
        f"cell:{name}": index
        for index, members in enumerate(blocks)
        for name in members
    }
    lines = [
        f"# Regrouped Verilog experiment: `{netlist_path}`",
        "",
        "Each inferred block is one Louvain community in the directed functional connectivity graph. Pure clock-buffer infrastructure remains at the top level.",
        "",
        "## Summary",
        "",
        f"- Recovered standard cells: **{len(cells)}**",
        f"- Inferred functional blocks: **{len(blocks)}**",
        f"- Clock-infrastructure cells left at top level: **{len(infrastructure)}**",
        f"- Total ungrouped cells left at top level: **{len(ungrouped)}**",
        "",
    ]
    if reference is not None:
        lines.extend(
            [
                "## Source-hierarchy comparison",
                "",
                f"- Source module definitions: **{len(reference['definitions'])}** — `{', '.join(reference['definitions'])}`",
                f"- Source child-module instances under the recovered top: **{len(reference['top_children'])}** — `{reference['top_children']}`",
                f"- Inferred functional block count: **{len(blocks)}**",
                "",
                "A matching count is only a hypothesis. The shift-chain overlap below checks whether community membership also resembles the source hierarchy.",
                "",
            ]
        )

    if owners is not None:
        lines.extend(
            [
                "## Exact warmup ownership through graph isomorphism",
                "",
                "The known synthesized warmup retains source-instance prefixes. Structural isomorphism maps each anonymous recovered cell back to one of those source instances.",
                "",
            ]
        )
        for index, members in enumerate(blocks):
            ownership = Counter(owners.get(name, "unmapped") for name in members)
            lines.append(f"- inferred_block_{index}: `{ownership.most_common()}`")
        lines.append("")

    lines.extend(["## Inferred blocks", ""])
    for block in descriptions:
        families = Counter(
            cells[name]["type"].split("__", 1)[-1]
            for name in block["members"]
        )
        lines.extend(
            [
                f"### inferred_block_{block['index']}",
                "",
                f"- Cells: **{len(block['members'])}**",
                f"- Flip-flops: **{sum(is_ff(cells[name]) for name in block['members'])}**",
                f"- Boundary nets: **{len(block['boundary_nets'])}**",
                f"- Direct top ports: `{block['top_ports']}`",
                f"- Dominant cell families: `{families.most_common(8)}`",
                f"- Members: `{', '.join(sorted(block['members'], key=lambda value: int(value.split('_')[-1])))}`",
                "",
            ]
        )

    lines.extend(["## Detected mux/hold chains", ""])
    if not chains:
        lines.append("No register chains were detected.")
    for chain in chains:
        community_path = [group_for_cell.get(node) for node in chain["members"]]
        lines.extend(
            [
                f"- **{len(chain['members'])}-bit chain** from `{chain['serial_sources']}`",
                f"  - Registers: `{' -> '.join(chain['members'])}`",
                f"  - Community path: `{community_path}`",
                f"  - Common controls: `{chain['common_controls']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The generated modules are connectivity communities, not recovered source declarations. A source module may be split across communities, and one community may combine logic from several source modules.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--netlist", type=Path, required=True)
    parser.add_argument("--pins", type=Path, default=Path("sky130/pin_definitions.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--reference-source", type=Path)
    parser.add_argument("--reference-netlist", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("sky130/cell_models.v"))
    args = parser.parse_args()

    cells, ports = parse_netlist(args.netlist, args.pins)
    _pin_graph, collapsed, net_drivers, net_loads = build_graphs(cells, ports)
    cones, _dependency = fold_at_registers(cells, ports, net_drivers)
    blocks, infrastructure, ungrouped = infer_blocks(cells, collapsed)
    chains = detect_hold_shift_chains(cells, cones)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    descriptions = emit_regrouped_verilog(
        args.netlist,
        args.output,
        cells,
        ports,
        blocks,
        ungrouped,
        net_drivers,
        net_loads,
    )
    header_match = MODULE_HEADER_RE.search(args.netlist.read_text())
    if header_match is None:
        raise ValueError(f"could not parse module header from {args.netlist}")
    top_name = header_match.group(2)
    write_report(
        args.report,
        args.netlist,
        cells,
        blocks,
        infrastructure,
        ungrouped,
        descriptions,
        chains,
        reference_hierarchy(args.reference_source, top_name),
        reference_cell_owners(args.reference_netlist, args.netlist, args.catalog),
    )

    emitted_cells = sum(len(block["members"]) for block in descriptions) + len(ungrouped)
    if emitted_cells != len(cells):
        raise AssertionError(f"emitted {emitted_cells} cells, expected {len(cells)}")
    print(f"wrote {args.output}")
    print(f"wrote {args.report}")
    print(f"inferred {len(blocks)} functional blocks; emitted {emitted_cells} cells")


if __name__ == "__main__":
    main()
