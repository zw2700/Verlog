#!/usr/bin/env bash
#SBATCH --job-name=qwen3_sft_eval200
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_eval200_%A_%a.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_eval200_%A_%a.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --gres=gpu:a6000:1
#SBATCH --array=0-6

set -euo pipefail

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
MODEL_ROOT=${MODEL_ROOT:-/zfsauton/scratch/frankwu2/unscripted/Verlog/models/sft/haiku_qwen3_sweep_v1}
NUM_SCENARIOS=${NUM_SCENARIOS:-200}
TASK_INDEX=${SLURM_ARRAY_TASK_ID:-}

case ${TASK_INDEX} in
    0)
        EVAL_NAME=base
        MODEL_PATH=Qwen/Qwen3-4B
        ;;
    1)
        EVAL_NAME=raw25_step7
        MODEL_PATH=${MODEL_ROOT}/raw25_step7
        ;;
    2)
        EVAL_NAME=raw50_step16
        MODEL_PATH=${MODEL_ROOT}/raw50_step16
        ;;
    3)
        EVAL_NAME=raw100_step8
        MODEL_PATH=${MODEL_ROOT}/raw100_step8
        ;;
    4)
        EVAL_NAME=raw100_step16
        MODEL_PATH=${MODEL_ROOT}/raw100_step16
        ;;
    5)
        EVAL_NAME=raw100_step32
        MODEL_PATH=${MODEL_ROOT}/raw100_step32
        ;;
    6)
        EVAL_NAME=compact100_step32
        MODEL_PATH=${MODEL_ROOT}/compact100_step32
        ;;
    *)
        echo "SLURM_ARRAY_TASK_ID must be between 0 and 6" >&2
        exit 2
        ;;
esac

if [[ ${MODEL_PATH} == /* && ! -d ${MODEL_PATH} ]]; then
    echo "Merged model does not exist: ${MODEL_PATH}" >&2
    exit 2
fi
if (( NUM_SCENARIOS <= 0 || NUM_SCENARIOS > 500 )); then
    echo "NUM_SCENARIOS must be between 1 and 500" >&2
    exit 2
fi

# Avoid port collisions if several array tasks share a physical node.
export VLLM_PORT=$((20000 + (SLURM_ARRAY_JOB_ID + TASK_INDEX * 1009) % 20000))
export EVAL_NUM_SCENARIOS=${NUM_SCENARIOS}

echo "array_job=${SLURM_ARRAY_JOB_ID} task=${TASK_INDEX}"
echo "eval_name=${EVAL_NAME} model=${MODEL_PATH} scenarios=${EVAL_NUM_SCENARIOS}"

cd "${PROJECT_DIR}"
exec bash scripts/sft/evaluate_sft.sbatch "${MODEL_PATH}" "${EVAL_NAME}"
