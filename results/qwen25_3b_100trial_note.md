# Qwen2.5-3B Best-Student Probe: 100-Trial Scale-Up

This note records the scaled-up diagnostic for the exact training-family model,
`Qwen/Qwen2.5-3B-Instruct`, served locally with vLLM on `auton-dgx2`.

## Setup

- Date run: 2026-07-01
- Host: `auton-dgx2`
- Serving stack: local vLLM OpenAI-compatible endpoint
- Model: `Qwen/Qwen2.5-3B-Instruct`
- Endpoint during run: `http://127.0.0.1:8000/v1`
- Environment prompt source: `AsyncTickerAdmissionsEnv._build_chat_messages`
- Prompt shape: one system message plus one user observation; the diagnostic
  instruction was appended to the env's existing user message.
- Trials: 100 distinct resets, seeds 0-99
- Professors: `prof_1`, `prof_2`, `prof_3`, cycled by trial
- Env config: 5 students, 5-dimensional profiles, token budget 1000,
  vote threshold 0.5

Two variants were run:

- Vote mode: ask the model to return
  `<THINK>short private reason</THINK><VOTE>N</VOTE>`.
- JSON/direct-answer mode: ask the model to identify the highest-utility
  student directly. The model often still returned env-style actions, but the
  parser extracted the selected student when possible.

## Results

### Vote Mode

- Completed calls: 100/100
- Parseable answers: 100/100
- Exact env top-1 accuracy: 71/100 = 0.71
- Displayed-table top accuracy: 75/100 = 0.75
- Exact misses: 29/100
- Real displayed-table misses: 25/100
- Displayed utility tie trials: 11/100
- Average utility regret: 0.1340
- Maximum utility regret: 1.6000

Top regret cases:

- Seed 90, `prof_1`: gold 0, predicted 4, regret 1.6000.
- Seed 97, `prof_2`: gold 0, predicted 4, regret 1.4000.
- Seed 79, `prof_2`: gold 0, predicted 2, regret 1.2000.
- Seed 82, `prof_2`: gold 0, predicted 3, regret 1.1000.

### JSON / Direct-Answer Mode

- Completed calls: 100/100
- Parseable answers: 100/100
- Exact env top-1 accuracy: 68/100 = 0.68
- Displayed-table top accuracy: 71/100 = 0.71
- Exact misses: 32/100
- Real displayed-table misses: 29/100
- Displayed utility tie trials: 11/100
- Average utility regret: 0.1410
- Maximum utility regret: 1.6000

Top regret cases:

- Seed 82, `prof_2`: gold 0, predicted 2, regret 1.6000.
- Seed 90, `prof_1`: gold 0, predicted 4, regret 1.6000.
- Seed 97, `prof_2`: gold 0, predicted 4, regret 1.4000.
- Seed 58, `prof_2`: gold 1, predicted 0, regret 1.2000.

## Interpretation

The 100-trial scale-up strengthens the conclusion from the 20-trial run: the
exact Qwen2.5-3B model has a real private-best identification weakness in this
environment prompt.

This is not just an env action-formatting problem. Vote mode and direct-answer
mode are both poor, and direct-answer mode is slightly worse. The model often
states that a lower-utility student has the highest utility, then votes for or
returns that student. These are table-reading or attention failures over the
visible utility column, not merely tie-breaking artifacts.

The 7B OpenRouter proxy previously looked reliable on the same basic diagnostic
(20/20 displayed-table top accuracy, zero regret), so the failure appears
model-size/model-capability dependent. For experiments using
`Qwen/Qwen2.5-3B-Instruct`, private-best identification should remain a primary
bottleneck hypothesis alongside coordination, timing, communication, and credit
assignment.

## Research Consequence

Before interpreting full rollout failures as failures of collaboration, we
should separately measure whether each professor can identify its own best
student at every decision point. Otherwise, downstream metrics such as consensus
quality, selected rank, and social welfare may be confounded by a simpler
individual perception/reading failure.

Recommended next metrics:

- Private-best recovery per professor per turn.
- Tie-aware private-best recovery.
- Utility regret of each vote relative to that professor's private best.
- Social-optimal recovery per step.
- Selected social-welfare rank over time.
- Whether conversation history makes private-best identification better or
  worse.

## Artifacts

- Vote-mode 100-trial results:
  `results/best_student_probe_qwen25_3b_vllm_vote_seed0_99_mergedprompt.jsonl`
- JSON/direct-answer 100-trial results:
  `results/best_student_probe_qwen25_3b_vllm_json_seed0_99_mergedprompt.jsonl`
- Probe script:
  `scripts/openrouter_best_student_probe.py`
