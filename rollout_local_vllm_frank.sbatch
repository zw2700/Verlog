#!/bin/bash
#SBATCH --job-name=rollout_local_vllm_frank
#SBATCH --output=logs/rollout_local_vllm_%j.out
#SBATCH --error=logs/rollout_local_vllm_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --gres=gpu:a6000:1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Slurm executes a copied script from its spool directory, so BASH_SOURCE does
# not identify the checkout inside a batch job. The submission directory does.
PROJECT_DIR="${PROJECT_DIR:-${SLURM_SUBMIT_DIR:-$SCRIPT_DIR}}"
ENV_PATH="${ENV_PATH:-/zfsauton/scratch/cpulling/conda_envs/verlog}"

cd "$PROJECT_DIR"

SUBMIT_ENV_VARS=(
    MODEL
    MODEL_REVISION
    NUM_EPISODES
    NUM_ENVS
    EPISODE_WORKERS
    SEED_BASE
    TEMPERATURE
    TOP_P
    MAX_OUTPUT_TOKENS
    REASONING_MODE
    INCLUDE_REASONING_TEXT
    ZERO_SHOT_CELL_NAME
    ZERO_SHOT_METADATA_PATH
    STUDENTS_PER_BATCH
    TOKEN_BUDGET
    FEATURE_DIM
    VOTE_THRESHOLD
    MAX_STEPS
    TERMINATE_ON_ALL_VOTED_NO_CONSENSUS
    PROFESSOR_PREFERENCE_MODE
    RANDOMIZE_TURN_ORDER
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
VLLM_COMMAND=("$PYTHON_BIN" -m vllm.entrypoints.cli.main)

export HF_HOME="${HF_HOME:-/zfsauton/scratch/$USER/.cache/huggingface}"
export TMPDIR="${TMPDIR:-/zfsauton/scratch/$USER/tmp}"
export RAY_TMPDIR="${RAY_TMPDIR:-$TMPDIR}"
mkdir -p "$HF_HOME" "$TMPDIR" logs

export PYTHONUNBUFFERED=1
export VLLM_USE_V1="${VLLM_USE_V1:-1}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
unset ROCR_VISIBLE_DEVICES

JOB_ID="${SLURM_JOB_ID:-local_$(date +%s)}"
MODEL="${MODEL:-Qwen/Qwen3-4B}"
MODEL_REVISION="${MODEL_REVISION:-}"
NUM_EPISODES="${NUM_EPISODES:-10}"
NUM_ENVS="${NUM_ENVS:-8}"
EPISODE_WORKERS="${EPISODE_WORKERS:-1}"
SEED_BASE="${SEED_BASE:-0}"
TEMPERATURE="${TEMPERATURE:-1.0}"
TOP_P="${TOP_P:-}"
MAX_OUTPUT_TOKENS="${MAX_OUTPUT_TOKENS:-512}"
REASONING_MODE="${REASONING_MODE:-manual-tags}"
INCLUDE_REASONING_TEXT="${INCLUDE_REASONING_TEXT:-0}"
ZERO_SHOT_CELL_NAME="${ZERO_SHOT_CELL_NAME:-}"
ZERO_SHOT_METADATA_PATH="${ZERO_SHOT_METADATA_PATH:-}"
STUDENTS_PER_BATCH="${STUDENTS_PER_BATCH:-5}"
TOKEN_BUDGET="${TOKEN_BUDGET:-500}"
FEATURE_DIM="${FEATURE_DIM:-5}"
VOTE_THRESHOLD="${VOTE_THRESHOLD:-0.5}"
MAX_STEPS="${MAX_STEPS:-50}"
TERMINATE_ON_ALL_VOTED_NO_CONSENSUS="${TERMINATE_ON_ALL_VOTED_NO_CONSENSUS:-0}"
PROFESSOR_PREFERENCE_MODE="${PROFESSOR_PREFERENCE_MODE:-random_permutation}"
RANDOMIZE_TURN_ORDER="${RANDOMIZE_TURN_ORDER:-0}"
REQUEST_LOGPROBS="${REQUEST_LOGPROBS:-0}"
ROLLOUT_POSTFIX="${ROLLOUT_POSTFIX:-}"
VLLM_HOST="${VLLM_HOST:-127.0.0.1}"
if [ -z "${VLLM_PORT:-}" ]; then
    if [ -n "${SLURM_JOB_ID:-}" ]; then
        # vLLM reserves nearby ports for its engine processes. Give each Slurm
        # job a disjoint block so consecutive jobs can share one node safely.
        VLLM_PORT=$((20000 + ((SLURM_JOB_ID % 1000) * 20)))
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
mkdir -p "$(dirname "$VERL_AGENT_EPISODE_LOG_PATH")" "$(dirname "$VERL_GAME_LOG_PATH")"
if [ -n "$ZERO_SHOT_METADATA_PATH" ]; then
    mkdir -p "$(dirname "$ZERO_SHOT_METADATA_PATH")"
fi

echo "=== Local vLLM Rollout Configuration ==="
echo "Job ID: $JOB_ID"
echo "Model: $MODEL"
echo "Model revision: ${MODEL_REVISION:-provider resolved}"
echo "Episodes: $NUM_EPISODES"
echo "Num env slots: $NUM_ENVS"
echo "Concurrent episode workers: $EPISODE_WORKERS"
echo "Seed base: $SEED_BASE"
echo "Temperature: $TEMPERATURE"
echo "Top-p: ${TOP_P:-provider default}"
echo "Reasoning mode: $REASONING_MODE"
echo "Log private reasoning text: $INCLUDE_REASONING_TEXT"
echo "Chat template enable_thinking: $([ "$REASONING_MODE" = native-thinking ] && echo true || echo false)"
echo "Rollout postfix: ${ROLLOUT_POSTFIX:-none}"
echo "vLLM base URL: $LOCAL_VLLM_BASE_URL"
echo "vLLM tensor parallel size: $VLLM_TENSOR_PARALLEL_SIZE"
echo "vLLM GPU memory utilization: $VLLM_GPU_MEMORY_UTILIZATION"
echo "vLLM max model len: $VLLM_MAX_MODEL_LEN"
echo "Cell name: ${ZERO_SHOT_CELL_NAME:-none}"
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
if [ -n "$MODEL_REVISION" ]; then
    VLLM_ARGS+=(--revision "$MODEL_REVISION")
fi
if [ -n "$VLLM_EXTRA_ARGS" ]; then
    # shellcheck disable=SC2206
    EXTRA_ARGS=($VLLM_EXTRA_ARGS)
    VLLM_ARGS+=("${EXTRA_ARGS[@]}")
fi

echo "Starting vLLM server. Log: $VLLM_LOG_PATH"
"${VLLM_COMMAND[@]}" "${VLLM_ARGS[@]}" >"$VLLM_LOG_PATH" 2>&1 &
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

REASONING_TEXT_ARG=()
if [ "$INCLUDE_REASONING_TEXT" = "1" ]; then
    REASONING_TEXT_ARG=(--include-reasoning-text)
fi

TOP_P_ARG=()
if [ -n "$TOP_P" ]; then
    TOP_P_ARG=(--top-p "$TOP_P")
fi

MODEL_REVISION_ARG=()
if [ -n "$MODEL_REVISION" ]; then
    MODEL_REVISION_ARG=(--model-revision "$MODEL_REVISION")
fi

METADATA_ARG=()
if [ -n "$ZERO_SHOT_METADATA_PATH" ]; then
    METADATA_ARG=(--metadata-json "$ZERO_SHOT_METADATA_PATH")
fi

CELL_ARG=()
if [ -n "$ZERO_SHOT_CELL_NAME" ]; then
    CELL_ARG=(--cell-name "$ZERO_SHOT_CELL_NAME")
fi

TURN_ORDER_ARG=()
if [ "$RANDOMIZE_TURN_ORDER" = "1" ]; then
    TURN_ORDER_ARG=(--randomize-turn-order)
fi

TERMINATION_ARG=(--no-terminate-on-all-voted-no-consensus)
if [ "$TERMINATE_ON_ALL_VOTED_NO_CONSENSUS" = "1" ]; then
    TERMINATION_ARG=(--terminate-on-all-voted-no-consensus)
fi

ROLLOUT_MODULE=scripts.rollout_frontier
if [ -n "${PROMPT_COMPARISON_RECOVERY:-}" ]; then
    ROLLOUT_MODULE=scripts.recover_prompt_comparison
elif [ "${REPEATED_BARGAINING:-0}" = "1" ]; then
    ROLLOUT_MODULE=scripts.rollout_repeated_comparison
elif [ "${PROMPT_COMPARISON:-0}" = "1" ]; then
    ROLLOUT_MODULE=scripts.rollout_prompt_comparison
fi
"$PYTHON_BIN" -m "$ROLLOUT_MODULE" \
    --provider local-vllm \
    --model "$MODEL" \
    "${MODEL_REVISION_ARG[@]}" \
    --base-url "$LOCAL_VLLM_BASE_URL" \
    --num-episodes "$NUM_EPISODES" \
    --num-envs "$NUM_ENVS" \
    --episode-workers "$EPISODE_WORKERS" \
    --seed-base "$SEED_BASE" \
    --temperature "$TEMPERATURE" \
    --reasoning-mode "$REASONING_MODE" \
    "${TOP_P_ARG[@]}" \
    --max-output-tokens "$MAX_OUTPUT_TOKENS" \
    --students-per-batch "$STUDENTS_PER_BATCH" \
    --token-budget "$TOKEN_BUDGET" \
    --feature-dim "$FEATURE_DIM" \
    --vote-threshold "$VOTE_THRESHOLD" \
    --max-steps "$MAX_STEPS" \
    --professor-preference-mode "$PROFESSOR_PREFERENCE_MODE" \
    "${TERMINATION_ARG[@]}" \
    "${TURN_ORDER_ARG[@]}" \
    --out-jsonl "$VERL_AGENT_EPISODE_LOG_PATH" \
    --game-log "$VERL_GAME_LOG_PATH" \
    "${METADATA_ARG[@]}" \
    "${CELL_ARG[@]}" \
    "${LOGPROB_ARG[@]}" \
    "${REASONING_TEXT_ARG[@]}" \
    "$@"
