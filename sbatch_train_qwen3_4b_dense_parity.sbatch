#!/bin/bash
#SBATCH --job-name=q3_4b_port_parity
#SBATCH --output=/zfsauton/scratch/cpulling/verlog_v08_data/logs/dense_parity_4b_%j.out
#SBATCH --error=/zfsauton/scratch/cpulling/verlog_v08_data/logs/dense_parity_4b_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=400G
#SBATCH --time=11:59:00
#SBATCH --gres=gpu:a6000:4
set -uo pipefail
# ============================================================================
# TIER-2 NUMERICAL-STABILITY run: PORT side (verl-0.8).
# Dense Qwen3-4B, matched to the OLD Verlog recipe (train_auton_frank.sbatch):
# 32 envs, adv=gae_dual(.99/.95), KL-in-reward, lr 1e-6/1e-5, entropy 1e-3,
# bs256/mini256/micro4, ppo_epochs2, token_budget 500, 5 students, 75 steps.
#
# CRITICAL: DENSE model -> FAST PACKED path. The hybrid overrides
# (use_remove_padding=False / use_dynamic_bsz=False) are DELIBERATELY ABSENT: if
# the dense path regressed, it fails/diverges here. Token-TIS OFF to isolate the stack.
# Pair with the old-branch run scripts/validation/run_old_verlog_qwen3_4b_parity.sbatch
# (same recipe on verl-0.6); compare curves in verl_parity_qwen3_4b on wandb.
# ============================================================================
cd /zfsauton2/home/cpulling/Verlog_v08
ENV_ROOT=/zfsauton/scratch/cpulling/conda_envs/qwen35
export PATH="$ENV_ROOT/bin:$PATH"; PY="$ENV_ROOT/bin/python3"
export HF_HOME=/zfsauton/scratch/cpulling/.cache/huggingface
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 VLLM_USE_V1=1 PYTHONUNBUFFERED=1 FLA_TILELANG=0
export TRITON_CACHE_DIR=/zfsauton/scratch/cpulling/.triton_cache
export PYTHONPATH=$PWD
export RAY_TMPDIR=/tmp/r${SLURM_JOB_ID}
export WANDB_API_KEY=$(cat ~/.wandb_key 2>/dev/null)   # never hardcode the key
export WANDB_START_METHOD=thread
export WANDB_ENTITY=aseo-carnegie-mellon-university
export CONSENSUS_GEN_LOG=/zfsauton/scratch/cpulling/verlog_v08_data/logs/genlog_dense4b_${SLURM_JOB_ID}.jsonl

MODEL="Qwen/Qwen3-4B"          # DENSE model (backwards-compat target)
NUM_ENVS=32
DATA=/zfsauton/scratch/cpulling/data
SEED=${SEED:-1}

$PY -m verl.trainer.main_ppo \
  algorithm.adv_estimator=gae_dual \
  algorithm.step_gamma=0.99 \
  algorithm.step_lam=0.95 \
  algorithm.use_kl_in_reward=True \
  actor_rollout_ref.model.path="$MODEL" \
  actor_rollout_ref.model.enable_gradient_checkpointing=True \
  actor_rollout_ref.rollout.name=vllm \
  actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
  actor_rollout_ref.rollout.n=1 \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.40 \
  actor_rollout_ref.rollout.enforce_eager=False \
  actor_rollout_ref.rollout.prompt_length=4096 \
  actor_rollout_ref.rollout.response_length=512 \
  actor_rollout_ref.rollout.max_model_len=8192 \
  actor_rollout_ref.rollout.max_num_seqs=32 \
  data.max_prompt_length=4096 \
  data.max_response_length=512 \
  actor_rollout_ref.rollout.agent.default_agent_loop=consensus_multi_agent \
  actor_rollout_ref.rollout.agent.num_workers=$NUM_ENVS \
  actor_rollout_ref.actor.use_kl_loss=False \
  actor_rollout_ref.actor.entropy_coeff=0.001 \
  actor_rollout_ref.actor.ppo_epochs=2 \
  actor_rollout_ref.actor.ppo_mini_batch_size=256 \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.actor.optim.lr=1e-6 \
  actor_rollout_ref.actor.fsdp_config.param_offload=True \
  actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
  critic.fsdp.param_offload=True \
  critic.fsdp.optimizer_offload=True \
  critic.optim.lr=1e-5 \
  critic.model.path="$MODEL" \
  critic.model.enable_gradient_checkpointing=True \
  critic.enable=True \
  critic.ppo_epochs=2 \
  critic.ppo_micro_batch_size_per_gpu=1 \
  critic.ppo_mini_batch_size=256 \
  envs.env_name=async_ticker_admissions \
  envs.num_envs=$NUM_ENVS \
  envs.env_config.reward_mode=individual \
  envs.env_config.students_per_batch=5 \
  envs.env_config.feature_dim=5 \
  envs.env_config.token_budget=500 \
  envs.env_config.vote_threshold=0.5 \
  envs.env_config.max_steps=50 \
  +envs.env_config.seed=$SEED \
  data.train_batch_size=256 \
  data.train_files=$DATA/consensus_train.parquet \
  data.val_files=$DATA/consensus_train.parquet \
  trainer.critic_warmup=10 \
  trainer.total_training_steps=75 \
  trainer.total_epochs=15 \
  trainer.val_before_train=False \
  trainer.test_freq=-1 \
  trainer.save_freq=25 \
  trainer.balance_batch=False \
  trainer.n_gpus_per_node=4 \
  trainer.nnodes=1 \
  trainer.project_name=verl_parity_qwen3_4b \
  trainer.experiment_name=port_dense4b_${SLURM_JOB_ID} \
  trainer.logger=[console,wandb]
echo "=== PORT DENSE PARITY EXIT=$? ==="
