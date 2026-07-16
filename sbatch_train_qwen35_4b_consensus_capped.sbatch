#!/bin/bash
#SBATCH --job-name=q35_4b_consensus_capped
#SBATCH --output=/zfsauton/scratch/cpulling/verlog_v08_data/logs/consensus_4b_capped_%j.out
#SBATCH --error=/zfsauton/scratch/cpulling/verlog_v08_data/logs/consensus_4b_capped_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=360G
#SBATCH --time=05:59:00
#SBATCH --gres=gpu:a6000:4
set -uo pipefail
# ============================================================================
# VALIDATION run: Qwen3.5-0.8B, 1 GPU, hiring env. Confirms the model actually TRAINS and
# PLAYS the game coherently (not gibberish). Longer than the smoke (12 steps) + CONSENSUS_GEN_LOG
# dumps the decoded professor turns so we can read the actual game-play text.
# ============================================================================
cd /zfsauton2/home/cpulling/Verlog_v08
ENV_ROOT=/zfsauton/scratch/cpulling/conda_envs/qwen35
export PATH="$ENV_ROOT/bin:$PATH"; PY="$ENV_ROOT/bin/python3"
export HF_HOME=/zfsauton/scratch/cpulling/.cache/huggingface
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 VLLM_USE_V1=1 PYTHONUNBUFFERED=1 FLA_TILELANG=0
export TRITON_CACHE_DIR=/zfsauton/scratch/cpulling/.triton_cache
export PYTHONPATH=$PWD
export RAY_TMPDIR=/tmp/r${SLURM_JOB_ID}
export WANDB_API_KEY=$(cat ~/.wandb_key 2>/dev/null)
export CONSENSUS_GEN_LOG=/zfsauton/scratch/cpulling/verlog_v08_data/logs/genlog_4b_capped_${SLURM_JOB_ID}.jsonl

MODEL="Qwen/Qwen3.5-4B"
NUM_ENVS=4
DATA=/zfsauton/scratch/cpulling/data

$PY -m verl.trainer.main_ppo \
  algorithm.adv_estimator=gae_dual \
  algorithm.step_gamma=0.99 \
  algorithm.step_lam=0.95 \
  algorithm.use_kl_in_reward=False \
  algorithm.rollout_correction.rollout_is=token \
  algorithm.rollout_correction.rollout_is_threshold=2.0 \
  actor_rollout_ref.model.path="$MODEL" \
  actor_rollout_ref.rollout.name=vllm \
  actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
  actor_rollout_ref.rollout.n=1 \
  actor_rollout_ref.rollout.calculate_log_probs=True \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.35 \
  actor_rollout_ref.rollout.enforce_eager=False \
  actor_rollout_ref.rollout.prompt_length=4096 \
  actor_rollout_ref.rollout.response_length=1024 \
  actor_rollout_ref.rollout.max_model_len=8192 \
  actor_rollout_ref.rollout.max_num_seqs=16 \
  data.max_prompt_length=4096 \
  data.max_response_length=1024 \
  actor_rollout_ref.rollout.agent.default_agent_loop=consensus_multi_agent \
  actor_rollout_ref.rollout.agent.num_workers=$NUM_ENVS \
  actor_rollout_ref.actor.use_kl_loss=True \
  actor_rollout_ref.actor.kl_loss_coef=0.01 \
  actor_rollout_ref.actor.use_remove_padding=False \
  actor_rollout_ref.actor.use_dynamic_bsz=False \
  actor_rollout_ref.actor.ppo_mini_batch_size=16 \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.actor.optim.lr=1e-6 \
  actor_rollout_ref.actor.fsdp_config.param_offload=True \
  actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
  critic.fsdp.param_offload=True \
  critic.fsdp.optimizer_offload=True \
  trainer.max_actor_ckpt_to_keep=2 \
  trainer.max_critic_ckpt_to_keep=2 \
  critic.model.path="$MODEL" \
  critic.enable=True \
  critic.model.use_remove_padding=False \
  critic.use_dynamic_bsz=False \
  critic.ppo_micro_batch_size_per_gpu=1 \
  envs.env_name=async_ticker_admissions \
  envs.num_envs=$NUM_ENVS \
  envs.env_config.reward_mode=individual \
  envs.env_config.students_per_batch=10 \
  envs.env_config.format_penalty_cap=0.3 \
  data.train_batch_size=64 \
  data.train_files=$DATA/consensus_train.parquet \
  data.val_files=$DATA/consensus_train.parquet \
  trainer.critic_warmup=10 \
  trainer.total_training_steps=40 \
  trainer.total_epochs=1 \
  trainer.val_before_train=False \
  trainer.test_freq=-1 \
  trainer.save_freq=10 \
  trainer.balance_batch=False \
  trainer.n_gpus_per_node=4 \
  trainer.nnodes=1 \
  trainer.project_name=verlog_qwen35_v08 \
  trainer.experiment_name=consensus_4b_capped_${SLURM_JOB_ID} \
  trainer.logger=[console]
echo "=== VAL EXIT=$? ==="
