import argparse
import math
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
MIN_EDIT_SCALE = 1.0 / INPUT_CYCLES
MAX_EDIT_SCALE = 0.5
DEFAULT_EDIT_SCALE = 0.1
EDIT_SCALE_FACTOR = 2.0


@dataclass
class PivotalBoard:
    bits: torch.Tensor
    frames: torch.Tensor
    edit_scale: float
    attempts: int = 0
    zero_gain_attempts: int = 0

    @property
    def failure_ratio(self) -> float:
        return (
            self.zero_gain_attempts + 1
        ) / (self.attempts + 20)


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
                    "edit_scale": board.edit_scale,
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


def encode_edit_scale(
    edit_scale: torch.Tensor,
) -> torch.Tensor:
    return torch.log(edit_scale / MIN_EDIT_SCALE) / math.log(
        MAX_EDIT_SCALE / MIN_EDIT_SCALE
    )


def decode_edit_scale(
    encoded_edit_scale: torch.Tensor,
) -> torch.Tensor:
    return MIN_EDIT_SCALE * torch.exp(
        encoded_edit_scale
        * math.log(MAX_EDIT_SCALE / MIN_EDIT_SCALE)
    )


def branch_edit_scales(
    current_scale: float,
) -> tuple[float, float]:
    return (
        max(
            MIN_EDIT_SCALE,
            current_scale / EDIT_SCALE_FACTOR,
        ),
        min(
            MAX_EDIT_SCALE,
            current_scale * EDIT_SCALE_FACTOR,
        ),
    )


def make_edit_distribution(
    edit_logits: torch.Tensor,
    edit_scale: torch.Tensor,
) -> tuple[
    torch.distributions.Bernoulli,
    torch.Tensor,
]:
    expected_scale_shape = (edit_logits.shape[0],)
    if tuple(edit_scale.shape) != expected_scale_shape:
        raise ValueError(
            "edit_scale must have shape "
            f"{expected_scale_shape}"
        )
    if bool(
        (
            (edit_scale < MIN_EDIT_SCALE)
            | (edit_scale > MAX_EDIT_SCALE)
        ).any()
    ):
        raise ValueError(
            "edit_scale must be between "
            f"{MIN_EDIT_SCALE} and {MAX_EDIT_SCALE}"
        )

    target_edits = edit_scale * edit_logits.shape[-1]
    detached_logits = edit_logits.detach()
    with torch.no_grad():
        lower_bias = (
            -40.0 - detached_logits.amax(dim=-1)
        )
        upper_bias = (
            40.0 - detached_logits.amin(dim=-1)
        )
        for _ in range(32):
            middle_bias = (
                lower_bias + upper_bias
            ) / 2.0
            expected_edits = torch.sigmoid(
                detached_logits + middle_bias[:, None]
            ).sum(dim=-1)
            lower_bias = torch.where(
                expected_edits < target_edits,
                middle_bias,
                lower_bias,
            )
            upper_bias = torch.where(
                expected_edits >= target_edits,
                middle_bias,
                upper_bias,
            )
        calibrated_bias = (
            lower_bias + upper_bias
        ) / 2.0

        calibrated_probabilities = torch.sigmoid(
            detached_logits + calibrated_bias[:, None]
        )
        probability_slopes = (
            calibrated_probabilities
            * (1.0 - calibrated_probabilities)
        )

    implicit_bias_gradient = -(
        probability_slopes
        * (edit_logits - detached_logits)
    ).sum(dim=-1) / probability_slopes.sum(
        dim=-1
    ).clamp_min(torch.finfo(edit_logits.dtype).eps)
    calibrated_logits = (
        edit_logits
        + calibrated_bias[:, None]
        + implicit_bias_gradient[:, None]
    )

    return (
        torch.distributions.Bernoulli(
            logits=calibrated_logits
        ),
        torch.sigmoid(calibrated_logits),
    )


def sample_candidate(
    current_bits: torch.Tensor,
    distribution: torch.distributions.Bernoulli,
) -> tuple[torch.Tensor, torch.Tensor]:
    sampled_edit_mask = distribution.sample()
    if current_bits.ndim != 1:
        raise ValueError(
            "current_bits must have shape [input_cycles]"
        )
    if (
        sampled_edit_mask.ndim != 2
        or sampled_edit_mask.shape[1]
        != current_bits.shape[0]
    ):
        raise ValueError(
            "sampled edit mask must have shape "
            "[batch, input_cycles]"
        )

    candidate_bits = (
        torch.bitwise_xor(
            current_bits[None].to(
                sampled_edit_mask.device
            ),
            sampled_edit_mask.to(torch.long),
        )
        .to(torch.long)
        .cpu()
    )
    return sampled_edit_mask, candidate_bits


