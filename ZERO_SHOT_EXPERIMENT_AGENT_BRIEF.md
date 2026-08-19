# Agent brief: Qwen 3 4B zero-shot thinking × temperature experiment

## Objective

Implement a reproducible, inference-only experiment that tests whether the fixed
`Qwen/Qwen3-4B` policy can be induced to enter substantive negotiation rather
than collapsing to instant decisions.

The experiment is a 2×2 factorial comparison:

| Cell | Sampling temperature | Reasoning mode |
| --- | --- | --- |
| `baseline` | current baseline | current literal `<THINK>...</THINK>` protocol |
| `temperature` | higher | current literal `<THINK>...</THINK>` protocol |
| `native-thinking` | current baseline | Qwen-native thinking enabled through the vLLM/chat-template switch |
| `temperature-native-thinking` | higher | Qwen-native thinking enabled through the vLLM/chat-template switch |

This is a capability/elicitation diagnostic. Do not train, update weights,
introduce reward shaping, change the critic, or mix in replay-buffer work.

## Research context

The current project evidence is:

- Naive PPO improved Qwen 3 4B social optimality from about 43% to 56%, but
  training increased consensus largely by collapsing toward instant decisions.
- Frontier models produce more substantive discussions and can reach better
  compromises in difficult, conflicting-preference scenarios.
- Longer critic warmup improves explained variance but does not materially
  change the actor. Privileged critic information did not produce a
  statistically significant downstream improvement.
- Therefore, the immediate question is whether Qwen 3 4B already has a useful
  discussion strategy that the current decoding and prompting setup fails to
  elicit.

The follow-up meeting needs a decision-ready answer: do temperature and/or
native thinking elicit useful discussion, or should the team proceed to a
reward-shaped training experiment?

## Read before editing

Read `AGENTS.md` completely and follow it. Important repository facts:

- The task is `async_ticker_admissions`, backed by
  `AsyncTickerAdmissionsEnv`.
- The hiring environment is the `verl/envs/hiring_env` Git submodule. It is
  initialized in this worktree at the recorded commit. If it ever needs to be
  restored, run `git submodule update --init verl/envs/hiring_env`. Do not use a
  recursive update just for this task: the unrelated private `claude-tools`
  submodule is unavailable to the current account. Do not casually create an
  unpublished submodule commit. Prefer a parent-repository implementation
  unless a submodule change is genuinely required and can be delivered
  correctly.
- Existing local-model rollout entry points are
  `scripts/rollout_frontier.py` and `rollout_local_vllm_frank.sbatch`.
- `scripts/rollout_frontier.py` already supports `--temperature` and local vLLM.
  Its current local-vLLM path can disable Qwen thinking through
  `chat_template_kwargs={"enable_thinking": false}` via
  `LOCAL_VLLM_DISABLE_THINKING`, but this is implicit environment-variable
  behavior and is not sufficient provenance for this experiment.
- The default hiring prompt explicitly requests literal
  `<THINK>...</THINK>` text. Native-thinking cells must not accidentally test
  “native thinking plus an instruction to emit a second literal THINK block.”
- Existing process categorization is in
  `analysis/v1/compute_category_metrics.py`; the taxonomy is documented in
  `analysis/v1/category.md`.
- Existing preference-scenario analysis is in
  `analysis/v1.5/compute_preference_scenario_metrics.py`.
- Episode JSONL construction is centralized in
  `verl/envs/hiring_episode_logging.py`.

## Fixed experimental contract

### Model and weights

- Use exactly `Qwen/Qwen3-4B` for all four cells.
- Use the same checkpoint revision for all cells and record it when it can be
  resolved.
- Do not use Qwen 3.5, Qwen 2.5, a trained checkpoint, or different weights in
  any cell unless the user explicitly changes the experiment.

### Environment

Hold every environment value constant across cells. Start from the established
rollout defaults unless the existing baseline artifact proves a different
setting:

- 3 professors: `prof_1`, `prof_2`, `prof_3`
- 5 students
- token budget 500
- feature dimension 5
- vote threshold 0.5
- maximum 50 steps
- `terminate_on_all_voted_no_consensus=false`
- `professor_preference_mode=random_permutation`
- fixed turn order unless the baseline used random order

