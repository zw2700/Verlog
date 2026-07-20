#!/usr/bin/env bash
#SBATCH --job-name=haiku_sft_collect
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/haiku_sft_collect_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/haiku_sft_collect_%j.err
#SBATCH --partition=cpu
#SBATCH --qos=qos_cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=12:00:00

set -euo pipefail

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
ENV_PATH=/zfsauton/scratch/cpulling/conda_envs/verlog
PYTHON_BIN="${ENV_PATH}/bin/python3"

SFT_ENV_FILE=${SFT_ENV_FILE:-${PROJECT_DIR}/rollout_frontier.env}
TARGET_TOKENIZER=${TARGET_TOKENIZER:-Qwen/Qwen3-4B}
OUTPUT_JSONL=${OUTPUT_JSONL:-${PROJECT_DIR}/outputs/sft/haiku_qwen3_pilot/attempts.jsonl}
SEED_BASE=${SEED_BASE:-10000}
NUM_SCENARIOS=${NUM_SCENARIOS:-500}
MAX_ATTEMPTS_PER_SCENARIO=${MAX_ATTEMPTS_PER_SCENARIO:-4}
NUM_WORKERS=${NUM_WORKERS:-8}

if [[ ! -x "${PYTHON_BIN}" ]]; then
    echo "Python environment not found: ${PYTHON_BIN}" >&2
    exit 2
fi
if [[ ! -f "${SFT_ENV_FILE}" ]]; then
    echo "Environment file not found: ${SFT_ENV_FILE}" >&2
    exit 2
fi

cd "${PROJECT_DIR}"
mkdir -p logs "$(dirname "${OUTPUT_JSONL}")"

export PATH="${ENV_PATH}/bin:${PATH}"
export CONDA_PREFIX="${ENV_PATH}"
export HF_HOME=${HF_HOME:-/zfsauton/scratch/frankwu2/.cache/huggingface}
export TMPDIR=${TMPDIR:-/zfsauton/scratch/frankwu2/tmp}
export PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false
mkdir -p "${HF_HOME}" "${TMPDIR}"

echo "Starting Haiku teacher collection"
echo "  job_id=${SLURM_JOB_ID:-local}"
echo "  env_file=${SFT_ENV_FILE}"
echo "  target_tokenizer=${TARGET_TOKENIZER}"
echo "  scenarios=${NUM_SCENARIOS} seeds=[${SEED_BASE}, $((SEED_BASE + NUM_SCENARIOS - 1))]"
echo "  max_attempts_per_scenario=${MAX_ATTEMPTS_PER_SCENARIO}"
echo "  num_workers=${NUM_WORKERS}"
echo "  output=${OUTPUT_JSONL}"

"${PYTHON_BIN}" -m scripts.sft.collect_teacher_rollouts \
    --env-file "${SFT_ENV_FILE}" \
    --target-tokenizer "${TARGET_TOKENIZER}" \
    --no-target-enable-thinking \
    --seed-base "${SEED_BASE}" \
    --num-scenarios "${NUM_SCENARIOS}" \
    --max-attempts-per-scenario "${MAX_ATTEMPTS_PER_SCENARIO}" \
    --num-workers "${NUM_WORKERS}" \
    --output-jsonl "${OUTPUT_JSONL}" \
    "$@"

echo "Collection complete"
echo "  episodes=${OUTPUT_JSONL}"
echo "  summary=${OUTPUT_JSONL%.jsonl}.summary.json"
