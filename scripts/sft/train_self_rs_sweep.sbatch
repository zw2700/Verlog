#!/usr/bin/env bash
#SBATCH --job-name=qwen3_self_rs_sft
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_self_rs_sft_%A_%a.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_self_rs_sft_%A_%a.err
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
DATASET_ROOT=${DATASET_ROOT:-${PROJECT_DIR}/outputs/sft/qwen3_self_rs_v1/sweep_datasets_v1}
CHECKPOINT_ROOT=${CHECKPOINT_ROOT:-/zfsauton/scratch/frankwu2/unscripted/Verlog/checkpoints/sft}
SWEEP_TAG=${SWEEP_TAG:-qwen3_self_rs_sweep_v1}
MODEL_PATH=${MODEL_PATH:-Qwen/Qwen3-4B}
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
        TRAINING_STEPS=7
        SAVE_FREQ=-1
        ;;
    1)
        ARM_NAME=raw50
        DATASET_NAME=raw50
        TRAINING_STEPS=16
        SAVE_FREQ=-1
        ;;
    2)
        ARM_NAME=raw100_steps8_32
        DATASET_NAME=raw100
        TRAINING_STEPS=32
        # The step-8 and step-16 checkpoints share the same 32-step cosine
        # schedule and training trajectory as the final checkpoint.
        SAVE_FREQ=8
        ;;
    3)
        ARM_NAME=compact100
        DATASET_NAME=compact100
        TRAINING_STEPS=32
        SAVE_FREQ=-1
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
export HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-1}
export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export TMPDIR=${TMPDIR:-/zfsauton/scratch/frankwu2/tmp}
export PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NCCL_DEBUG=${NCCL_DEBUG:-WARN}
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
unset ROCR_VISIBLE_DEVICES
mkdir -p "${HF_HOME}" "${TMPDIR}"

echo "=== Qwen self-RS SFT sweep arm ==="
echo "job_id=${SLURM_JOB_ID} array_task=${ARM_INDEX} restart_count=${SLURM_RESTART_COUNT:-0}"
echo "node=${SLURMD_NODENAME} start_time=$(date --iso-8601=seconds)"
echo "arm=${ARM_NAME} dataset=${DATASET_DIR}"
echo "model=${MODEL_PATH} output=${OUTPUT_DIR}"
echo "fixed_training_steps=${TRAINING_STEPS} save_freq=${SAVE_FREQ}"
echo "lr=${LEARNING_RATE} global_batch=${GLOBAL_BATCH_SIZE} micro_batch=${MICRO_BATCH_SIZE}"
echo "==================================="

if [[ $(nvidia-smi -L | wc -l) -ne ${NUM_GPUS} ]]; then
    echo "Expected ${NUM_GPUS} visible GPUs" >&2
    nvidia-smi -L || true
    exit 1
fi
nvidia-smi -L
nvidia-smi topo -m || true

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
export TRAINING_STEPS GLOBAL_BATCH_SIZE
"${PYTHON_BIN}" - <<'PY'
import json
import os

with open(os.environ["DATASET_REPORT"], encoding="utf-8") as handle:
    report = json.load(handle)
rows = int(report["train_decision_rows"])
batch = int(os.environ["GLOBAL_BATCH_SIZE"])
available_steps = rows // batch
requested_steps = int(os.environ["TRAINING_STEPS"])
if available_steps < 1:
    raise SystemExit(
        f"Dataset has {rows} training rows, fewer than one global batch of {batch}"
    )
required_epochs = (requested_steps + available_steps - 1) // available_steps
if required_epochs > 2:
    raise SystemExit(
        f"Dataset provides only {available_steps} full batches per epoch and would require "
        f"{required_epochs} epochs to reach {requested_steps} fixed steps"
    )
print(
    f"dataset report verified: {report['arm']} has {report['train_scenarios']} scenarios, "
    f"{rows} rows, {available_steps} full batches/epoch; training for {requested_steps} steps "
    f"within at most {required_epochs} epoch(s)"
)
PY

export NPROC_PER_NODE=${NUM_GPUS}
# Two epochs is only an upper bound for the trainer loop. Explicit fixed-step
# early stopping normally returns during epoch one; epoch two is available if
# unusually short selected trajectories yield too few full batches.
export SFT_EPOCHS=2
export SFT_LR=${LEARNING_RATE}
export SFT_GLOBAL_BATCH_SIZE=${GLOBAL_BATCH_SIZE}
export SFT_MICRO_BATCH_SIZE=${MICRO_BATCH_SIZE}
export SFT_MAX_LENGTH=${MAX_LENGTH}
export SFT_PROJECT_NAME=hiring-qwen-self-rs-sft
export SFT_EXPERIMENT_NAME=${SWEEP_TAG}-${ARM_NAME}
export SFT_RESUME_MODE=disable

START_SECONDS=${SECONDS}
scripts/sft/train_sft.sh \
    "${MODEL_PATH}" \
    "${DATASET_DIR}" \
    "${OUTPUT_DIR}" \
    'trainer.checkpoint.save_contents=["model"]' \
    'trainer.checkpoint.load_contents=["model"]' \
    "trainer.total_training_steps=${TRAINING_STEPS}" \
    "trainer.save_freq=${SAVE_FREQ}"
ELAPSED_SECONDS=$((SECONDS - START_SECONDS))

FINAL_CHECKPOINT=${OUTPUT_DIR}/global_step_${TRAINING_STEPS}
if [[ ! -d ${FINAL_CHECKPOINT} ]]; then
    echo "Training returned without expected checkpoint: ${FINAL_CHECKPOINT}" >&2
    exit 1
fi
if find "${FINAL_CHECKPOINT}" -maxdepth 1 -name 'optim_world_size_*' -print -quit | grep -q .; then
    echo "Model-only checkpoint unexpectedly contains optimizer shards" >&2
    exit 1
fi
if [[ ${ARM_NAME} == raw100_steps8_32 ]]; then
    for step in 8 16 32; do
        if [[ ! -d ${OUTPUT_DIR}/global_step_${step} ]]; then
            echo "Missing required raw100 checkpoint at step ${step}" >&2
            exit 1
        fi
    done
fi

echo "training_complete=$(date --iso-8601=seconds) wall_time_seconds=${ELAPSED_SECONDS}"
echo "final_checkpoint=${FINAL_CHECKPOINT}"
if [[ ${ARM_NAME} == raw100_steps8_32 ]]; then
    echo "evaluation_checkpoints=${OUTPUT_DIR}/global_step_8,${OUTPUT_DIR}/global_step_16,${OUTPUT_DIR}/global_step_32"
fi
du -sh "${OUTPUT_DIR}"
