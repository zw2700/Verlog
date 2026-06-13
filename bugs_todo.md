# Bugs / TODOs

## Training rollout: non-closing professors receive zero outcome reward — fixed

Status: fixed in `verl/experimental/agent_loop/tool_agent_loop.py`. At each
episode end during training, every non-closing professor's own terminal
utility is added to their last turn of that episode and that row is marked
`done=True` (closing their GAE chain at the episode boundary — previously
only the closer's chain had a `done` flag, so other agents' values
bootstrapped across episodes). The closer's utility stays on their real
terminal row (no double-counting). A professor with zero turns in an episode
gets no row and their utility for that episode is undeliverable (acceptable:
no action, no credit). Validation: the per-professor bootstrap rows now carry
each agent's OWN utility instead of the closer's `scalar_reward` replicated,
so `val/mean_rewards` is a true per-agent metric. Non-terminal truncation
bootstraps stay 0.0; the boundary case where a terminal turn also fills the
rollout counter routes utilities onto the truncation bootstrap rows (see
Implementation below). Was present on all branches (merge base,
verlog-frank-dev, verlog-merge-jun26) — not a merge artifact. NOTE: changes
the training signal globally; flag to collaborators.

Issue:

At episode end, `env.step()` returns a per-agent utility dict (e.g.
`{prof_1: 2.3, prof_2: 0.9, prof_3: 1.7}`), but only the utility of the
ACTING agent on the terminal turn (the professor whose vote closed
consensus) ever reaches a training row:

- `verl/experimental/agent_loop/tool_agent_loop.py`
  - `scalar_reward = float(reward.get(acting_agent_id, sum(reward.values())))`
  - terminal turn row gets the closer's utility; everyone else's is dropped.
  - end-of-episode bootstrap rows (one per professor, `done=True`) carry
    `rewards=0.0` in training — the natural slot for per-agent utility is
    unused.
- `verl/trainer/ppo/ray_trainer.py`
  - `get_multiagent_episode_structure()` groups GAE chains by
    `(env_idx, agent_id)`, so each professor's turns form an isolated
    sequence. The closer's terminal reward does NOT propagate into other
    professors' chains.

Effect:

- Per episode, only the consensus-closing professor's chain receives any
  outcome reward; the other professors' chains end with 0.0 (`done=True`
  bootstrap rows) — zero learning signal from the episode outcome.
- `reward_mode` does not mitigate this: group/combined only change what the
  closer's chain sees; the other chains still see nothing.
- Cooperation behaviors performed by non-closers (conceding, persuading,
  early constructive votes) are never directly rewarded — bad for a
  cooperation-focused project.
- ~2/3 of collected turns train against a critic fitted to all-zero returns;
  their advantages reduce to format/invalid penalties only.
- Validation mirror image: val bootstrap rows give EVERY professor the
  closer's reward (`rewards=scalar_reward if is_val else 0.0`), so
  `val/mean_rewards` reports the closer's reward replicated per agent.

Implementation (in `tool_agent_loop.py::ToolAgentLoop.run`):

The rollout loop now handles `done` BEFORE the `is_full` truncation exit, so a
terminal turn is recorded the same way whether or not it also fills the
counter:

