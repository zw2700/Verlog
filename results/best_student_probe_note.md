# Best-Student Identification Probe

This note records a narrow diagnostic for whether a model acting as one professor
can identify the student it should vote for from its private utility table.

For the full write-up with setup, motivation, examples, success/failure modes,
and artifact locations, see
`results/best_student_identification_experiment_report.md`.

## Setup
- Date run: 2026-06-26
- Environment prompt source: `AsyncTickerAdmissionsEnv._build_chat_messages`
- Task: given the normal professor observation, return an env-style vote:
  `<THINK>short private reason</THINK><VOTE>N</VOTE>`
- Trials: 20 distinct resets, seeds 0-19
- Professors: `prof_1`, `prof_2`, `prof_3`, cycled by trial
- Env config: 5 students, 5-dimensional profiles, token budget 1000,
  vote threshold 0.5
- Experiment model in training scripts: `Qwen/Qwen2.5-3B-Instruct`
- OpenRouter model used: `qwen/qwen-2.5-7b-instruct`

OpenRouter did not expose the exact experiment model id
`Qwen/Qwen2.5-3B-Instruct`; it returned that the model id was invalid. The 7B
Qwen2.5 Instruct endpoint should therefore be read as a same-family proxy, not
as an exact measurement of the 3B checkpoint used in training.

## Results

Over the 20 env-style vote trials:

- Completed calls: 20/20
- Parseable `<VOTE>N</VOTE>` answers: 20/20
- Exact env top-1 accuracy: 18/20 = 0.90
- Displayed-table top accuracy: 20/20 = 1.00
- Average utility regret: 0.0000
- Maximum utility regret: 0.0000
- Trials with displayed utility ties: 4/20
- Trials with exact top-two gap <= 0.05: 4/20

The two exact-top-1 misses were zero-regret tie cases:

- Seed 0, `prof_1`: env exact gold index 3, model voted 4. The displayed table
  showed students 3 and 4 tied at utility 2.7.
- Seed 5, `prof_3`: env exact gold index 0, model voted 2. The displayed table
  showed students 0 and 2 tied at utility 3.0.

## Interpretation

For this Qwen2.5-7B-Instruct OpenRouter proxy, the diagnostic does not support a
basic table-reading failure hypothesis. When asked directly to act as a
professor and vote for its own highest-utility student, the model always selected
a visible-table top option and incurred zero utility regret across 20 trials.

This suggests that if trained rollouts select suboptimal students, the bottleneck
is more likely downstream of private best-student identification: negotiation
dynamics, deciding when to vote, compromise under social pressure, history
distraction, tie-breaking, credit assignment, or a gap between this 7B proxy and
the exact 3B checkpoint used in training.

## Exact 3B vLLM Follow-Up

On 2026-07-01, we repeated the probe on `auton-dgx2` with local vLLM serving the
exact experiment model:

- Model: `Qwen/Qwen2.5-3B-Instruct`
- Endpoint: local vLLM OpenAI-compatible server at `http://127.0.0.1:8000/v1`
- Prompt shape: the diagnostic instruction was appended to the env's existing
  user observation, preserving the normal one-system/one-user chat structure.
- Trials: 20 distinct resets, seeds 0-19
- Task: env-style vote action,
  `<THINK>short private reason</THINK><VOTE>N</VOTE>`

Corrected 3B vote-mode results:

- Completed calls: 20/20
- Parseable answers: 20/20
- Exact env top-1 accuracy: 14/20 = 0.70
- Displayed-table top accuracy: 16/20 = 0.80
- Average utility regret: 0.1050
- Maximum utility regret: 0.7000

The 6 exact-top-1 misses included 2 zero-regret tie cases and 4 real displayed
table-reading failures:

- Seed 0, `prof_1`: env exact gold index 3, model voted 4. Displayed tie,
  zero regret.
- Seed 5, `prof_3`: env exact gold index 0, model voted 2. Displayed tie,
  zero regret.
- Seed 11, `prof_3`: gold 1, model voted 4, regret 0.7000.
- Seed 12, `prof_1`: gold 3, model voted 4, regret 0.6000.
- Seed 14, `prof_3`: gold 0, model voted 4, regret 0.2000.
- Seed 15, `prof_1`: gold 0, model voted 4, regret 0.6000.

We also ran a JSON diagnostic with the same corrected prompt shape. It gave a
very similar picture:

- Exact env top-1 accuracy: 14/20 = 0.70
- Displayed-table top accuracy: 16/20 = 0.80
- Average utility regret: 0.1100
- Maximum utility regret: 0.7000

