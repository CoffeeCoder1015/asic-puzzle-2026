import argparse
import os
from dataclasses import dataclass
from pathlib import Path

import torch
import wandb

from ml_model import TrajectoryEditor
from ml_rollout import (
    COVERABLE_VARIABLE_COUNT,
    INPUT_CYCLES,
    coverage_completion,
    coverage_from_rollout,
    record_rollout,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = (
    ROOT / "experiments" / "ml_training"
)


@dataclass
class PivotalBoard:
    bits: torch.Tensor
    frames: torch.Tensor
    attempts: int = 0
    zero_gain_attempts: int = 0

    @property
    def failure_ratio(self) -> float:
        return (
            self.zero_gain_attempts + 1
        ) / (self.attempts + 2)


def archive_probabilities(
    pivotal_boards: list[PivotalBoard],
    newness_strength: float,
    selection_temperature: float,
) -> torch.Tensor:
    selection_scores = torch.tensor(
        [
            -board.failure_ratio
            + newness_strength
            / ((board.attempts + 1) ** 0.5)
            for board in pivotal_boards
        ],
        dtype=torch.float64,
    )
    return torch.softmax(
        selection_scores / selection_temperature,
        dim=0,
    )


def save_progress(
    checkpoint_path: Path,
    replay_path: Path,
    model: TrajectoryEditor,
    optimizer: torch.optim.Optimizer,
    step: int,
    cumulative_coverage: set[str],
    pivotal_boards: list[PivotalBoard],
    current_board_index: int,
    replay_inputs: list[list[int]],
    config: dict[str, object],
) -> None:
    checkpoint_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    replay_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    torch.save(
        {
            "step": step,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "cumulative_coverage": sorted(
                cumulative_coverage
            ),
            "current_board_index": current_board_index,
            "pivotal_boards": [
                {
                    "bits": board.bits.tolist(),
                    "attempts": board.attempts,
                    "zero_gain_attempts": (
                        board.zero_gain_attempts
                    ),
                }
                for board in pivotal_boards
            ],
            "replay_inputs": replay_inputs,
            "config": config,
        },
        checkpoint_path,
    )

    replay_path.write_text(
        "\n".join(
            "".join(str(bit) for bit in puzzle_input)
            for puzzle_input in replay_inputs
        )
        + "\n",
        encoding="utf-8",
    )


def select_device(requested_device: str) -> torch.device:
    if requested_device == "auto":
        return torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

    if (
        requested_device == "cuda"
        and not torch.cuda.is_available()
    ):
        raise RuntimeError(
            "CUDA was requested but is not available"
        )

    return torch.device(requested_device)


def measure_candidate(
    candidate_bits: torch.Tensor,
    cumulative_coverage: set[str],
) -> tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    set[str],
    int,
]:
    candidate_bits, frames, phases = record_rollout(
        candidate_bits.tolist()
    )
    coverage = coverage_from_rollout(frames)
    gain = len(coverage - cumulative_coverage)

    return candidate_bits, frames, phases, coverage, gain


def measure_counterfactual_credits(
    candidate_bits: torch.Tensor,
    actual_gain: int,
    cumulative_coverage: set[str],
) -> torch.Tensor:
    credits = torch.empty(
        INPUT_CYCLES,
        dtype=torch.float32,
    )

    for bit_index in range(INPUT_CYCLES):
        counterfactual_bits = candidate_bits.clone()
        counterfactual_bits[bit_index] = (
            1 - counterfactual_bits[bit_index]
        )

        _, _, _, _, counterfactual_gain = measure_candidate(
            counterfactual_bits,
            cumulative_coverage,
        )
        credits[bit_index] = (
            actual_gain - counterfactual_gain
        )

    return credits


def optimize_model(
    model: TrajectoryEditor,
    optimizer: torch.optim.Optimizer,
    distribution: torch.distributions.Bernoulli,
    sampled_candidate: torch.Tensor,
    bit_credits: torch.Tensor,
    entropy_coefficient: float,
    max_gradient_norm: float,
) -> tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
]:
    device = sampled_candidate.device
    log_probabilities = distribution.log_prob(
        sampled_candidate
    )[0]
    entropy = distribution.entropy().mean()
    credit_scale = (
        bit_credits.abs().max().clamp_min(1.0)
    )
    scaled_credits = bit_credits / credit_scale
    policy_loss = -(
        scaled_credits.to(device) * log_probabilities
    ).mean()
    loss = policy_loss - entropy_coefficient * entropy

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    gradient_norm = torch.nn.utils.clip_grad_norm_(
        model.parameters(),
        max_norm=max_gradient_norm,
    )
    optimizer.step()

    return (
        policy_loss,
        entropy,
        loss,
        gradient_norm,
        credit_scale,
    )