1. On any terminal turn, the real closing-action row (`turn_data`) is appended
   — it carries the closing agent's own utility. The other professors'
   utilities are backpatched onto their last real turn of this episode, and
   those rows are marked `done=True` (closing each agent's GAE chain at the
   episode boundary — previously only the closer's row had `done` set, so other
   agents' values bootstrapped across episodes).
2. Then, if the counter is full, one value-carrier bootstrap row per agent is
   appended and the loop breaks. Because `turn_data` was appended first and the
   bootstrap rows get a higher `turn_id`,
   `remove_last_turn_in_episode_multiagent` drops the bootstrap rows and keeps
   `turn_data` as an interior row — so the closer's closing-action row and its
   utility survive into training.

Why utilities must land on interior real rows (not bootstrap rows):
`compute_gae_advantage_return_core` forces the last row of every (env, agent)
chain to advantage 0 and never reads its reward (the last row is a value
carrier only; `ray_trainer.py` then drops it). In real training the loop only
ever exits via truncation, so every agent always ends with a bootstrap row —
making all real rows, including closing-action rows, interior.

Non-terminal truncation (the counter fills mid-episode) adds no utilities — the
episode is incomplete, so there is no terminal reward; bootstrap rows carry 0.0.

Validation (natural-end bootstrap loop): each professor's bootstrap row carries
that professor's OWN utility instead of the closer's `scalar_reward` replicated
(the val metric reads the last row per (env, agent) directly, not via GAE).

A professor with zero turns in an episode has no row to attach to; their
utility for that episode is undeliverable (acceptable: no action, no credit).

## Hiring env: budget accounting mismatch — fixed

Status: fixed in `verl/envs/hiring_env/env.py`. Shared budget now advances
only by valid `<GROUP>` message content; `<THINK>`, `<WAIT>`, `<VOTE>`, and
invalid `raw`/`discuss` actions still advance ticker time but do not consume
shared group budget.

Original issue:

The system prompt says `<THINK>` tokens do not count against the shared token
budget, and only `<GROUP>` messages consume that budget. However,
`AsyncTickerAdmissionsEnv.step()` currently adds both private thinking tokens
and action tokens to `episode_state["tokens_used"]`.

Relevant code:

- `verl/envs/hiring_env/env.py`
  - `think_tokens = ...`
  - `action_tokens = ...`
  - `total_ticker_tokens = think_tokens + action_tokens`
  - `self.episode_state["tokens_used"] += total_ticker_tokens`

Effect:

- Long private `<THINK>` blocks prematurely exhaust the shared negotiation
  budget, despite the prompt telling agents that thinking is free.
- Logged budget metrics mix private reasoning cost and public communication
  cost.
- This can shorten episodes and distort negotiation-quality measurements.

Expected behavior:

- Agent ticker time should advance by `think_tokens + action_tokens`.
- Shared budget should probably advance only by public communication tokens
  from `<GROUP>...</GROUP>`, or at minimum match whatever the prompt says.

## Hiring env: vote revocability mismatch — fixed

Status: fixed in `verl/envs/hiring_env/env.py` and
`verl/envs/hiring_env/time_manager.py`. Voting now updates the professor's
current vote without removing them from future turn selection. A later
`<VOTE>N</VOTE>` can overwrite the previous vote while the game is still
ongoing.

Original issue:

The system prompt says `<VOTE>` is revocable and agents can change their vote
while the game is ongoing. In practice, once an agent votes, the time manager
marks that agent as voted and excludes them from future turns.

Relevant code:

- `verl/envs/hiring_env/env.py`
  - on vote: `self.episode_state["votes"][active_agent] = parsed["choice"]`
  - then: `self.time_manager.record_vote(active_agent)`
- `verl/envs/hiring_env/time_manager.py`
  - `record_vote()` adds the agent to `_voted_agents`
  - `get_next_agent()` skips agents in `_voted_agents`

Effect:

- Votes are final in practice, not revocable.
- Agents cannot revise a vote after seeing later votes or arguments.
- This limits negotiation dynamics and contradicts the prompt.

Expected behavior options:

- If votes should be final, update the prompt to say that voting ends the
  agent's participation.
- If votes should be revocable, do not remove voted agents from future turn
  selection, and let later `<VOTE>N</VOTE>` actions overwrite prior votes.

## Hiring env: parser contract mismatches — fixed

Status: fixed in `verl/envs/hiring_env/env.py`. The parser is now tolerant and
no longer emits invalid `raw`/`discuss` actions for normal generations.
Unrecognized output defaults to `<WAIT>`. Only text inside `<GROUP>...</GROUP>`
is visible to other professors and charged to the shared budget. Votes only
count when written in a valid `<VOTE>N</VOTE>` tag; vote-like text inside
`<GROUP>` remains a public message, not a vote. A `<GROUP>` and `<VOTE>` can
coexist in one model response and are recorded as separate public events from
the same turn, with parser type `composite`.

Original issue:

The system prompt said votes written inside `<GROUP>` messages do not count:

- `NEVER write your vote inside a <GROUP> message. <GROUP>Vote for Student 2</GROUP> does NOT count as a vote.`

However, `_parse_action()` currently contains a repair rule that converts
certain group messages into real votes when the group content starts with text
like `Vote for Student N`, `Voting for Student N`, or `I will cast my vote for
Student N`.

Relevant code:

- `verl/envs/hiring_env/env.py`
  - inside the `<GROUP>...</GROUP>` parsing branch:
    - `vote_in_group_match = re.match(...)`
    - if matched, returns `{"type": "vote", "choice": int(student_idx), ...}`

Effect:

- An output such as `<THINK>...</THINK><GROUP>Vote for Student 2 to balance group consensus.</GROUP>` is silently converted into `<VOTE>2</VOTE>`.
- The next observation shows `CURRENT VOTES: prof_X: student 2`, even though the model did not use a valid `<VOTE>` tag.
- This contradicts the prompt and makes vote metrics harder to interpret.

Other parser behaviors that are more permissive than the prompt contract:

- Missing `<THINK>` can still produce a valid action. Example:
  `<VOTE>2</VOTE>` is parsed as a vote with empty `think_text`, even though the
  prompt says every turn must begin with `<THINK>...</THINK>`.
- Text before `<THINK>` can be ignored. Example:
  `hello <THINK>x</THINK><VOTE>2</VOTE>` can still parse as a valid vote,
  even though the prompt says never add text outside tags.
- Text after a valid action can be accepted if it does not contain another
  action tag. Example:
  `<THINK>x</THINK><VOTE>2</VOTE> I hope this works` can still parse as a vote.
- The parser searches for action tags anywhere in the post-think remainder
  rather than requiring the action tag to start immediately after `</THINK>`.
- `<WAIT>` parsing is lenient and accepts multiple variants, such as
  `<WAIT/>`, `<WAIT></WAIT>`, and `<WAIT>`. This may be acceptable, but it is
  broader than the listed valid examples.

Expected behavior options:

- Strict: make `_parse_action()` match the prompt contract exactly, e.g.
  require `^<THINK>...</THINK>(<GROUP>...</GROUP>|<WAIT>|<VOTE>N</VOTE>)$`,
  remove the group-vote repair rule, and classify anything else as invalid.
- Lenient: keep one or more repair rules, but update the prompt and metrics so
  repaired actions are explicit and interpretable.

## Training rollout: extra generation after terminal env step — fixed

Status: fixed in `verl/experimental/agent_loop/tool_agent_loop.py`.
Validation still breaks on `done=True`. Training appends the terminal generated
turn, immediately resets the env, and continues filling the shared rollout
counter from a fresh episode. The loop no longer generates another model
response from a terminal observation, while preserving the trainer's expected
rollout batch size. The shared rollout counter boundary is checked before the
training terminal-reset path, so a boundary-crossing terminal turn cannot add
one extra real rollout row.

Original issue:

During training, `ToolAgentLoop.run()` does not break when the env returns
`done=True`. It only breaks on `done=True` during validation. Training rollouts
continue until the rollout counter is full.

Relevant code:

- `verl/experimental/agent_loop/tool_agent_loop.py`
  - after `env.step(actions)`, `done` is computed from `terminated/truncated`
  - `if done and is_val: ... break`
  - for training (`is_val=False`), the loop appends the turn and continues
  - the next iteration calls model generation before the wrapper has a chance
    to reset
- `verl/envs/hiring_env_wrapper.py`
  - auto-reset happens only inside the next `env.step()`
  - `if self.episode_done: obs, info = self.reset(); return obs, 0.0, False, False, info`

Effect:

- After consensus/no-consensus termination, the loop can generate one extra
  model response from a terminal observation.
- That prompt may show an already-terminal state, such as two matching votes
  for the same student.
- The generated action is then discarded by the wrapper's lazy auto-reset on
  the following `env.step()`, but the generated row can still be included as a
  normal training turn rather than a bootstrap-only row.
- This can train on impossible states and distort turn counts, response stats,
  value estimates, and policy gradients around terminal boundaries.

Expected behavior options:

- Break on `done=True` during training too, then add bootstrap rows as needed.
- Or immediately reset/build a fresh prompt before the next generation when a
  training env episode ends.
