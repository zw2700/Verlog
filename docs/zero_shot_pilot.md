# Rhea zero-shot protocol pilot

The code is prepared for one local GPU and Rhea's existing shared Verlog runtime:
Python 3.10.20, vLLM 0.10.0, PyTorch 2.7.1, and Transformers 4.55.4 (read-only
inspection on 2026-10-17). Qwen3-4B revision
`1cfa9a7208912126459214e8b04321603b3df60c` is already cached in
`/zfsauton/scratch/mwilinsk/.cache/huggingface`. GPU execution was subsequently
checked in the smoke test below; the larger pilot has not been launched.

## H200 smoke test: 2026-10-17

Job **87819**, `delib-smoke-h200`, completed on `gpu2` with exit code 0 in
**3m51s**, using commit `ae58ab5378a8bd166bfe4bc848292aade3298e4f` and hiring
submodule `aa7da2bc9947289eb2261fc3d0bf6f1875f4a631`. The request was one H200,
8 CPUs, 48G host RAM, 30 minutes, `project / qos_radio_freq`. Hydra overrides
were `num_episodes=1 tag=deliberation-smoke`: one matched scenario, three games.
All completed; scenario pairing was verified. No GPU out-of-memory error occurred.
The model used 7.5552 GiB; sampled device allocation reached 114493 MiB,
including the large KV cache reserved by the 0.8 memory setting. This sampled
value is not a measured instantaneous peak or the model's minimum requirement.

| Condition | Model calls | Malformed responses | Invalid actions | Agreement |
|---|---:|---:|---:|---|
| baseline | 6 | 0 | 0 | yes |
| deliberation | 63 | 46 | 53 | no |
| deliberation_no_communication | 63 | 53 | 59 | no |

Malformed and invalid counts overlap. The new protocol is **not yet ready for
an interpretable larger comparison**: the model frequently copied the literal
`<THINK>private reasoning</THINK>` template, put its actual reasoning outside
that block, and repeated old actions across phases. The strict parser rejects
these responses rather than risking publication of unmarked private reasoning.
The traces show a format-following problem; one scenario does not establish
mechanism performance. Clarifying the response interface and rechecking it is
the next step; do not relax privacy filtering or silently salvage malformed votes.

Remote artifacts are under
`/zfsauton/scratch/mwilinsk/unscripted/experiments/deliberation-voting-ae58ab53/logs/deliberation-smoke_87819/`.
Local copies, stdout/stderr, GPU samples, and submission details are in
`materials/experiment-results/2026-10-17/deliberation-voting/smoke-87819/`
under the surrounding project directory. Earlier attempts 87812 and 87813
exposed, respectively, the GPU-renumbering guard and CUDA/fork startup failures;
both launcher fixes are committed. No larger pilot was submitted.

## What runs

`configs/zero_shot_pilot.yaml` defines 20 scenarios per condition, batch size 16,
own continuous utility, temperature 0.7, top-p 1.0, and 512 output tokens per call.
It uses the initial Qwen3-4B checkpoint. Native Qwen thinking is disabled, matching
the existing template setting; the environment's explicit private THINK blocks
remain available in all phases. No PPO, replay, critic, or shaping is introduced.
The updated deliberation prompt uses shared fixed rules, the observing
professor's identity/private utility table, growing visible history, and current
turn metadata at the end. It explicitly describes how to enclose the professor's
own reasoning instead of showing a literal reasoning placeholder. The original
baseline prompt, strict parser, payoffs, and phase-transition rules are unchanged.
The 2026-10-17 smoke above predates this update; a new real-model check is required.
Each model request has a recorded seed derived from the scenario, professor,
phase, and that professor's opportunity count. Batch width and internal ballot
submission position do not reassign a professor's sampling seed.

The three conditions use identical candidate/utility scenarios at each seed:

1. `baseline`: Original asynchronous public voting and original prompt.
2. `deliberation`: Discussion, collective readiness, simultaneous sealed ballot.
3. `deliberation_no_communication`: Same new protocol, with GROUP delivery to
   other agents disabled. Senders retain their own messages and pay the same
   discussion-budget cost. The action interface, ballot, and deadlines remain.

The control truthfully tells agents that public delivery is disabled. Policies
can consequently change their behavior and duration. This tests communication
availability; it is not a claim of an observation-distribution-neutral ablation.
It blocks the GROUP content channel; public budget state and aggregate readiness
counts remain available, so it does not eliminate every possible signaling channel.
The original/new comparison covers the whole institution and its instructions,
including scheduling and complete ballot collection, not just a single rule.

## Local plan and CPU integration check

From a normal Verlog runtime at the repository root:

```bash
python -m scripts.zero_shot_pilot dry_run=true
python -m scripts.zero_shot_pilot backend=fake require_clean_git=false \
  num_episodes=3 output_dir=/tmp/deliberation-pilot-smoke-unique
```

Dry-run prints the resolved plan without creating an output directory or loading
vLLM. Fake mode exercises reset, actions, phases, pairing, privacy, and logging;
its manifest explicitly labels results as fake. It needs the ordinary environment
dependencies, not a GPU. The repo's minimal CPU tests bootstrap only environment
packages to avoid unrelated distributed-training imports.

`scripts/rollout_frontier.py` also accepts `--protocol deliberation_voting`,
`--max-discussion-rounds`, `--no-communication-enabled`, and all reward modes,
including both binary modes. It calls the same environment factory as training.
The batched pilot reuses its episode coroutine and logger rather than a copied
rollout implementation.

## Stage immutable sources after choosing the run

