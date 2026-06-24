# Base Policy Episode Categorization Instructions

## Task

Analyze a disjoint range of base-policy rollout episodes from:

`logs/game_log_train_auton_12993.log`

Only use content before line `144892`. These are base policy rollouts.

Your job is to categorize each assigned episode's dominant public behavior in the hiring committee game. The research question is whether the base policy ever explores the desired phenomenon: professors engaging in meaningful negotiation to reach a socially good choice among 5 students.

Do not only classify by final outcome. We care about the interaction style that produced the outcome.

## Episode Boundaries

Episodes end at blocks like:

```text
=== EPISODE DIAGNOSIS (env=0) ===
```

The diagnosis block gives the final outcome, per-professor turn counts, format errors, invalid-action errors, and consensus result.

For qualitative behavior, inspect the `[OUTPUT]` blocks for each turn in the episode. Be careful not to count tags that appear inside the static prompt, turn context, or copied conversation history. The actual action for a turn is after `[OUTPUT]`.

## Primary Category

Assign exactly one `primary_category` to each episode.

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

Do not use this category merely because the episode has format errors. Format errors are common and should usually be secondary tags.

## Secondary Tags

Assign any tags that apply. Keep the list concise but informative.

### Outcome Tags

- `consensus_yes`
- `consensus_no`
- `chosen_social_optimum`
- `chosen_suboptimal`
- `social_optimum_unknown`

Only use `chosen_social_optimum` or `chosen_suboptimal` when enough utility information is visible to compute the social optimum across all 5 students. If at least one professor never acted and their full utility vector is unavailable, usually use `social_optimum_unknown`.

### Interaction Tags

- `candidate_comparison`
- `counterproposal`
- `compromise_language`
- `preference_probe`
- `vote_switch`
- `repeated_proposal`
- `private_reasoning_only`
- `early_focal_candidate`

### Quality / Pathology Tags

- `format_error_light`
- `format_error_heavy`
- `invalid_action`
- `prompt_leak`
- `placeholder_output`
- `malformed_tags`
- `semantically_incoherent`

Use `format_error_heavy` when the diagnosis reports format errors on roughly half or more of the episode's turns, or when format errors materially shape the episode. Use `format_error_light` for smaller amounts.

## New Category Proposals

You may suggest a new category, but do not fragment the taxonomy casually.

Only propose a new category if:

- the existing categories genuinely fail to describe the episode,
- the behavior seems likely to recur in multiple episodes, and
- the distinction matters for the research question.

If proposing a new category, still assign the closest existing `primary_category`, and fill:

- `suggested_new_category`
- `why_existing_categories_fail`

The final merge step will decide whether to adopt the new category.

## Output Files

For your assigned range, produce two artifacts.

### 1. JSONL Labels

Create one JSON object per episode, one object per line.

Use this schema:

```json
{
  "episode_id": 14,
  "line_start": 5986,
  "diagnosis_line": 6675,
  "primary_category": "negotiation_like",
  "secondary_tags": [
    "consensus_yes",
    "candidate_comparison",
    "compromise_language",
    "vote_switch",
    "format_error_light"
  ],
  "consensus": true,
  "chosen_student": 2,
  "total_turns": 14,
  "public_message_count": 14,
  "vote_count": 6,
  "wait_count": 3,
  "wait_for_count": 11,
  "format_error_rate": 0.36,
  "invalid_error_count": 0,
  "confidence": "medium",
  "rationale": "Agents discuss Student 0 vs Student 2, mention stability and fallback options, and prof_3 eventually moves toward Student 2 to preserve consensus.",
  "notable_excerpt": "choosing student 2 seems most stable, but I believe student 0 also has merit",
  "suggested_new_category": null,
  "why_existing_categories_fail": null
}
```

Requirements:

- `episode_id` is 1-indexed among the 232 base-policy episodes before line 144892.
- `line_start` should be the approximate first line of the episode.
- `diagnosis_line` should be the line containing `=== EPISODE DIAGNOSIS`.
- `confidence` must be `high`, `medium`, or `low`.
- Keep `rationale` to 1-3 sentences.
- Keep `notable_excerpt` short. Do not paste long blocks.

### 2. Markdown Memo

Write a short memo for your assigned range with:

- assigned episode range
- category counts in your range
- 3-5 representative episodes
- low-confidence or borderline episodes
- any suggested new categories and why
- brief notes on whether desired negotiation-like behavior appears

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

- Do not treat private `<THINK>` content as public negotiation. It can inform whether behavior was private-only, but primary categories should emphasize public behavior and executed actions.
- Do not over-credit agents for saying they will negotiate privately if their public output only waits or repeats a proposal.
- Do not reveal exact private utility values in the final prose except when already shown in the local episode evidence and needed for analysis.
- Do not assume social optimum when the full utility matrix is unavailable.
- Do not create many new categories. The final report should remain readable and aggregatable.
