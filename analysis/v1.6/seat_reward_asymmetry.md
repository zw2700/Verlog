# Per-seat individual reward: what RL training actually optimized

Reproduce with `python3 analysis/v1.6/compute_seat_reward_tables.py` from the repo root.

## What is being measured, and why it is the right quantity

Every run to date used `reward_mode="individual"` — the default at
`verl/envs/hiring_env/env.py:88`. It has never been overridden in any sbatch or
config file, so the `group` and `combined` branches at `env.py:1193` are dead
code in all existing runs. Under `individual`, each professor's terminal reward
is its own utility for the chosen student, so the three seats sum exactly to
`actual_total_utility`.

All three professors are the **same shared policy**. The objective PPO's
gradient sums over is therefore the population average of individual reward,
which is social welfare / 3. That makes "mean individual reward" the quantity
the training objective is actually climbing, and it is directly comparable
across policies.

**Filtering.** All tables below are restricted to consensus episodes, and the
episode is the clustering unit for the average (the three seats within an
episode are not independent — they sum to total utility). This is why SO here
reads 0.574 for steps 66-75, whereas
`analysis/v1/train_auton_17323_steps_66_75/category_metrics_summary.md` reads
0.559: the latter divides by all 826 episodes, this divides by the 805 that
reached consensus (97.5%). Both are correct; they answer different questions.

`±` values are standard errors. Data source: `logs/episode_log_*` raw JSONL,
field `terminal_rewards`.

## Table 1 — Mean individual reward by run

| run                     | n (consensus) | social optimality | welfare efficiency | mean individual reward |
|:------------------------|--------------:|------------------:|-------------------:|-----------------------:|
| Haiku 4.5 (`14263`)     |            99 |     0.727 ± 0.045 |             0.9772 |    **2.3623 ± 0.0307** |
| RL `17323`, steps 66-75 |           805 |     0.574 ± 0.017 |             0.9517 |        2.3022 ± 0.0121 |
| Qwen3-4B base (`14988`) |            91 |     0.505 ± 0.052 |             0.9337 |        2.2502 ± 0.0345 |
| RL `17323`, steps 1-10  |          3087 |     0.484 ± 0.009 |             0.9302 |        2.2473 ± 0.0063 |

Reward ordering matches social-optimality ordering, as it must — mean individual
reward is welfare/3, and welfare efficiency is monotone in it.

## Table 2 — Mean individual reward by seat

| run                     |              prof_1 |          prof_2 |          prof_3 | average |     spread |
|:------------------------|--------------------:|----------------:|----------------:|--------:|-----------:|
| Haiku 4.5 (`14263`)     |     2.3768 ± 0.0609 | 2.3020 ± 0.0661 | 2.4081 ± 0.0689 |  2.3623 | **0.1061** |
| RL `17323`, steps 66-75 | **2.5416 ± 0.0205** | 2.1990 ± 0.0256 | 2.1658 ± 0.0251 |  2.3022 | **0.3758** |
| Qwen3-4B base (`14988`) |     2.3901 ± 0.0577 | 2.2121 ± 0.0690 | 2.1484 ± 0.0726 |  2.2502 |     0.2418 |
| RL `17323`, steps 1-10  |     2.4086 ± 0.0111 | 2.2110 ± 0.0120 | 2.1223 ± 0.0122 |  2.2473 |     0.2863 |

Turn order is fixed (`randomize_turn_order=False`, `env.py:100`; tiebreak is
`sorted(professor_ids)`), so `prof_1` is the habitual first mover — it opens
82.2% of episodes.

The seat spread is the headline. Base Qwen already arrives with a first-mover
advantage (0.242). RL **amplifies** it to 0.376. Haiku **suppresses** it to
0.106 — near-flat across seats. Haiku's distinguishing behavior is not "more
diversity"; it is specifically *not exploiting turn order*, which is a
role-conditional behavior.

## Table 3a — What training actually bought (RL early → late)

| seat        | steps 1-10 | steps 66-75 |                            Δ | share of average gain |
|:------------|-----------:|------------:|-----------------------------:|----------------------:|
| prof_1      |     2.4086 |      2.5416 | **+0.1330 ± 0.0233 (+5.7σ)** |             **80.8%** |
| prof_2      |     2.2110 |      2.1990 |     -0.0120 ± 0.0283 (-0.4σ) |                 -7.3% |
| prof_3      |     2.1223 |      2.1658 |     +0.0435 ± 0.0279 (+1.6σ) |                 26.4% |
| average     |     2.2473 |      2.3022 |     +0.0548 ± 0.0137 (+4.0σ) |                     — |
| seat spread |     0.2863 |      0.3758 |                      +0.0895 |                     — |

