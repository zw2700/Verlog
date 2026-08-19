# Asymmetric Critic Observation Experiment

Date recorded: 2026-07-29

## Executive summary

This experiment tests whether value learning and downstream PPO credit assignment improve when the value critic receives training-only privileged state from the hiring environment.

The treatment does **not** change the critic network architecture, optimizer, value head, sampled actions, rewards, or GAE calculation. It changes only the prompt tensors routed into critic forward and update calls:

- `actor_visible`: the critic receives exactly the prompt seen by the acting professor.
- `all_utilities`: the critic receives that same prompt plus a table containing every professor's utility for every student in the current batch.

The actor and reference policy always receive the original actor-visible prompt. The critic evaluates the exact response tokens sampled by that actor. The privileged utility table is never passed to actor log-probability computation, reference-policy computation, rollout generation, or actor updates.

The actual task is `envs.env_name=async_ticker_admissions`, backed by `AsyncTickerAdmissionsEnv`. Any `gsm8k`, BabyAI, or parquet names visible in inherited VERL configuration are prompt/dataloader plumbing and are not the research task.

## Hypotheses

### H1: privileged state improves critic fit

Under a fixed actor, `all_utilities` should predict professor-specific returns better than `actor_visible` because the critic can observe the complete payoff structure of the current hiring game.

Expected signature:

- higher `critic/v_s0_return_pearson`;
- higher `critic/v_return_pearson`;
- higher `critic/vf_explained_var`;
- lower `critic/vf_loss`;
- similar improvements in each `critic/per_agent/prof_*` slice rather than an aggregate gain driven by one professor.

The strongest primary measure is `critic/v_s0_return_pearson`: it compares the value at the first response token with return-to-go from the same point and is less dominated by repeated token positions than the token-level correlation.

### H2: better critic fit improves PPO credit assignment

When the actor is allowed to update, `all_utilities` should produce more informative, lower-noise advantages than `actor_visible`. If critic observability is a meaningful bottleneck, the actor trained with this critic should improve hiring outcomes despite never receiving privileged utilities itself.

Expected downstream signature:

- higher consensus and socially optimal selection rates;
- higher normalized social-welfare and consensus-quality metrics;
- lower utilitarian gap, regret, and Pareto-dominated-choice rate;
- more stable advantages and actor updates.

This is an indirect effect. The actor cannot exploit the utility table at inference time; any improvement must be learned through better PPO gradients.

### H0 and diagnostic outcomes

- If critic metrics do not improve, the full utility table is not sufficient for predicting returns under the current representation/training regime, or critic optimization itself is the bottleneck.
- If critic metrics improve but hiring outcomes do not, privileged state helps value regression but does not materially improve policy learning.
- If hiring outcomes improve without critic-fit improvement, the result is suspicious and should be checked for stochastic variation or a confound.
- The frozen pair should not show a systematic policy-level outcome difference because neither actor updates. A large frozen-pair behavior difference indicates rollout noise, differing seeds/runtime behavior, or leakage rather than a learned policy effect.

## Exact critic change

### 1. Environment exposes a critic-only utility matrix

`AsyncTickerEnvWrapper.get_critic_context()` obtains the current utilities from the underlying hiring environment and returns:

```python
{
    "professor_ids": ["prof_1", "prof_2", "prof_3"],
    "student_utilities": {
        "prof_1": [u_10, u_11, u_12, u_13, u_14],
        "prof_2": [u_20, u_21, u_22, u_23, u_24],
        "prof_3": [u_30, u_31, u_32, u_33, u_34],
    },
}
```

This contains the current per-professor, per-student utilities. It does not directly add future actions, the final selected student, a terminal reward label, or a precomputed optimal action.

### 2. The utility matrix is appended only to the critic system prompt

In `all_utilities` mode, the agent loop deep-copies the actor messages and appends a block of this form to the critic's system message:

```text
<CRITIC_ONLY_PRIVILEGED_STATE>
Training-only state for the value critic; this block is never visible to the acting policy.
Utilities for every professor and student:
student prof_1  prof_2  prof_3
0       ...     ...     ...
1       ...     ...     ...
...
</CRITIC_ONLY_PRIVILEGED_STATE>
```

Utilities are formatted to four decimal places. If no system message exists, a new critic-only system message is inserted. The implementation rejects missing/misaligned utility vectors and rejects a prompt that already contains the privileged-state marker.