Use a detached, commit-pinned checkout under
`/zfsauton/scratch/$USER/unscripted/experiments/`. Fetching/creating that checkout
and initializing its pinned hiring submodule are deployment steps, not performed
by the launcher. Do not modify a checkout serving another job. Do not copy local
credentials into it. The pilot records source state and refuses a dirty real run.

The historical `/zfsauton/scratch/mwilinsk/unscripted/Verlog` directory currently
contains a stale `.git` pointer to a Mac worktree (checked 2026-10-17). Stage from
a valid Git repository or a fresh clone; do not reuse or repair that directory
in place. Source deployment has not been performed as part of preparation.

## Submit only after selecting resources

Use the existing canonical launcher. This is an **example**, not a submitted job:

```bash
export PROJECT_DIR=/zfsauton/scratch/$USER/unscripted/experiments/COMMIT_PINNED_CHECKOUT
export ENV_PATH=/zfsauton/scratch/cpulling/conda_envs/verlog
export HF_HOME=/zfsauton/scratch/$USER/.cache/huggingface
export VERLOG_JOB_MODE=zero_shot
cd "$PROJECT_DIR"
mkdir -p logs
sbatch --partition=general --qos=qos_general \
  --gres=gpu:a6000:1 --cpus-per-task=8 --mem=48G --time=02:00:00 \
  --job-name=delib-zero-shot --export=ALL slurm/train_auton.sbatch \
  num_episodes=20 tag=deliberation-zero-shot
```

The two-hour limit is an initial cap, not a measured runtime estimate. First use
the 20-per-condition smoke pilot to measure throughput and inspect transcripts.
For the larger paired pilot change `num_episodes=100`. A single Qwen3-4B inference
worker is the starting request; there are no actor/critic/reference training
replicas. If selecting more GPUs, the model tensor parallel size follows the
Slurm-exposed GPU count unless explicitly overridden.

For H200, choose the currently eligible partition/QOS and replace the GPU type
with `h200:1`; do not assume the general partition includes H200. Query Slurm
before deciding. Do not pin a node merely because it looked free earlier.
On 2026-10-17, `project` allows `qos_radio_freq` (available to Michal's account)
and `qos_project_preempt`. The debug partition's current maximum is one hour.

The launcher preserves `CUDA_VISIBLE_DEVICES`, resolves allocated GPU UUIDs in
the NVML view (including Slurm's cgroup device renumbering), and checks compute
processes only on those UUIDs. A failed query aborts explicitly. It never stops
global Ray/process state. In
zero-shot mode no dataset or W&B login is required, and no PPO workers start.
Real model execution also refuses to start without a Slurm GPU allocation;
use `dry_run=true` for planning on the login node.
`VERLOG_JOB_MODE` defaults to `train`, preserving the original training entrypoint.
Zero-shot mode defaults `VLLM_WORKER_MULTIPROC_METHOD=spawn`: VERL/runtime imports
can touch CUDA before engine startup, making vLLM's default fork unsafe. Smoke
job 87813 exposed this before model loading. Cold imports from the shared runtime
also took several minutes on `gpu2`; include startup in timing estimates.

## Evidence and inspection

Each run gets a new `logs/<tag>_<jobid>/` directory containing:

- `manifest.json`: resolved settings, condition configs, code/submodule hashes,
  runtime versions, node/job identity, fake/real marker, status, and elapsed time.
- `results.jsonl`: one small result per condition and scenario seed, including
  scenario hash, welfare, agreement, calls, actual public messages, errors, and
  participation. Identical scenario hashes across conditions are mandatory.
- `<condition>/episodes/episodes.worker00.jsonl`: complete game/actor-context
  records using the training-compatible schema plus rollout seed/provenance.
- `<condition>/game.log`: readable dynamic actor contexts and outputs.
- `summary.json`: condition-level descriptive metrics and paired welfare
  differences against the baseline. These are pilot summaries, not significance
  claims or a multi-seed training replication.

Existing output directories are never overwritten. Completed games are written
immediately; failures preserve evidence and mark the manifest as failed. Partial
runs are not silently resumed or mixed with new settings. All private thoughts
and ballots remain available in privileged research logs, never in another
professor's actor prompt. Bootstrap and zero-shot observations use the same filter.

Prefix caching is enabled explicitly. When vLLM reports `num_cached_tokens`, each
turn records `cached_prompt_tokens`, and game/condition summaries report cached
input tokens and the hit fraction over input tokens with reported cache data.
Missing reports remain unavailable, not zero hits. The manifest's `inference`
section records batch count, request count, and total wall time inside `LLM.chat`.
That batch wall time includes prefill and decoding; it is not first-token latency
or an isolated decoding-throughput measurement. These metrics allow cache reuse
to be measured without claiming an unmeasured speedup. Changing metadata at the
end preserves the earlier prefix; the replaced suffix, re-rendered outputs,
trimming, and cache eviction can still require recomputation.

Inspect invalid-action counts and traces before interpreting outcomes. Report
GROUP messages and speaking professors separately from readiness/ballot calls;
the new protocol grants everyone a vote by construction. A fake completion test
cannot establish real-model instruction following, GPU memory needs, or speed.

## Checks

```bash
python -m pytest -q tests/envs/test_zero_shot_pilot.py \
  tests/envs/test_hiring_deliberation.py tests/envs/test_hiring_reward_comparison.py \
  tests/envs/test_hiring_env_wrapper_critic_probe.py tests/envs/test_hiring_episode_logging.py \
  tests/experimental/test_completed_episode_metric_lifecycle.py
bash -n slurm/train_auton.sbatch slurm/common.sh
```

The known existing baseline communication-process export failure remains
documented in `docs/deliberation_voting_protocol.md`; the pilot summarizes game
outcomes and public-message counts from the working episode-level metrics.
