# Hiring Committee Behavior Categories

This taxonomy is for `episode_log_*.jsonl` analysis. Categories describe the
episode process, not whether the outcome was good. Outcome metrics should be
reported separately by category.

## Categories

### `malformed_or_other`

The log is not reliable enough to classify.

Use only for logging/parsing problems, such as missing `tokens_used`, missing
`turns`, invalid actions, votes outside the episode's valid student indices, or
`consensus == true` with no valid `chosen_student`.

### `stalled_coordination_failure`

The agents have enough turns to act, but the episode does not make meaningful
progress.

Common signs:

- no consensus and no candidate is ever mentioned or voted for
- long wait / wait-for loops
- many turns but very few actual group messages or votes
- one professor dominates while others do not publicly engage
- the same action or message repeats many times
- many turns discussing only one candidate but still no consensus

This category is checked before `instant_decision`, because some stalled episodes
use very few tokens.

### `instant_decision`

The episode ends or fails quickly without real back-and-forth deliberation.

Use when any of these are true:

```text
tokens_used <= 40
total_turns <= 2
total_turns <= 3, consensus is reached, and only one candidate appears
```

This can include consensus or no-consensus episodes. The key point is that the
agents did not spend meaningful deliberation budget.

### `negotiation`

Everything else: non-malformed, non-stalled episodes that are not instant
decisions.

This is intentionally broad. It includes useful negotiation, failed negotiation,
one-candidate proposal/support, verbose candidate discussion, and short
multi-candidate disagreement. Outcome metrics should tell us whether this broad
negotiation bucket actually improves decisions.

## Classification Order

```python
if is_malformed(ep):
    return "malformed_or_other"
if is_stalled(ep):
    return "stalled_coordination_failure"
if is_instant_decision(ep):
    return "instant_decision"
return "negotiation"
```

## Suggested Stalled Checks

Use conservative stalled rules. Prefer leaving messy but candidate-directed
episodes as `negotiation`.

```text
no consensus and candidate_count == 0
total_turns > 6 and one exact action repeats >= 10 times
total_turns > 6 and wait-like turns are >= 65% with weak progress
total_turns >= 8 and action_turns <= 2
total_turns >= 10 and public_speakers <= 1
no consensus and total_turns >= 10 and candidate_count <= 1
```

## Metrics To Report

For each category, report:

```text
count and percent
consensus rate
socially optimal rate
socially optimal given consensus rate
average efficiency
average global rank over consensus episodes only
average tokens_used
average total_turns
```

The main comparison is:

```text
Instant Decision vs Negotiation:
Do episodes that spend deliberation budget achieve better social outcomes?
```