This updates the earlier interpretation: the 7B proxy can read the utility table
reliably, but the exact 3B model used in experiments does show a meaningful
private-best identification weakness. That means "can the professor identify
what it should vote for?" should remain an active bottleneck hypothesis for the
actual training model.

## Exact 3B 100-Trial Scale-Up

We scaled the exact 3B vLLM probe to 100 trials on 2026-07-01. Full details are
in `results/qwen25_3b_100trial_note.md`.

Vote-mode results, seeds 0-99:

- Exact env top-1 accuracy: 71/100 = 0.71
- Displayed-table top accuracy: 75/100 = 0.75
- Real displayed-table misses: 25/100
- Average utility regret: 0.1340
- Maximum utility regret: 1.6000

JSON/direct-answer results, seeds 0-99:

- Exact env top-1 accuracy: 68/100 = 0.68
- Displayed-table top accuracy: 71/100 = 0.71
- Real displayed-table misses: 29/100
- Average utility regret: 0.1410
- Maximum utility regret: 1.6000

The 100-trial scale-up strengthens the conclusion that the exact
`Qwen/Qwen2.5-3B-Instruct` training model has a genuine private-best
identification weakness on this prompt. This is not only an action-formatting
issue, because the direct-answer diagnostic is similarly weak.

## 7B vLLM 100-Trial Comparison

We also ran the same 100-trial vLLM setup for `Qwen/Qwen2.5-7B-Instruct` on
`auton-dgx2`. Full details are in `results/qwen25_7b_100trial_note.md`.

7B vote-mode results, seeds 0-99:

- Exact env top-1 accuracy: 90/100 = 0.90
- Displayed-table top accuracy: 92/100 = 0.92
- Real displayed-table misses: 8/100
- Average utility regret: 0.0210
- Maximum utility regret: 0.6000

7B JSON/direct-answer results, seeds 0-99:

- Exact env top-1 accuracy: 96/100 = 0.96
- Displayed-table top accuracy: 97/100 = 0.97
- Real displayed-table misses: 3/100
- Average utility regret: 0.0090
- Maximum utility regret: 0.6000

Same-host vLLM comparison:

| Model | Mode | Exact Top-1 | Displayed-Top | Avg Regret | Max Regret |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen2.5-3B-Instruct | vote | 71/100 | 75/100 | 0.1340 | 1.6000 |
| Qwen2.5-3B-Instruct | JSON/direct | 68/100 | 71/100 | 0.1410 | 1.6000 |
| Qwen2.5-7B-Instruct | vote | 90/100 | 92/100 | 0.0210 | 0.6000 |
| Qwen2.5-7B-Instruct | JSON/direct | 96/100 | 97/100 | 0.0090 | 0.6000 |

This suggests a strong model-size/capability effect. The exact 3B training model
has a clear private-best identification bottleneck. The 7B model mostly solves
that bottleneck, though it still makes occasional visible-table mistakes.

## Qwen3 And Qwen3.5 Follow-Up

On 2026-07-01, we added newer-generation controls. The closest dense Qwen3
sizes to the earlier 3B/7B question are `Qwen/Qwen3-4B` and `Qwen/Qwen3-8B`.
The corresponding Qwen3.5 sizes are `Qwen/Qwen3.5-4B` and `Qwen/Qwen3.5-9B`.

Qwen3 and Qwen3.5 required an isolated nightly vLLM venv because the existing
`vllm==0.10.0` stack does not support the new Qwen3.5 `qwen3_5` architecture.
The clean runs served without the Qwen reasoning parser and the probe passed
`chat_template_kwargs={"enable_thinking": false}` through `--disable-thinking`.
Without that flag, Qwen3/Qwen3.5 can spend the 128-token completion budget on a
thinking preamble rather than a parseable final answer.

Full setup, examples, raw-file locations, and vLLM log locations are in
`results/qwen_generation_comparison_note.md`.

Updated same-host comparison:

