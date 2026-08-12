from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import re

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "sky130_cell_models.v"

CATALOG_MODULE_PATTERN = re.compile(
    r"^module\s+(sky130_fd_sc_hd__\w+)\s*\(",
    re.MULTILINE,
)
INSTANCE_PATTERN = re.compile(
    r"^\s*(sky130_fd_sc_hd__\w+)\s+(.+?)\s*\((.*?)\)\s*;",
    re.MULTILINE | re.DOTALL,
)
PIN_PATTERN = re.compile(
    r"\.(\w+)\s*\(\s*(.*?)\s*\)",
    re.DOTALL,
)
PORT_PATTERN = re.compile(
    r"^\s*(input|output|inout)\s+"
    r"(?:(?:wire|reg|logic)\s+)?"
    r"(?:\[\s*(\d+)\s*:\s*(\d+)\s*\]\s+)?"
    r"([A-Za-z_]\w*)",
    re.MULTILINE,
)


def load_catalog_families(catalog_path: Path) -> set[str]:
    catalog = catalog_path.read_text(encoding="utf-8")
    return set(CATALOG_MODULE_PATTERN.findall(catalog))


def parse_ports(verilog: str) -> dict[str, str]:
    ports = {}

    for direction, first_index, last_index, name in PORT_PATTERN.findall(verilog):
        if not first_index:
            ports[name] = direction
            continue

        low = min(int(first_index), int(last_index))
        high = max(int(first_index), int(last_index))

        for bit_index in range(low, high + 1):
            ports[f"{name}[{bit_index}]"] = direction

    return ports


def normalize_cell_family(
    cell_type: str,
    catalog_families: set[str],
) -> str | None:
    if cell_type in catalog_families:
        return cell_type

    cell_family = cell_type.rsplit("_", 1)[0]

    if cell_family in catalog_families:
        return cell_family

    # Cells absent from the functional catalog are physical-only cells such
    # as tap and decap cells, rather than logic we need to compare.
    return None


def parse_netlist(
    netlist_path: Path,
    catalog_families: set[str],
) -> tuple[
    dict[str, str],
    list[tuple[str, str, list[tuple[str, str]]]],
    nx.MultiGraph,
]:
    verilog = netlist_path.read_text(encoding="utf-8")
    ports = parse_ports(verilog)
    instances: list[tuple[str, str, list[tuple[str, str]]]] = []

    for match in INSTANCE_PATTERN.finditer(verilog):
        cell_type, instance_name, arguments = match.groups()
        cell_family = normalize_cell_family(cell_type, catalog_families)

        if cell_family is None:
            continue

        pins = []

        for pin_name, net_name in PIN_PATTERN.findall(arguments):
            net_name = net_name.strip()

            if net_name:
                pins.append((pin_name, net_name))

        instances.append((cell_family, instance_name.strip(), pins))

    graph = nx.MultiGraph()

    # Add ports even if they are dangling. A missing boundary connection must
    # remain visible to both the comparison and plot.
    for port_name in ports:
        graph.add_node(
            ("net", port_name),
            match_kind=f"top-net:{port_name}",
            visual_kind="port",
            label=port_name,
        )

    for instance_index, (cell_family, instance_name, pins) in enumerate(instances):
        instance_node = ("instance", instance_index)
        graph.add_node(
            instance_node,
            match_kind=f"cell:{cell_family}",
            visual_kind="cell",
            label=instance_name,
        )

        for pin_name, net_name in pins:
            net_node = ("net", net_name)

            if net_name in ports:
                match_kind = f"top-net:{net_name}"
                visual_kind = "port"
            else:
                match_kind = "internal-net"
                visual_kind = "net"

            graph.add_node(
                net_node,
                match_kind=match_kind,
                visual_kind=visual_kind,
                label=net_name,
            )
            graph.add_edge(instance_node, net_node, pin=pin_name)

    return ports, instances, graph


def count_nets(graph: nx.MultiGraph) -> int:
    return sum(
        node_type == "net"
        for node_type, _ in graph.nodes
    )


