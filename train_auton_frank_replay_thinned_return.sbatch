#!/bin/bash
#SBATCH --job-name=marl_replay_ret
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/frank_replay_thinned_return_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/frank_replay_thinned_return_%j.err
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
    "Treatment: replay PPO for actor and critic; no interleaved SFT."
    "Warmup: critic trains on all 2,560 rows, while a uniform 256-row subset from each of steps 1-10 enters replay."
    "Replay: 50% of the mixed batch (256 fresh + 256 replay), sampled 90/10 using advantage^0.6 * mean_return^0.5 * recency and uniform."
    "Replay begins at step 11; exact sampled row IDs and source statistics are written to a run-specific JSONL trace."
    "Full resumable checkpoints, including replay state, at steps 10, 30, and 75."
)

REPLAY_ENABLE=true
REPLAY_FRACTION=0.5
REPLAY_SAMPLER=recency_advantage_return
REPLAY_MINIMUM_BUFFER_UPDATES=8
REPLAY_MINIMUM_BUFFER_ROWS=2048
REPLAY_CAPACITY_UPDATES=null
REPLAY_PRIORITY_ALPHA=0.6
REPLAY_RETURN_ALPHA=0.5
REPLAY_PRIORITIZED_FRACTION=0.9
REPLAY_RECENCY_HALF_LIFE_UPDATES=16.0
REPLAY_PRIORITY_EPSILON=1.0e-6
REPLAY_SEED=90001
REPLAY_WARMUP_MAX_ROWS_PER_UPDATE=256
REPLAY_WARMUP_ADMISSION_SEED=90003
REPLAY_SAMPLE_TRACE_PATH="/zfsauton2/home/frankwu2/unscripted/Verlog/logs/replay_sample_trace_${SLURM_JOB_ID}.jsonl"

INTERLEAVED_SFT_ENABLE=false

SAVE_ACTOR_CHECKPOINT=true
ACTOR_SAVE_STEPS='[10,30,75]'
CRITIC_SAVE_STEPS='[10,30,75]'
CRITIC_CHECKPOINT_CONTENTS='["model","optimizer","extra"]'

PROJECT_DIR="/zfsauton2/home/frankwu2/unscripted/Verlog"
source "$PROJECT_DIR/train_auton_frank.sbatch"