| Model | Mode | Exact Top-1 | Displayed-Top | Avg Regret | Max Regret |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen2.5-3B-Instruct | vote | 71/100 | 75/100 | 0.1340 | 1.6000 |
| Qwen2.5-3B-Instruct | JSON/direct | 68/100 | 71/100 | 0.1410 | 1.6000 |
| Qwen2.5-7B-Instruct | vote | 90/100 | 92/100 | 0.0210 | 0.6000 |
| Qwen2.5-7B-Instruct | JSON/direct | 96/100 | 97/100 | 0.0090 | 0.6000 |
| Qwen3-4B | vote | 78/100 | 81/100 | 0.0740 | 1.2000 |
| Qwen3-4B | JSON/direct | 80/100 | 83/100 | 0.0550 | 1.1000 |
| Qwen3-8B | vote | 85/100 | 87/100 | 0.0430 | 1.1000 |
| Qwen3-8B | JSON/direct | 81/100 | 84/100 | 0.0560 | 1.1000 |
| Qwen3.5-4B | vote | 94/100 | 96/100 | 0.0170 | 1.1000 |
| Qwen3.5-4B | JSON/direct | 94/100 | 96/100 | 0.0120 | 0.8000 |
| Qwen3.5-9B | vote | 93/100 | 94/100 | 0.0140 | 0.5000 |
| Qwen3.5-9B | JSON/direct | 96/100 | 97/100 | 0.0040 | 0.2000 |

The updated interpretation is sharper:

- The exact `Qwen/Qwen2.5-3B-Instruct` training model has a real private-best
  identification bottleneck.
- Scaling to Qwen2.5-7B helps a lot.
- Qwen3 improves over Qwen2.5-3B but does not solve the diagnostic; even
  Qwen3-8B remains behind Qwen2.5-7B in these runs.
- Qwen3.5 is strongest here. Qwen3.5-4B is already near the older 7B result,
  and Qwen3.5-9B JSON/direct has the lowest average and maximum regret in the
  comparison.

This supports the idea that a newer model generation can reduce the individual
private-utility identification bottleneck. It still does not prove that full
multi-agent collaboration improves; timing, speaking, consensus, and social
welfare need rollout-level metrics.

## Artifacts

- JSON diagnostic, seeds 0-9:
  `results/best_student_probe_qwen25_7b_openrouter.jsonl`
- Env-style vote diagnostic, seeds 0-9:
  `results/best_student_probe_qwen25_7b_vote_openrouter.jsonl`
- Env-style vote diagnostic, seeds 10-19:
  `results/best_student_probe_qwen25_7b_vote_openrouter_seed10_19.jsonl`
- Probe script:
  `scripts/openrouter_best_student_probe.py`
- Exact 3B vLLM vote diagnostic, seeds 0-19:
  `results/best_student_probe_qwen25_3b_vllm_vote_seed0_19_mergedprompt.jsonl`
- Exact 3B vLLM JSON diagnostic, seeds 0-19:
  `results/best_student_probe_qwen25_3b_vllm_json_seed0_19_mergedprompt.jsonl`
- Exact 3B vLLM vote diagnostic, seeds 0-99:
  `results/best_student_probe_qwen25_3b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Exact 3B vLLM JSON diagnostic, seeds 0-99:
  `results/best_student_probe_qwen25_3b_vllm_json_seed0_99_mergedprompt.jsonl`
- 100-trial summary note:
  `results/qwen25_3b_100trial_note.md`
- Exact 7B vLLM vote diagnostic, seeds 0-99:
  `results/best_student_probe_qwen25_7b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Exact 7B vLLM JSON diagnostic, seeds 0-99:
  `results/best_student_probe_qwen25_7b_vllm_json_seed0_99_mergedprompt.jsonl`
- 7B 100-trial summary note:
  `results/qwen25_7b_100trial_note.md`
- Qwen3.5-4B 100-trial summary note:
  `results/qwen35_4b_100trial_note.md`
- Qwen generation comparison note:
  `results/qwen_generation_comparison_note.md`
- Qwen3-4B vote diagnostic, seeds 0-99:
  `results/best_student_probe_qwen3_4b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Qwen3-4B JSON diagnostic, seeds 0-99:
  `results/best_student_probe_qwen3_4b_vllm_json_seed0_99_mergedprompt.jsonl`
- Qwen3-8B vote diagnostic, seeds 0-99:
  `results/best_student_probe_qwen3_8b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Qwen3-8B JSON diagnostic, seeds 0-99:
  `results/best_student_probe_qwen3_8b_vllm_json_seed0_99_mergedprompt.jsonl`
- Qwen3.5-4B vote diagnostic, seeds 0-99:
  `results/best_student_probe_qwen35_4b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Qwen3.5-4B JSON diagnostic, seeds 0-99:
  `results/best_student_probe_qwen35_4b_vllm_json_seed0_99_mergedprompt.jsonl`
- Qwen3.5-9B vote diagnostic, seeds 0-99:
  `results/best_student_probe_qwen35_9b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Qwen3.5-9B JSON diagnostic, seeds 0-99:
  `results/best_student_probe_qwen35_9b_vllm_json_seed0_99_mergedprompt.jsonl`