def select_winning_branch(
    lower_gain: int,
    higher_gain: int,
) -> int:
    if lower_gain > higher_gain:
        return 0
    if higher_gain > lower_gain:
        return 1
    return int(torch.randint(0, 2, ()).item())


def measure_candidate(
    candidate_bits: torch.Tensor,
) -> tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    set[str],
]:
    candidate_bits, frames, phases = record_rollout(
        candidate_bits.tolist()
    )
    coverage = coverage_from_rollout(frames)

    return candidate_bits, frames, phases, coverage


def score_rollout_coverage(
    rollout_coverage: set[str],
    cumulative_coverage: set[str],
) -> tuple[int, int, float, float]:
    new_count = len(
        rollout_coverage - cumulative_coverage
    )
    repeated_count = len(
        rollout_coverage & cumulative_coverage
    )
    coverage_ratio = (
        len(cumulative_coverage)
        / COVERABLE_VARIABLE_COUNT
    )
    repeat_fraction = (
        repeated_count / len(rollout_coverage)
        if rollout_coverage
        else 1.0
    )
    coverage_score = (
        coverage_ratio * new_count
        - (1.0 - coverage_ratio)
        * repeat_fraction
    )

    return (
        new_count,
        repeated_count,
        repeat_fraction,
        coverage_score,
    )


def measure_counterfactual_credits(
    candidate_bits: torch.Tensor,
    actual_coverage: set[str],
    actual_coverage_score: float,
    cumulative_coverage: set[str],
    edit_scale: float,
) -> tuple[
    torch.Tensor,
    int | None,
    PivotalBoard | None,
]:
    credits = torch.empty(
        INPUT_CYCLES,
        dtype=torch.float32,
    )
    post_actual_coverage = (
        cumulative_coverage | actual_coverage
    )
    best_residual_gain = 0
    best_bit_index = None
    best_board = None

    for bit_index in range(INPUT_CYCLES):
        counterfactual_bits = candidate_bits.clone()
        counterfactual_bits[bit_index] = (
            1 - counterfactual_bits[bit_index]
        )

        (
            counterfactual_bits,
            counterfactual_frames,
            _,
            counterfactual_coverage,
        ) = measure_candidate(counterfactual_bits)
        (
            _,
            _,
            _,
            counterfactual_coverage_score,
        ) = score_rollout_coverage(
            counterfactual_coverage,
            cumulative_coverage,
        )
        credits[bit_index] = (
            actual_coverage_score
            - counterfactual_coverage_score
        )

        residual_gain = len(
            counterfactual_coverage
            - post_actual_coverage
        )
        if residual_gain > best_residual_gain:
            best_residual_gain = residual_gain
            best_bit_index = bit_index
            best_board = PivotalBoard(
                bits=counterfactual_bits,
                frames=counterfactual_frames,
                edit_scale=edit_scale,
            )

    return credits, best_bit_index, best_board


def measure_edit_credits(
    candidate_bits: torch.Tensor,
    current_bits: torch.Tensor,
    zero_gain_attempts: int,
) -> torch.Tensor:
    edit_strength = min(
        0.10,
        0.01 * (1.0 + zero_gain_attempts / 10.0),
    )
    edit_directions = torch.where(
        candidate_bits != current_bits,
        1.0,
        -1.0,
    )

    return edit_strength * edit_directions