def compare_graphs(
    reference_graph: nx.MultiGraph,
    recovered_graph: nx.MultiGraph,
) -> dict[tuple[str, object], tuple[str, object]] | None:
    node_match = nx.algorithms.isomorphism.categorical_node_match(
        "match_kind",
        None,
    )
    edge_match = nx.algorithms.isomorphism.categorical_multiedge_match(
        "pin",
        None,
    )
    matcher = nx.algorithms.isomorphism.MultiGraphMatcher(
        reference_graph,
        recovered_graph,
        node_match=node_match,
        edge_match=edge_match,
    )

    return next(matcher.isomorphisms_iter(), None)


def draw_graph(
    axis,
    graph: nx.MultiGraph,
    positions: dict,
    title: str,
) -> None:
    nx.draw_networkx_edges(
        graph,
        positions,
        ax=axis,
        edge_color="#8b8b8b",
        alpha=0.20,
        width=0.45,
    )

    visual_styles = {
        "cell": {"shape": "s", "size": 28, "color": "#4c78a8"},
        "net": {"shape": "o", "size": 9, "color": "#b8b8b8"},
        "port": {"shape": "D", "size": 90, "color": "#f58518"},
    }

    for visual_kind, style in visual_styles.items():
        nodes = [
            node
            for node, attributes in graph.nodes(data=True)
            if attributes["visual_kind"] == visual_kind
        ]
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=nodes,
            node_shape=style["shape"],
            node_size=style["size"],
            node_color=style["color"],
            linewidths=0,
            ax=axis,
        )

    port_labels = {}
    bus_ports = {}

    for node, attributes in graph.nodes(data=True):
        if attributes["visual_kind"] != "port":
            continue

        label = attributes["label"]
        bus_match = re.fullmatch(r"(.+)\[(\d+)\]", label)

        if bus_match is None:
            port_labels[node] = label
            continue

        bus_name, bit_index = bus_match.groups()
        bus_ports.setdefault(bus_name, []).append((int(bit_index), node))

    # Keep every physical bus-bit node in the drawing, but label the group
    # once so O[0] through O[7] do not print on top of one another.
    for bus_name, bits in bus_ports.items():
        low_bit, representative_node = min(bits)
        high_bit = max(bit_index for bit_index, _ in bits)
        port_labels[representative_node] = f"{bus_name}[{high_bit}:{low_bit}]"

    nx.draw_networkx_labels(
        graph,
        positions,
        labels=port_labels,
        font_size=7,
        font_weight="bold",
        ax=axis,
    )

    axis.set_title(title)
    axis.set_axis_off()


def calculate_positions(graph: nx.MultiGraph) -> dict:
    if len(graph) >= 500:
        # ForceAtlas2 scales to the puzzle graph without requiring SciPy's
        # sparse-matrix layout path.
        return nx.forceatlas2_layout(
            graph,
            seed=7,
            max_iter=150,
            scaling_ratio=4.0,
            gravity=1.0,
        )

    return nx.spring_layout(
        graph,
        seed=7,
        iterations=200,
    )


def legend_handles() -> list[Line2D]:
    return [
        Line2D([], [], marker="s", linestyle="", color="#4c78a8", label="standard cell"),
        Line2D([], [], marker="o", linestyle="", color="#b8b8b8", label="internal net"),
        Line2D([], [], marker="D", linestyle="", color="#f58518", label="top-level port"),
    ]


def plot_netlist(
    netlist_path: Path,
    instances: list,
    graph: nx.MultiGraph,
    plot_path: Path,
) -> None:
    figure, axis = plt.subplots(figsize=(12, 10))
    draw_graph(
        axis,
        graph,
        calculate_positions(graph),
        netlist_path.name,
    )
    figure.suptitle(
        f"Structural netlist: {len(instances)} cells, "
        f"{count_nets(graph)} electrical nets"
    )
    figure.legend(
        handles=legend_handles(),
        loc="lower center",
        ncol=3,
        frameon=False,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 0.95))

    plot_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(plot_path, dpi=220, bbox_inches="tight")
    plt.close(figure)


