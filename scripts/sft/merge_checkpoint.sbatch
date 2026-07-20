#!/usr/bin/env bash
#SBATCH --job-name=qwen3_sft_merge
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_merge_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_merge_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=02:00:00

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: sbatch $0 CHECKPOINT_DIR MERGE_NAME" >&2
    echo "Example: sbatch $0 /path/to/raw50/global_step_16 raw50_step16" >&2
    exit 2
fi

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
ENV_PATH=/zfsauton/scratch/cpulling/conda_envs/verlog
PYTHON_BIN=${ENV_PATH}/bin/python3
MERGED_ROOT=${MERGED_ROOT:-/zfsauton/scratch/frankwu2/unscripted/Verlog/models/sft}
SWEEP_TAG=${SWEEP_TAG:-haiku_qwen3_sweep_v1}
CHECKPOINT_DIR=$(realpath "$1")
MERGE_NAME=$2
TARGET_DIR=${TARGET_DIR:-${MERGED_ROOT}/${SWEEP_TAG}/${MERGE_NAME}}

if [[ ! ${MERGE_NAME} =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "MERGE_NAME may contain only letters, digits, dot, underscore, and dash" >&2
    exit 2
fi
if [[ ! -f ${CHECKPOINT_DIR}/fsdp_config.json || ! -d ${CHECKPOINT_DIR}/huggingface ]]; then
    echo "Not a mergeable VERL FSDP checkpoint: ${CHECKPOINT_DIR}" >&2
    exit 2
fi
if [[ $(find "${CHECKPOINT_DIR}" -maxdepth 1 -name 'model_world_size_*_rank_*.pt' | wc -l) -lt 1 ]]; then
    echo "Checkpoint has no model shards: ${CHECKPOINT_DIR}" >&2
    exit 2
fi
if [[ -e ${TARGET_DIR} ]] && find "${TARGET_DIR}" -mindepth 1 -print -quit | grep -q .; then
    echo "Refusing to overwrite nonempty merged-model directory: ${TARGET_DIR}" >&2
    exit 2
fi

cd "${PROJECT_DIR}"
mkdir -p logs "${TARGET_DIR}"
export PATH=${ENV_PATH}/bin:${PATH}
export CONDA_PREFIX=${ENV_PATH}
export HF_HOME=${HF_HOME:-/zfsauton/scratch/frankwu2/.cache/huggingface}
export TMPDIR=${TMPDIR:-/zfsauton/scratch/frankwu2/tmp}
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK:-8}
mkdir -p "${HF_HOME}" "${TMPDIR}"

echo "=== FSDP checkpoint merge ==="
echo "job_id=${SLURM_JOB_ID} node=${SLURMD_NODENAME}"
echo "start_time=$(date --iso-8601=seconds)"
echo "checkpoint=${CHECKPOINT_DIR}"
echo "target=${TARGET_DIR}"
echo "============================="

"${PYTHON_BIN}" -m verl.model_merger merge \
    --backend fsdp \
    --local_dir "${CHECKPOINT_DIR}" \
    --target_dir "${TARGET_DIR}" \
    --use_cpu_initialization

if [[ ! -f ${TARGET_DIR}/config.json ]]; then
    echo "Merge did not produce config.json" >&2
    exit 1
fi
if ! find "${TARGET_DIR}" -maxdepth 1 \( -name '*.safetensors' -o -name 'pytorch_model*.bin' \) -print -quit | grep -q .; then
    echo "Merge did not produce model weights" >&2
    exit 1
fi

echo "merge_complete=$(date --iso-8601=seconds)"
du -sh "${TARGET_DIR}"