RL made a real improvement — +0.055 average at 4.0σ, and SO rose 0.484 → 0.574.
It is not broken; it climbed a genuine hill. But **81% of that gain is prof_1
alone**, at 5.7σ, while prof_2 did not move at all. Training's mechanism was
the first mover extracting more, not the committee deciding better.

Corroborating behavioral change over the same window: prof_1's-favorite-wins
went 53.4% → 76.0%, and the share of episodes involving negotiation fell from
70% to 22%.

## Table 3b — Δ from cooperating (Haiku − RL late)

Read as: if the converged RL policy switched to Haiku-style play, what would
each seat gain or lose?

| seat              | RL late |  Haiku |           Δ from cooperating |
|:------------------|--------:|-------:|-----------------------------:|
| prof_1            |  2.5416 | 2.3768 | **-0.1648 ± 0.0642 (-2.6σ)** |
| prof_2            |  2.1990 | 2.3020 |     +0.1030 ± 0.0709 (+1.5σ) |
| prof_3            |  2.1658 | 2.4081 | **+0.2422 ± 0.0734 (+3.3σ)** |
| average           |  2.3022 | 2.3623 | +0.0601 ± 0.0330 (**+1.8σ**) |
| social optimality |  0.5739 | 0.7273 |     +0.1534 ± 0.0480 (+3.2σ) |
| seat spread       |  0.3758 | 0.1061 |                      -0.2697 |

**Statistical caveat, stated up front.** The *average* reward gain is only
+1.8σ — suggestive, not established, and Haiku's n is 99 episodes. Do not
quote "+0.060 of headroom on PPO's own objective" as a settled number. What
*is* robust here is (a) the social-optimality gap, +0.153 at 3.2σ, and (b) the
seat **redistribution**: prof_1 −0.165 (2.6σ) against prof_3 +0.242 (3.3σ).
The reallocation across seats is far better established than the net average
gain, which is the reverse of what one might assume from Table 1.

## Table 4 — Stand-up rate: how often a responder holds its own favourite

Reproduce with `python3 analysis/v1.6/compute_standup_rates.py`.

