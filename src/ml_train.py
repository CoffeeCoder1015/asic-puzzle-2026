import argparse
import os
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


def save_progress(
    checkpoint_path: Path,
    replay_path: Path,
    model: TrajectoryEditor,
    optimizer: torch.optim.Optimizer,
    step: int,
    no_gain_steps: int,
    cumulative_coverage: set[str],
    reference_bits: torch.Tensor,
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
            "no_gain_steps": no_gain_steps,
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "cumulative_coverage": sorted(
                cumulative_coverage
            ),
            "reference_bits": reference_bits.tolist(),
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
]:
    device = sampled_candidate.device
    log_probabilities = distribution.log_prob(
        sampled_candidate
    )[0]
    entropy = distribution.entropy().mean()
    policy_loss = -(
        bit_credits.to(device) * log_probabilities
    ).mean()
    loss = policy_loss - entropy_coefficient * entropy

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    gradient_norm = torch.nn.utils.clip_grad_norm_(
        model.parameters(),
        max_norm=max_gradient_norm,
    )
    optimizer.step()

    return policy_loss, entropy, loss, gradient_norm


def log_training_step(
    run: wandb.sdk.wandb_run.Run,
    step: int,
    candidate_coverage: set[str],
    cumulative_coverage: set[str],
    coverage_gain: int,
    no_gain_steps: int,
    bit_credits: torch.Tensor,
    candidate_bits: torch.Tensor,
    logits: torch.Tensor,
    policy_loss: torch.Tensor,
    entropy: torch.Tensor,
    loss: torch.Tensor,
    gradient_norm: torch.Tensor,
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
            "coverage/no_gain_steps": no_gain_steps,
            "credit/positive_bits": positive_credits,
            "credit/negative_bits": negative_credits,
            "credit/mean_absolute": float(
                bit_credits.abs().mean()
            ),
            "credit/maximum_absolute": float(
                bit_credits.abs().max()
            ),
            "policy/loss": float(policy_loss.detach()),
            "policy/entropy": float(entropy.detach()),
            "policy/mean_probability": float(
                torch.sigmoid(logits).mean().detach()
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
        reference_bits,
        reference_frames,
        reference_phases,
    ) = record_rollout([0] * INPUT_CYCLES)

    cumulative_coverage = coverage_from_rollout(
        reference_frames
    )
    replay_inputs = [reference_bits.tolist()]
    no_gain_steps = 0

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
            completion = coverage_completion(
                cumulative_coverage
            )

            logits = model(
                reference_bits[None].to(device),
                reference_frames[None].to(device),
                completion[None].to(device),
                reference_phases[None].to(device),
            )
            distribution = (
                torch.distributions.Bernoulli(
                    logits=logits
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
                candidate_phases,
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

            if coverage_gain > 0:
                replay_inputs.append(
                    candidate_bits.tolist()
                )
                no_gain_steps = 0
            else:
                no_gain_steps += 1

            reference_bits = candidate_bits
            reference_frames = candidate_frames
            reference_phases = candidate_phases

            save_progress(
                checkpoint_path=args.checkpoint,
                replay_path=args.replay_inputs,
                model=model,
                optimizer=optimizer,
                step=step,
                no_gain_steps=no_gain_steps,
                cumulative_coverage=cumulative_coverage,
                reference_bits=reference_bits,
                replay_inputs=replay_inputs,
                config=config,
            )

            log_training_step(
                run=run,
                step=step,
                candidate_coverage=candidate_coverage,
                cumulative_coverage=cumulative_coverage,
                coverage_gain=coverage_gain,
                no_gain_steps=no_gain_steps,
                bit_credits=bit_credits,
                candidate_bits=candidate_bits,
                logits=logits,
                policy_loss=policy_loss,
                entropy=entropy,
                loss=loss,
                gradient_norm=gradient_norm,
            )

            if current_total == COVERABLE_VARIABLE_COUNT:
                print("coverage complete", flush=True)
                break

            if no_gain_steps >= args.plateau_steps:
                print(
                    "coverage plateau reached after "
                    f"{no_gain_steps} steps without gain",
                    flush=True,
                )
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
        "--plateau-steps",
        type=int,
        default=100,
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
    if args.plateau_steps <= 0:
        parser.error("--plateau-steps must be positive")
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