In `actor_visible` mode, the critic prompt IDs are an exact copy of the actor prompt IDs. This makes the control condition byte-for-byte identical at the token level rather than merely semantically similar.

Both prompt variants use the same tokenizer, chat template, and maximum prompt length. A long privileged prompt can therefore cause the critic's older conversation history to be truncated sooner than the actor's; this is part of the current treatment and is tracked through prompt-length metrics.

### 3. Actor response tokens are held fixed between views

The actor samples a response from its ordinary prompt. The batching layer then constructs two inputs using the same sampled response tokens:

```text
actor messages ------------------> actor prompt -----> rollout / actor / reference
                                                              |
                                                              | exact sampled response tokens
                                                              v
environment utility matrix + actor messages -> critic prompt -> value critic
```

Concretely:

```text
actor_input_ids  = actor_prompt_ids  + sampled_actor_response_ids
critic_input_ids = critic_prompt_ids + sampled_actor_response_ids
```

The critic is therefore evaluating the action actually produced by the actor, not a separately generated privileged response.

### 4. Routing guards prevent actor leakage

The PPO trainer uses two explicit views:

- `as_critic_input(...)` remaps `prompts`, `input_ids`, `attention_mask`, and `position_ids` to the critic-only tensors. It is used only by `compute_values` and `update_critic`.
- `without_critic_inputs(...)` removes every `critic_*` tensor. It is used for actor old log-probabilities, reference log-probabilities, and actor updates.

Per-professor bootstrap value rows also build the correct current actor observation and corresponding critic prompt. Thus both real action rows and rollout-fragment bootstrap rows use the selected critic observation mode.

### 5. What did not change

The following are held constant between observation modes:

- Qwen critic architecture and value head;
- critic initialization/model path;
- critic optimizer, learning rate, minibatches, microbatches, and PPO epochs;
- actor and reference-policy inputs;
- rollout sampling and actor response tokens;
- environment rewards and terminal-utility routing;
- KL reward shaping;
- GAE and PPO loss definitions.

## Experimental design

The experiment is a 2 x 2 design:

| Actor schedule | Actor-visible critic | All-utilities critic | Purpose |
|---|---|---|---|
| Frozen for all 75 steps | `frozencritic` | `allutils-frozen` | Isolate critic representation and fitting |
| Warm up critic for 10 steps, then train actor | `base` | `allutils` | Test end-to-end PPO consequences |

The actor-update condition in the trainer is `critic_warmup < global_step`:

- `critic_warmup=75` with `total_training_steps=75` means the actor never updates.
- `critic_warmup=10` means critic-only updates through step 10 and actor updates from step 11 onward.

Every cell overrides `trainer.critic_warmup_batch_repeat_times=1` and `trainer.critic_warmup_batch_divide_ratio=1`. This is important because the canonical config currently defaults those values to `40` and `4`; the experiment intentionally does not use those larger warmup-batch transformations.

`critic_probe_mode=off` in every cell. These runs use real hiring utilities and are not the random `-1/+1` visible-versus-hidden critic sanity probe.

## Fixed training configuration

### Task environment

| Setting | Value |
|---|---|
| Environment | `async_ticker_admissions` |
| Professors | `prof_1`, `prof_2`, `prof_3` |
| Students per batch | 5 |
| Parallel environments | 32 |
| Shared token budget | 500 |
| Feature dimension | 5 |
| Vote threshold | 0.5 |
| Maximum environment steps | 50 |
| Terminate when everyone voted without consensus | `false` |
| Preference generation | `random_permutation` |
| Preference correlation threshold | 0.0 |
| Critic probe | `off` |

Relevant implicit environment defaults at commit `e9e6b5ac` are:

- `reward_mode=individual`: each professor receives its own utility for the selected student;
- `utility_mode=linear`;
- `show_ability_vectors=true`;
- `randomize_turn_order=false`;
- per-turn format and invalid-action penalties are both 0.1.

Every professor's own terminal utility is routed to that professor's GAE chain, including professors who did not cast the consensus-closing action.

No explicit hiring-environment seed is set. The cells therefore sample different stochastic episodes and are not paired episode-by-episode.

### Model and rollout

