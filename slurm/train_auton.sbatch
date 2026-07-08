#!/bin/bash
#SBATCH --job-name=auton
#SBATCH --output=logs/auton_%j.out
#SBATCH --error=logs/auton_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=200G
#SBATCH --time=47:59:00
#SBATCH --gres=gpu:a6000:4
#
# Thin wrapper: all training hyperparameters live in configs/train_auton.yaml.
# This file only does Slurm resource requests + env setup, then one launch.
#
# Submit as-is:
#   sbatch slurm/train_auton.sbatch
#
# Override any config value (Hydra) by passing extra args — they flow through "$@":
#   sbatch slurm/train_auton.sbatch envs.env_config.students_per_batch=7 trainer.total_training_steps=100
#
# For an ablation, set `tag` so the wandb run name is self-describing:
#   sbatch slurm/train_auton.sbatch tag=students7 envs.env_config.students_per_batch=7
#   -> wandb run name "auton_students7_<jobid>"
#
# Pick a different experiment config without editing this file:
#   EXP=train_auton_smoke sbatch slurm/train_auton.sbatch

source "$(cd "$(dirname "$0")" && pwd)/common.sh"

EXP="${EXP:-train_auton}"

# experiment_name is built in the config from `tag` + $SLURM_JOB_ID, so we do NOT
# override it here — that keeps `tag=...` visible in the wandb run name.
$PYTHON_BIN -m verl.trainer.main_ppo \
    --config-path="$PROJECT_DIR/configs" \
    --config-name="$EXP" \
    "$@"

echo "=== Done ${JOB_ID} — $(date) ==="
