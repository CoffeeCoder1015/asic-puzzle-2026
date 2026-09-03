import importlib
from pathlib import Path
import random

from matplotlib import pyplot as plt

from ml_solver import trace_relevant_frames
import probed_program


INPUT_CYCLES = 121
READOUT_CYCLES = 11
FRAME_COUNT = INPUT_CYCLES + READOUT_CYCLES
SAMPLES_PER_DENSITY = 5
RANDOM_SEED = 2026
GRAPH_PATH = (
    Path(__file__).resolve().parent
    / "outputs"
    / "probe_coverage.png"
)
GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)

relevant_variables_by_frame = trace_relevant_frames(
    frame_count=FRAME_COUNT,
    target_frames=list(range(INPUT_CYCLES, FRAME_COUNT)),
)


def run_probe(puzzle_inputs):
    circuit = importlib.reload(probed_program)
    input_sequence = puzzle_inputs + [0] * READOUT_CYCLES

    covered_variables = set()
    output_characters = []

    for frame, input_bit in enumerate(input_sequence):
        timestamp = f"_{frame}"
        timed_variables = relevant_variables_by_frame[frame]
        probe_variables = [
            variable_name.removesuffix(timestamp)
            for variable_name in timed_variables
        ]

        _, output, probe_values = circuit.asic(
            None,
            input_bit,
            1,
            1,
            probe_variables,
        )

        if frame >= INPUT_CYCLES:
            output_byte = sum(
                int(value) << bit
                for bit, value in enumerate(output)
            )
            if output_byte:
                output_characters.append(chr(output_byte))

        for timed_variable, probe_variable in zip(
            timed_variables,
            probe_variables,
            strict=True,
        ):
            if probe_values[probe_variable]:
                covered_variables.add(timed_variable)

    return "".join(output_characters), covered_variables


coverable_variables = sum(
    len(frame_variables)
    for frame_variables in relevant_variables_by_frame
)

random_generator = random.Random(RANDOM_SEED)
random_inputs = []

for density_percent in range(10, 100, 10):
    one_count = round(
        INPUT_CYCLES * density_percent / 100
    )

    for _ in range(SAMPLES_PER_DENSITY):
        one_positions = set(
            random_generator.sample(
                range(INPUT_CYCLES),
                one_count,
            )
        )
        puzzle_inputs = [
            int(position in one_positions)
            for position in range(INPUT_CYCLES)
        ]
        random_inputs.append((one_count, puzzle_inputs))

random_generator.shuffle(random_inputs)

rollout_inputs = [
    (0, [0] * INPUT_CYCLES),
    *random_inputs,
    (INPUT_CYCLES, [1] * INPUT_CYCLES),
]

cumulative_coverage = set()
rollout_results = []

for attempt, (one_count, puzzle_inputs) in enumerate(
    rollout_inputs
):
    output, sample_coverage = run_probe(puzzle_inputs)

    previous_total = len(cumulative_coverage)
    cumulative_coverage.update(sample_coverage)
    current_total = len(cumulative_coverage)

    rollout_results.append(
        (
            one_count,
            len(sample_coverage),
            current_total,
            output,
        )
    )

    print(
        f"Attempt {attempt:2d}, "
        f"{one_count:3d} ones: "
        f"sample={len(sample_coverage)}/{coverable_variables} "
        f"({len(sample_coverage) / coverable_variables:.2%}), "
        f"union={current_total}/{coverable_variables} "
        f"({current_total / coverable_variables:.2%}), "
        f"gain={current_total - previous_total:+d}, "
        f"output={output!r}"
    )

figure, (sample_axis, union_axis) = plt.subplots(
    1,
    2,
    figsize=(14, 6),
)

random_results = rollout_results[1:-1]
sample_axis.scatter(
    [result[0] for result in random_results],
    [
        result[1] / coverable_variables * 100
        for result in random_results
    ],
    alpha=0.65,
    label="Random inputs",
)

sampled_one_counts = sorted({
    result[0]
    for result in random_results
})
mean_coverages = [
    sum(
        result[1]
        for result in random_results
        if result[0] == one_count
    )
    / SAMPLES_PER_DENSITY
    / coverable_variables
    * 100
    for one_count in sampled_one_counts
]

sample_axis.plot(
    sampled_one_counts,
    mean_coverages,
    color="black",
    linewidth=1.5,
    label="Mean coverage",
)
sample_axis.scatter(
    [0, INPUT_CYCLES],
    [
        rollout_results[0][1]
        / coverable_variables
        * 100,
        rollout_results[-1][1]
        / coverable_variables
        * 100,
    ],
    marker="*",
    s=180,
    color=["tab:red", "tab:green"],
    label="All-zero / all-one",
)
sample_axis.set(
    title="Coverage of each rollout",
    xlabel="Number of 1 bits",
    ylabel="Relevant variables active (%)",
    xlim=(-2, INPUT_CYCLES + 2),
)
sample_axis.grid(alpha=0.25)
sample_axis.legend()

attempts = range(len(rollout_results))
union_axis.plot(
    attempts,
    [
        result[2] / coverable_variables * 100
        for result in rollout_results
    ],
    marker="o",
    markersize=3,
    linewidth=1.5,
    label="Cumulative union",
)
union_axis.set(
    title="Total coverage found over time",
    xlabel="Rollout attempt",
    ylabel="Unioned relevant variables active (%)",
    xlim=(0, len(rollout_results) - 1),
    ylim=(0, 100),
)
union_axis.grid(alpha=0.25)
union_axis.legend()

figure.tight_layout()
figure.savefig(GRAPH_PATH, dpi=160)
plt.close(figure)

print(f"Coverage graph: {GRAPH_PATH}")