| Setting | Value |
|---|---|
| Actor, reference, and critic base model | `Qwen/Qwen3-4B` |
| Thinking mode | `false` |
| Rollout backend | asynchronous vLLM |
| Rollout samples per prompt | 1 |
| Tensor parallel size | 1 |
| vLLM GPU-memory utilization | 0.4 |
| Train batch size | 256 |
| Maximum actor/critic prompt length | 4096 tokens |
| Maximum response length | 512 tokens |

### PPO and critic optimization

| Setting | Value |
|---|---|
| Advantage estimator | GAE |
| Token discount / lambda | 1.0 / 1.0 |
| Step discount / lambda | 0.99 / 0.95 |
| KL shaping in reward | enabled |
| Fixed KL coefficient | 0.001 |
| Actor learning rate | `1e-6` |
| Actor PPO epochs | 2 |
| Actor minibatch / per-GPU microbatch | 256 / 4 |
| Actor entropy coefficient | 0.001 |
| Actor KL loss | disabled; KL is applied in reward |
| Critic learning rate | `1e-5` |
| Critic PPO epochs | 2 |
| Critic minibatch / per-GPU microbatch | 256 / 4 |
| Total training steps | 75 |
| Validation before training | disabled |
| Periodic validation | disabled (`test_freq=-1`) |
| Checkpoint saving | disabled (`save_freq=-1`) |

Because validation and checkpoint saving are disabled, these runs provide critic-learning curves and on-policy training outcomes, but not a held-out post-training actor evaluation.

## Run matrix and provenance

The pinned Rhea worktree is:

```text
/zfsauton/scratch/mwilinsk/unscripted/experiments/asymcritic-e9e6b5ac
```

The worktree was clean when recorded and pointed to:

```text
e9e6b5ac0e4b0b7ff599f0712360524adbbf2ed4
```

Rhea cells use the canonical `slurm/train_auton.sbatch` launcher with one node, four A6000 GPUs, 32 CPUs, 200 GiB RAM, `general/qos_general`, and a 47:59:00 limit.

