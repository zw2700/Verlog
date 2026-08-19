The hiring game is partially observable: each professor acts from its own prompt, but the return depends on the full preference structure and the other professors' behavior. We are testing whether PPO gets a better learning signal when the **critic**, during training only, sees every professor's utility for every student. This is centralized training with decentralized execution: the actor remains deployable with ordinary observations.

The actor still sees the original prompt, generates the same response tokens, and must operate without privileged information at inference time. Only the critic input changes.

The mechanism is working: the treatment adds about 174 critic-only tokens and adds zero tokens to the actor/control view.

## The problem

The default critic sees exactly what the acting professor sees. That may be insufficient for predicting professor-specific returns in a multi-agent negotiation:

- the actor observes only its permitted game view;
- the eventual reward depends on the joint utility landscape, communication, votes, and consensus;
- an under-informed critic can produce noisy or systematically wrong advantages;
- noisy advantages weaken PPO credit assignment even if the actor itself is capable.

This branch asks whether **critic observability**, rather than actor capacity, is a bottleneck.

## The intervention

```text
Actor path — unchanged
  normal prompt
      -> actor
      -> sampled response tokens

Control critic
  normal prompt + the same response tokens
      -> value / advantage

Treatment critic
  normal prompt + full utility table
      + the same response tokens
      -> value / advantage

Value / advantage
      -> PPO actor update, when enabled
```

Two critic views are compared:


| Condition       | Critic input                             | Actor input         |
| --------------- | ---------------------------------------- | ------------------- |
| `actor_visible` | Exact actor prompt                       | Normal actor prompt |
| `all_utilities` | Actor prompt plus the full utility table | Normal actor prompt |


Within every rollout, the critic evaluates the **exact tokens sampled by the actor**. Privileged utilities never enter rollout generation, actor log-probabilities, reference-policy computation, or actor updates. The separate experimental runs are stochastic and are not paired episode-by-episode.

Nothing else changes: model architecture, value head, rewards, GAE, optimizer, and actor-generation mechanism are held fixed.

## Hypothesis

```text
More complete critic state
            |
            v
Better return prediction
            |
            v
Less noisy advantages
            |
            v
Better PPO updates
            |
            v
Better consensus and social welfare
```

The experiment separates the first link from the downstream policy effect:


| Experiment                 | Actor schedule             | Question                                           |
| -------------------------- | -------------------------- | -------------------------------------------------- |
| Frozen actor, 75 steps     | Actor never updates        | Does privileged state improve critic fit?          |
| PPO, 10-step critic warmup | Actor updates from step 11 | Does better critic fit improve the learned policy? |