def log_training_step(
    run: wandb.sdk.wandb_run.Run,
    step: int,
    candidate_coverage: set[str],
    cumulative_coverage: set[str],
    coverage_gain: int,
    bit_credits: torch.Tensor,
    candidate_bits: torch.Tensor,
    logits: torch.Tensor,
    policy_loss: torch.Tensor,
    entropy: torch.Tensor,
    loss: torch.Tensor,
    gradient_norm: torch.Tensor,
    temperature: float,
    credit_scale: torch.Tensor,
    pivotal_boards: list[PivotalBoard],
    current_board_index: int,
    current_board_probability: float,
    selection_entropy: float,
) -> None:
    positive_credits = int((bit_credits > 0).sum())
    negative_credits = int((bit_credits < 0).sum())
    current_total = len(cumulative_coverage)

    run.log(
        {
            "search/step": step,
            "coverage/rollout": len(candidate_coverage),
            "coverage/union": current_total,
            "coverage/gain": coverage_gain,
            "coverage/union_ratio": (
                current_total / COVERABLE_VARIABLE_COUNT
            ),
            "archive/size": len(pivotal_boards),
            "archive/current_attempts": (
                pivotal_boards[
                    current_board_index
                ].attempts
            ),
            "archive/current_failure_ratio": (
                pivotal_boards[
                    current_board_index
                ].failure_ratio
            ),
            "archive/current_probability": (
                current_board_probability
            ),
            "archive/selection_entropy": (
                selection_entropy
            ),
            "credit/positive_bits": positive_credits,
            "credit/negative_bits": negative_credits,
            "credit/mean_absolute": float(
                bit_credits.abs().mean()
            ),
            "credit/maximum_absolute": float(
                bit_credits.abs().max()
            ),
            "credit/scale": float(credit_scale),
            "policy/loss": float(policy_loss.detach()),
            "policy/entropy": float(entropy.detach()),
            "policy/temperature": temperature,
            "policy/mean_probability": float(
                torch.sigmoid(
                    logits / temperature
                ).mean().detach()
            ),
            "policy/candidate_ones": int(
                candidate_bits.sum()
            ),
            "optimization/gradient_norm": float(
                gradient_norm
            ),
        }
    )

    print(
        f"step={step} "
        f"rollout={len(candidate_coverage)} "
        f"union={current_total}/"
        f"{COVERABLE_VARIABLE_COUNT} "
        f"gain={coverage_gain:+d} "
        f"archive={len(pivotal_boards)} "
        f"current={current_board_index} "
        "failure="
        f"{pivotal_boards[current_board_index].failure_ratio:.3f} "
        f"credits=+{positive_credits}/"
        f"-{negative_credits} "
        f"loss={float(loss.detach()):.6f}",
        flush=True,
    )