| Cell | Platform/job | W&B run | Critic view | Warmup | Recorded state on 2026-07-29 |
|---|---|---|---|---:|---|
| Frozen control | Rhea `23238`, `gpu30` | [`unscripted_auton_frozencritic_23238`](https://wandb.ai/szopa-michala/unscripted/runs/zuz5ag7n) | `actor_visible` | 75 | running |
| PPO control | Rhea `23239`, `gpu25` | [`unscripted_auton_base_23239`](https://wandb.ai/szopa-michala/unscripted/runs/0geazph4) | `actor_visible` | 10 | running |
| Frozen treatment | DGX2 label `dgx2priv23240` | [`unscripted_auton_allutils-frozen_dgx2priv23240`](https://wandb.ai/szopa-michala/unscripted/runs/fvagz4xj) | `all_utilities` | 75 | running |
| PPO treatment | Rhea `23241` | W&B run created after job starts | `all_utilities` | 10 | pending for priority |

Exact Rhea submissions:

```bash
sbatch slurm/train_auton.sbatch \
  tag=frozencritic \
  critic_observation.mode=actor_visible \
  trainer.critic_warmup=75 \
  trainer.critic_warmup_batch_repeat_times=1 \
  trainer.critic_warmup_batch_divide_ratio=1

sbatch slurm/train_auton.sbatch \
  tag=base \
  critic_observation.mode=actor_visible \
  trainer.critic_warmup=10 \
  trainer.critic_warmup_batch_repeat_times=1 \
  trainer.critic_warmup_batch_divide_ratio=1

sbatch slurm/train_auton.sbatch \
  tag=allutils \
  critic_observation.mode=all_utilities \
  trainer.critic_warmup=10 \
  trainer.critic_warmup_batch_repeat_times=1 \
  trainer.critic_warmup_batch_divide_ratio=1
```

W&B recorded these exact Hydra treatment overrides for the DGX2 frozen cell:

```text
tag=allutils-frozen
critic_observation.mode=all_utilities
trainer.critic_warmup=75
trainer.critic_warmup_batch_repeat_times=1
trainer.critic_warmup_batch_divide_ratio=1
```

W&B reports four GPUs, CUDA 13.2, and the same shared run root for the DGX2 cell, but did not record Git metadata for that run. Its source commit therefore cannot be independently proven from W&B. The shared worktree was clean and pinned to `e9e6b5ac` when checked, but this is weaker provenance than the explicit Git commit recorded by both Rhea W&B runs.

The frozen comparison also spans Rhea and DGX2. Hardware/runtime differences should not create a directional information advantage, but they can affect optimization numerics, throughput, and stochastic reproducibility. A final claim should replicate both cells on matched hardware.

### PPO memory-fix reruns

The original PPO cells failed when actor updates began after critic warmup:

- `base` job `23239` completed step 12 and then raised CUDA OOM during `actor.update_policy -> loss.backward()` while trying to allocate 4.12 GiB with 3.90 GiB free.
- `allutils` job `23241` completed step 10 and then raised CUDA OOM during the same actor-backward operation while trying to allocate 4.51 GiB with 2.48 GiB free.

The critic-only cells were unaffected because they never execute actor backward. Both PPO cells were resubmitted from the same clean worktree and commit with one shared, treatment-neutral memory override:

```text
actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2
```

The actor PPO minibatch remains 256; the smaller per-GPU microbatch increases gradient accumulation and reduces activation-memory peaks.

| Replacement cell | Rhea job | Tag | State when submitted |
|---|---:|---|---|
| PPO control | `23359` | `base-mb2` | pending for priority |
| PPO treatment | `23360` | `allutils-mb2` | pending for priority |

Exact replacement submissions:

```bash
sbatch slurm/train_auton.sbatch \
  tag=base-mb2 \
  critic_observation.mode=actor_visible \
  trainer.critic_warmup=10 \
  trainer.critic_warmup_batch_repeat_times=1 \
  trainer.critic_warmup_batch_divide_ratio=1 \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2

sbatch slurm/train_auton.sbatch \
  tag=allutils-mb2 \
  critic_observation.mode=all_utilities \
  trainer.critic_warmup=10 \
  trainer.critic_warmup_batch_repeat_times=1 \
  trainer.critic_warmup_batch_divide_ratio=1 \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=2
```

## What is logged

### W&B configuration and provenance

Every W&B run stores the full resolved Hydra config and `config_provenance`, including:

- primary config name;
- exact `hydra_task_overrides`;
- the original config composed without task overrides;
- `resolved_changes`, mapping affected paths to original and overridden values.

Use W&B Run Comparer with **Diff only** and verify that treatment cells differ only in the intended observation mode and actor schedule.

### Primary critic metrics

| Metric | Interpretation | Expected treatment direction |
|---|---|---|
| `critic/v_s0_return_pearson` | Rank correlation between start value and trajectory return | higher |
| `critic/v_return_pearson` | Token-level value/return rank correlation | higher |
| `critic/vf_explained_var` | Scale-sensitive explained variance | higher |
| `critic/vf_loss` | Critic regression loss | lower |
| `critic/v_s0/mean`, `critic/v_s0/std` | Calibration/spread at trajectory start | diagnose collapse or drift |
| `critic/per_agent/prof_*/ev` | Per-professor explained variance | higher and balanced |
| `critic/per_agent/prof_*/critic_loss` | Per-professor squared prediction error | lower and balanced |
| `critic/values/*`, `critic/returns/*`, `critic/advantages/*` | Distribution and stability checks | finite, non-collapsed |

### Treatment-integrity metrics

| Metric | Expected control | Expected treatment |
|---|---:|---:|
| `critic_prompt_length/privileged_token_delta_mean` | 0 | positive |
| `critic_prompt_length/privileged_token_delta_max` | 0 | positive |
| `prompt_length/*` | actor prompt only | comparable across cells |
| `critic_prompt_length/*` | equal to actor prompt | longer unless truncation binds |

These metrics verify that the utility block reached the critic while leaving the actor prompt unchanged.

### Hiring outcome metrics

Primary end-to-end outcomes:

- `env/step/socially_optimal_rate`;
- `env_consensus/ratio` and `env/negotiation/consensus_reached`;
- `env/social_welfare/util_efficiency_normalized`;
- `env/social_welfare/utilitarian_gap`;
- `env/outcome/chosen_student_rank_global`;
- `env/outcome/pareto_dominated_choice`;
- `env/consensus_quality/mean_rank_efficiency`;
- `env/consensus_quality/min_rank_efficiency`;
- `env/consensus_quality/rank_dispersion`;
- per-professor `env/satisfaction/prof_*/normalized_regret` and `got_top_choice`.

`env/*` aggregates all episodes. `env_consensus/*` conditions on episodes that reached consensus, while `env_no_consensus/*` isolates failures. This prevents no-consensus episodes from silently distorting consensus-quality averages.

Behavioral diagnostics include:

- turns to first vote and consensus;
- communication count, length, and silent agents;
- vote changes, minority persistence, justification, and plurality adoption;
- leader/influence metrics;
- token-budget utilization and per-professor token use;
- action validity and malformed/invalid actions;
- Schelling/likability metrics.

Training-health metrics include actor entropy, KL reward penalty, actor and critic gradient norms, learning rates, response clipping/aborts, rollout-probability mismatch, throughput, memory/utilization telemetry, and `timing_s/*`.

### Row-level artifacts

Each job writes:

- `logs/critic_rows_<jobid>.jsonl`: global step, professor, environment/episode/turn identity, `value_s0`, `return_s0`, `advantage_s0`, reward, done/bootstrap status, response length, actor/critic prompt lengths, and critic observation mode;
- `logs/episode_log_<jobid>.jsonl`: complete episode state, turns, actions, utilities, professor rewards, consensus choice, social welfare, token accounting, and flattened metrics;
- `logs/agent_model_<jobid>.log`: model I/O summaries and step metrics;
- `logs/game_log_<jobid>.log`: human-readable sampled-game traces;
- `logs/auton_<jobid>.out` and `.err`: launcher, Ray, training progress, and failures for Rhea jobs.

For offline critic analysis, use `critic_rows` to separate professors and naturally completed rows, and explicitly inspect or exclude rows marked `is_bootstrap=true` depending on the analysis target.

`critic_probe/*` metrics are not success criteria for this experiment because `critic_probe_mode=off`.

## Planned analysis

### Frozen critic comparison

Compare `frozencritic` against `allutils-frozen` over all 75 steps:

1. Verify the prompt-length treatment first.
2. Plot `v_s0_return_pearson`, token-level Pearson, explained variance, and value loss.
3. Inspect per-professor fit to ensure the aggregate is not hiding one failed agent.
4. Compare learning-curve area and the mean over the final 10 steps rather than choosing a single favorable step.
5. Confirm there is no systematic hiring-outcome shift attributable to a frozen actor.

### End-to-end comparison

Compare `base` against `allutils`:

1. Treat steps 1-10 as critic warmup.
2. Evaluate actor and environment curves from step 11 onward.
3. Check that improved critic metrics precede, rather than merely accompany, outcome changes.
4. Compare consensus rate separately from quality conditional on consensus.
5. Track social welfare, per-professor regret, and Pareto domination so one aggregate reward cannot hide a decomposition failure.

## Limitations and requirements before a strong claim

1. **One stochastic run per cell.** No explicit environment seed is set, so current differences are descriptive rather than statistically reliable.
2. **Frozen pair is cross-platform.** Rhea versus DGX2 introduces runtime and numerical confounds.
3. **DGX2 Git provenance is incomplete.** W&B did not record its commit.
4. **No held-out evaluation.** Validation and checkpoint saving are disabled, so current runs do not directly measure the final actor on a fixed evaluation set.
5. **Prompt-length treatment includes truncation effects.** The privileged block can displace older critic history at the 4096-token limit; prompt-length and clipping metrics must be checked.

Before claiming that privileged critic state improves policy learning, repeat the four cells with explicit matched seeds, matched hardware/runtime, immutable commit provenance, checkpoint saving, and a fixed actor-only evaluation suite.

## Relevant implementation files

- `configs/train_auton.yaml`
- `configs/env/auton_admissions.yaml`
- `verl/envs/hiring_env_wrapper.py`
- `verl/experimental/agent_loop/tool_agent_loop.py`
- `verl/experimental/agent_loop/agent_loop.py`
- `verl/trainer/ppo/ray_trainer.py`
- `verl/trainer/ppo/metric_utils.py`
- `tests/experimental/test_asymmetric_critic_prompt.py`
- `tests/trainer/ppo/test_ray_trainer_tracking_on_cpu.py`
- `tests/trainer/ppo/test_metric_utils_on_cpu.py`
