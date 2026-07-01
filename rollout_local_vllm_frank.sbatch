#!/bin/bash
#SBATCH --job-name=rollout_local_vllm_frank
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/rollout_local_vllm_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/rollout_local_vllm_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --gres=gpu:a6000:1

set -euo pipefail

PROJECT_DIR="/zfsauton2/home/frankwu2/unscripted/Verlog"
ENV_PATH="/zfsauton/scratch/cpulling/conda_envs/verlog"

cd "$PROJECT_DIR"

SUBMIT_ENV_VARS=(
    MODEL
    NUM_EPISODES
    NUM_ENVS
    SEED_BASE
    TEMPERATURE
    TOP_P
    MAX_OUTPUT_TOKENS
    REQUEST_LOGPROBS
    ROLLOUT_POSTFIX
    VERL_AGENT_EPISODE_LOG_PATH
    VERL_GAME_LOG_PATH
    VLLM_PORT
    VLLM_HOST
    VLLM_TENSOR_PARALLEL_SIZE
    VLLM_GPU_MEMORY_UTILIZATION
    VLLM_MAX_MODEL_LEN
    VLLM_DTYPE
    VLLM_EXTRA_ARGS
    VLLM_READY_TIMEOUT
)
for name in "${SUBMIT_ENV_VARS[@]}"; do
    if [ "${!name+x}" = "x" ]; then
        export "SUBMIT_OVERRIDE_${name}=1"
        export "SUBMIT_VALUE_${name}=${!name}"
    fi
done

ROLLOUT_LOCAL_VLLM_ENV_FILE="${ROLLOUT_LOCAL_VLLM_ENV_FILE:-$PROJECT_DIR/rollout_local_vllm.env}"
if [ -f "$ROLLOUT_LOCAL_VLLM_ENV_FILE" ]; then
    echo "Loading local vLLM rollout config from $ROLLOUT_LOCAL_VLLM_ENV_FILE"
    set -a
    # shellcheck disable=SC1090
    source "$ROLLOUT_LOCAL_VLLM_ENV_FILE"
    set +a
fi
for name in "${SUBMIT_ENV_VARS[@]}"; do
    override_var="SUBMIT_OVERRIDE_${name}"
    value_var="SUBMIT_VALUE_${name}"
    if [ "${!override_var:-}" = "1" ]; then
        printf -v "$name" "%s" "${!value_var}"
        export "$name"
    fi
done

export PATH="$ENV_PATH/bin:$PATH"
export CONDA_PREFIX="$ENV_PATH"
PYTHON_BIN="$ENV_PATH/bin/python3"
VLLM_BIN="$ENV_PATH/bin/vllm"

export HF_HOME="${HF_HOME:-/zfsauton/scratch/frankwu2/.cache/huggingface}"
export TMPDIR="${TMPDIR:-/zfsauton/scratch/frankwu2/tmp}"
export RAY_TMPDIR="${RAY_TMPDIR:-$TMPDIR}"
mkdir -p "$HF_HOME" "$TMPDIR" logs

export PYTHONUNBUFFERED=1
export VLLM_USE_V1="${VLLM_USE_V1:-1}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
unset ROCR_VISIBLE_DEVICES

JOB_ID="${SLURM_JOB_ID:-local_$(date +%s)}"
MODEL="${MODEL:-Qwen/Qwen3.5-4B}"
NUM_EPISODES="${NUM_EPISODES:-10}"
NUM_ENVS="${NUM_ENVS:-8}"
SEED_BASE="${SEED_BASE:-0}"
TEMPERATURE="${TEMPERATURE:-1.0}"
TOP_P="${TOP_P:-}"
MAX_OUTPUT_TOKENS="${MAX_OUTPUT_TOKENS:-512}"
REQUEST_LOGPROBS="${REQUEST_LOGPROBS:-0}"
ROLLOUT_POSTFIX="${ROLLOUT_POSTFIX:-}"
VLLM_HOST="${VLLM_HOST:-127.0.0.1}"
if [ -z "${VLLM_PORT:-}" ]; then
    if [ -n "${SLURM_JOB_ID:-}" ]; then
        VLLM_PORT=$((20000 + (SLURM_JOB_ID % 20000)))
    else
        VLLM_PORT=8000
    fi
fi
VLLM_TENSOR_PARALLEL_SIZE="${VLLM_TENSOR_PARALLEL_SIZE:-1}"
VLLM_GPU_MEMORY_UTILIZATION="${VLLM_GPU_MEMORY_UTILIZATION:-0.85}"
VLLM_MAX_MODEL_LEN="${VLLM_MAX_MODEL_LEN:-8192}"
VLLM_DTYPE="${VLLM_DTYPE:-auto}"
VLLM_EXTRA_ARGS="${VLLM_EXTRA_ARGS:-}"
VLLM_READY_TIMEOUT="${VLLM_READY_TIMEOUT:-900}"

SAFE_MODEL="${MODEL//\//_}"
SAFE_MODEL="${SAFE_MODEL//:/_}"
SAFE_POSTFIX="${ROLLOUT_POSTFIX//\//_}"
SAFE_POSTFIX="${SAFE_POSTFIX//:/_}"
SAFE_POSTFIX="${SAFE_POSTFIX// /_}"
if [ -n "$SAFE_POSTFIX" ] && [[ "$SAFE_POSTFIX" != _* ]]; then
    SAFE_POSTFIX="_$SAFE_POSTFIX"
fi

