import argparse
import math
import os
from dataclasses import dataclass
from pathlib import Path

import torch
import wandb

from ml_model import ReferenceTokenizer, TrajectoryEditor
from ml_rollout import (
    BoardEvaluation,
    COVERABLE_VARIABLE_COUNT,
    INPUT_CYCLES,
    coverage_completion,
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
class TrajectoryHead:
    board: BoardEvaluation
    covered: torch.Tensor
    edit_scale: float
    attempts: int = 0
    zero_gain_attempts: int = 0

    def __post_init__(self) -> None:
        expected_shape = (COVERABLE_VARIABLE_COUNT,)
        if tuple(self.covered.shape) != expected_shape:
            raise ValueError(
                "covered must have shape "
                f"{expected_shape}"
            )
        if self.covered.dtype != torch.bool:
            raise ValueError("covered must be a bool tensor")

    @property
    def failure_ratio(self) -> float:
        return (
            self.zero_gain_attempts + 1
        ) / (self.attempts + 20)


@dataclass
class Trajectory:
    beam: list[TrajectoryHead]
    current_index: int
    stage_discoveries: torch.Tensor
    stage_gain: int = 0
    stage_steps: int = 0

    def __post_init__(self) -> None:
        if not self.beam:
            raise ValueError("trajectory beam cannot be empty")
        if not 0 <= self.current_index < len(self.beam):
            raise ValueError(
                "current_index must identify a beam head"
            )
        expected_shape = (COVERABLE_VARIABLE_COUNT,)
        if tuple(self.stage_discoveries.shape) != expected_shape:
            raise ValueError(
                "stage_discoveries must have shape "
                f"{expected_shape}"
            )
        if self.stage_discoveries.dtype != torch.bool:
            raise ValueError(
                "stage_discoveries must be a bool tensor"
            )

    @property
    def current_head(self) -> TrajectoryHead:
        return self.beam[self.current_index]

    def append_head(
        self,
        head: TrajectoryHead,
        beam_size: int,
    ) -> int:
        self.beam.append(head)
        overflow = len(self.beam) - beam_size
        if overflow > 0:
            del self.beam[:overflow]
            self.current_index = max(
                0,
                self.current_index - overflow,
            )
        return len(self.beam) - 1

    def record_discoveries(
        self,
        rollout_coverage: torch.Tensor,
        global_checkpoint: torch.Tensor,
    ) -> None:
        self.stage_discoveries |= (
            rollout_coverage & ~global_checkpoint
        )
        self.stage_gain = int(
            self.stage_discoveries.sum().item()
        )

    def reset(
        self,
        head: TrajectoryHead,
    ) -> None:
        self.beam = [head]
        self.current_index = 0
        self.stage_discoveries = torch.zeros_like(
            head.covered
        )
        self.stage_gain = 0
        self.stage_steps = 0


def save_progress(
    checkpoint_path: Path,
    replay_path: Path,
    reference_tokenizer: ReferenceTokenizer,
    trajectory_editor: TrajectoryEditor,
    optimizer: torch.optim.Optimizer,
    step: int,
    generation: int,
    next_trajectory_index: int,
    global_checkpoint: torch.Tensor,
    trajectories: list[Trajectory],
    discovered_outputs: set[str],
    board_generator: torch.Generator,
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
            "reference_tokenizer": (
                reference_tokenizer.state_dict()
            ),
            "trajectory_editor": (
                trajectory_editor.state_dict()
            ),
            "optimizer": optimizer.state_dict(),
            "generation": generation,
            "next_trajectory_index": (
                next_trajectory_index
            ),
            "global_checkpoint": global_checkpoint,
            "trajectories": [
                {
                    "current_index": (
                        trajectory.current_index
                    ),
                    "stage_discoveries": (
                        trajectory.stage_discoveries
                    ),
                    "stage_gain": trajectory.stage_gain,
                    "stage_steps": trajectory.stage_steps,
                    "beam": [
                        {
                            "bits": head.board.bits.tolist(),
                            "covered": head.covered,
                            "edit_scale": head.edit_scale,
                            "attempts": head.attempts,
                            "zero_gain_attempts": (
                                head.zero_gain_attempts
                            ),
                        }
                        for head in trajectory.beam
                    ],
                }
                for trajectory in trajectories
            ],
            "discovered_outputs": sorted(
                discovered_outputs
            ),
            "board_generator_state": (
                board_generator.get_state()
            ),
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
        + ("\n" if replay_inputs else ""),
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


def random_board(
    generator: torch.Generator,
) -> BoardEvaluation:
    bits = torch.randint(
        0,
        2,
        (INPUT_CYCLES,),
        generator=generator,
        dtype=torch.long,
    )
    return record_rollout(bits.tolist())


def pending_coverage(
    global_checkpoint: torch.Tensor,
    trajectories: list[Trajectory],
) -> torch.Tensor:
    pending = global_checkpoint.clone()
    for trajectory in trajectories:
        pending |= trajectory.stage_discoveries
    return pending


def synchronize_trajectories(
    trajectories: list[Trajectory],
    global_checkpoint: torch.Tensor,
    board_generator: torch.Generator,
    initial_edit_scale: float,
    preserve_trajectory_index: int | None = None,
) -> None:
    for trajectory in trajectories:
        global_checkpoint |= trajectory.stage_discoveries

    for trajectory_index, trajectory in enumerate(
        trajectories
    ):
        if (
            trajectory.stage_gain > 0
            or trajectory_index
            == preserve_trajectory_index
        ):
            baseline_board = trajectory.current_head.board
            baseline_scale = trajectory.current_head.edit_scale
        else:
            baseline_board = random_board(board_generator)
            baseline_scale = initial_edit_scale

        trajectory.reset(
            TrajectoryHead(
                board=baseline_board,
                covered=global_checkpoint.clone(),
                edit_scale=baseline_scale,
            )
        )


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
) -> BoardEvaluation:
    return record_rollout(candidate_bits.tolist())


def score_rollout_coverage(
    rollout_coverage: torch.Tensor,
    covered: torch.Tensor,
) -> tuple[int, int, float, float]:
    new_count = int(
        (rollout_coverage & ~covered).sum().item()
    )
    repeated_count = int(
        (rollout_coverage & covered).sum().item()
    )
    coverage_ratio = (
        int(covered.sum().item())
        / COVERABLE_VARIABLE_COUNT
    )
    rollout_count = int(rollout_coverage.sum().item())
    repeat_fraction = (
        repeated_count / rollout_count
        if rollout_count
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
    actual_coverage: torch.Tensor,
    actual_coverage_score: float,
    covered: torch.Tensor,
    edit_scale: float,
) -> tuple[
    torch.Tensor,
    int | None,
    TrajectoryHead | None,
]:
    credits = torch.empty(
        INPUT_CYCLES,
        dtype=torch.float32,
    )
    post_actual_coverage = covered | actual_coverage
    best_residual_gain = 0
    best_bit_index = None
    best_head = None

    for bit_index in range(INPUT_CYCLES):
        counterfactual_bits = candidate_bits.clone()
        counterfactual_bits[bit_index] = (
            1 - counterfactual_bits[bit_index]
        )

        counterfactual_board = measure_candidate(
            counterfactual_bits
        )
        (
            _,
            _,
            _,
            counterfactual_coverage_score,
        ) = score_rollout_coverage(
            counterfactual_board.rollout_coverage,
            covered,
        )
        credits[bit_index] = (
            actual_coverage_score
            - counterfactual_coverage_score
        )

        residual_gain = int(
            (
                counterfactual_board.rollout_coverage
                & ~post_actual_coverage
            ).sum().item()
        )
        if residual_gain > best_residual_gain:
            best_residual_gain = residual_gain
            best_bit_index = bit_index
            best_head = TrajectoryHead(
                board=counterfactual_board,
                covered=covered.clone(),
                edit_scale=edit_scale,
            )

    return credits, best_bit_index, best_head


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
    trainable_parameters: list[torch.nn.Parameter],
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
        trainable_parameters,
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
    generation: int,
    trajectory_index: int,
    trajectory: Trajectory,
    global_checkpoint: torch.Tensor,
    pending_union: torch.Tensor,
    candidate_coverage: torch.Tensor,
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
    discovered_outputs: set[str],
) -> None:
    positive_credits = int((bit_credits > 0).sum())
    negative_credits = int((bit_credits < 0).sum())
    global_count = int(global_checkpoint.sum().item())
    pending_count = int(pending_union.sum().item())
    local_count = int(
        trajectory.current_head.covered.sum().item()
    )
    rollout_count = int(candidate_coverage.sum().item())

    run.log(
        {
            "search/step": step,
            "search/generation": generation,
            "search/trajectory": trajectory_index,
            "trajectory/stage_step": (
                trajectory.stage_steps
            ),
            "trajectory/stage_gain": (
                trajectory.stage_gain
            ),
            "beam/size": len(trajectory.beam),
            "beam/current_index": (
                trajectory.current_index
            ),
            "beam/current_attempts": (
                trajectory.current_head.attempts
            ),
            "beam/current_failure_ratio": (
                trajectory.current_head.failure_ratio
            ),
            "coverage/rollout": rollout_count,
            "coverage/gain": coverage_gain,
            "coverage/repeated": repeated_coverage,
            "coverage/repeat_surface_ratio": (
                repeated_coverage
                / COVERABLE_VARIABLE_COUNT
            ),
            "coverage/repeat_fraction": repeat_fraction,
            "coverage/score": coverage_score,
            "coverage/global_checkpoint": global_count,
            "coverage/global_checkpoint_ratio": (
                global_count
                / COVERABLE_VARIABLE_COUNT
            ),
            "coverage/pending_union": pending_count,
            "coverage/pending_union_ratio": (
                pending_count / COVERABLE_VARIABLE_COUNT
            ),
            "coverage/local": local_count,
            "coverage/local_ratio": (
                local_count / COVERABLE_VARIABLE_COUNT
            ),
            "output/discovered": len(discovered_outputs),
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
        f"generation={generation} "
        f"trajectory={trajectory_index} "
        f"stage={trajectory.stage_steps} "
        "beam="
        f"{trajectory.current_index}/{len(trajectory.beam)} "
        f"global={global_count} "
        f"pending={pending_count} "
        f"local={local_count} "
        f"gain={coverage_gain:+d} "
        f"credits=+{positive_credits}/"
        f"-{negative_credits} "
        f"loss={float(loss.detach()):.6f}",
        flush=True,
    )


def train(args: argparse.Namespace) -> None:
    torch.manual_seed(args.seed)
    device = select_device(args.device)
    board_generator = torch.Generator().manual_seed(
        args.seed
    )

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

    reference_tokenizer = ReferenceTokenizer().to(device)
    trajectory_editor = TrajectoryEditor(
        reference_token_count=(
            reference_tokenizer.output_token_count
        ),
        d_model=reference_tokenizer.d_model,
    ).to(device)
    reference_tokenizer.train()
    trajectory_editor.train()
    trainable_parameters = [
        *reference_tokenizer.parameters(),
        *trajectory_editor.parameters(),
    ]
    optimizer = torch.optim.AdamW(
        trainable_parameters,
        lr=args.learning_rate,
    )

    global_checkpoint = torch.zeros(
        COVERABLE_VARIABLE_COUNT,
        dtype=torch.bool,
    )
    trajectories = [
        Trajectory(
            beam=[
                TrajectoryHead(
                    board=random_board(board_generator),
                    covered=global_checkpoint.clone(),
                    edit_scale=args.initial_edit_scale,
                )
            ],
            current_index=0,
            stage_discoveries=torch.zeros_like(
                global_checkpoint
            ),
        )
        for _ in range(args.trajectory_count)
    ]
    discovered_outputs: set[str] = set()
    replay_inputs: list[list[int]] = []
    replay_input_keys: set[tuple[int, ...]] = set()
    generation = 0
    next_trajectory_index = 0

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
        for parameter in trainable_parameters
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
            trajectory_index = next_trajectory_index
            next_trajectory_index = (
                next_trajectory_index + 1
            ) % len(trajectories)
            trajectory = trajectories[trajectory_index]
            current_head = trajectory.current_head
            completion = coverage_completion(
                current_head.covered
            )

            current_edit_scale = current_head.edit_scale
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
            reference_tokens = reference_tokenizer(
                current_head.board.bits[None].to(device),
                current_head.board.frames[None].to(device),
                completion[None].to(device),
                current_head.board.phases[None].to(device),
            )
            (
                edit_logits,
                predicted_scale_logits,
            ) = trajectory_editor(
                reference_tokens,
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
                current_bits=current_head.board.bits,
                distribution=distribution,
            )

            candidate_boards = [
                measure_candidate(candidate_bits[index])
                for index in range(branch_count)
            ]
            branch_gains = [
                int(
                    (
                        board.rollout_coverage
                        & ~current_head.covered
                    ).sum().item()
                )
                for board in candidate_boards
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
            winning_board = candidate_boards[winning_branch]
            candidate_coverage = (
                winning_board.rollout_coverage
            )
            (
                coverage_gain,
                repeated_coverage,
                repeat_fraction,
                coverage_score,
            ) = score_rollout_coverage(
                candidate_coverage,
                current_head.covered,
            )
            (
                bit_credits,
                best_counterfactual_bit,
                best_counterfactual_head,
            ) = measure_counterfactual_credits(
                winning_board.bits,
                candidate_coverage,
                coverage_score,
                current_head.covered,
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
                candidate_bits=winning_board.bits,
                current_bits=current_head.board.bits,
                zero_gain_attempts=(
                    current_head.zero_gain_attempts
                ),
            )

            (
                policy_loss,
                entropy,
                loss,
                gradient_norm,
                credit_scale,
            ) = optimize_model(
                trainable_parameters=trainable_parameters,
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

            current_head.attempts += 1
            if coverage_gain == 0:
                current_head.zero_gain_attempts += 1

            if coverage_gain > 0:
                child_attempts = 0
                child_zero_gain_attempts = 0
            else:
                child_attempts = current_head.attempts
                child_zero_gain_attempts = (
                    current_head.zero_gain_attempts
                )

            winning_head = TrajectoryHead(
                board=winning_board,
                covered=(
                    current_head.covered
                    | candidate_coverage
                ),
                edit_scale=winning_edit_scale,
                attempts=child_attempts,
                zero_gain_attempts=(
                    child_zero_gain_attempts
                ),
            )
            trajectory.record_discoveries(
                candidate_coverage,
                global_checkpoint,
            )
            trajectory.stage_steps += 1

            major_output_event = (
                bool(winning_board.output)
                and winning_board.output
                not in discovered_outputs
            )
            if major_output_event:
                discovered_outputs.add(winning_board.output)

            if coverage_gain > 0 or major_output_event:
                replay_key = tuple(
                    int(bit)
                    for bit in winning_board.bits.tolist()
                )
                if replay_key not in replay_input_keys:
                    replay_input_keys.add(replay_key)
                    replay_inputs.append(list(replay_key))

            if best_counterfactual_head is not None:
                trajectory.append_head(
                    best_counterfactual_head,
                    args.beam_size,
                )
            winning_head_index = trajectory.append_head(
                winning_head,
                args.beam_size,
            )
            trajectory.current_index = winning_head_index

            if (
                coverage_gain == 0
                and not major_output_event
                and len(trajectory.beam) > 1
                and float(torch.rand(()))
                < winning_head.failure_ratio
            ):
                other_indices = [
                    index
                    for index in range(len(trajectory.beam))
                    if index != winning_head_index
                ]
                selected_other = int(
                    torch.randint(
                        len(other_indices),
                        (),
                    ).item()
                )
                trajectory.current_index = other_indices[
                    selected_other
                ]

            current_pending_coverage = pending_coverage(
                global_checkpoint,
                trajectories,
            )
            log_training_step(
                run=run,
                step=step,
                generation=generation,
                trajectory_index=trajectory_index,
                trajectory=trajectory,
                global_checkpoint=global_checkpoint,
                pending_union=current_pending_coverage,
                candidate_coverage=candidate_coverage,
                coverage_gain=coverage_gain,
                repeated_coverage=repeated_coverage,
                repeat_fraction=repeat_fraction,
                coverage_score=coverage_score,
                bit_credits=bit_credits,
                candidate_bits=winning_board.bits,
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
                discovered_outputs=discovered_outputs,
            )

            generation_complete = all(
                item.stage_steps
                >= args.steps_per_generation
                for item in trajectories
            )
            if (
                major_output_event
                or generation_complete
                or bool(current_pending_coverage.all())
            ):
                synchronize_trajectories(
                    trajectories=trajectories,
                    global_checkpoint=global_checkpoint,
                    board_generator=board_generator,
                    initial_edit_scale=(
                        args.initial_edit_scale
                    ),
                    preserve_trajectory_index=(
                        trajectory_index
                        if major_output_event
                        else None
                    ),
                )
                generation += 1
                next_trajectory_index = 0

            save_progress(
                checkpoint_path=args.checkpoint,
                replay_path=args.replay_inputs,
                reference_tokenizer=reference_tokenizer,
                trajectory_editor=trajectory_editor,
                optimizer=optimizer,
                step=step,
                generation=generation,
                next_trajectory_index=next_trajectory_index,
                global_checkpoint=global_checkpoint,
                trajectories=trajectories,
                discovered_outputs=discovered_outputs,
                board_generator=board_generator,
                replay_inputs=replay_inputs,
                config=config,
            )

            if bool(global_checkpoint.all()):
                print("coverage complete", flush=True)
                break

        final_pending_coverage = pending_coverage(
            global_checkpoint,
            trajectories,
        )
        global_count = int(global_checkpoint.sum().item())
        pending_count = int(
            final_pending_coverage.sum().item()
        )
        run.summary["final_global_coverage"] = global_count
        run.summary["final_global_ratio"] = (
            global_count / COVERABLE_VARIABLE_COUNT
        )
        run.summary["final_pending_coverage"] = (
            pending_count
        )
        run.summary["final_pending_ratio"] = (
            pending_count
            / COVERABLE_VARIABLE_COUNT
        )
        run.summary["generations"] = generation
        run.summary["discovered_outputs"] = len(
            discovered_outputs
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
        "--trajectory-count",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--steps-per-generation",
        type=int,
        default=32,
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=8,
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
    if args.trajectory_count <= 0:
        parser.error(
            "--trajectory-count must be positive"
        )
    if args.steps_per_generation <= 0:
        parser.error(
            "--steps-per-generation must be positive"
        )
    if args.beam_size <= 0:
        parser.error(
            "--beam-size must be positive"
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
