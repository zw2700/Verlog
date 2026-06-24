# Hiring Committee Episode Categorization Instructions

## Task

Categorize assigned hiring committee rollout episodes by their dominant public behavior.

This rubric is intentionally compatible with the earlier base-policy analysis. Use the same primary categories so final trained-policy behavior can be compared against base-policy behavior.

For this final-10-step analysis, use:

`analysis/final10_train_steps_agent_model/complete_episode_segments.jsonl`

Scope:

- Source log: `logs/agent_model_train_auton_12993.log`
- Training steps: `global_steps=66..75`
- Agent-model line slice: `12887502..13148260`
- Episodes to label: complete bounded episodes only, `complete_episode_id=1..716`
- Boundary fragments are excluded from label percentages.

## Input Format

Each JSONL record is one extracted complete episode segment. Important fields:

- `complete_episode_id`: stable chronological ID for labeling.
- `segment_id`: original segment ID from extraction.
- `env`: rollout environment index.
- `start_line`, `end_line`: source line range in `agent_model_train_auton_12993.log`.
- `start_global_step`, `end_global_step`: inferred global step range.
- `turn_count`, `public_message_count`, `vote_count`, `wait_count`, `wait_for_count`.
- `consensus`: inferred from final executed votes. `true` means at least two professors' latest votes agree.
- `chosen_student`: inferred chosen student when `consensus=true`; otherwise `null`.
- `final_votes`: latest executed vote per professor.
- `full_utility_matrix_visible`: whether utility rows for all three professors are visible in the segment.
- `turns`: ordered turn records with `agent`, `line`, `output`, `action_text`, `group_messages`, `votes`, `wait_for`, and `utilities`.

Use `action_text`, `group_messages`, `votes`, `wait_count`, and `wait_for` for executed public/action behavior. The full `output` includes private `<THINK>` and is useful context, but primary categories should emphasize public messages and executed actions.

## Primary Category

Assign exactly one `primary_category`.

### `instant_consensus`

Consensus is reached very quickly, usually in 2-3 turns, through votes or simple agreement. There is no meaningful public deliberation.

Typical signs:

- two professors vote for the same student immediately
- at most one short public proposal
- no real comparison of alternatives
- no adaptation to another professor's stated preference

### `proposal_following`

One professor proposes or votes for a candidate, and another professor follows. There is some public rationale, but the episode is mainly endorsement rather than bargaining.

Typical signs:

- one candidate becomes focal early
- later professor accepts or repeats the candidate
- little or no counterproposal
- little or no tradeoff reasoning

### `coordination_theater`

Agents talk about coordinating, gauging preferences, checking votes, waiting for others, or building consensus, but they do not exchange useful information or make concrete tradeoffs.

Typical signs:

- repeated statements like "let's see what others think"
- claims about needing to check vote tally or voting history
- private thoughts contain strategic plans, but public actions do not execute them
- little substantive candidate comparison
- public messages are meta-discussion about process rather than useful negotiation

### `thin_candidate_discussion`

Agents discuss candidate qualities, utilities, or research fit, but the discussion stays shallow. There may be multiple candidate mentions, but the episode lacks clear bargaining, compromise, or effective response to others.

Typical signs:

- candidate strengths are listed
- utilities or ability dimensions are cited
- multiple candidates may be mentioned
- claims are repeated rather than developed
- no clear concession, coalition-building, or compromise logic

### `negotiation_like`

The episode contains behavior close to the desired phenomenon. Multiple candidates are seriously considered, agents respond to others' proposals, and at least one agent adapts, offers a compromise, switches vote, or explicitly balances competing preferences.

Typical signs:

- genuine candidate comparison
- counterproposal or fallback candidate
- compromise language
- vote switch or stated willingness to switch based on others
- public response to another professor's stated concern
- effort to reconcile different professor preferences, not just personal preference

This category can end in either consensus or no consensus. Use outcome tags separately.

### `stalled_waiting_loop`

Waiting behavior dominates the episode and prevents progress.

Typical signs:

- many `<WAIT>` or `<WAIT_FOR>` actions
- agents repeatedly wait for each other
- few concrete proposals or votes
- little progress despite many turns

Use this when waiting is the dominant behavioral failure, even if there are occasional candidate comments.

### `execution_breakdown`