def train(args: argparse.Namespace) -> None:
    torch.manual_seed(args.seed)
    device = select_device(args.device)

    wandb_entity = os.environ.get("WANDB_ENTITY")
    if args.wandb_mode == "online":
        if not os.environ.get("WANDB_API_KEY"):
            raise RuntimeError(
                "WANDB_API_KEY is required for online logging"
            )
        if not wandb_entity:
            raise RuntimeError(
                "WANDB_ENTITY is required for online logging"
            )

    model = TrajectoryEditor().to(device)
    model.train()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
    )

    (
        initial_bits,
        initial_frames,
        rollout_phases,
    ) = record_rollout([0] * INPUT_CYCLES)

    cumulative_coverage = coverage_from_rollout(
        initial_frames
    )
    pivotal_boards = [
        PivotalBoard(
            bits=initial_bits,
            frames=initial_frames,
        )
    ]
    current_board_index = 0
    replay_inputs = [initial_bits.tolist()]

    config = {
        key: (
            str(value)
            if isinstance(value, Path)
            else value
        )
        for key, value in vars(args).items()
    }
    config["model_parameters"] = sum(
        parameter.numel()
        for parameter in model.parameters()
    )
    config["coverable_variables"] = (
        COVERABLE_VARIABLE_COUNT
    )
    config["device_used"] = str(device)

    with wandb.init(
        entity=wandb_entity,
        project=args.wandb_project,
        mode=args.wandb_mode,
        config=config,
    ) as run:
        for step in range(args.max_steps):
            current_board = pivotal_boards[
                current_board_index
            ]
            completion = coverage_completion(
                cumulative_coverage
            )

            logits = model(
                current_board.bits[None].to(device),
                current_board.frames[None].to(device),
                completion[None].to(device),
                rollout_phases[None].to(device),
            )
            temperature = min(
                8.0,
                1.0
                + current_board.zero_gain_attempts
                / 8.0,
            )
            distribution = (
                torch.distributions.Bernoulli(
                    logits=logits / temperature
                )
            )
            sampled_candidate = distribution.sample()
            candidate_bits = (
                sampled_candidate[0]
                .to(torch.long)
                .cpu()
            )

            (
                candidate_bits,
                candidate_frames,
                _,
                candidate_coverage,
                actual_gain,
            ) = measure_candidate(
                candidate_bits,
                cumulative_coverage,
            )
            bit_credits = measure_counterfactual_credits(
                candidate_bits,
                actual_gain,
                cumulative_coverage,
            )

            (
                policy_loss,
                entropy,
                loss,
                gradient_norm,
                credit_scale,
            ) = optimize_model(
                model=model,
                optimizer=optimizer,
                distribution=distribution,
                sampled_candidate=sampled_candidate,
                bit_credits=bit_credits,
                entropy_coefficient=(
                    args.entropy_coefficient
                ),
                max_gradient_norm=(
                    args.max_gradient_norm
                ),
            )

            previous_total = len(cumulative_coverage)
            cumulative_coverage.update(
                candidate_coverage
            )
            current_total = len(cumulative_coverage)
            coverage_gain = (
                current_total - previous_total
            )

            current_board.attempts += 1
            if coverage_gain > 0:
                pivotal_boards.append(
                    PivotalBoard(
                        bits=candidate_bits,
                        frames=candidate_frames,
                    )
                )
                replay_inputs.append(
                    candidate_bits.tolist()
                )
                current_board_index = (
                    len(pivotal_boards) - 1
                )
            else:
                current_board.zero_gain_attempts += 1

            probabilities = archive_probabilities(
                pivotal_boards=pivotal_boards,
                newness_strength=(
                    args.archive_newness_strength
                ),
                selection_temperature=(
                    args.archive_selection_temperature
                ),
            )
            if coverage_gain == 0:
                current_board_index = int(
                    torch.multinomial(
                        probabilities,
                        num_samples=1,
                    ).item()
                )
            current_board_probability = float(
                probabilities[current_board_index]
            )
            selection_entropy = float(
                -(
                    probabilities
                    * probabilities.clamp_min(
                        torch.finfo(
                            probabilities.dtype
                        ).tiny
                    ).log()
                ).sum()
            )

            save_progress(
                checkpoint_path=args.checkpoint,
                replay_path=args.replay_inputs,
                model=model,
                optimizer=optimizer,
                step=step,
                cumulative_coverage=cumulative_coverage,
                pivotal_boards=pivotal_boards,
                current_board_index=current_board_index,
                replay_inputs=replay_inputs,
                config=config,
            )

            log_training_step(
                run=run,
                step=step,
                candidate_coverage=candidate_coverage,
                cumulative_coverage=cumulative_coverage,
                coverage_gain=coverage_gain,
                bit_credits=bit_credits,
                candidate_bits=candidate_bits,
                logits=logits,
                policy_loss=policy_loss,
                entropy=entropy,
                loss=loss,
                gradient_norm=gradient_norm,
                temperature=temperature,
                credit_scale=credit_scale,
                pivotal_boards=pivotal_boards,
                current_board_index=current_board_index,
                current_board_probability=(
                    current_board_probability
                ),
                selection_entropy=selection_entropy,
            )

            if current_total == COVERABLE_VARIABLE_COUNT:
                print("coverage complete", flush=True)
                break

        run.summary["final_union_coverage"] = len(
            cumulative_coverage
        )
        run.summary["final_union_ratio"] = (
            len(cumulative_coverage)
            / COVERABLE_VARIABLE_COUNT
        )
        run.summary["replay_input_count"] = len(
            replay_inputs
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Train the trajectory editor through "
            "counterfactual novelty search."
        )
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=1000,
    )
    parser.add_argument(
        "--archive-newness-strength",
        type=float,
        default=0.5,
    )
    parser.add_argument(
        "--archive-selection-temperature",
        type=float,
        default=0.25,
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-4,
    )
    parser.add_argument(
        "--entropy-coefficient",
        type=float,
        default=0.01,
    )
    parser.add_argument(
        "--max-gradient-norm",
        type=float,
        default=1.0,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2026,
    )
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=DEFAULT_RESULTS / "checkpoint.pt",
    )
    parser.add_argument(
        "--replay-inputs",
        type=Path,
        default=DEFAULT_RESULTS / "replay_inputs.txt",
    )
    parser.add_argument(
        "--wandb-mode",
        choices=("disabled", "offline", "online"),
        default="online",
    )
    parser.add_argument(
        "--wandb-project",
        default="asic-puzzle-ml",
    )
    args = parser.parse_args()

    if args.max_steps <= 0:
        parser.error("--max-steps must be positive")
    if args.archive_newness_strength < 0:
        parser.error(
            "--archive-newness-strength cannot be negative"
        )
    if args.archive_selection_temperature <= 0:
        parser.error(
            "--archive-selection-temperature must be positive"
        )
    if args.learning_rate <= 0:
        parser.error("--learning-rate must be positive")
    if args.entropy_coefficient < 0:
        parser.error(
            "--entropy-coefficient cannot be negative"
        )
    if args.max_gradient_norm <= 0:
        parser.error(
            "--max-gradient-norm must be positive"
        )

    return args


def main() -> None:
    train(parse_args())


if __name__ == "__main__":
    main()
