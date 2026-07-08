# Qwen Generation Comparison: Best-Student Probe

This note records the same 100-trial private-best-student diagnostic across
Qwen2.5, Qwen3, and Qwen3.5 models. It is meant to answer the question:

> Does simply moving to a newer Qwen generation or larger nearby checkpoint make
> the professor better at identifying its own highest-utility student?

## Why This Matters

Full Verlog rollouts mix several abilities: reading the private utility table,
knowing when to speak, deciding what to reveal, waiting, voting, and aggregating
private preferences into a socially good consensus. This diagnostic isolates the
first ability.

If a model cannot reliably identify its own best student from the prompt, then
bad consensus in full rollouts is not yet clean evidence of a collaboration or
credit-assignment failure. It may be a simpler individual competence bottleneck.

## Model Choices

For the original training-model comparison we used:

- `Qwen/Qwen2.5-3B-Instruct`
- `Qwen/Qwen2.5-7B-Instruct`

For the newer-generation controls we used the nearest available dense sizes:

- `Qwen/Qwen3-4B`
- `Qwen/Qwen3-8B`
- `Qwen/Qwen3.5-4B`
- `Qwen/Qwen3.5-9B`

The Qwen model cards list Qwen3-4B at 4.0B parameters, Qwen3-8B at 8.2B
parameters, Qwen3.5-4B at 4B language-model parameters, and Qwen3.5-9B at 9B
language-model parameters:

- <https://huggingface.co/Qwen/Qwen3-4B>
- <https://huggingface.co/Qwen/Qwen3-8B>
- <https://huggingface.co/Qwen/Qwen3.5-4B>
- <https://huggingface.co/Qwen/Qwen3.5-9B>

## Probe Setup

- Date run: 2026-07-01
- Host: `auton-dgx2`
- Endpoint during runs: `http://127.0.0.1:8000/v1`
- Prompt source: `AsyncTickerAdmissionsEnv._build_chat_messages`
- Prompt shape: one system message plus one user observation; the diagnostic
  instruction was appended to the env's existing user message.
- Trials: 100 resets, seeds 0-99
- Professors: `prof_1`, `prof_2`, `prof_3`, cycled by trial index
- Env config: 5 students, 5-dimensional profiles, token budget 1000,
  vote threshold 0.5
- Decoding: `temperature=0`, `max_tokens=128`
- Metrics: exact top-1, displayed-table top, real displayed-table misses,
  average utility regret, maximum utility regret

Two modes were run for each model:

- Vote mode: model returns `<THINK>short private reason</THINK><VOTE>N</VOTE>`.
- JSON/direct mode: model returns a direct student index in JSON.

The parser accepts JSON, `<VOTE>N</VOTE>`, `Student N`, or a single unambiguous
integer. Thus JSON/direct should be read as direct-answer mode, not strict JSON
format compliance.

## Serving Setup

Qwen2.5 runs used the repo's existing local vLLM setup.

Qwen3 and Qwen3.5 runs used an isolated nightly vLLM environment at
`/home/mwilinsk/qwen35-vllm-venv`, because the original repo stack
(`vllm==0.10.0`, `transformers==4.55.4`) did not support Qwen3.5's `qwen3_5`
architecture. The working nightly stack was:

- vLLM: `0.23.1rc1.dev693+g5c4db60f0`
- `--enforce-eager`
- Qwen3.5 also used `--language-model-only`
- `LD_LIBRARY_PATH` included the venv CUDA runtime directories
- `PATH` included the venv `bin` directory so FlashInfer JIT could find `ninja`

The probe used `--disable-thinking`, which sends
`chat_template_kwargs={"enable_thinking": false}`. This mattered because Qwen3
and Qwen3.5 are thinking-mode models by default, and earlier Qwen3.5 attempts
spent the 128-token answer budget on reasoning instead of emitting a parseable
final answer.

We did not serve with a Qwen reasoning parser in the valid runs. An earlier
Qwen3.5 attempt with `--reasoning-parser qwen3` returned generated text under
`message.reasoning` with `message.content = null`, which made the probe parser
see answers as unparseable.

## Results

| Model | Mode | Exact Top-1 | Displayed-Top | Real Displayed Misses | Avg Regret | Max Regret |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-3B-Instruct | vote | 71/100 | 75/100 | 25/100 | 0.1340 | 1.6000 |
| Qwen2.5-3B-Instruct | JSON/direct | 68/100 | 71/100 | 29/100 | 0.1410 | 1.6000 |
| Qwen2.5-7B-Instruct | vote | 90/100 | 92/100 | 8/100 | 0.0210 | 0.6000 |
| Qwen2.5-7B-Instruct | JSON/direct | 96/100 | 97/100 | 3/100 | 0.0090 | 0.6000 |
| Qwen3-4B | vote | 78/100 | 81/100 | 19/100 | 0.0740 | 1.2000 |
| Qwen3-4B | JSON/direct | 80/100 | 83/100 | 17/100 | 0.0550 | 1.1000 |
| Qwen3-8B | vote | 85/100 | 87/100 | 13/100 | 0.0430 | 1.1000 |
| Qwen3-8B | JSON/direct | 81/100 | 84/100 | 16/100 | 0.0560 | 1.1000 |
| Qwen3.5-4B | vote | 94/100 | 96/100 | 4/100 | 0.0170 | 1.1000 |
| Qwen3.5-4B | JSON/direct | 94/100 | 96/100 | 4/100 | 0.0120 | 0.8000 |
| Qwen3.5-9B | vote | 93/100 | 94/100 | 6/100 | 0.0140 | 0.5000 |
| Qwen3.5-9B | JSON/direct | 96/100 | 97/100 | 3/100 | 0.0040 | 0.2000 |

