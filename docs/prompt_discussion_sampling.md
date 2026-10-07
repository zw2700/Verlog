# Initial-checkpoint discussion prompt comparison

Requested September 16, 2026. Inference only; do not start training as part of this experiment.

Job 55148, named exactly `experiment`, uses one H200 and 64 GB host RAM on
Rhea's `project` partition. Both existing jobs on gpu2 were still running after
this job started. The launcher is the existing `rollout_local_vllm_frank.sbatch`,
with `PROMPT_COMPARISON=1` selecting `scripts.rollout_prompt_comparison`.
Normal inference and training entrypoints are unchanged.

Model: Qwen/Qwen3-4B, revision `1cfa9a7208912126459214e8b04321603b3df60c`.
Both prompts use the same initial weights, manual THINK tags (native thinking
disabled), temperature 1.0, top-p 1.0, 512 output tokens, and 8192 model context.
The environment uses 3 professors, 5 students, 500 shared message tokens,
50% consensus, 50 turns, random-permutation preferences, fixed initial turn
order, and no termination merely because all professors voted differently.
Full environment configs and exact prompts are saved with the results.

Compare 1000 episode seeds (0–999) per condition. Each pair receives the same
scenario seed and vLLM request seed. Eight isolated worker processes avoid
concurrent resets interfering with process-global environment random state.
Condition order alternates with seed parity. This controls scenarios and
sampling settings; it does not promise identical token draws across different
prompts or GPU batch schedules.

The baseline prompt is unchanged. The discussion prompt replaces the sentence
encouraging immediate voting when decided and appends DISCUSSION_GUIDANCE from
the runner. It asks for a preferred candidate, an acceptable alternative,
qualitative preference strength, a colleague's response before voting, and
reconsideration when the response changes the feasible agreement. It preserves
the personal-utility objective, exact-utility nondisclosure rule, reward,
action space, environment dynamics, and token budget. No discussion behavior
is enforced by the environment.

Remote checkout:
`/zfsauton/scratch/mwilinsk/unscripted/experiments/zero-shot-thinking-e888c0e2`

Run artifacts relative to that checkout:
`artifacts/prompt-comparison-20260916/prompt-comparison/`

Each condition has exact prompts, raw per-episode logs, combined episode JSONL,
the existing preference-scenario metrics and SVG plot. `summary.json` compares
consensus, social optimality, messages, message tokens, turns, vote revisions,
and output truncation. Final analysis asserts identical student batches and
professor preferences for every matched pair.

Validation: four paired fake-model CPU episodes passed, including scenario
pairing, logging, and both SVG plots. Fake-model outputs are infrastructure
checks only and must never be included in the scientific results.

Interpretation: the treatment is a bundle of prompt instructions. A larger
negotiation category alone does not establish useful communication; inspect
decision quality and representative transcripts. Keep these prompts fixed
for any later before/after-training comparison.

## Unanimity comparison

Job **55149**, also named `experiment`, repeats the paired comparison with
`VOTE_THRESHOLD=1.0` (three of three professors must agree). It uses the same
model revision, prompt strategy, seeds 0–999, and inference/environment
settings. No training is performed. It requests one A6000, 16 CPUs, 64 GB RAM,
and six hours in `general`, excluding gpu27/gpu30/gpu31 because those nodes
also host the preemptible queue. GPU cache allocation is 0.85 on the A6000
instead of 0.4 on the H200; GPU hardware differs between threshold experiments.

Remote artifacts: `artifacts/prompt-unanimity-20260916/` (includes exact
`submission.json`); results and plots under its `prompt-comparison/` directory.
Two fake-model paired episodes verified that both prompts say 100% agreement,
consensus takes three votes, scenario pairing matches, and both plots generate.
