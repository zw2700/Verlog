#!/bin/bash
#SBATCH --job-name=marl_replay_sft
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/frank_replay_sft_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/frank_replay_sft_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=200G
#SBATCH --time=47:59:00
#SBATCH --gres=gpu:a6000:4
#SBATCH --gres-flags=enforce-binding
#SBATCH --requeue

set -euo pipefail

EXP_NOTES=(
    "Treatment: replay PPO plus interleaved SFT on sampled replay responses."
    "Replay: 50% of the mixed batch, recency+advantage sampling, and warmup collection; SFT: 0.25 updates/step with batch size 32."
    "Full resumable checkpoints, including replay and SFT state, at steps 10, 30, and 75."
)

REPLAY_ENABLE=true
REPLAY_FRACTION=0.5
REPLAY_SAMPLER=recency_advantage
REPLAY_MINIMUM_BUFFER_UPDATES=8
REPLAY_CAPACITY_UPDATES=null

INTERLEAVED_SFT_ENABLE=true
SFT_UPDATES_PER_GLOBAL_STEP=0.25
SFT_GLOBAL_BATCH_SIZE=32
SFT_LEARNING_RATE_MULTIPLIER=1.0

SAVE_ACTOR_CHECKPOINT=true
ACTOR_SAVE_STEPS='[10,30,75]'
CRITIC_SAVE_STEPS='[10,30,75]'
CRITIC_CHECKPOINT_CONTENTS='["model","optimizer","extra"]'

PROJECT_DIR="/zfsauton2/home/frankwu2/unscripted/Verlog"
source "$PROJECT_DIR/train_auton_frank.sbatch"
