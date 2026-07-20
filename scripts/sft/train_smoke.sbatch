#!/usr/bin/env bash
#SBATCH --job-name=qwen3_sft_smoke
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_smoke_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_smoke_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=200G
#SBATCH --time=04:00:00
#SBATCH --gres=gpu:a6000:4
#SBATCH --gres-flags=enforce-binding

set -euo pipefail

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
ENV_PATH=/zfsauton/scratch/cpulling/conda_envs/verlog
PYTHON_BIN="${ENV_PATH}/bin/python3"

MODEL_PATH=${MODEL_PATH:-Qwen/Qwen3-4B}
DATASET_DIR=${DATASET_DIR:-${PROJECT_DIR}/outputs/sft/haiku_qwen3_pilot/dataset_raw}
SMOKE_STEPS=${SMOKE_STEPS:-8}
NUM_GPUS=${NUM_GPUS:-4}
GLOBAL_BATCH_SIZE=${GLOBAL_BATCH_SIZE:-32}
MICRO_BATCH_SIZE=${MICRO_BATCH_SIZE:-1}
MAX_LENGTH=${MAX_LENGTH:-4608}
LEARNING_RATE=${LEARNING_RATE:-5e-6}
OUTPUT_DIR=${OUTPUT_DIR:-/zfsauton/scratch/frankwu2/unscripted/Verlog/checkpoints/sft/haiku_qwen3_smoke_${SLURM_JOB_ID}}

if [[ ! -x "${PYTHON_BIN}" ]]; then
    echo "Python environment not found: ${PYTHON_BIN}" >&2
    exit 2
fi
if [[ ! -f "${DATASET_DIR}/train.parquet" || ! -f "${DATASET_DIR}/validation.parquet" ]]; then
    echo "Missing train.parquet or validation.parquet in ${DATASET_DIR}" >&2
    exit 2
fi
if (( SMOKE_STEPS <= 0 )); then
    echo "SMOKE_STEPS must be positive" >&2
    exit 2
fi

cd "${PROJECT_DIR}"
mkdir -p logs "${OUTPUT_DIR}"

export PATH="${ENV_PATH}/bin:${PATH}"
export CONDA_PREFIX="${ENV_PATH}"
export HF_HOME=${HF_HOME:-/zfsauton/scratch/frankwu2/.cache/huggingface}
export TMPDIR=${TMPDIR:-/zfsauton/scratch/frankwu2/tmp}
export PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NCCL_DEBUG=${NCCL_DEBUG:-WARN}
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
unset ROCR_VISIBLE_DEVICES
mkdir -p "${HF_HOME}" "${TMPDIR}"

echo "=== SFT smoke-run configuration ==="
echo "job_id=${SLURM_JOB_ID}"
echo "node=${SLURMD_NODENAME}"
echo "start_time=$(date --iso-8601=seconds)"
echo "cuda_visible_devices=${CUDA_VISIBLE_DEVICES:-unset}"
echo "model=${MODEL_PATH}"
echo "dataset=${DATASET_DIR}"
echo "output=${OUTPUT_DIR}"
echo "optimizer_steps=${SMOKE_STEPS}"
echo "global_batch_size=${GLOBAL_BATCH_SIZE}"
echo "micro_batch_size_per_gpu=${MICRO_BATCH_SIZE}"
echo "max_length=${MAX_LENGTH}"
echo "learning_rate=${LEARNING_RATE}"
echo "==================================="

nvidia-smi -L
nvidia-smi topo -m || true

# Four A6000s split across both CPU sockets make FSDP collectives several times
# slower on this cluster and would invalidate the timing estimate. Abort early
# unless the split is explicitly accepted.
# Slurm's device cgroup exposes only the allocated GPUs to nvidia-smi. Query
# every visible device here: SLURM_JOB_GPUS contains node-global indices, which
# can refer to nonexistent indices inside the remapped job namespace.
GPU_NUMA_NODES=$( { nvidia-smi --query-gpu=pci.bus_id --format=csv,noheader | while read -r bus; do
        device="0000:$(echo "${bus}" | cut -d: -f2- | tr '[:upper:]' '[:lower:]')"
        cat "/sys/bus/pci/devices/${device}/numa_node" 2>/dev/null || echo "?"
    done | sort -u; } || true )
echo "gpu_numa_nodes=$(echo "${GPU_NUMA_NODES}" | tr '\n' ' ')"
if [[ $(echo "${GPU_NUMA_NODES}" | grep -cE '^[0-9]+$') -gt 1 && ${ALLOW_SPLIT_GPUS:-0} != 1 ]]; then
    echo "Allocated GPUs span multiple NUMA domains; resubmit for a useful timing measurement." >&2
    echo "Set ALLOW_SPLIT_GPUS=1 only if a slower, nonrepresentative smoke run is acceptable." >&2
    exit 1
fi

export NPROC_PER_NODE=${NUM_GPUS}
export SFT_EPOCHS=1
export SFT_LR=${LEARNING_RATE}
export SFT_GLOBAL_BATCH_SIZE=${GLOBAL_BATCH_SIZE}
export SFT_MICRO_BATCH_SIZE=${MICRO_BATCH_SIZE}
export SFT_MAX_LENGTH=${MAX_LENGTH}
export SFT_PROJECT_NAME=hiring-haiku-sft
export SFT_EXPERIMENT_NAME=qwen3-4b-haiku-raw-smoke-${SLURM_JOB_ID}
export SFT_RESUME_MODE=disable

START_SECONDS=${SECONDS}
scripts/sft/train_sft.sh \
    "${MODEL_PATH}" \
    "${DATASET_DIR}" \
    "${OUTPUT_DIR}" \
    trainer.total_training_steps="${SMOKE_STEPS}"
ELAPSED_SECONDS=$((SECONDS - START_SECONDS))

echo "=== SFT smoke run complete ==="
echo "end_time=$(date --iso-8601=seconds)"
echo "wall_time_seconds=${ELAPSED_SECONDS}"
echo "checkpoint_dir=${OUTPUT_DIR}"
find "${OUTPUT_DIR}" -maxdepth 1 -type d -name 'global_step_*' -print | sort
