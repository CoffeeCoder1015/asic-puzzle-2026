import importlib
from collections.abc import Collection, Sequence

import torch
from torch import Tensor

from ml_solver import (
    compute_graph,
    trace_relevant_frames,
)
import probed_program


INPUT_CYCLES = 121
READOUT_CYCLES = 11
FRAME_COUNT = INPUT_CYCLES + READOUT_CYCLES

CIRCUIT_VARIABLES = tuple(
    sorted(compute_graph.nodes)
)
CIRCUIT_VARIABLE_INDEX = {
    variable_name: index
    for index, variable_name
    in enumerate(CIRCUIT_VARIABLES)
}

RELEVANT_VARIABLES_BY_FRAME = trace_relevant_frames(
    frame_count=FRAME_COUNT,
    target_frames=list(
        range(INPUT_CYCLES, FRAME_COUNT)
    ),
)

coverage_variable_names = []
coverage_flat_indices = []

for frame, timed_variables in enumerate(
    RELEVANT_VARIABLES_BY_FRAME
):
    timestamp = f"_{frame}"

    for timed_variable in timed_variables:
        base_variable = timed_variable.removesuffix(
            timestamp
        )
        coverage_variable_names.append(timed_variable)
        coverage_flat_indices.append(
            frame * len(CIRCUIT_VARIABLES)
            + CIRCUIT_VARIABLE_INDEX[base_variable]
        )

COVERAGE_VARIABLE_NAMES = tuple(
    coverage_variable_names
)
COVERAGE_FLAT_INDICES = torch.tensor(
    coverage_flat_indices,
    dtype=torch.long,
)
COVERABLE_VARIABLE_COUNT = len(
    COVERAGE_VARIABLE_NAMES
)


def record_rollout(
    puzzle_inputs: Sequence[int],
) -> tuple[Tensor, Tensor, Tensor]:
    input_bits = [int(bit) for bit in puzzle_inputs]

    if len(input_bits) != INPUT_CYCLES:
        raise ValueError(
            f"expected {INPUT_CYCLES} input bits, "
            f"received {len(input_bits)}"
        )

    if any(bit not in (0, 1) for bit in input_bits):
        raise ValueError(
            "puzzle inputs must contain only 0 and 1"
        )

    circuit = importlib.reload(probed_program)
    circuit_frames = []
    input_sequence = (
        input_bits
        + [0] * READOUT_CYCLES
    )

    for input_bit in input_sequence:
        _, _, probe_values = circuit.asic(
            True,
            input_bit,
            True,
            True,
            CIRCUIT_VARIABLES,
        )

        circuit_frames.append([
            float(bool(probe_values[variable_name]))
            for variable_name in CIRCUIT_VARIABLES
        ])

    phases = (
        [0] * INPUT_CYCLES
        + [1] * READOUT_CYCLES
    )

    return (
        torch.tensor(input_bits, dtype=torch.long),
        torch.tensor(
            circuit_frames,
            dtype=torch.float32,
        ),
        torch.tensor(phases, dtype=torch.long),
    )


def coverage_from_rollout(
    circuit_frames: Tensor,
) -> set[str]:
    expected_shape = (
        FRAME_COUNT,
        len(CIRCUIT_VARIABLES),
    )
    if tuple(circuit_frames.shape) != expected_shape:
        raise ValueError(
            "circuit_frames must have shape "
            f"{expected_shape}"
        )

    flat_frames = circuit_frames.reshape(-1)
    active_values = flat_frames[
        COVERAGE_FLAT_INDICES.to(
            flat_frames.device
        )
    ].bool()

    return {
        variable_name
        for variable_name, active
        in zip(
            COVERAGE_VARIABLE_NAMES,
            active_values.tolist(),
            strict=True,
        )
        if active
    }


def coverage_completion(
    cumulative_coverage: Collection[str],
) -> Tensor:
    completion = torch.ones(
        FRAME_COUNT * len(CIRCUIT_VARIABLES),
        dtype=torch.float32,
    )
    uncovered_indices = [
        flat_index
        for variable_name, flat_index
        in zip(
            COVERAGE_VARIABLE_NAMES,
            coverage_flat_indices,
            strict=True,
        )
        if variable_name not in cumulative_coverage
    ]

    completion[uncovered_indices] = 0.0

    return completion.reshape(
        FRAME_COUNT,
        len(CIRCUIT_VARIABLES),
    )
