import importlib
from collections.abc import Sequence
from dataclasses import dataclass

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


@dataclass
class BoardEvaluation:
    bits: Tensor
    frames: Tensor
    phases: Tensor
    output: str
    rollout_coverage: Tensor


def record_rollout(
    puzzle_inputs: Sequence[int],
) -> BoardEvaluation:
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
    output_characters = []
    input_sequence = (
        input_bits
        + [0] * READOUT_CYCLES
    )

    for frame, input_bit in enumerate(input_sequence):
        _, output_bits, probe_values = circuit.asic(
            True,
            input_bit,
            True,
            True,
            CIRCUIT_VARIABLES,
        )

        if frame >= INPUT_CYCLES:
            output_byte = sum(
                int(value) << bit
                for bit, value in enumerate(output_bits)
            )
            if output_byte:
                output_characters.append(chr(output_byte))

        circuit_frames.append([
            float(bool(probe_values[variable_name]))
            for variable_name in CIRCUIT_VARIABLES
        ])

    phases = (
        [0] * INPUT_CYCLES
        + [1] * READOUT_CYCLES
    )
    bits_tensor = torch.tensor(
        input_bits,
        dtype=torch.long,
    )
    frames_tensor = torch.tensor(
        circuit_frames,
        dtype=torch.float32,
    )
    phases_tensor = torch.tensor(
        phases,
        dtype=torch.long,
    )

    return BoardEvaluation(
        bits=bits_tensor,
        frames=frames_tensor,
        phases=phases_tensor,
        output="".join(output_characters),
        rollout_coverage=coverage_from_rollout(
            frames_tensor
        ),
    )


def coverage_from_rollout(
    circuit_frames: Tensor,
) -> Tensor:
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

    return active_values.detach().to(
        device="cpu",
        dtype=torch.bool,
    )


def coverage_completion(
    cumulative_coverage: Tensor,
) -> Tensor:
    expected_shape = (COVERABLE_VARIABLE_COUNT,)
    if tuple(cumulative_coverage.shape) != expected_shape:
        raise ValueError(
            "cumulative_coverage must have shape "
            f"{expected_shape}"
        )

    if cumulative_coverage.dtype != torch.bool:
        raise ValueError(
            "cumulative_coverage must have dtype bool"
        )

    if cumulative_coverage.device.type != "cpu":
        raise ValueError(
            "cumulative_coverage must be on the CPU"
        )

    completion = torch.ones(
        FRAME_COUNT * len(CIRCUIT_VARIABLES),
        dtype=torch.float32,
    )
    completion[COVERAGE_FLAT_INDICES] = (
        cumulative_coverage.to(torch.float32)
    )

    return completion.reshape(
        FRAME_COUNT,
        len(CIRCUIT_VARIABLES),
    )
