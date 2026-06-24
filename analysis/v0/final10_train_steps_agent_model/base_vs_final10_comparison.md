# Base Policy vs Final 10 Training Steps

| Category | Base count | Base percent | Final10 count | Final10 percent | Change pp |
|---|---:|---:|---:|---:|---:|
| `negotiation_like` | 65 | 28.0% | 1 | 0.1% | -27.9 |
| `proposal_following` | 54 | 23.3% | 109 | 15.2% | -8.1 |
| `thin_candidate_discussion` | 50 | 21.6% | 66 | 9.2% | -12.3 |
| `instant_consensus` | 30 | 12.9% | 467 | 65.2% | +52.3 |
| `coordination_theater` | 18 | 7.8% | 41 | 5.7% | -2.0 |
| `stalled_waiting_loop` | 14 | 6.0% | 31 | 4.3% | -1.7 |
| `execution_breakdown` | 1 | 0.4% | 1 | 0.1% | -0.3 |

Note: base-policy labels came from `analysis/first10_base_policy_game_log/`, using compact env=0 diagnosis episodes before line 144892; final10 labels come from all-env complete bounded episodes reconstructed from the agent-model log. The comparison is behaviorally useful but the sampling/logging sources differ.