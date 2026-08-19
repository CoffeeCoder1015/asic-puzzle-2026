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


class CircuitFrameEncoder(nn.Module):
    def __init__(
        self,
        circuit_width: int,
        frame_count: int,
        d_model: int,
        hidden_width: int,
    ):
        super().__init__()
        self.circuit_width = circuit_width
        self.frame_count = frame_count

        self.frame_mlp = nn.Sequential(
            nn.Linear(
                circuit_width * 2,
                hidden_width,
            ),
            nn.GELU(),
            nn.Linear(hidden_width, d_model),
        )
        self.cycle_embedding = nn.Embedding(
            frame_count,
            d_model,
        )
        self.phase_embedding = nn.Embedding(2, d_model)
        self.token_type_embedding = nn.Embedding(
            1,
            d_model,
        )
        self.output_norm = nn.LayerNorm(d_model)

    def forward(
        self,
        circuit_frames: Tensor,
        coverage_completion: Tensor,
        phases: Tensor,
    ) -> Tensor:
        if circuit_frames.ndim != 3:
            raise ValueError(
                "circuit_frames must have shape "
                "[batch, frame_count, circuit_width]"
            )

        expected_frame_shape = (
            circuit_frames.shape[0],
            self.frame_count,
            self.circuit_width,
        )
        if tuple(circuit_frames.shape) != expected_frame_shape:
            raise ValueError(
                "circuit_frames must have shape "
                f"{expected_frame_shape}"
            )

        if tuple(coverage_completion.shape) != (
            expected_frame_shape
        ):
            raise ValueError(
                "coverage_completion must have shape "
                f"{expected_frame_shape}"
            )

        expected_phase_shape = (
            circuit_frames.shape[0],
            self.frame_count,
        )
        if tuple(phases.shape) != expected_phase_shape:
            raise ValueError(
                f"phases must have shape {expected_phase_shape}"
            )

        cycle_positions = torch.arange(
            self.frame_count,
            device=circuit_frames.device,
        )
        frame_features = torch.stack(
            (
                circuit_frames,
                coverage_completion,
            ),
            dim=-1,
        ).flatten(start_dim=-2)
        signed_frame_features = (
            frame_features * 2.0 - 1.0
        )

        return self.output_norm(
            self.frame_mlp(signed_frame_features)
            + self.cycle_embedding(
                cycle_positions
            ).unsqueeze(0)
            + self.phase_embedding(phases)
            + self.token_type_embedding.weight[0]
        )


class TrajectoryEditor(nn.Module):
    def __init__(
        self,
        input_length: int = INPUT_CYCLES,
        frame_count: int = FRAME_COUNT,
        circuit_width: int = len(CIRCUIT_VARIABLES),
        d_model: int = 128,
        circuit_hidden: int = 512,
        attention_heads: int = 4,
        transformer_blocks: int = 4,
        feedforward_width: int = 512,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.input_length = input_length

        self.input_embedding = InputTokenEmbedding(
            input_length=input_length,
            d_model=d_model,
        )
        self.circuit_encoder = CircuitFrameEncoder(
            circuit_width=circuit_width,
            frame_count=frame_count,
            d_model=d_model,
            hidden_width=circuit_hidden,
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
        self.output_head = nn.Linear(d_model, 1)

    def forward(
        self,
        input_bits: Tensor,
        circuit_frames: Tensor,
        coverage_completion: Tensor,
        phases: Tensor,
    ) -> Tensor:
        if input_bits.shape[0] != circuit_frames.shape[0]:
            raise ValueError(
                "input_bits and circuit_frames must have "
                "the same batch size"
            )

        input_tokens = self.input_embedding(input_bits)
        circuit_tokens = self.circuit_encoder(
            circuit_frames,
            coverage_completion,
            phases,
        )
        context = torch.cat(
            (input_tokens, circuit_tokens),
            dim=1,
        )
        contextualized = self.transformer(context)
        input_context = contextualized[
            :,
            :self.input_length,
        ]

        return self.output_head(
            input_context
        ).squeeze(-1)
