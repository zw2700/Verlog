# Binary social-optimum training

Test whether rewarding exact welfare-optimal agreement changes the learned policy
when the runner-up's utility is close to the best student's utility.

## Task reward

Every professor receives 1 if consensus selects a student whose total utility is
the maximum across candidates, and 0 otherwise. Use full-precision utilities and
accept every exact welfare tie. Do not accept merely near-optimal candidates or
ties created by rounding the prompt's utility table. All intermediate rewards
are zero; format and invalid-action penalties are disabled.

The mode lives in the parent-repo subclass, leaving the hiring submodule pinned.
Episode metrics and JSONL records use the same binary reward; welfare and private
utility diagnostics continue to measure the original utilities.

This intervention changes both reward shape and objective: ordinary individual
utility becomes shared social-optimum success. It does not isolate binarization
alone. A single run cannot establish that discussion causes improved decisions.

## Run specification

- Initial model: Qwen/Qwen3-4B, ordinary actor-visible critic.
- Vanilla game: 3 professors, 5 students, random-permutation preferences,
  linear utilities, majority threshold 0.5, budget 500, maximum 50 actions.
- Original private-utility instructions; no discussion instructions, hidden
  horizon, utility reshaping, privileged critic inputs, or discussion bonuses.
- Native thinking disabled; baseline sampling and PPO parameters retained.
- 32 environments, batch size 256.
- 30 critic warmup steps, 95 total steps: 65 actor-update steps.
- Warmup batch repeat/divide both 1; actor microbatch 2, critic microbatch 4.
- Existing in-reward KL regularization retained: the *environment* reward is
  binary, while PPO's regularized training reward need not be binary.
- Before/after validation and final actor/critic checkpoint.
- Primary metric: social-optimal rate across completed games, including failure
  as zero. Also inspect consensus, welfare efficiency, communication, preference
  strata, critic fit, and malformed actions. Training episodes are not independent
  held-out checkpoint evaluations.

## Canonical submission

Run from an isolated, verified checkout with private paths configured through
the standard launcher environment. Resource overrides use the same sbatch file.

```bash
sbatch --partition=project --qos=qos_radio_freq \
  --gres=gpu:h200:4 --cpus-per-task=64 --mem=240G --time=24:00:00 \
  slurm/train_auton.sbatch \
  tag=binary-social-optimum-warm30 \
  model_path=Qwen/Qwen3-4B \
  envs.env_config.reward_mode=binary_social_optimum \
  envs.env_config.format_penalty=0 \
  envs.env_config.invalid_action_penalty=0 \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2 \
  trainer.critic_warmup=30 \
  trainer.critic_warmup_batch_repeat_times=1 \
  trainer.critic_warmup_batch_divide_ratio=1 \
  trainer.total_training_steps=95 \
  trainer.val_before_train=true trainer.test_freq=95 trainer.save_freq=95
```

W&B: project `unscripted`, run name
`unscripted_auton_binary-social-optimum-warm30_<jobid>`.

## Validation

```bash
python -m pytest -q tests/envs/test_hiring_env_binary_reward.py \
  tests/envs/test_hiring_env_metrics.py
```

Checks include real majority-vote transitions, zero intermediate rewards,
suboptimal and near-optimal choices, exact ties, failure without consensus,
invalid choices/actions, auxiliary-penalty rejection, unchanged vanilla rewards,
and consistency of returned rewards, logged rewards, and welfare metrics.
