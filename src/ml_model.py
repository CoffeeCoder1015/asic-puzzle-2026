import torch
from torch import Tensor, nn
from torch.utils.checkpoint import checkpoint

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


class ContentWeightedFrameCompressor(nn.Module):
    def __init__(
        self,
        source_count: int,
        input_width: int,
        output_width: int,
        output_count: int,
    ):
        super().__init__()
        self.source_count = source_count
        self.input_width = input_width
        self.output_count = output_count

        self.value_projection = nn.Linear(
            input_width,
            output_width,
        )
        self.weight_projection = nn.Linear(
            input_width,
            output_count,
            bias=False,
        )
        self.variable_bias = nn.Parameter(
            torch.zeros(output_count, source_count)
        )
        self.slot_embedding = nn.Embedding(
            output_count,
            output_width,
        )
        self.output_norm = nn.LayerNorm(output_width)

    def forward(self, source_tokens: Tensor) -> Tensor:
        if source_tokens.ndim != 3:
            raise ValueError(
                "source_tokens must have shape "
                "[batch, source_count, input_width]"
            )

        expected_shape = (
            source_tokens.shape[0],
            self.source_count,
            self.input_width,
        )
        if tuple(source_tokens.shape) != expected_shape:
            raise ValueError(
                "source_tokens must have shape "
                f"{expected_shape}"
            )

        values = self.value_projection(source_tokens)
        weight_logits = self.weight_projection(
            source_tokens
        ).transpose(1, 2)
        weight_logits = (
            weight_logits
            + self.variable_bias.unsqueeze(0)
        )
        weights = torch.softmax(
            weight_logits.float(),
            dim=-1,
        ).to(values.dtype)
        compressed = torch.matmul(weights, values)

        return self.output_norm(
            compressed
            + self.slot_embedding.weight.unsqueeze(0)
        )


