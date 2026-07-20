#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
    echo "Usage: $0 MODEL_PATH DATASET_DIR OUTPUT_DIR [additional Hydra overrides ...]" >&2
    exit 2
fi

MODEL_PATH=$1
DATASET_DIR=$2
OUTPUT_DIR=$3
shift 3

TRAIN_FILE="${DATASET_DIR}/train.parquet"
VALIDATION_FILE="${DATASET_DIR}/validation.parquet"

if [[ ! -f "${TRAIN_FILE}" ]]; then
    echo "Missing training dataset: ${TRAIN_FILE}" >&2
    exit 2
fi
if [[ ! -f "${VALIDATION_FILE}" ]]; then
    echo "Missing validation dataset: ${VALIDATION_FILE}" >&2
    exit 2
fi

NPROC_PER_NODE=${NPROC_PER_NODE:-4}
SFT_EPOCHS=${SFT_EPOCHS:-1}
SFT_LR=${SFT_LR:-5e-6}
SFT_GLOBAL_BATCH_SIZE=${SFT_GLOBAL_BATCH_SIZE:-32}
SFT_MICRO_BATCH_SIZE=${SFT_MICRO_BATCH_SIZE:-1}
SFT_MAX_LENGTH=${SFT_MAX_LENGTH:-4608}
SFT_PROJECT_NAME=${SFT_PROJECT_NAME:-hiring-haiku-sft}
SFT_EXPERIMENT_NAME=${SFT_EXPERIMENT_NAME:-qwen-haiku-sft}
SFT_RESUME_MODE=${SFT_RESUME_MODE:-disable}

torchrun --standalone --nnodes=1 --nproc-per-node="${NPROC_PER_NODE}" \
    -m verl.trainer.fsdp_sft_trainer \
    data.train_files="${TRAIN_FILE}" \
    data.val_files="${VALIDATION_FILE}" \
    data.max_length="${SFT_MAX_LENGTH}" \
    data.truncation=error \
    data.train_batch_size="${SFT_GLOBAL_BATCH_SIZE}" \
    data.micro_batch_size_per_gpu="${SFT_MICRO_BATCH_SIZE}" \
    data.balance_dp_token=true \
    data.multiturn.enable=true \
    data.multiturn.messages_key=messages \
    data.multiturn.enable_thinking_key=enable_thinking \
    model.partial_pretrain="${MODEL_PATH}" \
    model.strategy=fsdp2 \
    model.fsdp_config.model_dtype=bf16 \
    model.enable_gradient_checkpointing=true \
    optim.lr="${SFT_LR}" \
    optim.warmup_steps_ratio=0.03 \
    trainer.project_name="${SFT_PROJECT_NAME}" \
    trainer.experiment_name="${SFT_EXPERIMENT_NAME}" \
    trainer.default_local_dir="${OUTPUT_DIR}" \
    trainer.logger='["console"]' \
    trainer.total_epochs="${SFT_EPOCHS}" \
    trainer.n_gpus_per_node="${NPROC_PER_NODE}" \
    trainer.resume_mode="${SFT_RESUME_MODE}" \
    trainer.save_freq=-1 \
    trainer.test_freq=-1 \
    ulysses_sequence_parallel_size=1 \
    use_remove_padding=true \
    "$@"
