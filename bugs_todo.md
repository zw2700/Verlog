# Bugs / TODOs

## Hiring env: budget accounting mismatch

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

## Hiring env: vote revocability mismatch

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
