import torch
from torch import Tensor, nn

from ml_rollout import (
    CIRCUIT_VARIABLES,
    FRAME_COUNT,
    INPUT_CYCLES,
)


class InputTokenEmbedding(nn.Module):
    def __init__(
        self,
        input_length: int,
        d_model: int,
    ):
        super().__init__()
        self.input_length = input_length
        self.bit_embedding = nn.Embedding(2, d_model)
        self.position_embedding = nn.Embedding(
            input_length,
            d_model,
        )
        self.token_type_embedding = nn.Embedding(
            1,
            d_model,
        )

    def forward(self, input_bits: Tensor) -> Tensor:
        if input_bits.ndim != 2:
            raise ValueError(
                "input_bits must have shape "
                "[batch, input_length]"
            )

        if input_bits.shape[1] != self.input_length:
            raise ValueError(
                f"expected {self.input_length} input bits, "
                f"received {input_bits.shape[1]}"
            )

        positions = torch.arange(
            self.input_length,
            device=input_bits.device,
        )

        return (
            self.bit_embedding(input_bits)
            + self.position_embedding(positions).unsqueeze(0)
            + self.token_type_embedding.weight[0]
        )


class RolloutFrameEncoder(nn.Module):
    def __init__(
        self,
        frame_width: int,
        frame_count: int,
        d_model: int,
        hidden_width: int,
        tokens_per_frame: int,
    ):
        super().__init__()
        self.frame_width = frame_width
        self.frame_count = frame_count
        self.d_model = d_model
        self.tokens_per_frame = tokens_per_frame

        self.frame_mlp = nn.Sequential(
            nn.Linear(
                frame_width,
                hidden_width,
            ),
            nn.GELU(),
            nn.Linear(
                hidden_width,
                tokens_per_frame * d_model,
            ),
        )
        self.position_embedding = nn.Embedding(
            frame_count * tokens_per_frame,
            d_model,
        )
        self.phase_embedding = nn.Embedding(2, d_model)
        self.token_type_embedding = nn.Embedding(
            2,
            d_model,
        )
        self.output_norm = nn.LayerNorm(d_model)

    def forward(
        self,
        frames: Tensor,
        phases: Tensor,
        token_type: int,
    ) -> Tensor:
        if frames.ndim != 3:
            raise ValueError(
                "frames must have shape "
                "[batch, frame_count, frame_width]"
            )

        expected_frame_shape = (
            frames.shape[0],
            self.frame_count,
            self.frame_width,
        )
        if tuple(frames.shape) != expected_frame_shape:
            raise ValueError(
                "frames must have shape "
                f"{expected_frame_shape}"
            )

        expected_phase_shape = (
            frames.shape[0],
            self.frame_count,
        )
        if tuple(phases.shape) != expected_phase_shape:
            raise ValueError(
                f"phases must have shape {expected_phase_shape}"
            )

        if token_type not in (0, 1):
            raise ValueError("token_type must be 0 or 1")

        token_count = (
            self.frame_count * self.tokens_per_frame
        )
        token_positions = torch.arange(
            token_count,
            device=frames.device,
        )
        token_phases = phases.unsqueeze(-1).expand(
            -1,
            -1,
            self.tokens_per_frame,
        ).reshape(
            frames.shape[0],
            token_count,
        )
        signed_frames = frames * 2.0 - 1.0

        frame_tokens = self.frame_mlp(
            signed_frames
        ).reshape(
            frames.shape[0],
            token_count,
            self.d_model,
        )

        return self.output_norm(
            frame_tokens
            + self.position_embedding(
                token_positions
            ).unsqueeze(0)
            + self.phase_embedding(token_phases)
            + self.token_type_embedding.weight[token_type]
        )


class TrajectoryEditor(nn.Module):
    def __init__(
        self,
        input_length: int = INPUT_CYCLES,
        frame_count: int = FRAME_COUNT,
        circuit_width: int = len(CIRCUIT_VARIABLES),
        d_model: int = 256,
        circuit_hidden: int = 1024,
        rollout_tokens_per_frame: int = 4,
        attention_heads: int = 8,
        transformer_blocks: int = 4,
        feedforward_width: int = 1024,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.input_length = input_length

        self.input_embedding = InputTokenEmbedding(
            input_length=input_length,
            d_model=d_model,
        )
        self.rollout_encoder = RolloutFrameEncoder(
            frame_width=circuit_width,
            frame_count=frame_count,
            d_model=d_model,
            hidden_width=circuit_hidden,
            tokens_per_frame=rollout_tokens_per_frame,
        )

        transformer_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=attention_heads,
            dim_feedforward=feedforward_width,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(
            transformer_layer,
            num_layers=transformer_blocks,
            norm=nn.LayerNorm(d_model),
            enable_nested_tensor=False,
        )
        self.edit_scale_embedding = nn.Linear(1, d_model)
        self.scale_token_embedding = nn.Embedding(1, d_model)
        self.output_head = nn.Linear(d_model, 1)
        self.scale_output_head = nn.Linear(d_model, 1)

    def forward(
        self,
        input_bits: Tensor,
        circuit_frames: Tensor,
        coverage_completion: Tensor,
        phases: Tensor,
        edit_scale: Tensor,
    ) -> tuple[Tensor, Tensor]:
        if input_bits.shape[0] != circuit_frames.shape[0]:
            raise ValueError(
                "input_bits and circuit_frames must have "
                "the same batch size"
            )

        expected_edit_scale_shape = (input_bits.shape[0],)
        if tuple(edit_scale.shape) != expected_edit_scale_shape:
            raise ValueError(
                "edit_scale must have shape "
                f"{expected_edit_scale_shape}"
            )

        input_tokens = self.input_embedding(input_bits)
        circuit_tokens = self.rollout_encoder(
            circuit_frames,
            phases,
            token_type=0,
        )
        coverage_tokens = self.rollout_encoder(
            coverage_completion,
            phases,
            token_type=1,
        )
        scale_condition = self.edit_scale_embedding(
            edit_scale[:, None]
        )
        scale_token = self.scale_token_embedding.weight[
            0
        ][None, None, :].expand(
            input_bits.shape[0],
            -1,
            -1,
        )
        scale_token = scale_token + scale_condition[:, None, :]
        context = torch.cat(
            (
                scale_token,
                input_tokens,
                circuit_tokens,
                coverage_tokens,
            ),
            dim=1,
        )
        contextualized = self.transformer(context)
        input_context = contextualized[
            :,
            1:1 + self.input_length,
        ]
        scale_context = contextualized[:, 0]

        return (
            self.output_head(input_context).squeeze(-1),
            self.scale_output_head(
                scale_context
            ).squeeze(-1),
        )