export VERL_AGENT_EPISODE_LOG_PATH="${VERL_AGENT_EPISODE_LOG_PATH:-$PROJECT_DIR/logs/episode_log_rollout_local-vllm_${SAFE_MODEL}_${JOB_ID}${SAFE_POSTFIX}.jsonl}"
export VERL_GAME_LOG_PATH="${VERL_GAME_LOG_PATH:-$PROJECT_DIR/logs/game_log_rollout_local-vllm_${SAFE_MODEL}_${JOB_ID}${SAFE_POSTFIX}.log}"
export LOCAL_VLLM_BASE_URL="http://${VLLM_HOST}:${VLLM_PORT}/v1"
export LOCAL_VLLM_API_KEY="${LOCAL_VLLM_API_KEY:-dummy}"

echo "=== Local vLLM Rollout Configuration ==="
echo "Job ID: $JOB_ID"
echo "Model: $MODEL"
echo "Episodes: $NUM_EPISODES"
echo "Num env slots: $NUM_ENVS"
echo "Seed base: $SEED_BASE"
echo "Temperature: $TEMPERATURE"
echo "Top-p: ${TOP_P:-provider default}"
echo "Rollout postfix: ${ROLLOUT_POSTFIX:-none}"
echo "vLLM base URL: $LOCAL_VLLM_BASE_URL"
echo "vLLM tensor parallel size: $VLLM_TENSOR_PARALLEL_SIZE"
echo "vLLM GPU memory utilization: $VLLM_GPU_MEMORY_UTILIZATION"
echo "vLLM max model len: $VLLM_MAX_MODEL_LEN"
echo "Local vLLM disable thinking: ${LOCAL_VLLM_DISABLE_THINKING:-0}"
echo "Episode JSONL: $VERL_AGENT_EPISODE_LOG_PATH"
echo "Game log: $VERL_GAME_LOG_PATH"
echo "========================================"

if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi -L || true
fi

VLLM_LOG_PATH="$PROJECT_DIR/logs/vllm_server_${JOB_ID}.log"
export VLLM_LOG_PATH
VLLM_ARGS=(
    serve "$MODEL"
    --host "$VLLM_HOST"
    --port "$VLLM_PORT"
    --tensor-parallel-size "$VLLM_TENSOR_PARALLEL_SIZE"
    --gpu-memory-utilization "$VLLM_GPU_MEMORY_UTILIZATION"
    --max-model-len "$VLLM_MAX_MODEL_LEN"
    --dtype "$VLLM_DTYPE"
)
if [ -n "$VLLM_EXTRA_ARGS" ]; then
    # shellcheck disable=SC2206
    EXTRA_ARGS=($VLLM_EXTRA_ARGS)
    VLLM_ARGS+=("${EXTRA_ARGS[@]}")
fi

echo "Starting vLLM server. Log: $VLLM_LOG_PATH"
"$VLLM_BIN" "${VLLM_ARGS[@]}" >"$VLLM_LOG_PATH" 2>&1 &
VLLM_PID=$!
export VLLM_PID
export VLLM_READY_TIMEOUT

cleanup() {
    if kill -0 "$VLLM_PID" >/dev/null 2>&1; then
        echo "Stopping vLLM server pid=$VLLM_PID"
        kill "$VLLM_PID" >/dev/null 2>&1 || true
        wait "$VLLM_PID" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

echo "Waiting for vLLM server readiness..."
"$PYTHON_BIN" - <<'PY'
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

base_url = os.environ["LOCAL_VLLM_BASE_URL"].rstrip("/")
pid = int(os.environ["VLLM_PID"])
deadline = time.time() + int(os.environ.get("VLLM_READY_TIMEOUT", "900"))
last_error = None
while time.time() < deadline:
    try:
        with urllib.request.urlopen(f"{base_url}/models", timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        model_ids = [item.get("id") for item in payload.get("data", []) if isinstance(item, dict)]
        print(f"vLLM ready. Served models: {model_ids}", flush=True)
        sys.exit(0)
    except Exception as exc:
        last_error = exc
    try:
        os.kill(pid, 0)
    except OSError:
        log_path = os.environ.get("VLLM_LOG_PATH")
        if log_path:
            print(f"vLLM process exited before readiness. Last readiness error: {last_error}", file=sys.stderr)
            print(f"--- tail -n 80 {log_path} ---", file=sys.stderr)
            subprocess.run(["tail", "-n", "80", log_path], check=False)
        raise SystemExit(f"vLLM process exited before readiness. Last readiness error: {last_error}")
    time.sleep(5)
log_path = os.environ.get("VLLM_LOG_PATH")
if log_path:
    print(f"Timed out waiting for vLLM readiness at {base_url}. Last error: {last_error}", file=sys.stderr)
    print(f"--- tail -n 80 {log_path} ---", file=sys.stderr)
    subprocess.run(["tail", "-n", "80", log_path], check=False)
raise SystemExit(f"Timed out waiting for vLLM readiness at {base_url}. Last error: {last_error}")
PY

LOGPROB_ARG=()
if [ "$REQUEST_LOGPROBS" = "1" ]; then
    LOGPROB_ARG=(--request-logprobs)
fi

TOP_P_ARG=()
if [ -n "$TOP_P" ]; then
    TOP_P_ARG=(--top-p "$TOP_P")
fi

"$PYTHON_BIN" -m scripts.rollout_frontier \
    --provider local-vllm \
    --model "$MODEL" \
    --base-url "$LOCAL_VLLM_BASE_URL" \
    --num-episodes "$NUM_EPISODES" \
    --num-envs "$NUM_ENVS" \
    --seed-base "$SEED_BASE" \
    --temperature "$TEMPERATURE" \
    "${TOP_P_ARG[@]}" \
    --max-output-tokens "$MAX_OUTPUT_TOKENS" \
    --out-jsonl "$VERL_AGENT_EPISODE_LOG_PATH" \
    --game-log "$VERL_GAME_LOG_PATH" \
    "${LOGPROB_ARG[@]}" \
    "$@"