def plot_comparison(
    reference_path: Path,
    recovered_path: Path,
    reference_graph: nx.MultiGraph,
    recovered_graph: nx.MultiGraph,
    node_mapping: dict | None,
    plot_path: Path,
) -> None:
    reference_positions = calculate_positions(reference_graph)

    if node_mapping is None:
        recovered_positions = calculate_positions(recovered_graph)
    else:
        # Reuse each reference node's position for its recovered counterpart.
        # Isomorphic structures therefore appear in exactly the same shape.
        recovered_positions = {
            recovered_node: reference_positions[reference_node]
            for reference_node, recovered_node in node_mapping.items()
        }

    figure, axes = plt.subplots(1, 2, figsize=(16, 8))
    draw_graph(
        axes[0],
        reference_graph,
        reference_positions,
        reference_path.name,
    )
    draw_graph(
        axes[1],
        recovered_graph,
        recovered_positions,
        recovered_path.name,
    )

    status = "isomorphic" if node_mapping is not None else "different"
    figure.suptitle(f"Structural netlist comparison: {status}")
    figure.legend(
        handles=legend_handles(),
        loc="lower center",
        ncol=3,
        frameon=False,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 0.95))

    plot_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def main() -> int:
    parser = ArgumentParser(
        description=(
            "Plot one structural SKY130 Verilog netlist, or compare two while "
            "ignoring instance names, internal net names, and drive-strength "
            "suffixes."
        )
    )
    parser.add_argument("reference", type=Path)
    parser.add_argument("recovered", type=Path, nargs="?")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG,
        help=f"functional cell catalog (default: {DEFAULT_CATALOG})",
    )
    parser.add_argument(
        "--plot",
        type=Path,
        help="write an aligned reference/recovered graph image",
    )
    arguments = parser.parse_args()

    catalog_families = load_catalog_families(arguments.catalog)
    reference_ports, reference_instances, reference_graph = parse_netlist(
        arguments.reference,
        catalog_families,
    )

    if arguments.recovered is None:
        print(f"Ports:             {len(reference_ports)}")
        print(f"Logical instances: {len(reference_instances)}")
        print(f"Electrical nets:   {count_nets(reference_graph)}")
        print(f"Pin terminals:     {reference_graph.number_of_edges()}")

        if arguments.plot is not None:
            plot_netlist(
                arguments.reference,
                reference_instances,
                reference_graph,
                arguments.plot,
            )
            print(f"Wrote plot:        {arguments.plot}")

        return 0

    recovered_ports, recovered_instances, recovered_graph = parse_netlist(
        arguments.recovered,
        catalog_families,
    )

    reference_families = Counter(
        family for family, _, _ in reference_instances
    )
    recovered_families = Counter(
        family for family, _, _ in recovered_instances
    )
    node_mapping = compare_graphs(reference_graph, recovered_graph)

    ports_match = reference_ports == recovered_ports
    families_match = reference_families == recovered_families
    graphs_match = node_mapping is not None

    print(f"Ports match:       {ports_match}")
    print(
        "Logical instances: "
        f"{len(reference_instances)} / {len(recovered_instances)}"
    )
    print(f"Families match:    {families_match}")
    print(
        "Electrical nets:   "
        f"{count_nets(reference_graph)} / {count_nets(recovered_graph)}"
    )
    print(
        "Pin terminals:     "
        f"{reference_graph.number_of_edges()} / "
        f"{recovered_graph.number_of_edges()}"
    )
    print(f"Graphs isomorphic: {graphs_match}")

    if arguments.plot is not None:
        plot_comparison(
            arguments.reference,
            arguments.recovered,
            reference_graph,
            recovered_graph,
            node_mapping,
            arguments.plot,
        )
        print(f"Wrote plot:        {arguments.plot}")

    return 0 if ports_match and families_match and graphs_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
