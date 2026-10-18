# Deliberation and voting protocol

This opt-in protocol is implemented in `verl/envs/hiring_deliberation.py` in the
parent repository. The hiring-environment submodule remains pinned and untouched.
The original asynchronous public-vote protocol remains the default baseline.

## Select the protocol

Use the existing Hydra configuration and canonical Slurm launcher:

```bash
sbatch slurm/train_auton.sbatch \
  env@envs=deliberation_voting \
  +experiment=reward_comparison \
  envs.env_config.reward_mode=individual \
  tag=deliberation-voting-own-numerical
```

This is a reproducible launch example, not a submitted job. The environment
factory still uses `envs.env_name=async_ticker_admissions`; the actual protocol
is recorded in `envs.env_config.protocol` and episode logs.

The default `env@envs=auton_admissions` / `protocol=async_ticker` retains the old
behavior. Reward comparison's existing numerical and binary modes still work
with either protocol. The new prompt describes the actual payoff of the selected
condition, including shared rewards; it does not ask agents to cooperate.

## State machine

1. **Discussion:** Three professors, five candidates, and the existing private
   utility/public candidate structure. Each professor gets one opportunity to
   send `<GROUP>message</GROUP>` or `<PASS>`. The initial order is shuffled using
   an independent scheduling RNG; the first speaker rotates between rounds.
   Candidate ballots and readiness signals are invalid during this phase.
2. **Readiness:** After a complete round, all professors independently submit
   `<READY_TO_VOTE>` or `<CONTINUE_DISCUSSION>` against the same completed public
   transcript. Submissions remain private. Only after all respond is the ready
   count announced. By default, all but one must be ready (two of three). Signals
   are fresh at every check. Being ready does not commit a candidate choice.
3. **Deadlines:** Only GROUP content consumes the 500-token discussion budget.
   Exhausting it immediately opens the ballot, even mid-round. An oversized
   message is rejected as an invalid pass and does not overspend the budget.
   Discussion also ends after the readiness check of round 10, regardless of
   readiness. No speech is mandatory. These are initial configurable budgets,
   not optimized mechanism parameters.
4. **Ballot:** Each professor gets exactly one `<VOTE>N</VOTE>` opportunity. All
   submissions are collected before resolution, even when two already match.
   Ballots are sealed by default and never appear in another actor's observation,
   including after the election. Only the winner/no-agreement and aggregate tally
   are announced. Invalid or missing ballots count as abstentions.
5. **Outcome:** A strict majority is required (two of three at the default
   threshold). A three-way split or insufficient valid support ends with no
   agreement and zero terminal selection reward. There is no runoff or return
   to discussion. Existing per-action error penalties remain separate from
   terminal utility and trainer KL regularization.

For larger groups, readiness defaults to N−1. The decision quorum is the greater
of a strict majority and `ceil(vote_threshold * N)`, so there cannot be two
simultaneous winners. `deliberation.readiness_quorum` can override closure.

Every response starts with `<THINK>private reasoning</THINK>` followed by exactly
one phase-appropriate action. THINK is retained privately across all phases and
does not spend the public-message budget. Normal model generation and context
limits still apply. Malformed/unclosed THINK output fails closed: it is never
treated as a public fallback message. Invalid discussion actions become passes,
invalid readiness means continue, and every invalid response consumes a slot.

With three professors and 10 rounds, an episode takes at most **63 model calls**:
30 discussion opportunities, 30 readiness submissions, and three ballots. The
new preset sets legacy `max_steps=null`; that asynchronous cap must not prevent
the reserved readiness/ballot opportunities. The protocol's own limits are finite.

## Actor visibility and research metadata

Each actor prompt contains only its own utility table, public candidate data
(unless hidden by the existing information ablation), public GROUP messages,
announced readiness counts, phase/budget state, and that actor's private THINK
and action history. Histories are filtered by ownership **before** context
trimming. Pending choices and other professors' private entries cannot change
another professor's prompt. There is no `CURRENT VOTES` table in sealed mode.

The shared transcript is identical across readiness/ballot participants; private
thoughts, private past actions, and private utility tables differ by owner.
Aggregate announced results can logically reveal information about votes; ballot
secrecy means direct submissions are hidden, not that all inference is impossible.

As in the baseline, Gym `info`/`episode_state` are **privileged research metadata**
for the trainer/logger, not agent observations. Logs deliberately retain all
private thoughts and ballots for audit. Do not concatenate these objects into
actor prompts. The wrapper's `get_observation_for_agent` is also used for
per-professor bootstrap rows and obeys the same visibility filter. A privileged
critic may still receive utility tables via the existing explicit critic mode;
this never changes actor-visible inputs.

## Metrics and controls

Episode JSONL records identify the protocol; each turn identifies its phase and
summarizes readiness/PASS actions. The `deliberation/*` metrics separately count
discussion turns, readiness turns, ballots, checks, abstentions, and closure
reasons. Raw turn counts include control calls, so use public GROUP-message
counts and discussion turns when comparing deliberation effort with the baseline.
Welfare still uses actual utilities for all reward conditions. Consensus timing
uses the final collected ballot. Sequential vote-following/plurality-persistence
metrics are marked inapplicable for sealed ballots instead of being presented as
evidence of herding.

`envs.env_config.deliberation.ballot_visibility=public` is a separate ablation.
It reveals submitted ballots but preserves thought privacy and complete ballot
collection. Phase separation and ballot secrecy should be compared separately.

## Verification

```bash
python -m pytest -q tests/envs/test_hiring_deliberation.py \
  tests/envs/test_hiring_reward_comparison.py \
  tests/envs/test_hiring_env_wrapper_critic_probe.py \
  tests/envs/test_hiring_episode_logging.py \
  tests/experimental/test_completed_episode_metric_lifecycle.py
```

The tests drive real reset/step/wrapper observation paths, including cached and
per-professor observations, in all phases. Counterfactual tests change one
professor's thoughts or pending choice while holding public actions fixed and
assert that other professors' prompts are byte-identical. They also cover
malformed reasoning, split votes, abstentions, deadlines, reward variants,
context trimming, reset isolation, Hydra composition, and the original baseline.

Broader baseline check: the existing
`tests/envs/test_hiring_env_metrics.py::test_communication_process_metrics_from_group_messages`
fails because the pinned submodule returns from `_flatten_metrics_for_logging`
before its communication-process flattening block. The identical failure is
reproducible in the untouched `michal/reward-comparison` worktree. This protocol
change deliberately does not modify that submodule or repair baseline metrics.

The institutional distinction is motivated by Anesi and Safronov (2023),
[Deciding When to Decide: Collective Deliberation and Obstruction](https://doi.org/10.1111/iere.12614).
Our thresholds, budgets, and natural-language action space are experimental
choices, not claims that this paper proves the protocol improves hiring welfare.
