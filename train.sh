export WANDB_ENTITY="<your-wandb-entity>"
read -rsp "W&B API key: " WANDB_API_KEY
echo
export WANDB_API_KEY

uv run python src/ml_train.py \
    --wandb-mode online \
    --wandb-project asic-puzzle-ml \
    --device auto \
    --trajectory-count 4 \
    --steps-per-generation 32 \
    --beam-size 8 \
    --max-steps 1000