def optimize_model(
    model: TrajectoryEditor,
    optimizer: torch.optim.Optimizer,
    distribution: torch.distributions.Bernoulli,
    sampled_edit_mask: torch.Tensor,
    selected_sample: int,
    bit_credits: torch.Tensor,
    edit_credits: torch.Tensor,
    counterfactual_bonus: torch.Tensor,
    scale_loss: torch.Tensor,
    scale_loss_coefficient: float,
    entropy_coefficient: float,
    max_gradient_norm: float,
) -> tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
]:
    device = sampled_edit_mask.device
    log_probabilities = distribution.log_prob(
        sampled_edit_mask
    )[selected_sample]
    entropy = distribution.entropy()[
        selected_sample
    ].mean()
    credit_scale = bit_credits.abs().max().clamp_min(
        1.0
    )
    scaled_credits = bit_credits / credit_scale
    advantages = (
        scaled_credits.to(device)
        + edit_credits.to(device)
        + counterfactual_bonus.to(device)
    )
    policy_loss = -(
        advantages * log_probabilities
    ).mean()
    loss = (
        policy_loss
        + scale_loss_coefficient * scale_loss
        - entropy_coefficient * entropy
    )

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
    repeated_coverage: int,
    repeat_fraction: float,
    coverage_score: float,
    bit_credits: torch.Tensor,
    candidate_bits: torch.Tensor,
    edit_probabilities: torch.Tensor,
    policy_loss: torch.Tensor,
    entropy: torch.Tensor,
    loss: torch.Tensor,
    gradient_norm: torch.Tensor,
    edit_scale: float,
    current_edit_scale: float,
    predicted_next_scale: torch.Tensor,
    scale_gain_delta: int,
    scale_loss: torch.Tensor,
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
            "coverage/repeated": repeated_coverage,
            "coverage/repeat_surface_ratio": (
                repeated_coverage
                / COVERABLE_VARIABLE_COUNT
            ),
            "coverage/repeat_fraction": repeat_fraction,
            "coverage/score": coverage_score,
            "coverage/reference_union_ratio": (
                (current_total - coverage_gain)
                / COVERABLE_VARIABLE_COUNT
            ),
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
            "policy/edit_scale": edit_scale,
            "policy/mean_edit_probability": float(
                edit_probabilities.mean().detach()
            ),
            "scale/current": current_edit_scale,
            "scale/predicted_next": float(
                predicted_next_scale.detach()
            ),
            "scale/gain_delta": scale_gain_delta,
            "scale/loss": float(scale_loss.detach()),
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
            edit_scale=args.initial_edit_scale,
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

            current_edit_scale = current_board.edit_scale
            branch_scales = branch_edit_scales(
                current_edit_scale
            )
            model_scales = (
                current_edit_scale,
                *branch_scales,
            )
            model_edit_scales = torch.tensor(
                model_scales,
                dtype=torch.float32,
                device=device,
            )
            branch_count = len(branch_scales)
            model_batch_size = len(model_scales)
            (
                edit_logits,
                predicted_scale_logits,
            ) = model(
                current_board.bits[None].expand(
                    model_batch_size,
                    -1,
                ).to(device),
                current_board.frames[None].expand(
                    model_batch_size,
                    -1,
                    -1,
                ).to(device),
                completion[None].expand(
                    model_batch_size,
                    -1,
                    -1,
                ).to(device),
                rollout_phases[None].expand(
                    model_batch_size,
                    -1,
                ).to(device),
                encode_edit_scale(model_edit_scales),
            )
            predicted_encoded_scale = torch.sigmoid(
                predicted_scale_logits[0]
            )
            predicted_next_scale = decode_edit_scale(
                predicted_encoded_scale
            )
            (
                distribution,
                edit_probabilities,
            ) = make_edit_distribution(
                edit_logits=edit_logits[1:],
                edit_scale=model_edit_scales[1:],
            )
            (
                sampled_edit_mask,
                candidate_bits,
            ) = sample_candidate(
                current_bits=current_board.bits,
                distribution=distribution,
            )

            candidate_results = [
                measure_candidate(candidate_bits[index])
                for index in range(branch_count)
            ]
            branch_gains = [
                len(result[3] - cumulative_coverage)
                for result in candidate_results
            ]
            winning_branch = select_winning_branch(
                lower_gain=branch_gains[0],
                higher_gain=branch_gains[1],
            )
            winning_edit_scale = branch_scales[
                winning_branch
            ]
            scale_gain_delta = (
                branch_gains[1] - branch_gains[0]
            )
            if scale_gain_delta:
                target_encoded_scale = encode_edit_scale(
                    torch.tensor(
                        [winning_edit_scale],
                        dtype=torch.float32,
                        device=device,
                    )
                )[0]
                scale_loss = (
                    target_encoded_scale
                    - predicted_encoded_scale
                ).square()
            else:
                scale_loss = predicted_encoded_scale * 0.0
            (
                candidate_bits,
                candidate_frames,
                _,
                candidate_coverage,
            ) = candidate_results[winning_branch]
            (
                coverage_gain,
                repeated_coverage,
                repeat_fraction,
                coverage_score,
            ) = score_rollout_coverage(
                candidate_coverage,
                cumulative_coverage,
            )
            (
                bit_credits,
                best_counterfactual_bit,
                best_counterfactual_board,
            ) = measure_counterfactual_credits(
                candidate_bits,
                candidate_coverage,
                coverage_score,
                cumulative_coverage,
                winning_edit_scale,
            )
            counterfactual_bonus = torch.zeros(
                INPUT_CYCLES,
                dtype=torch.float32,
            )
            if best_counterfactual_bit is not None:
                # Negative advantage favors the complementary
                # edit decision that produced the better board.
                counterfactual_bonus[
                    best_counterfactual_bit
                ] = -args.best_counterfactual_bonus
            edit_credits = measure_edit_credits(
                candidate_bits=candidate_bits,
                current_bits=current_board.bits,
                zero_gain_attempts=(
                    current_board.zero_gain_attempts
                ),
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
                sampled_edit_mask=sampled_edit_mask,
                selected_sample=winning_branch,
                bit_credits=bit_credits,
                edit_credits=edit_credits,
                counterfactual_bonus=(
                    counterfactual_bonus
                ),
                scale_loss=scale_loss,
                scale_loss_coefficient=(
                    args.scale_loss_coefficient
                ),
                entropy_coefficient=(
                    args.entropy_coefficient
                ),
                max_gradient_norm=(
                    args.max_gradient_norm
                ),
            )

            cumulative_coverage.update(
                candidate_coverage
            )
            current_total = len(cumulative_coverage)

            current_board.attempts += 1
            if (
                best_counterfactual_board is not None
                and not any(
                    torch.equal(
                        best_counterfactual_board.bits,
                        board.bits,
                    )
                    for board in pivotal_boards
                )
            ):
                pivotal_boards.append(
                    best_counterfactual_board
                )

            if coverage_gain > 0:
                pivotal_boards.append(
                    PivotalBoard(
                        bits=candidate_bits,
                        frames=candidate_frames,
                        edit_scale=winning_edit_scale,
                    )
                )
                replay_inputs.append(
                    candidate_bits.tolist()
                )
                current_board_index = (
                    len(pivotal_boards) - 1
                )
                current_board_probability = 1.0
                selection_entropy = 0.0
            else:
                current_board.bits = candidate_bits
                current_board.frames = candidate_frames
                current_board.edit_scale = (
                    winning_edit_scale
                )
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

                if len(pivotal_boards) > 1:
                    leave_probability = (
                        current_board.failure_ratio
                    )
                    probabilities[
                        current_board_index
                    ] = 0.0
                    probabilities /= probabilities.sum()
                    probabilities *= leave_probability
                    probabilities[
                        current_board_index
                    ] = 1.0 - leave_probability

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
                repeated_coverage=repeated_coverage,
                repeat_fraction=repeat_fraction,
                coverage_score=coverage_score,
                bit_credits=bit_credits,
                candidate_bits=candidate_bits,
                edit_probabilities=edit_probabilities[
                    winning_branch
                ],
                policy_loss=policy_loss,
                entropy=entropy,
                loss=loss,
                gradient_norm=gradient_norm,
                edit_scale=winning_edit_scale,
                current_edit_scale=current_edit_scale,
                predicted_next_scale=predicted_next_scale,
                scale_gain_delta=scale_gain_delta,
                scale_loss=scale_loss,
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
        "--best-counterfactual-bonus",
        type=float,
        default=0.25,
    )
    parser.add_argument(
        "--initial-edit-scale",
        type=float,
        default=DEFAULT_EDIT_SCALE,
    )
    parser.add_argument(
        "--scale-loss-coefficient",
        type=float,
        default=1.0,
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
    if args.best_counterfactual_bonus < 0:
        parser.error(
            "--best-counterfactual-bonus cannot be negative"
        )
    if not (
        MIN_EDIT_SCALE
        <= args.initial_edit_scale
        <= MAX_EDIT_SCALE
    ):
        parser.error(
            "--initial-edit-scale must be between "
            f"{MIN_EDIT_SCALE} and {MAX_EDIT_SCALE}"
        )
    if args.scale_loss_coefficient < 0:
        parser.error(
            "--scale-loss-coefficient cannot be negative"
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
