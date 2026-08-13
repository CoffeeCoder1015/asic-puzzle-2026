from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
import argparse
import json
import time


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIN_DEFINITIONS_PATH = PROJECT_ROOT / "sky130" / "pin_definitions.json"
DEFAULT_RECONSTRUCTIONS = (
    PROJECT_ROOT / "warmup" / "reversed_04_final.json",
    PROJECT_ROOT / "puzzle" / "reversed_puzzle.json",
)
DEFAULT_OUTPUT = Path(__file__).with_name("sky130_logic.json")


def download_json(url: str) -> dict:
    for attempt in range(3):
        try:
            with urlopen(url, timeout=30) as response:
                return json.load(response)
        except (TimeoutError, URLError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)

    raise AssertionError("unreachable")


def logical_behavior(liberty_cell: dict) -> dict:
    outputs = {}

    for key, pin in liberty_cell.items():
        if not key.startswith("pin,") or pin.get("direction") != "output":
            continue

        function = pin.get("function")
        if function is not None:
            outputs[key.removeprefix("pin,")] = function

    state_entries = [
        (key, value)
        for key, value in liberty_cell.items()
        if key.startswith(("ff,", "latch,"))
    ]

    if not state_entries:
        return {
            "kind": "combinational" if outputs else "passive",
            "outputs": outputs,
        }

    if len(state_entries) != 1:
        raise RuntimeError(
            f"expected one state definition, found {len(state_entries)}"
        )

    state_key, state = state_entries[0]
    state_kind, *state_variables = state_key.split(",")

    return {
        "kind": "sequential",
        "outputs": outputs,
        "state": {
            "kind": state_kind,
            "variables": state_variables,
            **state,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Collect the authoritative Boolean/state behavior of the "
            "SKY130 cells present in recovered netlists."
        )
    )
    parser.add_argument(
        "reconstructions",
        nargs="*",
        type=Path,
        default=list(DEFAULT_RECONSTRUCTIONS),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    pin_metadata = json.loads(PIN_DEFINITIONS_PATH.read_text(encoding="utf-8"))
    repository = pin_metadata["source"]["repository"].rstrip("/")
    commit = pin_metadata["source"]["commit"]

    variants_by_family: dict[str, set[str]] = {}

    for reconstruction_path in args.reconstructions:
        reconstruction = json.loads(
            reconstruction_path.read_text(encoding="utf-8")
        )

        for instance in reconstruction["instances"]:
            if not any(
                pin["kind"] == "signal"
                for pin in instance["pins"].values()
            ):
                continue

            variant = instance["cell_type"]
            family = variant.rsplit("_", 1)[0]
            variants_by_family.setdefault(family, set()).add(variant)

    cells = {}

    for family, variants in sorted(variants_by_family.items()):
        behaviors = []

        for variant in sorted(variants):
            short_name = family.split("__", 1)[1]
            source_path = (
                f"cells/{short_name}/"
                f"{variant}__tt_025C_1v80.lib.json"
            )
            url = f"{repository}/raw/{commit}/{source_path}"
            behavior = logical_behavior(download_json(url))
            behaviors.append((variant, source_path, behavior))

        reference_behavior = behaviors[0][2]

        for variant, _, behavior in behaviors[1:]:
            if behavior != reference_behavior:
                raise RuntimeError(
                    f"drive variants of {family} disagree: "
                    f"{behaviors[0][0]} and {variant}"
                )

        cells[family] = {
            **reference_behavior,
            "source": behaviors[0][1],
            "variants": [variant for variant, _, _ in behaviors],
        }

    catalog = {
        "source": {
            "repository": repository,
            "commit": commit,
            "liberty_corner": "tt_025C_1v80",
        },
        "cells": cells,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(catalog, indent=2) + "\n",
        encoding="utf-8",
    )

    kinds = {}
    for cell in cells.values():
        kinds[cell["kind"]] = kinds.get(cell["kind"], 0) + 1

    print(f"wrote {args.output}")
    print(f"cell families: {len(cells)}")
    for kind, count in sorted(kinds.items()):
        print(f"  {kind}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
