# Hiring Env Metrics

Working notes for hiring-env negotiation metrics.

## Done: Outcome Quality

### `has_final_choice`

Whether the episode produced a valid final selected student.

- `1` = final selected student exists
- `0` = no final selected student

Use this as the denominator/mask for final-choice-dependent metrics. Metrics that are not applicable when there is no final choice should be logged as `None`, not `-1`, so they are skipped by numeric aggregation.

### `chosen_student_rank_global`

Rank of the final selected student by collective utility.

- `1` = globally optimal student
- `5` = worst collective student
- `None` = no final selected student; skip from averages

Collective utility means the sum of all professors' utilities for a student.

### `pareto_dominated_choice`

Whether the final selected student is Pareto dominated by another student.

- `1` = another student is weakly better for every professor and strictly better for at least one professor
- `0` = final choice is not Pareto dominated
- `None` = no final selected student; skip from averages

This catches clearly bad collective outcomes.

## Done: Individual Satisfaction

### `final_choice_rank_by_agent`

For each professor, rank of the final selected student in that professor's private utility ranking.

- `1` = professor's favorite student
- `5` = professor's least preferred student
- `None` = no final selected student; skip from averages

### `regret_by_agent`

For each professor:

```text
max_private_utility - final_choice_utility
```

Measures how much utility the professor gave up relative to their favorite student.

Use `None` when there is no final selected student so it is skipped from averages.

### `normalized_regret_by_agent`

For each professor:

```text
(max_private_utility - final_choice_utility) / max_private_utility
```

Use `0.0` if `max_private_utility` is zero. Use `None` when there is no final selected student so it is skipped from averages.

### `final_choice_rank_variance`

Variance of the three professors' `final_choice_rank_by_agent` values.

Low variance means the selected student was similarly acceptable to everyone. High variance means the choice was more polarizing.

Use `None` when there is no final selected student so it is skipped from averages.

## Done: Voting Dynamics

### `total_vote_changes`

Total number of times professors changed their vote during the episode.

Initial votes do not count as changes. Only transitions from one valid voted student to a different valid voted student count.

### `vote_changes_by_agent`

Per-professor version of `total_vote_changes`.

### `first_vote_turn_by_agent`

For each professor, the environment turn index of their first valid vote.

Use `-1` if the professor never voted.

### `final_vote_turn_by_agent`

For each professor, the environment turn index of their last valid vote.

Use `-1` if the professor never voted.

### `vote_without_discussion`

For each professor:

- `1` = professor cast a valid vote before sending any public `<GROUP>` message
- `0` = professor sent at least one public `<GROUP>` message before their first valid vote
- `-1` = professor never voted

### `minority_persistence`

How long professors keep voting against the current plurality after a unique plurality exists.

Suggested implementation:

- At each vote event, compute the unique current plurality before the event.
- If the acting professor already had a vote different from that plurality, increment that professor's minority-persistence counter by the number of elapsed turns since their previous vote/turn checkpoint.
- Do not count tied plurality states.

Track both:

- `minority_persistence_total`
- `minority_persistence_by_agent`

## Done: Influence

### `leader_agent`

First professor to actively propose a student in a public `<GROUP>` message.

Use `none` or flatten to `-1` if no clear proposal occurs.

### `leader_student`

Student proposed by `leader_agent`.

Use `-1` if no clear proposal occurs.

### `leader_success`

Whether the leader's proposed student became the final selected student.

- `1` = `leader_student` equals final selected student
- `0` = leader proposed a student, but that student was not selected
- `None` = no clear proposal or no final selected student; skip from averages

### Proposal detection for `leader_*`

Use conservative text parsing on public `<GROUP>` messages only.

Count clear active proposal phrases such as:

- `I propose Student 2`
- `I recommend Student 2`
- `I support Student 2`
- `I think Student 2 is the best choice`
- `Student 2 should be our choice`
- `let's choose Student 2`
- `we should vote for Student 2`

Do not count plain mentions or ambiguous statements such as:

- `Student 2 has high AI/ML`
- `What do you think about Student 2?`
- `Student 2 is not ideal`

If a message contains multiple proposed students, treat it as ambiguous and do not set the leader from that message.

### `vote_adopted_from_plurality`

For each valid vote event, whether the professor's new vote matches the unique current plurality before the vote.

Episode-level metrics:

- `votes_adopted_from_plurality_count`
- `votes_adopted_from_plurality_rate`
- `votes_adopted_from_plurality_ambiguous`

Use ambiguous when there is no current vote or the current plurality is tied.

### `vote_changes_to_plurality`

Subset of vote changes where a professor switches from a different valid vote into the unique current plurality.

Episode-level metrics:

- `vote_changes_to_plurality_count`
- `vote_changes_to_plurality_rate`
- `vote_changes_to_plurality_ambiguous`

This is cleaner than all plurality adoption events because it focuses on actual switches, not first votes.

## New Metrics to Add

These are the next focused metrics for negotiation behavior. The goal is to measure process quality, not just final efficiency.

Skipped duplicates:

