"""Reproduce the seeded baseline and compare the writeup's five witnesses."""

import ast
import random
import re
import sys
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src/ml"))

import torch
from ml_rollout import (
    COVERABLE_VARIABLE_COUNT, COVERAGE_VARIABLE_NAMES, INPUT_CYCLES,
    READOUT_CYCLES, RELEVANT_VARIABLES_BY_FRAME, record_rollout,
)
import circuit_model
import probed_program


def full_output(bits):
    circuit = importlib.reload(circuit_model)
    characters = []
    for frame, bit in enumerate(bits + [0] * 30):
        _, output = circuit.asic(None, bit, 1, 1)
        value = sum(int(value) << index for index, value in enumerate(output))
        if frame >= INPUT_CYCLES and value:
            characters.append(chr(value))
    return "".join(characters)


def original_probe(bits):
    """Use the original baseline's set-based probe without running its plot."""
    source = (ROOT / "src/ml/probed_test_bench.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "run_probe")
    namespace = {
        "importlib": importlib,
        "probed_program": probed_program,
        "READOUT_CYCLES": READOUT_CYCLES,
        "INPUT_CYCLES": INPUT_CYCLES,
        "relevant_variables_by_frame": RELEVANT_VARIABLES_BY_FRAME,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(ROOT / "src/ml/probed_test_bench.py"), "exec"), namespace)
    return namespace["run_probe"](bits)


def main():
    rng = random.Random(2026)
    boards = []
    for density in range(10, 100, 10):
        count = round(INPUT_CYCLES * density / 100)
        for _ in range(5):
            positions = set(rng.sample(range(INPUT_CYCLES), count))
            boards.append([int(i in positions) for i in range(INPUT_CYCLES)])
    rng.shuffle(boards)
    boards = [[0] * INPUT_CYCLES, *boards, [1] * INPUT_CYCLES]

    baseline = torch.zeros(COVERABLE_VARIABLE_COUNT, dtype=torch.bool)
    for index, bits in enumerate(boards):
        result = record_rollout(bits)
        baseline |= result.rollout_coverage
        if index in (0, len(boards) - 1):
            print(f"endpoint {index}: {result.output!r}, {result.rollout_coverage.sum().item()}/{COVERABLE_VARIABLE_COUNT}")
    print(f"baseline: {baseline.sum().item()}/{COVERABLE_VARIABLE_COUNT} ({baseline.float().mean().item():.4%})")

    data = (ROOT / "writeup/src/lib/circuit-data.ts").read_text(encoding="utf-8")
    witnesses = re.findall(r'message: "([^"]+)",\s*bits: "([01]+)"', data)
    combined = baseline.clone()
    for message, bits in witnesses:
        input_bits = [int(bit) for bit in bits]
        result = record_rollout(input_bits)
        decoded = full_output(input_bits)
        if decoded != message:
            raise ValueError(f"{message!r} witness decoded as {decoded!r}")
        original_output, original_coverage = original_probe(input_bits)
        coverage_names = {name for name, active in zip(COVERAGE_VARIABLE_NAMES, result.rollout_coverage.tolist(), strict=True) if active}
        if original_output != result.output or original_coverage != coverage_names:
            raise ValueError(f"original and ML probes disagree for {message!r}")
        gain = (result.rollout_coverage & ~baseline).sum().item()
        combined |= result.rollout_coverage
        print(f"{message}: readout={result.output!r}, new versus baseline={gain}, combined={combined.sum().item()}")
    print(f"all witnesses: {combined.sum().item()}/{COVERABLE_VARIABLE_COUNT} ({combined.float().mean().item():.4%})")


if __name__ == "__main__":
    main()