Use identical episode seeds in every cell. Paired seeds are essential: each
condition must see the same preference tables and student batches.

### Temperatures

- The current local rollout launcher defaults to `temperature=1.0`; confirm
  this against the baseline run configuration and treat the confirmed value as
  `base_temperature`.
- Make `high_temperature` an explicit, configurable run parameter. A value such
  as `1.3` is a reasonable first proposal above a confirmed 1.0 baseline, but it
  is not a scientific constant and must be visible in commands and metadata.
- Keep `top_p`, maximum output tokens, and every other sampling parameter fixed
  across all cells.

### Reasoning modes

Implement two explicit, auditable modes. Do not infer them from a missing
environment variable.

1. `manual-tags`
   - Pass `chat_template_kwargs.enable_thinking=false` to local vLLM.
   - Preserve the current environment instructions requiring literal
     `<THINK>...</THINK>` text before action tags.
   - This is the backward-compatible baseline.

2. `native-thinking`
   - Pass `chat_template_kwargs.enable_thinking=true` through the local vLLM
     OpenAI-compatible request.
   - Do not instruct the model to emit an additional literal
     `<THINK>...</THINK>` block. Adapt the rollout-visible system prompt and
     per-turn reminder so they request model-native private reasoning followed
     by the visible action grammar.
   - Preserve the visible action protocol exactly:
     `<GROUP>...</GROUP>`, `<VOTE>N</VOTE>`, `<WAIT>`, and
     `<WAIT_FOR>prof_name</WAIT_FOR>`.
   - Correctly handle whichever response representation the deployed vLLM
     version returns: thinking embedded in `message.content` with think tokens,
     or a separated `reasoning`/`reasoning_content` field plus visible content.
     Only visible action text should be sent to the environment when reasoning
     is separated, but raw reasoning metadata may be logged for diagnosis.
   - Verify with a smoke request that native thinking is genuinely enabled and
     that the model still emits a parseable visible action. Do not assume the
     request field worked merely because the server returned HTTP 200.

The mode adapter must be narrow and tested. It must not delete strategic game
instructions, change utilities, alter the voting rules, or reveal private
information.

### Output budget

Use the same `max_output_tokens` in all four cells. Native reasoning may consume
part of this budget. Before the full matrix, run a small smoke set and inspect
the valid-action/truncation rate. If native-thinking responses routinely exhaust
the budget before producing an action, increase the shared output limit and
rerun every cell with that same limit. Do not silently give only the native cells
more generation budget.

### Episode count

Make episode count configurable. Provide:

- a fast smoke mode (for example 2–5 paired seeds per cell);
- a pilot mode suitable for the next meeting;
- a documented larger run for a more credible comparison.

Do not claim statistical significance from a tiny pilot. The implementation
must make it easy to rerun with more paired seeds without changing code.

## Required implementation

### 1. Explicit rollout configuration

Extend the local-vLLM rollout path so the command line explicitly records:

- reasoning mode (`manual-tags` or `native-thinking`);
- temperature;
- model;
- seed base or explicit seed set;
- episode count;
- environment configuration;
- output paths;
- relevant vLLM/chat-template settings.

Backward compatibility matters: existing calls should retain current
manual-tag behavior unless the caller explicitly selects native thinking.

Avoid a hidden combination of `LOCAL_VLLM_DISABLE_THINKING`, absent variables,
and provider defaults. Environment variables may still feed the launcher, but
the resolved mode must be printed and written to metadata.

### 2. Reproducible four-cell launcher

Provide one documented command or small launcher that starts all four
independent cells with descriptive names. Suggested cell slugs:

- `qwen3-4b-zs-base-manual`
- `qwen3-4b-zs-high-temp-manual`
- `qwen3-4b-zs-base-native`
- `qwen3-4b-zs-high-temp-native`

Each cell must write to its own JSONL, game log, and metadata/report directory.
Never allow one cell to truncate or append to another cell's artifact.

Do not submit cluster jobs while implementing this task. Remote sync, package
installation, Slurm submission/cancellation, and monitor changes require user
approval under `AGENTS.md`. It is sufficient to implement and locally validate
the commands.