- Do not add concession cost separately for now; `regret_by_agent` and `normalized_regret_by_agent` already cover the main idea for final outcomes.
- Do not add final vote collective rank for now; it is close to `chosen_student_rank_global` when consensus is reached.
- Do not add delayed voting; existing `turns_to_first_vote` already covers the rough timing signal.

### Vote Movement Toward Good Outcomes

These metrics ask whether vote changes are meaningful convergence rather than random churn.

For every vote change by an agent:

```text
old_vote -> new_vote
```

Compute:

```text
global_rank_delta = global_rank(old_vote) - global_rank(new_vote)
collective_utility_delta = collective_utility(new_vote) - collective_utility(old_vote)
agent_utility_delta = agent_utility(new_vote) - agent_utility(old_vote)
```

Positive `global_rank_delta` means the new vote is globally better. Positive utility deltas mean the switch improved collective or private utility.

Suggested flattened metrics:

- `voting/vote_change_global_rank_delta_mean`
- `voting/vote_change_collective_utility_delta_mean`
- `voting/vote_change_agent_utility_delta_mean`
- `voting/vote_change_improves_global_rank_rate`
- `voting/vote_change_improves_collective_utility_rate`
- `voting/vote_change_improves_agent_utility_rate`

Use `0.0` for means/rates when there are no vote changes, and interpret them together with `voting/total_vote_changes`.

Implementation notes:

- Use tie-aware global ranks: `1 + number of students with strictly higher collective utility`.
- Only count transitions from one valid vote to a different valid vote.
- Initial votes are not vote changes.

### Argument Repetition Rate

This metric asks whether professors keep repeating the same public argument.

Compare each professor's public `<GROUP>` message to that same professor's previous public `<GROUP>` message.

Suggested flattened metrics:

- `communication/argument_repetition_rate`
- `communication/repetitive_messages`
- `communication/repetition_comparisons`
- `communication/{agent_id}/argument_repetition_rate`
- `communication/{agent_id}/max_repetition_streak`

Suggested implementation:

1. Extract public communication messages only.
2. Normalize text:
   - lowercase
   - remove punctuation
   - remove common stopwords
   - optionally remove student IDs, so repeated templates with different student numbers are still detectable
3. Compute token Jaccard similarity with the agent's previous normalized group message.
4. Count as repetitive if similarity is at least `0.65`.

Use `0.0` for rates when there are no comparisons.

Interpretation:

- High repetition with high message volume means the agents are talking, but not adding much new substance.
- This should help distinguish "more discussion" from "better negotiation."

### New Student Introduction Rate

This metric asks whether the conversation broadens to new candidates instead of repeatedly discussing the same one.

For each public `<GROUP>` message, extract student mentions using conservative patterns like:

```text
Student 0
student 0
```

Suggested flattened metrics:

- `communication/new_student_mentions_count`
- `communication/new_student_mentions_rate`
- `communication/distinct_students_discussed`

Definition:

- `new_student_mentions_count`: number of first-time student mentions introduced by group messages in the episode.
- `new_student_mentions_rate`: first-time student mentions divided by total student mentions in group messages.
- `distinct_students_discussed`: number of unique students mentioned in public discussion.

Implementation notes:

- Count a student as "new" only the first time that student appears in any public `<GROUP>` message in the episode.
- Do not try to infer whether the mention is positive or negative.
- This is intentionally simpler and less ambiguous than candidate-comparison parsing.

### Vote Justification Rate

This metric asks whether professors explain votes publicly instead of silently voting.

For each valid vote event, check whether the same agent has a public `<GROUP>` message in the same environment turn.

Composite actions like:

```text
<GROUP>I can support Student 2 because it seems acceptable to everyone.</GROUP><VOTE>2</VOTE>
```

should count as justified.

Suggested flattened metrics:

- `voting/vote_with_group_justification_count`
- `voting/vote_with_group_justification_rate`
- `voting/{agent_id}/vote_with_group_justification_rate`

Implementation notes:

- Use `(agent_id, ticker_time)` to identify same-turn communication and vote records.
- Count all valid vote events, including vote changes.
- Use `0.0` when there are no valid vote events.

Interpretation:

- Higher values suggest agents are making their voting rationale public.
- Pair with `argument_repetition_rate`, because a vote can be "justified" with a repetitive or low-substance message.

### Direct Consensus Language

This metric asks whether agents use explicit agreement, support, or consensus language.

Suggested flattened metrics:

- `communication/consensus_language_rate`
- `communication/consensus_language_messages`
- `communication/{agent_id}/consensus_language_rate`

Use conservative phrase matching on public `<GROUP>` messages.

Initial phrase list:

- `consensus`
- `agree`
- `agreement`
- `align`
- `aligned`
- `support`
- `acceptable`
- `works for me`
- `I can support`
- `willing to support`
- `I could support`
- `for consensus`
- `reach consensus`
- `settle on`

Implementation notes:

- Count at most once per message, even if multiple phrases occur.
- This is a fuzzy language signal, not a proof of real negotiation.
- Interpret alongside vote dynamics and repetition.
