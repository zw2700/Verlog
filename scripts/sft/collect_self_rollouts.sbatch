#!/usr/bin/env bash
#SBATCH --job-name=qwen3_self_rs_collect
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_self_rs_collect_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_self_rs_collect_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=24:00:00
#SBATCH --gres=gpu:a6000:1

set -euo pipefail

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
ENV_PATH=/zfsauton/scratch/cpulling/conda_envs/verlog
PYTHON_BIN=${ENV_PATH}/bin/python3
VLLM_BIN=${ENV_PATH}/bin/vllm

MODEL_PATH=${MODEL_PATH:-Qwen/Qwen3-4B}
TARGET_TOKENIZER=${TARGET_TOKENIZER:-Qwen/Qwen3-4B}
RUN_TAG=${RUN_TAG:-qwen3_self_rs_v1}
OUTPUT_ROOT=${OUTPUT_ROOT:-${PROJECT_DIR}/outputs/sft}
OUTPUT_DIR=${OUTPUT_ROOT}/${RUN_TAG}
OUTPUT_JSONL=${OUTPUT_JSONL:-${OUTPUT_DIR}/attempts.jsonl}
SUMMARY_JSON=${SUMMARY_JSON:-${OUTPUT_DIR}/attempts.summary.json}
SEED_BASE=${SEED_BASE:-10000}
NUM_SCENARIOS=${NUM_SCENARIOS:-500}
MAX_ATTEMPTS_PER_SCENARIO=${MAX_ATTEMPTS_PER_SCENARIO:-4}
NUM_WORKERS=${NUM_WORKERS:-8}
TEMPERATURE=${TEMPERATURE:-1.0}
TOP_P=${TOP_P:-1.0}
TOP_K=${TOP_K:--1}
MAX_OUTPUT_TOKENS=${MAX_OUTPUT_TOKENS:-512}

VLLM_HOST=127.0.0.1
VLLM_PORT=${VLLM_PORT:-$((20000 + SLURM_JOB_ID % 20000))}
VLLM_GPU_MEMORY_UTILIZATION=${VLLM_GPU_MEMORY_UTILIZATION:-0.85}
VLLM_MAX_MODEL_LEN=${VLLM_MAX_MODEL_LEN:-8192}
VLLM_READY_TIMEOUT=${VLLM_READY_TIMEOUT:-900}
BASE_URL=http://${VLLM_HOST}:${VLLM_PORT}/v1
VLLM_LOG=${PROJECT_DIR}/logs/vllm_qwen3_self_rs_collect_${SLURM_JOB_ID}.log

if [[ ! -x ${PYTHON_BIN} || ! -x ${VLLM_BIN} ]]; then
    echo "Missing Python or vLLM in ${ENV_PATH}" >&2
    exit 2
fi
if (( NUM_SCENARIOS <= 0 || MAX_ATTEMPTS_PER_SCENARIO <= 0 || NUM_WORKERS <= 0 )); then
    echo "Scenario, attempt, and worker counts must be positive" >&2
    exit 2
fi
if [[ -d ${MODEL_PATH} ]]; then
    MODEL_PATH=$(realpath "${MODEL_PATH}")