class RolloutFrameEncoder(nn.Module):
    def __init__(
        self,
        frame_width: int,
        frame_count: int,
        d_model: int,
        tokens_per_frame: int,
        inner_width: int,
        attention_heads: int,
        feedforward_width: int,
        dropout: float,
        frame_chunk_size: int,
    ):
        super().__init__()
        if frame_chunk_size <= 0:
            raise ValueError(
                "frame_chunk_size must be positive"
            )

        self.frame_width = frame_width
        self.frame_count = frame_count
        self.d_model = d_model
        self.tokens_per_frame = tokens_per_frame
        self.frame_chunk_size = frame_chunk_size

        self.bit_embedding = nn.Embedding(2, inner_width)
        self.variable_embedding = nn.Embedding(
            frame_width,
            inner_width,
        )
        self.transformer_block = nn.TransformerEncoderLayer(
            d_model=inner_width,
            nhead=attention_heads,
            dim_feedforward=feedforward_width,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.transformer_output_norm = nn.LayerNorm(
            inner_width
        )
        self.compressor = ContentWeightedFrameCompressor(
            source_count=frame_width,
            input_width=inner_width,
            output_width=d_model,
            output_count=tokens_per_frame,
        )

    def _encode_frame_chunk(
        self,
        frame_bits: Tensor,
    ) -> Tensor:
        variable_positions = torch.arange(
            self.frame_width,
            device=frame_bits.device,
        )
        cell_tokens = (
            self.bit_embedding(frame_bits)
            + self.variable_embedding(
                variable_positions
            ).unsqueeze(0)
        )
        contextualized = self.transformer_block(
            cell_tokens
        )
        contextualized = self.transformer_output_norm(
            contextualized
        )

        return self.compressor(contextualized)

    def forward(
        self,
        frames: Tensor,
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

        frame_bits = frames.to(torch.long).reshape(
            frames.shape[0] * self.frame_count,
            self.frame_width,
        )
        encoded_chunks = []

        for frame_chunk in frame_bits.split(
            self.frame_chunk_size
        ):
            if self.training:
                encoded_chunk = checkpoint(
                    self._encode_frame_chunk,
                    frame_chunk,
                    use_reentrant=False,
                )
            else:
                encoded_chunk = (
                    self._encode_frame_chunk(frame_chunk)
                )

            encoded_chunks.append(encoded_chunk)

        return torch.cat(
            encoded_chunks,
            dim=0,
        ).reshape(
            frames.shape[0],
            self.frame_count,
            self.tokens_per_frame,
            self.d_model,
        )


class ReferenceTokenizer(nn.Module):
    def __init__(
        self,
        input_length: int = INPUT_CYCLES,
        frame_count: int = FRAME_COUNT,
        circuit_width: int = len(CIRCUIT_VARIABLES),
        d_model: int = 256,
        rollout_tokens_per_frame: int = 4,
        frame_inner_width: int = 128,
        frame_attention_heads: int = 4,
        frame_feedforward_width: int = 512,
        dropout: float = 0.1,
        frame_chunk_size: int = 16,
    ):
        super().__init__()
        self.input_length = input_length
        self.frame_count = frame_count
        self.d_model = d_model
        self.rollout_tokens_per_frame = (
            rollout_tokens_per_frame
        )
        self.output_token_count = (
            input_length
            + 2 * frame_count * rollout_tokens_per_frame
        )

        self.input_embedding = InputTokenEmbedding(
            input_length=input_length,
            d_model=d_model,
        )
        self.rollout_encoder = RolloutFrameEncoder(
            frame_width=circuit_width,
            frame_count=frame_count,
            d_model=d_model,
            tokens_per_frame=rollout_tokens_per_frame,
            inner_width=frame_inner_width,
            attention_heads=frame_attention_heads,
            feedforward_width=frame_feedforward_width,
            dropout=dropout,
            frame_chunk_size=frame_chunk_size,
        )
        self.rollout_position_embedding = nn.Embedding(
            frame_count * rollout_tokens_per_frame,
            d_model,
        )
        self.phase_embedding = nn.Embedding(2, d_model)
        self.rollout_type_embedding = nn.Embedding(
            2,
            d_model,
        )
        self.rollout_output_norm = nn.LayerNorm(d_model)

    def _add_rollout_metadata(
        self,
        frame_tokens: Tensor,
        phases: Tensor,
        token_type: int,
    ) -> Tensor:
        token_count = (
            self.frame_count
            * self.rollout_tokens_per_frame
        )
        token_positions = torch.arange(
            token_count,
            device=frame_tokens.device,
        )
        token_phases = phases.unsqueeze(-1).expand(
            -1,
            -1,
            self.rollout_tokens_per_frame,
        ).reshape(
            frame_tokens.shape[0],
            token_count,
        )
        flattened_tokens = frame_tokens.reshape(
            frame_tokens.shape[0],
            token_count,
            self.d_model,
        )

        return self.rollout_output_norm(
            flattened_tokens
            + self.rollout_position_embedding(
                token_positions
            ).unsqueeze(0)
            + self.phase_embedding(token_phases)
            + self.rollout_type_embedding.weight[
                token_type
            ]
        )

    def forward(
        self,
        input_bits: Tensor,
        circuit_frames: Tensor,
        coverage_completion: Tensor,
        phases: Tensor,
    ) -> Tensor:
        batch_size = input_bits.shape[0]
        if (
            circuit_frames.shape[0] != batch_size
            or coverage_completion.shape[0] != batch_size
            or phases.shape[0] != batch_size
        ):
            raise ValueError(
                "all reference inputs must have the same "
                "batch size"
            )

        expected_phase_shape = (
            batch_size,
            self.frame_count,
        )
        if tuple(phases.shape) != expected_phase_shape:
            raise ValueError(
                "phases must have shape "
                f"{expected_phase_shape}"
            )

        input_tokens = self.input_embedding(input_bits)
        circuit_tokens = self._add_rollout_metadata(
            self.rollout_encoder(circuit_frames),
            phases,
            token_type=0,
        )
        coverage_tokens = self._add_rollout_metadata(
            self.rollout_encoder(coverage_completion),
            phases,
            token_type=1,
        )

        return torch.cat(
            (
                input_tokens,
                circuit_tokens,
                coverage_tokens,
            ),
            dim=1,
        )


class TrajectoryEditor(nn.Module):
    def __init__(
        self,
        input_length: int = INPUT_CYCLES,
        reference_token_count: int = (
            INPUT_CYCLES + 2 * FRAME_COUNT * 4
        ),
        d_model: int = 256,
        attention_heads: int = 8,
        transformer_blocks: int = 4,
        feedforward_width: int = 1024,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.input_length = input_length
        self.reference_token_count = reference_token_count
        self.d_model = d_model

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
        reference_tokens: Tensor,
        edit_scale: Tensor,
    ) -> tuple[Tensor, Tensor]:
        if reference_tokens.ndim != 3:
            raise ValueError(
                "reference_tokens must have shape "
                "[1, reference_token_count, d_model]"
            )

        expected_reference_shape = (
            1,
            self.reference_token_count,
            self.d_model,
        )
        if tuple(reference_tokens.shape) != (
            expected_reference_shape
        ):
            raise ValueError(
                "reference_tokens must have shape "
                f"{expected_reference_shape}"
            )

        if edit_scale.ndim != 1 or edit_scale.shape[0] == 0:
            raise ValueError(
                "edit_scale must contain at least one branch"
            )

        branch_count = edit_scale.shape[0]
        expected_edit_scale_shape = (branch_count,)
        if tuple(edit_scale.shape) != expected_edit_scale_shape:
            raise ValueError(
                "edit_scale must have shape "
                f"{expected_edit_scale_shape}"
            )

        branch_reference_tokens = reference_tokens.expand(
            branch_count,
            -1,
            -1,
        )
        scale_condition = self.edit_scale_embedding(
            edit_scale[:, None]
        )
        scale_token = self.scale_token_embedding.weight[
            0
        ][None, None, :].expand(
            branch_count,
            -1,
            -1,
        )
        scale_token = scale_token + scale_condition[:, None, :]
        context = torch.cat(
            (
                scale_token,
                branch_reference_tokens,
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