If you touch the existing rollout sbatch, remove assumptions that make it usable
only from another researcher's hard-coded checkout, but do not broaden this into
an unrelated cluster refactor. Do not create copied training launchers.

### 3. Run provenance

Write machine-readable metadata for every cell, preferably adjacent to the
episode JSONL. Include at least:

- branch and Git commit;
- model and resolved revision when available;
- reasoning mode and exact chat-template kwargs;
- temperature, top-p, max output tokens;
- episode seeds;
- complete environment config;
- start/end timestamps;
- vLLM version if available;
- artifact paths;
- completion/failure status.

Do not store credentials or large raw server objects by default.

### 4. Matrix analysis

Reuse, call, or narrowly extend the existing analysis rather than inventing a
conflicting definition.

For each cell, report overall and by preference scenario:

- episode count;
- `instant_decision`, `negotiation`, `stalled_coordination_failure`, and
  `malformed_or_other` counts/rates using the v1 repository taxonomy;
- consensus rate;
- social optimality rate;
- social optimality given consensus;
- average social-welfare efficiency;
- average total turns;
- average shared tokens used;
- invalid or unparseable action rate if available.

At minimum, separate:

- `all_three_share_top` (discussion often unnecessary), and
- `no_pair_shares_top` (the clearest difficult/conflicting scenario).

Produce both CSV/JSON and a compact Markdown comparison table. The main question
is not “which condition talks longest?” It is:

> In scenarios where preferences conflict, does the condition reduce instant
> decisions and improve welfare or social optimality without causing stalls,
> malformed actions, or empty verbosity?

### 5. Qualitative trace sample

Make it easy to select a small, paired trace set for the meeting:

- at least one conflicting-scenario success;
- one instant decision in a conflicting scenario;
- one long discussion that fails to improve welfare, if present;
- the same seed across two or more cells whenever possible.

Do not add large generated logs to Git.

## Tests and validation

Add targeted tests for the experiment-critical behavior:

- manual mode sends `enable_thinking=false`;
- native mode sends `enable_thinking=true`;
- native prompt adaptation removes instructions to emit literal THINK blocks
  while preserving all visible action tags and core game rules;
- manual prompt remains unchanged;
- separated reasoning fields do not replace or corrupt visible action content;
- all four cells generate distinct artifact paths and identical paired seeds;
- metadata contains the resolved experimental variables;
- analysis can consume a minimal fixture and produces the expected four-cell
  comparison fields.

Use the fake provider or mocked OpenAI-compatible responses for local tests; do
not require a GPU or external API. Run the relevant existing targeted tests from
`AGENTS.md` when the changed paths make them applicable. Run `ruff` on touched
Python files. Clearly report anything that could not be run locally.

## Expected agent deliverables

Before handing back the worktree, provide:

1. The implementation and targeted tests.
2. A short runbook with exact smoke, pilot, and full-matrix commands.
3. The resolved experiment defaults and every assumption that remains open.
4. A list of files changed and tests run.
5. No submitted jobs, remote writes, credentials, checkpoints, or committed
   rollout logs.

## Meeting decision rule

Interpret the experiment as follows:

- If temperature and/or native thinking increases useful negotiation and
  improves welfare in conflicting scenarios, use the best inference setup as
  the rollout configuration for the next training experiment.
- If discussion increases but welfare does not, do not treat it as success; the
  intervention is producing performative or ineffective dialogue.
- If native thinking produces malformed or truncated actions, fix the interface
  or shared output budget before drawing a capability conclusion.
- If none of the four cells produces useful discussion, proceed to the proposed
  outcome-aware reward-shaping experiment.
- If good zero-shot traces appear but subsequent training cannot retain them,
  the next bottleneck is learning/optimization rather than elicitation.

## Out of scope

Do not implement any of the following in this branch:

- reward-shaped training;
- privileged-critic changes;
- critic-warmup experiments;
- replay-buffer PPO fixes;
- SFT, GAIL, or IMLE;
- Qwen 2.5 or Qwen 3.5 comparisons;
- unrelated VERL refactors;
- changes to the scientific category definitions unless a demonstrated bug
  makes the current analysis unusable.
