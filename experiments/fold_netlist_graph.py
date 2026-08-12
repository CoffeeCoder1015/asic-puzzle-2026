"""Throwaway structural experiment for folding a flat standard-cell netlist.

The script deliberately does not depend on the extraction pipeline.  It parses the
small Verilog subset emitted by the extractor, directs pins using the Sky130 pin
metadata, then traces combinational cones between primary inputs, flip-flops, and
primary outputs.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

import networkx as nx


INSTANCE_RE = re.compile(
    r"^\s*(sky130_fd_sc_hd__\w+)\s+(\w+)\s*\((.*?)^\s*\);",
    re.MULTILINE | re.DOTALL,
)
PIN_RE = re.compile(r"\.(\w+)\s*\(\s*([^()\s]+)\s*\)")
PORT_RE = re.compile(
    r"^\s*(input|output)\s+wire(?:\s+\[\s*(\d+)\s*:\s*(\d+)\s*\])?\s+(\w+)\s*[,;)]",
    re.MULTILINE,
)


def parse_netlist(verilog_path: Path, pin_path: Path):
    text = verilog_path.read_text()
    pin_defs = json.loads(pin_path.read_text())["cells"]

    ports: dict[str, str] = {}
    for direction, high, low, name in PORT_RE.findall(text):
        if high:
            lo, hi = sorted((int(low), int(high)))
            for bit in range(lo, hi + 1):
                ports[f"{name}[{bit}]"] = direction
        else:
            ports[name] = direction

    cells = {}
    missing_pin_defs = []
    for cell_type, name, body in INSTANCE_RE.findall(text):
        pins = dict(PIN_RE.findall(body))
        family = re.sub(r"_\d+$", "", cell_type)
        definitions = pin_defs.get(family)
        if definitions is None:
            missing_pin_defs.append((name, family))
            continue
        cells[name] = {"type": family, "pins": pins, "pin_defs": definitions}

    if missing_pin_defs:
        raise ValueError(f"missing pin definitions: {missing_pin_defs[:10]}")
    return cells, ports


def build_graphs(cells, ports):
    """Return a pin-faithful cell/net graph and a net-collapsed cell graph."""
    graph = nx.MultiDiGraph()
    net_drivers = defaultdict(list)
    net_loads = defaultdict(list)

    for port, direction in ports.items():
        graph.add_node(f"port:{port}", kind="port", direction=direction, label=port)
        graph.add_node(f"net:{port}", kind="net", label=port)
        if direction == "input":
            graph.add_edge(f"port:{port}", f"net:{port}", pin=port, role="port")
            net_drivers[port].append((f"port:{port}", port))
        else:
            graph.add_edge(f"net:{port}", f"port:{port}", pin=port, role="port")
            net_loads[port].append((f"port:{port}", port))

    for name, cell in cells.items():
        graph.add_node(
            f"cell:{name}", kind="cell", label=name, cell_type=cell["type"]
        )
        for pin, net in cell["pins"].items():
            definition = cell["pin_defs"].get(pin)
            if not definition or definition["kind"] != "signal":
                continue
            graph.add_node(f"net:{net}", kind="net", label=net)
            if definition["direction"] == "output":
                graph.add_edge(f"cell:{name}", f"net:{net}", pin=pin, role="drive")
                net_drivers[net].append((f"cell:{name}", pin))
            elif definition["direction"] == "input":
                graph.add_edge(f"net:{net}", f"cell:{name}", pin=pin, role="load")
                net_loads[net].append((f"cell:{name}", pin))

    collapsed = nx.MultiDiGraph()
    for node, data in graph.nodes(data=True):
        if data["kind"] != "net":
            collapsed.add_node(node, **data)
    for net in set(net_drivers) | set(net_loads):
        for driver, driver_pin in net_drivers[net]:
            for load, load_pin in net_loads[net]:
                collapsed.add_edge(
                    driver,
                    load,
                    net=net,
                    driver_pin=driver_pin,
                    load_pin=load_pin,
                )
    return graph, collapsed, net_drivers, net_loads


def is_ff(cell):
    return cell["type"].split("__", 1)[-1].startswith("df")


def trace_cone(target, start_net, cells, net_drivers):
    """Walk backward from one data/output net, stopping at sequential boundaries."""
    queue = deque([(start_net, 0)])
    visited_nets = set()
    combinational_cells = set()
    sources = set()
    max_depth = 0

    while queue:
        net, depth = queue.popleft()
        if net in visited_nets:
            continue
        visited_nets.add(net)
        max_depth = max(max_depth, depth)
        for driver, _pin in net_drivers.get(net, []):
            if driver.startswith("port:"):
                sources.add(driver)
                continue
            name = driver.removeprefix("cell:")
            if is_ff(cells[name]):
                sources.add(driver)
                continue
            if name in combinational_cells:
                continue
            combinational_cells.add(name)
            for pin, input_net in cells[name]["pins"].items():
                definition = cells[name]["pin_defs"].get(pin)
                if definition and definition["kind"] == "signal" and definition["direction"] == "input":
                    queue.append((input_net, depth + 1))

    return {
        "target": target,
        "start_net": start_net,
        "sources": sorted(sources),
        "combinational_cells": sorted(combinational_cells),
        "nets": sorted(visited_nets),
        "max_depth": max_depth,
    }


def fold_at_registers(cells, ports, net_drivers):
    cones = {}
    for name, cell in cells.items():
        if is_ff(cell) and "D" in cell["pins"]:
            node = f"cell:{name}"
            cones[node] = trace_cone(node, cell["pins"]["D"], cells, net_drivers)
    for port, direction in ports.items():
        if direction == "output":
            node = f"port:{port}"
            cones[node] = trace_cone(node, port, cells, net_drivers)

    dependency = nx.DiGraph()
    for target, cone in cones.items():
        dependency.add_node(target, kind="output" if target.startswith("port:") else "ff")
        for source in cone["sources"]:
            kind = "input" if source.startswith("port:") else "ff"
            dependency.add_node(source, kind=kind)
            dependency.add_edge(
                source,
                target,
                cone_cells=len(cone["combinational_cells"]),
                depth=cone["max_depth"],
            )
    return cones, dependency


def functional_cell_graph(collapsed, cells):
    """Remove clock/reset/control-only sequential arcs for functional clustering."""
    graph = nx.Graph()
    excluded_pins = {"CLK", "RESET_B", "SET_B"}
    for source, target, data in collapsed.edges(data=True):
        if data.get("load_pin") in excluded_pins:
            continue
        if source.startswith("cell:") and target.startswith("cell:"):
            graph.add_edge(source, target, net=data["net"])
        elif source.startswith("port:") or target.startswith("port:"):
            graph.add_edge(source, target, net=data["net"])
    for name in cells:
        graph.add_node(f"cell:{name}")
    return graph


def communities_for(graph):
    active = graph.subgraph([n for n in graph if graph.degree(n) > 0]).copy()
    return sorted(
        nx.community.louvain_communities(active, seed=2026, resolution=1.0),
        key=len,
        reverse=True,
    )


def boundary_communities(dependency):
    # Repeated dependencies in both directions are stronger than a one-way touch.
    undirected = nx.Graph()
    for source, target in dependency.edges:
        if dependency.nodes[source]["kind"] == "input" or dependency.nodes[target]["kind"] == "output":
            continue
        weight = undirected.get_edge_data(source, target, {}).get("weight", 0) + 1
        undirected.add_edge(source, target, weight=weight)
    return sorted(
        nx.community.louvain_communities(undirected, weight="weight", seed=2026),
        key=len,
        reverse=True,
    )


def cone_summary(label, node, cones, dependency, cells):
    cone = cones[node]
    source_kinds = Counter(dependency.nodes[s]["kind"] for s in cone["sources"])
    families = Counter(cells[c]["type"].split("__", 1)[-1] for c in cone["combinational_cells"])
    return {
        "label": label,
        "boundary": node,
        "direct_sources": dict(sorted(source_kinds.items())),
        "source_names": cone["sources"],
        "combinational_cell_count": len(cone["combinational_cells"]),
        "net_count": len(cone["nets"]),
        "logic_depth_upper_bound": cone["max_depth"],
        "top_cell_families": families.most_common(8),
        "cells": cone["combinational_cells"],
    }


def classify_register_shape(node, dependency, cones):
    ff_predecessors = {
        p for p in dependency.predecessors(node) if dependency.nodes[p]["kind"] == "ff"
    }
    self_feedback = node in ff_predecessors
    other_pred = ff_predecessors - {node}
    cone_size = len(cones[node]["combinational_cells"])
    if len(other_pred) == 1 and len(ff_predecessors) <= 2 and cone_size <= 3:
        return "shift-like"
    if self_feedback and len(other_pred) <= 2:
        return "state/counter-like"
    if len(ff_predecessors) >= 8:
        return "wide-state-dependent"
    if not ff_predecessors:
        return "input/constant-fed"
    return "mixed"


def detect_mux_hold_shift_banks(cells, cones):
    """Find chains whose bits all use the same mux+gate hold/shift structure."""
    candidates = set()
    for node, cone in cones.items():
        if not node.startswith("cell:") or node not in cone["sources"]:
            continue
        families = Counter(
            cells[name]["type"].split("__", 1)[-1]
            for name in cone["combinational_cells"]
        )
        if families == {"and2b": 1, "mux2": 1}:
            candidates.add(node)

    candidate_graph = nx.DiGraph()
    candidate_graph.add_nodes_from(candidates)
    for target in candidates:
        for source in cones[target]["sources"]:
            if source in candidates and source != target:
                candidate_graph.add_edge(source, target)

    banks = []
    for component in nx.weakly_connected_components(candidate_graph):
        subgraph = candidate_graph.subgraph(component)
        if len(component) < 3 or not nx.is_directed_acyclic_graph(subgraph):
            continue
        order = list(nx.topological_sort(subgraph))
        if not all(subgraph.in_degree(n) <= 1 and subgraph.out_degree(n) <= 1 for n in order):
            continue
        common_sources = set.intersection(*(set(cones[n]["sources"]) for n in order))
        first_external = sorted(
            set(cones[order[0]]["sources"])
            - set(order)
            - common_sources
            - {order[0]}
        )
        banks.append(
            {
                "size": len(order),
                "ordered_members": order,
                "common_boundaries": sorted(common_sources - set(order)),
                "serial_input_boundaries": first_external,
            }
        )
    return sorted(banks, key=lambda bank: bank["size"], reverse=True)


def write_markdown(result, path):
    stats = result["statistics"]
    lines = [
        "# Directed netlist folding experiment",
        "",
        "This is a structural experiment, not a recovered RTL claim. Pin direction comes from `sky130/pin_definitions.json`; flip-flop clock/reset/set arcs are excluded only from functional clustering.",
        "",
        "## Graph sizes",
        "",
    ]
    for key, value in stats.items():
        lines.append(f"- **{key.replace('_', ' ')}:** {value}")
    lines += ["", "## Primary-output cones", ""]
    for cone in result["output_cones"]:
        lines += [
            f"### {cone['label']}",
            "",
            f"- {cone['combinational_cell_count']} combinational cells, {cone['net_count']} nets, backward depth upper bound {cone['logic_depth_upper_bound']}",
            f"- Direct sequential/input boundaries: `{', '.join(cone['source_names'])}`",
            f"- Most common logic families: `{cone['top_cell_families']}`",
            "",
        ]
    success = result["success_checker"]
    generator = result["output_generator"]
    lines += [
        "## Folded functional blocks",
        "",
        "### Registered success checker",
        "",
        f"- `success` is the Q output of `{success['register']}`. Its D cone has {success['combinational_cell_count']} cells and direct support from {len(success['source_registers'])} FFs.",
        f"- Logic-family signature: `{success['cell_families']}`",
        f"- The checker includes self-feedback: `{success['self_feedback']}`.",
        "",
        "### Eight-bit output generator",
        "",
        f"- The union of O[7:0] contains {generator['unique_combinational_cells']} combinational cells fed directly by {len(generator['source_registers'])} FFs.",
        f"- All bits share {len(generator['common_source_registers'])} source FFs and {generator['common_combinational_cells']} combinational cells.",
        f"- Per-bit exclusive source FF: `{generator['exclusive_source_by_bit']}`",
        f"- SCC sizes inside its 23-FF support: `{generator['source_register_scc_sizes']}`",
        f"- Nontrivial source SCCs: `{[scc for scc in generator['source_register_sccs'] if len(scc) > 1]}`",
        "",
        "### Mux/hold shift bank",
        "",
    ]
    for bank in result["detected_shift_banks"]:
        lines.append(
            f"- {bank['size']} bits, ordered source-to-sink: `{' -> '.join(bank['ordered_members'])}`; "
            f"common boundaries `{bank['common_boundaries']}`; serial input `{bank['serial_input_boundaries']}`"
        )
    lines += ["", "## Register-dependency communities", ""]
    for community in result["register_communities"]:
        lines.append(
            f"- C{community['id']}: {community['size']} FFs; shapes {community['shape_counts']}; "
            f"directly feeds outputs {community['direct_outputs']}; members `{', '.join(community['members'])}`"
        )
    lines += ["", "## Full functional-graph communities", ""]
    for community in result["functional_communities"][:15]:
        lines.append(
            f"- F{community['id']}: {community['size']} nodes, {community['ff_count']} FFs, "
            f"ports {community['ports']}; dominant families {community['top_families']}"
        )
    lines += [
        "",
        "## Structural interpretation",
        "",
        *[f"- {finding}" for finding in result["findings"]],
        "",
        "## Limitations",
        "",
        "- Community detection is topology-based and has no physical placement or Boolean semantics.",
        "- A backward cone is the transitive combinational support of one boundary. Shared cells appear in multiple cones, so cone sizes cannot be summed as a partition.",
        "- `shift-like` and `state/counter-like` are structural hints, not proofs of behavior.",
        "- The depth number is a traversal upper bound in the recovered graph; reconvergent logic and combinational cycles can make it differ from timing depth.",
    ]
    path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--netlist", type=Path, default=Path("puzzle/reversed_puzzle.v"))
    parser.add_argument("--pins", type=Path, default=Path("sky130/pin_definitions.json"))
    parser.add_argument("--out", type=Path, default=Path("experiments/fold_graph_results"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    cells, ports = parse_netlist(args.netlist, args.pins)
    pin_graph, collapsed, net_drivers, net_loads = build_graphs(cells, ports)
    cones, dependency = fold_at_registers(cells, ports, net_drivers)
    functional = functional_cell_graph(collapsed, cells)
    register_communities = boundary_communities(dependency)
    cell_communities = communities_for(functional)

    ff_nodes = sorted(n for n in dependency if dependency.nodes[n]["kind"] == "ff")
    outputs = sorted(n for n in dependency if dependency.nodes[n]["kind"] == "output")
    shapes = {n: classify_register_shape(n, dependency, cones) for n in ff_nodes}
    shift_banks = detect_mux_hold_shift_banks(cells, cones)

    output_cones = [
        cone_summary(node.removeprefix("port:"), node, cones, dependency, cells)
        for node in outputs
    ]
    output_sources = {c["label"]: set(c["source_names"]) for c in output_cones}

    reg_community_rows = []
    for index, community in enumerate(register_communities):
        members = sorted(community)
        direct_outputs = []
        for output in outputs:
            if any(member in cones[output]["sources"] for member in members):
                direct_outputs.append(output.removeprefix("port:"))
        reg_community_rows.append(
            {
                "id": index,
                "size": len(members),
                "members": members,
                "shape_counts": dict(Counter(shapes[n] for n in members)),
                "direct_outputs": direct_outputs,
            }
        )

    cell_community_rows = []
    for index, community in enumerate(cell_communities):
        member_cells = [n.removeprefix("cell:") for n in community if n.startswith("cell:")]
        families = Counter(cells[n]["type"].split("__", 1)[-1] for n in member_cells)
        cell_community_rows.append(
            {
                "id": index,
                "size": len(community),
                "ff_count": sum(is_ff(cells[n]) for n in member_cells),
                "ports": sorted(n.removeprefix("port:") for n in community if n.startswith("port:")),
                "top_families": families.most_common(6),
                "members": sorted(community),
            }
        )

    overlap = {}
    for left in output_sources:
        for right in output_sources:
            if left < right:
                overlap[f"{left}|{right}"] = sorted(output_sources[left] & output_sources[right])

    ff_edges = [
        (a, b)
        for a, b in dependency.edges
        if dependency.nodes[a]["kind"] == dependency.nodes[b]["kind"] == "ff"
    ]
    ff_dependency = nx.DiGraph(ff_edges)
    register_sccs = sorted(
        (sorted(component) for component in nx.strongly_connected_components(ff_dependency)),
        key=len,
        reverse=True,
    )
    scc_sizes = [len(component) for component in register_sccs]
    undriven_nets = sorted(net for net in net_loads if not net_drivers.get(net))
    multidriver_nets = sorted(net for net, ds in net_drivers.items() if len(ds) > 1)

    success = next((c for c in output_cones if c["label"] == "success"), None)
    byte_outputs = [c for c in output_cones if c["label"].startswith("O[")]
    byte_union = set().union(*(set(c["cells"]) for c in byte_outputs)) if byte_outputs else set()
    if success is None or len(success["source_names"]) != 1:
        raise ValueError("expected success to be driven by exactly one boundary")
    success_register = success["source_names"][0]
    success_d_cone = cones[success_register]
    success_families = Counter(
        cells[name]["type"].split("__", 1)[-1]
        for name in success_d_cone["combinational_cells"]
    )
    success_sources = {
        source for source in success_d_cone["sources"] if source.startswith("cell:")
    }
    byte_source_sets = {
        cone["label"]: {s for s in cone["source_names"] if s.startswith("cell:")}
        for cone in byte_outputs
    }
    byte_cell_sets = {cone["label"]: set(cone["cells"]) for cone in byte_outputs}
    byte_sources = set().union(*byte_source_sets.values())
    common_byte_sources = set.intersection(*byte_source_sets.values())
    common_byte_cells = set.intersection(*byte_cell_sets.values())
    exclusive_sources = {
        bit: sorted(sources - set().union(*(other for name, other in byte_source_sets.items() if name != bit)))
        for bit, sources in byte_source_sets.items()
    }
    byte_dependency = nx.DiGraph(
        (a, b)
        for a, b in dependency.edges
        if a in byte_sources and b in byte_sources
    )
    byte_sccs = sorted(
        (sorted(component) for component in nx.strongly_connected_components(byte_dependency)),
        key=len,
        reverse=True,
    )
    byte_scc_sizes = [len(component) for component in byte_sccs]

    success_checker = {
        "register": success_register,
        "combinational_cell_count": len(success_d_cone["combinational_cells"]),
        "net_count": len(success_d_cone["nets"]),
        "logic_depth_upper_bound": success_d_cone["max_depth"],
        "source_registers": sorted(success_sources),
        "self_feedback": success_register in success_sources,
        "cell_families": success_families.most_common(),
        "cells": success_d_cone["combinational_cells"],
    }
    output_generator = {
        "unique_combinational_cells": len(byte_union),
        "source_registers": sorted(byte_sources),
        "common_source_registers": sorted(common_byte_sources),
        "common_combinational_cells": len(common_byte_cells),
        "exclusive_source_by_bit": exclusive_sources,
        "source_register_scc_sizes": byte_scc_sizes,
        "source_register_sccs": byte_sccs,
        "cells": sorted(byte_union),
    }
    findings = [
        f"The success pin is the Q output of {success_register}; its next-state/predicate cone is {len(success_d_cone['combinational_cells'])} cells with {len(success_sources)} direct FF inputs and an AND-heavy signature {success_families.most_common(6)}.",
        f"The eight O cones together contain {len(byte_union)} unique combinational cells driven by {len(byte_sources)} FFs. Every bit shares {len(common_byte_sources)} FF inputs and {len(common_byte_cells)} logic cells, then has a bit-specific branch.",
        f"The success predicate and O generator share {len(set(success_d_cone['combinational_cells']) & byte_union)} combinational cells and {len(success_sources & byte_sources)} direct FF sources.",
        f"A {shift_banks[0]['size']}-bit mux/hold chain was recovered from I through {' -> '.join(shift_banks[0]['ordered_members'])}; every stage shares control boundaries {shift_banks[0]['common_boundaries']}.",
        f"The largest mutually coupled state island has 9 FFs {register_sccs[0]}; its 3-to-8-cell next-state cones, XOR/XNOR use, enable dependence, and connection through cell:cell_125 to the shift bank make it the strongest controller/counter candidate, but topology alone cannot distinguish those roles.",
        f"Register shapes by the deliberately simple dependency heuristic: {dict(Counter(shapes.values()))}.",
        f"The register-only dependency graph has {len(ff_edges)} directed edges and SCC sizes {scc_sizes[:12]}; large SCCs indicate mutually coupled state banks, while chains of singleton SCCs are compatible with shifts/pipelines.",
        f"Raw connectivity anomalies: {len(undriven_nets)} loaded nets have no recovered driver and {len(multidriver_nets)} nets have multiple recovered drivers.",
    ]

    result = {
        "statistics": {
            "cells": len(cells),
            "flip_flops": len(ff_nodes),
            "combinational_cells": len(cells) - len(ff_nodes),
            "primary_inputs": sum(d == "input" for d in ports.values()),
            "primary_outputs": sum(d == "output" for d in ports.values()),
            "pin_graph_nodes": pin_graph.number_of_nodes(),
            "pin_graph_edges": pin_graph.number_of_edges(),
            "collapsed_graph_nodes": collapsed.number_of_nodes(),
            "collapsed_graph_edges": collapsed.number_of_edges(),
            "register_dependency_nodes": dependency.number_of_nodes(),
            "register_dependency_edges": dependency.number_of_edges(),
            "functional_connected_components": nx.number_connected_components(functional),
            "register_communities": len(register_communities),
            "functional_communities": len(cell_communities),
            "undriven_loaded_nets": len(undriven_nets),
            "multi_driver_nets": len(multidriver_nets),
        },
        "output_cones": output_cones,
        "output_boundary_overlap": overlap,
        "success_checker": success_checker,
        "output_generator": output_generator,
        "detected_shift_banks": shift_banks,
        "register_shapes": shapes,
        "register_communities": reg_community_rows,
        "functional_communities": cell_community_rows,
        "largest_register_scc_sizes": scc_sizes[:25],
        "largest_register_sccs": register_sccs[:25],
        "undriven_loaded_nets": undriven_nets,
        "multi_driver_nets": multidriver_nets,
        "findings": findings,
    }

    nx.write_graphml(pin_graph, args.out / "cell_net_directed.graphml")
    nx.write_graphml(dependency, args.out / "register_dependency.graphml")
    (args.out / "analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    write_markdown(result, args.out / "report.md")
    print(json.dumps(result["statistics"], indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