## Interpretation

The exact Qwen2.5-3B training model has a real private-best identification
bottleneck. It misses visible-table top students in roughly a quarter of trials.

Scaling within Qwen2.5 helps a lot. Qwen2.5-7B reaches 90/100 exact in vote mode
and 96/100 exact in direct-answer mode.

Qwen3 does not monotonically solve this diagnostic. Qwen3-4B improves over
Qwen2.5-3B but is still far from Qwen2.5-7B and Qwen3.5-4B. Qwen3-8B is better
than Qwen3-4B, but still below Qwen2.5-7B in both modes here.

Qwen3.5 is the strongest family in this comparison. Qwen3.5-4B already matches
or beats the older Qwen2.5-7B vote result, and Qwen3.5-9B JSON/direct matches
Qwen2.5-7B JSON/direct exact accuracy while cutting average regret from 0.0090
to 0.0040 and max regret from 0.6000 to 0.2000.

The main caveat is that this is a narrow single-agent table-reading diagnostic.
It does not prove that full multi-agent collaboration improves. It says the
individual identification bottleneck is much smaller for Qwen2.5-7B and Qwen3.5
than for the exact Qwen2.5-3B training model.

## Success And Failure Modes

### Clean Success

Qwen3.5-9B JSON/direct, seed 61, `prof_2`:

- Displayed utilities: `[2.1, 2.4, 2.3, 2.7, 2.1]`
- Gold student: 3
- Predicted student: 3
- Regret: 0.0

Model response:

```text
{"student_index": 3, "reason": "Student 3 has the highest utility score of 2.7 among all candidates."}
```

### Same Seed, Vote-Mode Failure

Qwen3.5-9B vote, seed 61, `prof_2`:

- Displayed utilities: `[2.1, 2.4, 2.3, 2.7, 2.1]`
- Gold student: 3
- Predicted student: 1
- Regret: 0.3

Model response:

```text
<THINK>Student 1 has the highest utility score of 2.4, so I will vote for them immediately.</THINK><VOTE>1</VOTE>
```

This shows that even a strong model can make a shallow max-selection error in
the rollout-style answer format.

### High-Regret Qwen3-4B Failure

Qwen3-4B vote, seed 0, `prof_1`:

- Displayed utilities: `[1.0, 1.3, 1.5, 2.7, 2.7]`
- Visible top students: 3 and 4
- Predicted student: 2
- Regret: 1.2

Model response:

```text
<THINK>Student 2 has the highest utility score of 1.5, so I will vote for them.</THINK><VOTE>2</VOTE>
```

This is not a tie-breaking issue. The model calls a visibly non-top value the
highest value.

### Scale Helps But Does Not Fully Solve Qwen3

Qwen3-8B vote, seed 57, `prof_1`:

- Displayed utilities: `[2.3, 1.6, 2.4, 2.8, 1.4]`
- Gold student: 3
- Predicted student: 2
- Regret: 0.4

Model response:

```text
<THINK>Student 2 has the highest utility score of 2.4, making them the best choice based on my private preferences.</THINK><VOTE>2</VOTE>
```

Qwen3-8B is much better than Qwen3-4B on aggregate, but this failure mode
persists.

### Qwen3.5 Still Has Edge Cases

Qwen3.5-4B vote, seed 82, `prof_2`:

- Displayed utilities: `[3.3, 1.7, 1.7, 2.2, 1.6]`
- Gold student: 0
- Predicted student: 3
- Regret: 1.1

Model response:

```text
<THINK>I must vote for the student with the highest utility for me, which is Student 3 with a utility of 2.2. I will cast my vote immediately as instructed.</THINK><VOTE>3</VOTE>
```

The stronger models reduce the bottleneck but do not make it disappear.

## Artifacts

Probe script:

- `scripts/openrouter_best_student_probe.py`

Raw 100-trial JSONLs:

- `results/best_student_probe_qwen25_3b_vllm_vote_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen25_3b_vllm_json_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen25_7b_vllm_vote_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen25_7b_vllm_json_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen3_4b_vllm_vote_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen3_4b_vllm_json_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen3_8b_vllm_vote_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen3_8b_vllm_json_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen35_4b_vllm_vote_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen35_4b_vllm_json_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen35_9b_vllm_vote_seed0_99_mergedprompt.jsonl`
- `results/best_student_probe_qwen35_9b_vllm_json_seed0_99_mergedprompt.jsonl`

vLLM logs copied from `auton-dgx2`:

- `results/vllm_qwen35_4b_nightly_noparser_eager_20260701.log`
- `results/vllm_qwen35_9b_nightly_noparser_eager_20260701.log`
- `results/vllm_qwen3_4b_nightly_noparser_eager_20260701.log`
- `results/vllm_qwen3_8b_nightly_noparser_eager_20260701.log`

