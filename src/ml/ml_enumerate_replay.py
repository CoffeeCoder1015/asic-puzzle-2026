import argparse
import importlib
from pathlib import Path
import sys


ML_ROOT = Path(__file__).resolve().parent
SRC_ROOT = ML_ROOT.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ml_rollout import INPUT_CYCLES, READOUT_CYCLES
import circuit_model


DEFAULT_REPLAY = (
    ML_ROOT / "outputs" / "replay_inputs.txt"
)


def load_replay_inputs(path: Path) -> list[str]:
    replay_inputs = []

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        puzzle_input = line.strip()

        if not puzzle_input:
            continue

        if (
            len(puzzle_input) != INPUT_CYCLES
            or set(puzzle_input) - {"0", "1"}
        ):
            raise ValueError(
                f"{path}:{line_number}: expected "
                f"{INPUT_CYCLES} binary digits"
            )

        replay_inputs.append(puzzle_input)

    return replay_inputs


def decode_output(puzzle_input: str) -> str:
    circuit = importlib.reload(circuit_model)
    output_characters = []
    input_sequence = (
        [int(bit) for bit in puzzle_input]
        + [0] * READOUT_CYCLES
    )

    for frame, input_bit in enumerate(input_sequence):
        _, output = circuit.asic(
            None,
            input_bit,
            1,
            1,
        )

        if frame >= INPUT_CYCLES:
            output_byte = sum(
                int(value) << bit
                for bit, value in enumerate(output)
            )
            if output_byte:
                output_characters.append(chr(output_byte))

    return "".join(output_characters)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Replay accepted ML inputs and decode their "
            "circuit text outputs."
        )
    )
    parser.add_argument(
        "--replay-inputs",
        type=Path,
        default=DEFAULT_REPLAY,
    )
    args = parser.parse_args()

    replay_inputs = load_replay_inputs(
        args.replay_inputs
    )
    seen_outputs = set()

    for puzzle_input in replay_inputs:
        output = decode_output(puzzle_input)

        if output in seen_outputs:
            continue

        seen_outputs.add(output)
        print(output)


if __name__ == "__main__":
    main()
