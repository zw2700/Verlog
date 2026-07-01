#!/bin/bash
#SBATCH --job-name=rollout_frontier_frank
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/rollout_frontier_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/rollout_frontier_%j.err
#SBATCH --partition=cpu
#SBATCH --qos=qos_cpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16G
#SBATCH --time=12:00:00

set -euo pipefail

PROJECT_DIR="/zfsauton2/home/frankwu2/unscripted/Verlog"
ENV_PATH="/zfsauton/scratch/cpulling/conda_envs/verlog"

cd "$PROJECT_DIR"

SUBMIT_ENV_VARS=(
    PROVIDER
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
)
for name in "${SUBMIT_ENV_VARS[@]}"; do
    if [ "${!name+x}" = "x" ]; then
        export "SUBMIT_OVERRIDE_${name}=1"
        export "SUBMIT_VALUE_${name}=${!name}"
    fi
done

ROLLOUT_FRONTIER_ENV_FILE="${ROLLOUT_FRONTIER_ENV_FILE:-$PROJECT_DIR/rollout_frontier.env}"
if [ -f "$ROLLOUT_FRONTIER_ENV_FILE" ]; then
    echo "Loading rollout config from $ROLLOUT_FRONTIER_ENV_FILE"
    set -a
    # shellcheck disable=SC1090
    source "$ROLLOUT_FRONTIER_ENV_FILE"
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

mkdir -p logs
export PYTHONUNBUFFERED=1

JOB_ID="${SLURM_JOB_ID:-local_$(date +%s)}"
PROVIDER="${PROVIDER:-openai}"
MODEL="${MODEL:-gpt-4o-mini}"
NUM_EPISODES="${NUM_EPISODES:-100}"
NUM_ENVS="${NUM_ENVS:-32}"
SEED_BASE="${SEED_BASE:-0}"
TEMPERATURE="${TEMPERATURE:-1.0}"
TOP_P="${TOP_P:-}"
MAX_OUTPUT_TOKENS="${MAX_OUTPUT_TOKENS:-512}"
REQUEST_LOGPROBS="${REQUEST_LOGPROBS:-0}"
ROLLOUT_POSTFIX="${ROLLOUT_POSTFIX:-}"

SAFE_MODEL="${MODEL//\//_}"
SAFE_MODEL="${SAFE_MODEL//:/_}"
SAFE_POSTFIX="${ROLLOUT_POSTFIX//\//_}"
SAFE_POSTFIX="${SAFE_POSTFIX//:/_}"
SAFE_POSTFIX="${SAFE_POSTFIX// /_}"
if [ -n "$SAFE_POSTFIX" ] && [[ "$SAFE_POSTFIX" != _* ]]; then
    SAFE_POSTFIX="_$SAFE_POSTFIX"
fi

export VERL_AGENT_EPISODE_LOG_PATH="${VERL_AGENT_EPISODE_LOG_PATH:-$PROJECT_DIR/logs/episode_log_rollout_${PROVIDER}_${SAFE_MODEL}_${JOB_ID}${SAFE_POSTFIX}.jsonl}"
export VERL_GAME_LOG_PATH="${VERL_GAME_LOG_PATH:-$PROJECT_DIR/logs/game_log_rollout_${PROVIDER}_${SAFE_MODEL}_${JOB_ID}${SAFE_POSTFIX}.log}"

echo "=== Frontier Rollout Configuration ==="
echo "Job ID: $JOB_ID"
echo "Provider: $PROVIDER"
echo "Model: $MODEL"
echo "Episodes: $NUM_EPISODES"
echo "Num env slots: $NUM_ENVS"
echo "Seed base: $SEED_BASE"
echo "Temperature: $TEMPERATURE"
echo "Top-p: ${TOP_P:-provider default}"
echo "Rollout postfix: ${ROLLOUT_POSTFIX:-none}"
echo "Episode JSONL: $VERL_AGENT_EPISODE_LOG_PATH"
echo "Game log: $VERL_GAME_LOG_PATH"
echo "======================================"

LOGPROB_ARG=()
if [ "$REQUEST_LOGPROBS" = "1" ]; then
    LOGPROB_ARG=(--request-logprobs)
fi

TOP_P_ARG=()
if [ -n "$TOP_P" ]; then
    TOP_P_ARG=(--top-p "$TOP_P")
fi

"$PYTHON_BIN" -m scripts.rollout_frontier \
    --provider "$PROVIDER" \
    --model "$MODEL" \
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
