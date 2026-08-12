from pathlib import Path, PurePosixPath
from urllib.request import urlopen
import json
import posixpath
import re

import klayout.db as kdb


ROOT = Path(__file__).resolve().parents[1]
GDS_PATHS = (
    ROOT / "warmup" / "04_final.gds",
    ROOT / "puzzle" / "puzzle.gds",
)
PIN_DEFINITIONS_PATH = ROOT / "sky130" / "pin_definitions.json"
OUTPUT_PATH = ROOT / "sky130" / "cell_models.v"

CELL_PREFIX = "sky130_fd_sc_hd__"
EXPECTED_LOGICAL_VARIANTS = 67
EXPECTED_LOGICAL_FAMILIES = 65
INCLUDE_PATTERN = re.compile(
    r'^[ \t]*`include[ \t]+"([^"]+)"[ \t]*(?:\r?\n)?$'
)
REQUIRED_PRIMITIVES = {
    PurePosixPath("models/udp_dff_p/sky130_fd_sc_hd__udp_dff_p.v"),
    PurePosixPath("models/udp_dff_pr/sky130_fd_sc_hd__udp_dff_pr.v"),
    PurePosixPath("models/udp_dff_ps/sky130_fd_sc_hd__udp_dff_ps.v"),
    PurePosixPath("models/udp_mux_2to1/sky130_fd_sc_hd__udp_mux_2to1.v"),
}


def collect_exact_variants() -> set[str]:
    variants: set[str] = set()

    for gds_path in GDS_PATHS:
        layout = kdb.Layout()
        layout.read(str(gds_path))
        top_cell = layout.top_cell()

        if top_cell is None:
            raise RuntimeError(f"{gds_path} has no top cell")

        variants.update(
            instance.cell.name
            for instance in top_cell.each_inst()
            if instance.cell.name.startswith(CELL_PREFIX)
        )

    return variants


def collect_logical_families(
    pin_definitions: dict[str, dict[str, dict[str, object]]],
) -> tuple[set[str], set[str]]:
    logical_variants: set[str] = set()
    logical_families: set[str] = set()

    for variant in collect_exact_variants():
        family = variant.rsplit("_", 1)[0]

        if family not in pin_definitions:
            raise RuntimeError(f"missing pin definitions for {family}")

        has_signal_pin = any(
            pin["kind"] == "signal"
            for pin in pin_definitions[family].values()
        )
        if has_signal_pin:
            logical_variants.add(variant)
            logical_families.add(family)

    if len(logical_variants) != EXPECTED_LOGICAL_VARIANTS:
        raise RuntimeError(
            f"expected {EXPECTED_LOGICAL_VARIANTS} logical variants, "
            f"found {len(logical_variants)}"
        )
    if len(logical_families) != EXPECTED_LOGICAL_FAMILIES:
        raise RuntimeError(
            f"expected {EXPECTED_LOGICAL_FAMILIES} logical families, "
            f"found {len(logical_families)}"
        )

    return logical_variants, logical_families


def family_source_path(family: str) -> PurePosixPath:
    short_name = family.removeprefix(CELL_PREFIX)
    return PurePosixPath("cells") / short_name / f"{family}.functional.v"


def variant_source_path(variant: str) -> PurePosixPath:
    family = variant.rsplit("_", 1)[0]
    short_name = family.removeprefix(CELL_PREFIX)
    return PurePosixPath("cells") / short_name / f"{variant}.v"


def resolve_include(
    source_path: PurePosixPath,
    include_target: str,
) -> PurePosixPath:
    if include_target.startswith("/"):
        raise RuntimeError(
            f"absolute include in {source_path}: {include_target}"
        )

    normalized = posixpath.normpath(
        (source_path.parent / include_target).as_posix()
    )
    resolved = PurePosixPath(normalized)

    if resolved.is_absolute() or ".." in resolved.parts:
        raise RuntimeError(
            f"include escapes the source repository in {source_path}: "
            f"{include_target}"
        )

    return resolved


