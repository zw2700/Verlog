#!/bin/bash
#SBATCH --job-name=verlog_simple
#SBATCH --output=logs/simple_%j.out
#SBATCH --error=logs/simple_%j.err
#SBATCH --partition=debug
#SBATCH --qos=qos_debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --gres=gpu:a6000:1

set -euo pipefail

echo "=== Job $SLURM_JOB_ID on $SLURMD_NODENAME at $(date) ==="

PROJECT_DIR="/zfsauton/scratch/cpulling/Verlog"
ENV_PATH="/zfsauton/scratch/cpulling/conda_envs/verlog"
DATA_DIR="/zfsauton/scratch/cpulling/data/gsm8k"

cd "$PROJECT_DIR"

source /home/scratch/cpulling/miniconda3/etc/profile.d/conda.sh
conda activate "$ENV_PATH"

export HF_HOME="/zfsauton/scratch/${USER}/models_cache"
export TMPDIR="/zfsauton/scratch/${USER}/tmp"
export RAY_TMPDIR="$TMPDIR"
mkdir -p "$HF_HOME" "$TMPDIR" logs

ulimit -n 65535 || true
export VLLM_USE_V1=1

if [ -f "$HOME/.wandb_key" ]; then
    export WANDB_API_KEY="$(cat "$HOME/.wandb_key")"
else
    echo "WARN: no ~/.wandb_key — running with wandb disabled"
    export WANDB_MODE=disabled
fi

echo "SLURM-assigned CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi -L || echo "WARN: nvidia-smi failed"

NUM_GPUS_PER_NODE=1
NUM_ENVS=4
BATCH_SIZE=32
MINI_BATCH_SIZE=$((BATCH_SIZE))
MICRO_BATCH_SIZE=4
FORWARD_BATCH_SIZE=$((4 * MICRO_BATCH_SIZE))
OFFLOAD=true
PPO_EPOCHS=1

python3 -m verl.trainer.main_ppo \
    --config-path="$PROJECT_DIR/examples/sglang_multiturn/config" \
    --config-name='gsm8k_multiturn_grpo' \
    algorithm.adv_estimator=gae \
    data.train_batch_size=${BATCH_SIZE} \
    data.max_prompt_length=4096 \
    data.max_response_length=512 \
    data.filter_overlong_prompts=True \
    data.truncation=error \
    data.return_raw_chat=True \
    data.train_files="$DATA_DIR/train.parquet" \
    data.val_files="$DATA_DIR/test.parquet" \
    actor_rollout_ref.rollout.mode=async \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.4 \
    actor_rollout_ref.rollout.n=1 \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=${FORWARD_BATCH_SIZE} \
    actor_rollout_ref.rollout.agent.num_workers=${NUM_ENVS} \
    actor_rollout_ref.model.path=Qwen/Qwen2.5-0.5B-Instruct \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.actor.ppo_mini_batch_size=${MINI_BATCH_SIZE} \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=${MICRO_BATCH_SIZE} \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.ppo_epochs=${PPO_EPOCHS} \
    actor_rollout_ref.actor.fsdp_config.param_offload=${OFFLOAD} \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=${OFFLOAD} \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=${FORWARD_BATCH_SIZE} \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.use_kl_in_reward=True \
    trainer.balance_batch=False \
    trainer.critic_warmup=0 \
    trainer.logger='["console"]' \
    trainer.project_name=verlog_simple \
    trainer.experiment_name="simple_${SLURM_JOB_ID}" \
    trainer.n_gpus_per_node=${NUM_GPUS_PER_NODE} \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
    trainer.test_freq=-1 \
    trainer.total_epochs=1 \
    trainer.total_training_steps=5 \
    trainer.val_before_train=False \
    envs.num_envs=${NUM_ENVS} \
    envs.env_name=async_ticker_admissions \
    +envs.env_config.professor_ids='["prof_1","prof_2","prof_3"]' \
    +envs.env_config.students_per_batch=5 \
    +envs.env_config.token_budget=1000 \
    +envs.env_config.feature_dim=5 \
    +envs.env_config.vote_threshold=0.5 \
    +envs.env_config.max_steps=50 \
    critic.optim.lr=1e-5 \
    critic.model.use_remove_padding=True \
    critic.model.path=Qwen/Qwen2.5-0.5B-Instruct \
    critic.model.enable_gradient_checkpointing=True \
    critic.ppo_epochs=${PPO_EPOCHS} \
    critic.ppo_micro_batch_size_per_gpu=${MICRO_BATCH_SIZE} \
    critic.ppo_mini_batch_size=${MINI_BATCH_SIZE} \
    critic.model.fsdp_config.param_offload=${OFFLOAD} \
    critic.model.fsdp_config.optimizer_offload=${OFFLOAD} \
    critic.forward_micro_batch_size_per_gpu=${FORWARD_BATCH_SIZE}

echo "=== Done at $(date) ==="
