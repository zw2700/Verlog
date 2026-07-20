#!/usr/bin/env bash
#SBATCH --job-name=qwen3_sft_sweep
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_sweep_%A_%a.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_sweep_%A_%a.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=200G
#SBATCH --time=08:00:00
#SBATCH --gres=gpu:a6000:4
#SBATCH --gres-flags=enforce-binding
#SBATCH --array=0-3%1
#SBATCH --requeue

set -euo pipefail

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
ENV_PATH=/zfsauton/scratch/cpulling/conda_envs/verlog
PYTHON_BIN=${ENV_PATH}/bin/python3
DATASET_ROOT=${DATASET_ROOT:-${PROJECT_DIR}/outputs/sft/haiku_qwen3_pilot/sweep_datasets_v1}
CHECKPOINT_ROOT=${CHECKPOINT_ROOT:-/zfsauton/scratch/frankwu2/unscripted/Verlog/checkpoints/sft}
SWEEP_TAG=${SWEEP_TAG:-haiku_qwen3_sweep_v1}
MODEL_PATH=${MODEL_PATH:-Qwen/Qwen3-4B}
SMOKE_CHECKPOINT=${SMOKE_CHECKPOINT:-/zfsauton/scratch/frankwu2/unscripted/Verlog/checkpoints/sft/haiku_qwen3_smoke_18999/global_step_8}
NUM_GPUS=4
GLOBAL_BATCH_SIZE=${GLOBAL_BATCH_SIZE:-32}
MICRO_BATCH_SIZE=${MICRO_BATCH_SIZE:-1}
MAX_LENGTH=${MAX_LENGTH:-4608}
LEARNING_RATE=${LEARNING_RATE:-5e-6}
ARM_INDEX=${SLURM_ARRAY_TASK_ID:-}

case ${ARM_INDEX} in
    0)
        ARM_NAME=raw25
        DATASET_NAME=raw25
        EXPECTED_STEPS=7
        RESUME_FROM=
        ;;
    1)
        ARM_NAME=raw50
        DATASET_NAME=raw50
        EXPECTED_STEPS=16
        RESUME_FROM=
        ;;
    2)
        ARM_NAME=raw100_steps16_32
        DATASET_NAME=raw100
        EXPECTED_STEPS=32
        RESUME_FROM=${SMOKE_CHECKPOINT}
        ;;
    3)
        ARM_NAME=compact100
        DATASET_NAME=compact100
        EXPECTED_STEPS=32
        RESUME_FROM=
        ;;
    *)
        echo "SLURM_ARRAY_TASK_ID must be 0, 1, 2, or 3" >&2
        exit 2
        ;;
esac

DATASET_DIR=${DATASET_ROOT}/${DATASET_NAME}
OUTPUT_DIR=${CHECKPOINT_ROOT}/${SWEEP_TAG}/${ARM_NAME}

if [[ ! -x ${PYTHON_BIN} ]]; then
    echo "Python environment not found: ${PYTHON_BIN}" >&2
    exit 2
fi
for required in train.parquet validation.parquet dataset_report.json; do
    if [[ ! -f ${DATASET_DIR}/${required} ]]; then
        echo "Missing dataset artifact: ${DATASET_DIR}/${required}" >&2
        exit 2
    fi
done

cd "${PROJECT_DIR}"
mkdir -p logs

export PATH=${ENV_PATH}/bin:${PATH}
export CONDA_PREFIX=${ENV_PATH}
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

echo "=== SFT sweep arm ==="
echo "job_id=${SLURM_JOB_ID} array_task=${ARM_INDEX} restart_count=${SLURM_RESTART_COUNT:-0}"
echo "node=${SLURMD_NODENAME} start_time=$(date --iso-8601=seconds)"
echo "arm=${ARM_NAME} dataset=${DATASET_DIR}"
echo "model=${MODEL_PATH} output=${OUTPUT_DIR}"
echo "expected_final_step=${EXPECTED_STEPS} resume_from=${RESUME_FROM:-none}"
echo "lr=${LEARNING_RATE} global_batch=${GLOBAL_BATCH_SIZE} micro_batch=${MICRO_BATCH_SIZE}"
echo "====================="

if [[ $(nvidia-smi -L | wc -l) -ne ${NUM_GPUS} ]]; then
    echo "Expected ${NUM_GPUS} visible GPUs" >&2
    nvidia-smi -L || true
    exit 1
fi
nvidia-smi -L
nvidia-smi topo -m || true

# FSDP collectives are unacceptably slow when the four GPUs cross CPU sockets.
# Query all devices visible inside Slurm's remapped namespace. Do not use
# SLURM_JOB_GPUS as an nvidia-smi selector: those are node-global indices.
GPU_NUMA_NODES=$( { nvidia-smi --query-gpu=pci.bus_id --format=csv,noheader | while read -r bus; do
        device="0000:$(echo "${bus}" | cut -d: -f2- | tr '[:upper:]' '[:lower:]')"
        cat "/sys/bus/pci/devices/${device}/numa_node" 2>/dev/null || echo "?"
    done | sort -u; } || true )