def main() -> int:
    with PIN_DEFINITIONS_PATH.open(encoding="utf-8") as file:
        metadata = json.load(file)

    repository = metadata["source"]["repository"].rstrip("/")
    commit = metadata["source"]["commit"]
    logical_variants, logical_families = collect_logical_families(
        metadata["cells"]
    )
    family_sources = [
        family_source_path(family)
        for family in sorted(logical_families)
    ]
    variant_sources = [
        variant_source_path(variant)
        for variant in sorted(logical_variants)
    ]

    downloaded: dict[PurePosixPath, str] = {}

    def download(source_path: PurePosixPath) -> str:
        if source_path not in downloaded:
            url = (
                f"{repository}/raw/{commit}/"
                f"{source_path.as_posix()}"
            )
            with urlopen(url, timeout=30) as response:
                downloaded[source_path] = response.read().decode("utf-8")
        return downloaded[source_path]

    direct_includes: set[PurePosixPath] = set()
    for source_path in family_sources:
        for line in download(source_path).splitlines(keepends=True):
            match = INCLUDE_PATTERN.fullmatch(line)
            if match:
                direct_includes.add(
                    resolve_include(source_path, match.group(1))
                )

    if direct_includes != REQUIRED_PRIMITIVES:
        expected = ", ".join(
            path.as_posix() for path in sorted(REQUIRED_PRIMITIVES)
        )
        found = ", ".join(
            path.as_posix() for path in sorted(direct_includes)
        )
        raise RuntimeError(
            f"expected primitive includes [{expected}], found [{found}]"
        )

    def expand_source(
        source_path: PurePosixPath,
        stack: tuple[PurePosixPath, ...] = (),
    ) -> str:
        if source_path in stack:
            chain = " -> ".join(
                path.as_posix() for path in (*stack, source_path)
            )
            raise RuntimeError(f"cyclic Verilog include: {chain}")

        pieces = [
            f"// BEGIN OFFICIAL SOURCE: {source_path.as_posix()}\n"
        ]
        source = download(source_path)

        for line in source.splitlines(keepends=True):
            match = INCLUDE_PATTERN.fullmatch(line)
            if match:
                included_path = resolve_include(
                    source_path,
                    match.group(1),
                )
                pieces.append(
                    expand_source(included_path, (*stack, source_path))
                )
            else:
                pieces.append(line)

        if source and not source.endswith(("\n", "\r")):
            pieces.append("\n")
        pieces.append(
            f"// END OFFICIAL SOURCE: {source_path.as_posix()}\n"
        )
        return "".join(pieces)

    def expand_variant_wrapper(source_path: PurePosixPath) -> str:
        """Bundle an exact drive-strength wrapper around its family model."""
        variant = source_path.stem
        family = variant.rsplit("_", 1)[0]
        expected_include = source_path.parent / f"{family}.v"
        pieces = [
            f"// BEGIN OFFICIAL SOURCE: {source_path.as_posix()}\n"
        ]
        source = download(source_path)

        for line in source.splitlines(keepends=True):
            match = INCLUDE_PATTERN.fullmatch(line)

            if match:
                included_path = resolve_include(
                    source_path,
                    match.group(1),
                )
                if included_path != expected_include:
                    raise RuntimeError(
                        f"unexpected include in {source_path}: "
                        f"{included_path}"
                    )

                # The generic functional model was bundled above. Expanding
                # this include would also pull in unused behavioral branches.
                pieces.append(
                    f"// {included_path.name} already bundled above\n"
                )
            else:
                pieces.append(line)

        if source and not source.endswith(("\n", "\r")):
            pieces.append("\n")
        pieces.append(
            f"// END OFFICIAL SOURCE: {source_path.as_posix()}\n"
        )
        return "".join(pieces)

    header = (
        "/*\n"
        " * Generated by scripts/collect_sky130_cell_models.py.\n"
        " * Do not edit this bundle by hand.\n"
        " *\n"
        f" * Official source: {repository}\n"
        f" * Commit: {commit}\n"
        f" * Logical variants in the GDS inputs: {len(logical_variants)}\n"
        f" * Logical cell families: {len(logical_families)}\n"
        " */\n\n"
    )
    bundle = header + "\n".join(
        [
            *(expand_source(source_path) for source_path in family_sources),
            *(
                expand_variant_wrapper(source_path)
                for source_path in variant_sources
            ),
        ]
    )
    OUTPUT_PATH.write_bytes(bundle.encode("utf-8"))

    print(
        f"wrote {OUTPUT_PATH.name}: {len(logical_variants)} logical "
        f"variants, {len(logical_families)} families, "
        f"{len(downloaded)} official source files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