Use this rare override only when malformed or incoherent outputs prevent meaningful behavioral classification.

Typical signs:

- most public actions are placeholders, prompt leaks, or broken text
- valid actions are too sparse to infer negotiation style
- outcome is mainly driven by parser/action failures
- public messages are semantically unreadable

Do not use this category merely because the episode has format oddities. Format/pathology should usually be secondary tags.

## Secondary Tags

Assign concise tags that apply.

### Outcome Tags

- `consensus_yes`
- `consensus_no`
- `chosen_social_optimum`
- `chosen_suboptimal`
- `social_optimum_unknown`

Only use `chosen_social_optimum` or `chosen_suboptimal` when `full_utility_matrix_visible=true` and utilities for all five students are visible for all three professors. Otherwise use `social_optimum_unknown`.

### Interaction Tags

- `candidate_comparison`
- `counterproposal`
- `compromise_language`
- `preference_probe`
- `vote_switch`
- `repeated_proposal`
- `private_reasoning_only`
- `early_focal_candidate`
- `vote_only`
- `no_public_messages`

### Quality / Pathology Tags

- `format_error_light`
- `format_error_heavy`
- `invalid_action`
- `prompt_leak`
- `placeholder_output`
- `malformed_tags`
- `semantically_incoherent`

For extracted agent-model segments, there is no compact diagnosis field with official format-error counts. Use these tags only when visible from `action_text`/`output`, for example broken tags, placeholder text, leaked prompt fragments, or invalid action-like syntax.

## Output Schema

Create one JSON object per assigned episode, one object per line:

```json
{
  "complete_episode_id": 1,
  "segment_id": 674,
  "env": 28,
  "start_line": 12887918,
  "end_line": 12891851,
  "start_global_step": 66,
  "end_global_step": 66,
  "primary_category": "instant_consensus",
  "secondary_tags": [
    "consensus_yes",
    "social_optimum_unknown",
    "vote_only",
    "no_public_messages",
    "early_focal_candidate"
  ],
  "consensus": true,
  "chosen_student": 1,
  "total_turns": 2,
  "public_message_count": 0,
  "vote_count": 2,
  "wait_count": 0,
  "wait_for_count": 0,
  "confidence": "high",
  "rationale": "Two professors voted for Student 1 immediately with no public message or candidate comparison.",
  "notable_excerpt": "<VOTE>1</VOTE>",
  "suggested_new_category": null,
  "why_existing_categories_fail": null
}
```

Requirements:

- `confidence` must be `high`, `medium`, or `low`.
- Keep `rationale` to 1-3 sentences.
- Keep `notable_excerpt` short.
- Preserve the input episode IDs and line numbers exactly.

## Markdown Memo

Write a short memo for your assigned range with:

- assigned `complete_episode_id` range
- category counts in your range
- consensus/no-consensus counts
- representative episodes
- low-confidence or borderline episodes
- any suggested new categories and why
- brief notes on whether desired negotiation-like behavior appears

## New Category Proposals

You may suggest a new category, but do not fragment the taxonomy casually. Still assign the closest existing `primary_category`, and fill:

- `suggested_new_category`
- `why_existing_categories_fail`

The final merge step will decide whether to adopt the new category.

## Classification Priorities

When categories overlap, use these tie-breakers:

1. If the episode is unreadable or mostly invalid, use `execution_breakdown`.
2. If waiting dominates and prevents progress, use `stalled_waiting_loop`.
3. If multiple candidates are actively compared and agents adapt, use `negotiation_like`.
4. If candidate content exists but is shallow or repetitive, use `thin_candidate_discussion`.
5. If the public talk is mostly about process rather than candidates, use `coordination_theater`.
6. If one proposal is simply accepted, use `proposal_following`.
7. If consensus happens almost immediately, use `instant_consensus`.

## Important Caveats

- Do not treat private `<THINK>` content as public negotiation. It can inform tags like `private_reasoning_only`, but the primary category should emphasize public messages and executed actions.
- Do not over-credit agents for saying they will negotiate privately if their `action_text` only votes or waits.
- Many trained-policy episodes are vote-only and short. Classify those directly; do not infer hidden negotiation.
- Do not assume social optimum when the full utility matrix is unavailable.
- Keep categories broad enough for aggregate comparison.
