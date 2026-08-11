#!/bin/bash
#SBATCH --job-name=replay_smoke_1g
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/replay_smoke_1g_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/replay_smoke_1g_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=200G
#SBATCH --time=05:59:00
#SBATCH --gres=gpu:a6000:1
#SBATCH --gres-flags=enforce-binding

set -euo pipefail

PROJECT_DIR="/zfsauton2/home/frankwu2/unscripted/Verlog"

# Keep the smoke run small while exercising the complete replay dataflow:
# steps 1-2 collect warmup rollouts; steps 3-4 consume strictly-past replay.
export NUM_GPUS_PER_NODE=1
export NUM_ENVS=4
export BATCH_SIZE=32
export VAL_BATCH_SIZE=8
# A 3B critic reaches vLLM startup but OOMs when Adam lazily initializes its
# unsharded state on one GPU (job 25753). Use the same model family at 1.5B and
# omit the independent reference-policy model; this smoke targets replay/SFT
# integration rather than production-scale memory behavior.
export MODEL_PATH="${MODEL_PATH:-Qwen/Qwen2.5-1.5B-Instruct}"
export TOTAL_TRAINING_STEPS=4
export CRITIC_WARMUP=2
export CRITIC_WARMUP_BATCH_REPEAT_TIMES=1
export CRITIC_WARMUP_BATCH_DIVIDE_RATIO=1
export OFFLOAD=true
# At 1.5B with no reference worker, 0.25 has sufficient startup and KV-cache
# headroom while leaving room for unsharded actor/critic optimizer state.
export ROLLOUT_GPU_MEMORY_UTILIZATION="${ROLLOUT_GPU_MEMORY_UTILIZATION:-0.25}"
export USE_KL_IN_REWARD=false

export REPLAY_ENABLE=true
export REPLAY_FRACTION=0.5
export REPLAY_SAMPLER=recency_advantage
export REPLAY_MINIMUM_BUFFER_UPDATES=2
export REPLAY_CAPACITY_UPDATES=null

# Naive replay PPO is the default smoke treatment. Passing `sft` as the first
# script argument enables the SFT path without relying on Slurm --export/user
# environment retrieval. A rate of 1 guarantees an SFT update on each
# post-warmup step instead of accumulating only half an update in this run.
SMOKE_MODE="${1:-replay}"
case "$SMOKE_MODE" in
    replay)
        export INTERLEAVED_SFT_ENABLE=false
        ;;
    sft)
        export INTERLEAVED_SFT_ENABLE=true
        ;;
    *)
        echo "Unknown smoke mode '$SMOKE_MODE'; expected 'replay' or 'sft'." >&2
        exit 2
        ;;
esac
export SFT_UPDATES_PER_GLOBAL_STEP="${SFT_UPDATES_PER_GLOBAL_STEP:-1.0}"
export SFT_GLOBAL_BATCH_SIZE="${SFT_GLOBAL_BATCH_SIZE:-8}"

# The four-step smoke run does not need model checkpoints.
export ACTOR_SAVE_STEPS=null
export CRITIC_SAVE_STEPS=null

exec bash "$PROJECT_DIR/train_auton_frank.sbatch"
