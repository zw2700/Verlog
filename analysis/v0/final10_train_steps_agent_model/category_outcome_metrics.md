# Final 10 Train-Step Category Outcome Metrics

Metrics follow the env definitions: social optimum means `outcome/chosen_student_rank_global == 1`; `social_welfare/efficiency` is actual total utility divided by optimal total utility, with no-consensus episodes counted as 0 when the full utility matrix is visible.

- total labeled episodes: 716
- metric-computable episodes: 353 (0.493)
- metric-computable consensus episodes: 291

| Category | Episodes | Metric episodes | Coverage | Socially optimum rate | Socially optimum given consensus | Avg efficiency | Avg global rank, consensus only |
|---|---:|---:|---:|---:|---:|---:|---:|
| instant_consensus | 467 | 191 | 0.409 | 0.393 | 0.431 | 0.848 | 1.994 |
| proposal_following | 109 | 54 | 0.495 | 0.407 | 0.407 | 0.926 | 2.093 |
| thin_candidate_discussion | 66 | 66 | 1.000 | 0.152 | 0.385 | 0.367 | 1.846 |
| coordination_theater | 41 | 33 | 0.805 | 0.273 | 0.300 | 0.838 | 2.300 |
| stalled_waiting_loop | 31 | 8 | 0.258 | 0.500 | 0.667 | 0.719 | 1.500 |
| execution_breakdown | 1 | 0 | 0.000 | NA | NA | NA | NA |
| negotiation_like | 1 | 1 | 1.000 | 0.000 | 0.000 | 0.868 | 2.000 |

Coverage caveat: rows marked non-computable are usually short episodes where one professor never acted, so their full utility vector was not printed in the log. The env could compute those metrics from hidden state, but the log artifact cannot reconstruct them exactly.