echo "gpu_numa_nodes=$(echo "${GPU_NUMA_NODES}" | tr '\n' ' ')"
if [[ $(echo "${GPU_NUMA_NODES}" | grep -cE '^[0-9]+$') -gt 1 && ${ALLOW_SPLIT_GPUS:-0} != 1 ]]; then
    echo "Allocated GPUs span multiple NUMA domains; rejecting this placement." >&2
    restarts=${SLURM_RESTART_COUNT:-0}
    if (( restarts < ${MAX_SPLIT_GPU_REQUEUES:-5} )); then
        previous_excludes=$(scontrol show job "${SLURM_JOB_ID}" | grep -oE 'ExcNodeList=[^ ]+' | cut -d= -f2 || true)
        new_excludes=${SLURMD_NODENAME}
        if [[ -n ${previous_excludes} && ${previous_excludes} != "(null)" ]]; then
            new_excludes=${previous_excludes},${SLURMD_NODENAME}
        fi
        echo "Requeueing and excluding: ${new_excludes}"
        if scontrol requeue "${SLURM_JOB_ID}"; then
            scontrol update JobId="${SLURM_JOB_ID}" ExcNodeList="${new_excludes}" || true
            exit 0
        fi
    fi
    echo "Topology rerolls exhausted. Resubmit with an exclusion or set ALLOW_SPLIT_GPUS=1." >&2
    exit 1
fi

if [[ -e ${OUTPUT_DIR} ]] && find "${OUTPUT_DIR}" -mindepth 1 -print -quit | grep -q .; then
    echo "Refusing to write into nonempty output directory: ${OUTPUT_DIR}" >&2
    echo "Set a new SWEEP_TAG; existing checkpoints are never overwritten by this launcher." >&2
    exit 2
fi
mkdir -p "${OUTPUT_DIR}"

export DATASET_REPORT=${DATASET_DIR}/dataset_report.json
export EXPECTED_STEPS
"${PYTHON_BIN}" - <<'PY'
import json
import os

with open(os.environ["DATASET_REPORT"], encoding="utf-8") as handle:
    report = json.load(handle)
observed = report["expected_optimizer_steps_per_epoch_global_batch_32"]
expected = int(os.environ["EXPECTED_STEPS"])
if observed != expected:
    raise SystemExit(f"Dataset reports {observed} steps, launcher expects {expected}")
print(f"dataset report verified: {report['arm']} has {report['train_scenarios']} scenarios, "
      f"{report['train_decision_rows']} rows, {observed} steps")
PY

HYDRA_OVERRIDES=(
    'trainer.checkpoint.save_contents=["model"]'
    'trainer.checkpoint.load_contents=["model"]'
)
if [[ -n ${RESUME_FROM} ]]; then
    for rank in 0 1 2 3; do
        for prefix in model optim extra_state; do
            if [[ ! -f ${RESUME_FROM}/${prefix}_world_size_4_rank_${rank}.pt ]]; then
                echo "Incomplete resumable checkpoint: missing ${prefix} rank ${rank} in ${RESUME_FROM}" >&2
                exit 2
            fi
        done
    done
    if [[ ! -f ${RESUME_FROM}/data.pt ]]; then
        echo "Resumable checkpoint lacks data.pt: ${RESUME_FROM}" >&2
        exit 2
    fi
    export SFT_RESUME_MODE=resume_path
    HYDRA_OVERRIDES+=(
        "trainer.resume_from_path=${RESUME_FROM}"
        'trainer.checkpoint.load_contents=["model","optimizer","extra"]'
        'trainer.save_freq=16'
    )
else
    export SFT_RESUME_MODE=disable
fi

export NPROC_PER_NODE=${NUM_GPUS}
export SFT_EPOCHS=1
export SFT_LR=${LEARNING_RATE}
export SFT_GLOBAL_BATCH_SIZE=${GLOBAL_BATCH_SIZE}
export SFT_MICRO_BATCH_SIZE=${MICRO_BATCH_SIZE}
export SFT_MAX_LENGTH=${MAX_LENGTH}
export SFT_PROJECT_NAME=hiring-haiku-sft
export SFT_EXPERIMENT_NAME=${SWEEP_TAG}-${ARM_NAME}

START_SECONDS=${SECONDS}
scripts/sft/train_sft.sh \
    "${MODEL_PATH}" \
    "${DATASET_DIR}" \
    "${OUTPUT_DIR}" \
    "${HYDRA_OVERRIDES[@]}"
ELAPSED_SECONDS=$((SECONDS - START_SECONDS))

FINAL_CHECKPOINT=${OUTPUT_DIR}/global_step_${EXPECTED_STEPS}
if [[ ! -d ${FINAL_CHECKPOINT} ]]; then
    echo "Training returned without expected checkpoint: ${FINAL_CHECKPOINT}" >&2
    exit 1
fi
if find "${FINAL_CHECKPOINT}" -maxdepth 1 -name 'optim_world_size_*' -print -quit | grep -q .; then
    echo "Model-only checkpoint unexpectedly contains optimizer shards" >&2
    exit 1
fi

echo "=== SFT arm complete ==="
echo "end_time=$(date --iso-8601=seconds) wall_time_seconds=${ELAPSED_SECONDS}"
echo "final_checkpoint=${FINAL_CHECKPOINT}"
if [[ ${ARM_NAME} == raw100_steps16_32 ]]; then
    echo "mid_checkpoint=${OUTPUT_DIR}/global_step_16"
fi
du -sh "${OUTPUT_DIR}"
