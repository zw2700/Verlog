#!/bin/bash
#SBATCH --job-name=replay_ret_smoke
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/replay_ret_smoke_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/replay_ret_smoke_%j.err
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

# Steps 1-2 each train the critic on 64 rows and uniformly admit 32. Step 3
# starts replay from the 64 strictly-past admitted rows; steps 3-4 exercise the
# return-aware sampler, trace writer, mixed PPO, and post-warmup insertion.
export NUM_GPUS_PER_NODE=1
export NUM_ENVS=4
export BATCH_SIZE=32
export VAL_BATCH_SIZE=8
export MODEL_PATH="${MODEL_PATH:-Qwen/Qwen2.5-1.5B-Instruct}"
export TOTAL_TRAINING_STEPS=4
export CRITIC_WARMUP=2
export CRITIC_WARMUP_BATCH_REPEAT_TIMES=2
export CRITIC_WARMUP_BATCH_DIVIDE_RATIO=1
export OFFLOAD=true
export ROLLOUT_GPU_MEMORY_UTILIZATION="${ROLLOUT_GPU_MEMORY_UTILIZATION:-0.25}"
export USE_KL_IN_REWARD=false

export REPLAY_ENABLE=true
export REPLAY_FRACTION=0.5
export REPLAY_SAMPLER=recency_advantage_return
export REPLAY_MINIMUM_BUFFER_UPDATES=2
export REPLAY_MINIMUM_BUFFER_ROWS=64
export REPLAY_CAPACITY_UPDATES=null
export REPLAY_PRIORITY_ALPHA=0.6
export REPLAY_RETURN_ALPHA=0.5
export REPLAY_PRIORITIZED_FRACTION=0.9
export REPLAY_RECENCY_HALF_LIFE_UPDATES=16.0
export REPLAY_PRIORITY_EPSILON=1.0e-6
export REPLAY_SEED=90001
export REPLAY_WARMUP_MAX_ROWS_PER_UPDATE=32
export REPLAY_WARMUP_ADMISSION_SEED=90003
export REPLAY_SAMPLE_TRACE_PATH="$PROJECT_DIR/logs/replay_sample_trace_smoke_${SLURM_JOB_ID}.jsonl"

export INTERLEAVED_SFT_ENABLE=false
export ACTOR_SAVE_STEPS=null
export CRITIC_SAVE_STEPS=null

exec bash "$PROJECT_DIR/train_auton_frank.sbatch"
