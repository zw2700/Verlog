#!/usr/bin/env bash
#SBATCH --job-name=qwen3_self_rs_merge
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_self_rs_merge_%A_%a.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_self_rs_merge_%A_%a.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --array=0-5%2

set -euo pipefail

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
CHECKPOINT_ROOT=${CHECKPOINT_ROOT:-/zfsauton/scratch/frankwu2/unscripted/Verlog/checkpoints/sft}
SWEEP_TAG=${SWEEP_TAG:-qwen3_self_rs_sweep_v1}
TASK_INDEX=${SLURM_ARRAY_TASK_ID:-}
SWEEP_ROOT=${CHECKPOINT_ROOT}/${SWEEP_TAG}

case ${TASK_INDEX} in
    0)
        CHECKPOINT_DIR=${SWEEP_ROOT}/raw25/global_step_7
        MERGE_NAME=raw25_step7
        ;;
    1)
        CHECKPOINT_DIR=${SWEEP_ROOT}/raw50/global_step_16
        MERGE_NAME=raw50_step16
        ;;
    2)
        CHECKPOINT_DIR=${SWEEP_ROOT}/raw100_steps8_32/global_step_8
        MERGE_NAME=raw100_step8
        ;;
    3)
        CHECKPOINT_DIR=${SWEEP_ROOT}/raw100_steps8_32/global_step_16
        MERGE_NAME=raw100_step16
        ;;
    4)
        CHECKPOINT_DIR=${SWEEP_ROOT}/raw100_steps8_32/global_step_32
        MERGE_NAME=raw100_step32
        ;;
    5)
        CHECKPOINT_DIR=${SWEEP_ROOT}/compact100/global_step_32
        MERGE_NAME=compact100_step32
        ;;
    *)
        echo "SLURM_ARRAY_TASK_ID must be between 0 and 5" >&2
        exit 2
        ;;
esac

if [[ ! -d ${CHECKPOINT_DIR} ]]; then
    echo "Checkpoint does not exist: ${CHECKPOINT_DIR}" >&2
    exit 2
fi

export SWEEP_TAG
cd "${PROJECT_DIR}"
exec bash scripts/sft/merge_checkpoint.sbatch "${CHECKPOINT_DIR}" "${MERGE_NAME}"
