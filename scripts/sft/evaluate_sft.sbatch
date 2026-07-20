#!/usr/bin/env bash
#SBATCH --job-name=qwen3_sft_eval
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_eval_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/qwen3_sft_eval_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --gres=gpu:a6000:1

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: sbatch $0 MODEL_PATH EVAL_NAME" >&2
    echo "Example: EVAL_NUM_SCENARIOS=20 sbatch $0 Qwen/Qwen3-4B base" >&2
    exit 2
fi

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
ENV_PATH=/zfsauton/scratch/cpulling/conda_envs/verlog
PYTHON_BIN=${ENV_PATH}/bin/python3
VLLM_BIN=${ENV_PATH}/bin/vllm
SWEEP_TAG=${SWEEP_TAG:-haiku_qwen3_sweep_v1}
EVALUATION_ROOT=${EVALUATION_ROOT:-${PROJECT_DIR}/outputs/sft/evaluations}
MODEL_PATH=$1
EVAL_NAME=$2
TARGET_TOKENIZER=${TARGET_TOKENIZER:-Qwen/Qwen3-4B}
EVAL_NUM_SCENARIOS=${EVAL_NUM_SCENARIOS:-20}
NUM_WORKERS=${NUM_WORKERS:-8}
TEMPERATURE=${TEMPERATURE:-1.0}
MAX_OUTPUT_TOKENS=${MAX_OUTPUT_TOKENS:-512}
VLLM_HOST=127.0.0.1
VLLM_PORT=${VLLM_PORT:-$((20000 + SLURM_JOB_ID % 20000))}
VLLM_GPU_MEMORY_UTILIZATION=${VLLM_GPU_MEMORY_UTILIZATION:-0.85}
VLLM_MAX_MODEL_LEN=${VLLM_MAX_MODEL_LEN:-8192}
VLLM_READY_TIMEOUT=${VLLM_READY_TIMEOUT:-900}

if [[ ! ${EVAL_NAME} =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "EVAL_NAME may contain only letters, digits, dot, underscore, and dash" >&2
    exit 2
fi
if (( EVAL_NUM_SCENARIOS <= 0 || EVAL_NUM_SCENARIOS > 500 )); then
    echo "EVAL_NUM_SCENARIOS must be between 1 and 500" >&2
    exit 2
fi
if [[ -d ${MODEL_PATH} ]]; then
    MODEL_PATH=$(realpath "${MODEL_PATH}")
elif [[ ${MODEL_PATH} == /* ]]; then
    echo "Local model path does not exist: ${MODEL_PATH}" >&2
    exit 2
fi

OUTPUT_DIR=${EVALUATION_ROOT}/${SWEEP_TAG}/${EVAL_NAME}
OUTPUT_JSONL=${OUTPUT_DIR}/episodes.jsonl
SUMMARY_JSON=${OUTPUT_DIR}/summary.json
BASE_URL=http://${VLLM_HOST}:${VLLM_PORT}/v1
VLLM_LOG=${PROJECT_DIR}/logs/vllm_sft_eval_${SLURM_JOB_ID}.log

cd "${PROJECT_DIR}"
mkdir -p logs "${OUTPUT_DIR}"
export PATH=${ENV_PATH}/bin:${PATH}
export CONDA_PREFIX=${ENV_PATH}
export HF_HOME=${HF_HOME:-/zfsauton/scratch/frankwu2/.cache/huggingface}
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

echo "=== SFT rollout evaluation ==="
echo "job_id=${SLURM_JOB_ID} node=${SLURMD_NODENAME}"
echo "start_time=$(date --iso-8601=seconds)"
echo "model=${MODEL_PATH} eval_name=${EVAL_NAME}"
echo "scenarios=${EVAL_NUM_SCENARIOS} seeds=0..$((EVAL_NUM_SCENARIOS - 1))"
echo "temperature=${TEMPERATURE} target_tokenizer=${TARGET_TOKENIZER}"
echo "output=${OUTPUT_JSONL}"
echo "=============================="
nvidia-smi -L

VLLM_ARGS=(
    serve "${MODEL_PATH}"
    --host "${VLLM_HOST}"
    --port "${VLLM_PORT}"
    --tensor-parallel-size 1
    --gpu-memory-utilization "${VLLM_GPU_MEMORY_UTILIZATION}"
    --max-model-len "${VLLM_MAX_MODEL_LEN}"
    --dtype auto
)
echo "Starting vLLM; server log: ${VLLM_LOG}"
"${VLLM_BIN}" "${VLLM_ARGS[@]}" >"${VLLM_LOG}" 2>&1 &
VLLM_PID=$!
export VLLM_PID VLLM_LOG BASE_URL VLLM_READY_TIMEOUT

cleanup() {
    if kill -0 "${VLLM_PID}" >/dev/null 2>&1; then
        kill "${VLLM_PID}" >/dev/null 2>&1 || true
        wait "${VLLM_PID}" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

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

"${PYTHON_BIN}" -m scripts.sft.evaluate_policy \
    --provider local-vllm \
    --model "${MODEL_PATH}" \
    --base-url "${BASE_URL}" \
    --target-tokenizer "${TARGET_TOKENIZER}" \
    --no-target-enable-thinking \
    --temperature "${TEMPERATURE}" \
    --max-output-tokens "${MAX_OUTPUT_TOKENS}" \
    --num-workers "${NUM_WORKERS}" \
    --seed-base 0 \
    --num-scenarios "${EVAL_NUM_SCENARIOS}" \
    --samples-per-scenario 1 \
    --output-jsonl "${OUTPUT_JSONL}" \
    --summary-json "${SUMMARY_JSON}" \
    "${RESUME_ARG[@]}"

echo "evaluation_complete=$(date --iso-8601=seconds)"
echo "summary=${SUMMARY_JSON}"