elif [[ ${MODEL_PATH} == /* ]]; then
    echo "Local model path does not exist: ${MODEL_PATH}" >&2
    exit 2
fi

cd "${PROJECT_DIR}"
mkdir -p logs "${OUTPUT_DIR}"
export PATH=${ENV_PATH}/bin:${PATH}
export CONDA_PREFIX=${ENV_PATH}
export HF_HOME=${HF_HOME:-/zfsauton/scratch/frankwu2/.cache/huggingface}
export HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-1}
export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export TMPDIR=${TMPDIR:-/zfsauton/scratch/frankwu2/tmp}
export PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false
export VLLM_USE_V1=${VLLM_USE_V1:-1}
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export LOCAL_VLLM_API_KEY=dummy
export LOCAL_VLLM_BASE_URL=${BASE_URL}
export LOCAL_VLLM_DISABLE_THINKING=1
unset ROCR_VISIBLE_DEVICES
mkdir -p "${HF_HOME}" "${TMPDIR}"

echo "=== Qwen3 rejection-sampling collection ==="
echo "job_id=${SLURM_JOB_ID} node=${SLURMD_NODENAME}"
echo "start_time=$(date --iso-8601=seconds)"
echo "model=${MODEL_PATH} target_tokenizer=${TARGET_TOKENIZER}"
echo "scenarios=${NUM_SCENARIOS} seeds=${SEED_BASE}..$((SEED_BASE + NUM_SCENARIOS - 1))"
echo "max_attempts=${MAX_ATTEMPTS_PER_SCENARIO} workers=${NUM_WORKERS}"
echo "temperature=${TEMPERATURE} top_p=${TOP_P} top_k=${TOP_K} max_output_tokens=${MAX_OUTPUT_TOKENS}"
echo "output=${OUTPUT_JSONL}"
echo "==========================================="
nvidia-smi -L

VLLM_ARGS=(
    serve "${MODEL_PATH}"
    --host "${VLLM_HOST}"
    --port "${VLLM_PORT}"
    --tensor-parallel-size 1
    --gpu-memory-utilization "${VLLM_GPU_MEMORY_UTILIZATION}"
    --max-model-len "${VLLM_MAX_MODEL_LEN}"
    --dtype auto
    --generation-config vllm
    --disable-log-requests
)
echo "Starting vLLM; server log: ${VLLM_LOG}"
"${VLLM_BIN}" "${VLLM_ARGS[@]}" >"${VLLM_LOG}" 2>&1 &
VLLM_PID=$!

cleanup() {
    if kill -0 "${VLLM_PID}" >/dev/null 2>&1; then
        kill "${VLLM_PID}" >/dev/null 2>&1 || true
        wait "${VLLM_PID}" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

export VLLM_PID VLLM_LOG BASE_URL VLLM_READY_TIMEOUT
"${PYTHON_BIN}" - <<'PY'
import json
import os
import subprocess
import time
import urllib.request

base_url = os.environ["BASE_URL"].rstrip("/")
pid = int(os.environ["VLLM_PID"])
deadline = time.time() + int(os.environ["VLLM_READY_TIMEOUT"])
last_error = None
while time.time() < deadline:
    try:
        with urllib.request.urlopen(f"{base_url}/models", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        print("vLLM ready; served models:", [row.get("id") for row in payload.get("data", [])], flush=True)
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as exc:
        last_error = exc
    try:
        os.kill(pid, 0)
    except OSError:
        subprocess.run(["tail", "-n", "100", os.environ["VLLM_LOG"]], check=False)
        raise SystemExit(f"vLLM exited before readiness: {last_error}")
    time.sleep(5)
subprocess.run(["tail", "-n", "100", os.environ["VLLM_LOG"]], check=False)
raise SystemExit(f"vLLM readiness timeout: {last_error}")
PY

RESUME_ARG=()
if [[ -s ${OUTPUT_JSONL} ]]; then
    RESUME_ARG=(--resume)
fi

"${PYTHON_BIN}" -m scripts.sft.collect_teacher_rollouts \
    --provider local-vllm \
    --model "${MODEL_PATH}" \
    --base-url "${BASE_URL}" \
    --target-tokenizer "${TARGET_TOKENIZER}" \
    --no-target-enable-thinking \
    --temperature "${TEMPERATURE}" \
    --top-p "${TOP_P}" \
    --top-k "${TOP_K}" \
    --max-output-tokens "${MAX_OUTPUT_TOKENS}" \
    --seed-base "${SEED_BASE}" \
    --num-scenarios "${NUM_SCENARIOS}" \
    --max-attempts-per-scenario "${MAX_ATTEMPTS_PER_SCENARIO}" \
    --num-workers "${NUM_WORKERS}" \
    --stop-on-socially-optimal \
    --output-jsonl "${OUTPUT_JSONL}" \
    --summary-json "${SUMMARY_JSON}" \
    "${RESUME_ARG[@]}"

echo "collection_complete=$(date --iso-8601=seconds)"
echo "episodes=${OUTPUT_JSONL}"
echo "summary=${SUMMARY_JSON}"