An episode is a **conflict** episode for responder R when prof_1's first vote is
not R's own argmax — R actually faces a choice. Within those, R "stands up" if
its own first vote goes to its own argmax, and "caves" if it goes to prof_1's
pick; votes for a third student are excluded. Rates are broken out by **stakes**
(`fg`, forgone utility): what R gives up by caving, u_R(own argmax) −
u_R(prof_1's pick). Intervals are Wilson 95%.

### prof_2

| era                | n conflict |    overall |     fg[0,0.5) |     fg[0.5,1) |     fg[1,1.5) |     fg[1.5,∞) |
|:-------------------|-----------:|-----------:|--------------:|--------------:|--------------:|--------------:|
| steps 1-10 (early) |       1190 | 36.6% ±2.7 | 19.9% (n=342) | 31.6% (n=323) | 43.0% (n=272) | 58.9% (n=253) |
| steps 18-27 (mid)  |        454 | 20.7% ±3.7 |  2.9% (n=104) | 19.8% (n=131) | 29.3% (n=116) | 30.1% (n=103) |
| steps 66-75 (late) |        581 | 44.6% ±4.0 | 14.5% (n=152) | 43.9% (n=155) | 60.3% (n=131) | 62.9% (n=143) |
| Haiku 4.5          |         74 | 97.3% ±4.3 |  93.8% (n=16) |  95.7% (n=23) | 100.0% (n=15) | 100.0% (n=20) |

### prof_3

| era                | n conflict |    overall |     fg[0,0.5) |     fg[0.5,1) |     fg[1,1.5) |     fg[1.5,∞) |
|:-------------------|-----------:|-----------:|--------------:|--------------:|--------------:|--------------:|
| steps 1-10 (early) |        740 | 35.0% ±3.4 | 18.8% (n=218) | 29.8% (n=191) | 40.8% (n=169) | 56.8% (n=162) |
| steps 18-27 (mid)  |        101 | 43.6% ±9.5 |  32.4% (n=34) |  38.5% (n=26) |  44.4% (n=18) |  65.2% (n=23) |
| steps 66-75 (late) |        165 | 61.8% ±7.3 |  37.5% (n=48) |  58.3% (n=48) |  75.7% (n=37) |  87.5% (n=32) |
| Haiku 4.5          |         53 | 98.1% ±4.8 |  94.7% (n=19) | 100.0% (n=12) | 100.0% (n=12) | 100.0% (n=10) |

Three things to read off these.

**The policy does condition on stakes.** Stand-up rate rises monotonically with
forgone utility in every era, for both seats. It is not blindly caving — it
caves cheaply and holds firm when holding firm is worth more.

**prof_2 is U-shaped, not monotone.** 36.6% → **20.7%** → 44.6%. The
capitulation collapse happens mid-training and bottoms out hard: at low stakes
prof_2 stands up just **2.9%** of the time at steps 18-27. It then partially
recovers, to 44.6% against Haiku's 97.3%. prof_3 is monotone instead
(35.0 → 43.6 → 61.8).

**prof_3's rise is partly an artifact of who gets a turn.** These rates are
conditional on prof_3 voting at all, and its conflict-episode count falls from
740 to 165. Late, prof_3 votes in only 34.7% of episodes (vs 72.7% for Haiku)
because the 2-of-3 threshold closes the vote before it speaks. prof_3 stands up
more often *when it gets a turn*, while getting a turn far less often.

### Why the U-shape: the incentive reversed mid-training

Payoff to standing up, for the responder doing it, stratified by stakes so the
selection effect is removed (responders stand up when caving costs more —
forgone utility 1.235 when standing up vs 0.781 when caving):

| prof_2, pooled Δ reward from standing up |                      value |
|:-----------------------------------------|---------------------------:|
| steps 1-10 (early)                       | **−0.186 ± 0.062 (−3.0σ)** |
| steps 66-75 (late)                       | **+0.318 ± 0.065 (+4.9σ)** |

Reward on no-consensus is a hard **0.0000**, against ~2.0 on consensus. Early,
standing up dropped the consensus rate to ~0.68, so it cost −0.186 at 3σ and the
gradient correctly learned to cave. By late training the consensus rate when
standing up has risen to 0.86–0.96, and the payoff has flipped to +0.318,
increasing monotonically with stakes (+0.825 at 6.0σ in the top bin). Social
optimality is also higher when standing up, in every bin above the lowest.

So the policy is recovering from a lesson that is no longer true, and has not
finished. Note this is observational: stratified by stakes, but the policy chose
when to stand up, so residual confounding remains. The clean version is
interventional — force the responder's vote at rollout time.

## Interpretation

Individual reward gives seat *i* an advantage that credits only *uᵢ*.
Since ∇E[Σⱼuⱼ] = Σⱼ∇E[uⱼ], the term ∂E[uⱼ]/∂θ for j≠i — the effect of *i*'s
action on its colleagues — is dropped. The shared policy therefore descends a
gradient that keeps only the diagonal terms, and its fixed point is not the
welfare optimum. Table 3a is what that bias looks like empirically: the gain
concentrates in the one seat where individually-selfish play pays.

Table 3b shows why undirected exploration will not escape it. The first mover —
the seat with 82.2% of the openings — *loses* by cooperating. The deviation
required is both joint and role-conditional: stop dictating as prof_1 **and**
stop caving as prof_2/3. Either half alone is worse than the current point
(prof_1 alone yields no leader; prof_2/3 alone yields deadlock and lost
consensus). Adding stochasticity has to land both halves simultaneously.

Consistent with this, the diverse behavior was abundantly sampled early
(70% negotiation) and training *removed* it — that is sampled-then-optimized-away,
not never-sampled.

Table 4 sharpens that. Standing up occurs in 44.6% of prof_2's conflict
episodes, conditioned sensibly on stakes, and its advantage is positive and
large (+0.318, 4.9σ). So the policy is failing to move onto a gradient it can
already see — the behavior is neither absent nor unrewarded. Shared weights are
the reason it cannot: +0.318 is the payoff to a *unilateral* deviation, but one
weight update moves all three seats, so responders cannot get braver without the
proposer hardening in lockstep (prof_1's switch rate is 3.1%).

Note that a healthy critic is not evidence against this. Critic EV of 0.82–0.84
measures how well V predicts the return of the *current* policy, and a perfect
critic of a caving policy is still perfect. In GAE the action comparison comes
from realized rewards, with V serving only as a baseline — so critic quality
bounds gradient variance and never supplies a counterfactual for an action that
was not taken.

## Bounding what this implies

Haiku's edge is narrower than the aggregate suggests. In
`no_pair_shares_top` — the hardest preference cell, 36% of episodes — Haiku
scores 0.400 against Qwen's 0.381, indistinguishable. Haiku's entire advantage
lives in cells where a 2-of-3 coalition exists. Separately, the 2-of-3 majority
rule (`vote_threshold=0.5`, `env.py:52`) caps social optimality near 75%
regardless of policy, so Haiku's 72.7% already sits at that ceiling.

## Caveats

- Haiku (n=99) and Qwen3-4B base (n=91) are single evaluation rollouts, not
  seeded replicates; the RL rows pool 10 training steps each.
- The three rows are not matched on preference draws, so between-run deltas are
  unpaired. A paired comparison on identical scenario seeds would tighten the
  average-gain estimate materially, and is the obvious follow-up if that number
  needs to be load-bearing.
- Haiku is not optimizing individual reward at all, so it demonstrates the
  cooperative behavior is *representable*, not that it is a fixed point of this
  training objective.
