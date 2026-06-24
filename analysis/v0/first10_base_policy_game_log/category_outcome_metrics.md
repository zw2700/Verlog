# First 10 Base-Policy Category Outcome Metrics

Metrics follow the env definitions: social optimum means `outcome/chosen_student_rank_global == 1`; `social_welfare/efficiency` is actual total utility divided by optimal total utility, with no-consensus episodes counted as 0 when the full utility matrix is visible.

- total labeled episodes: 232
- metric-computable episodes: 228 (0.983)
- metric-computable consensus episodes: 153

| Category | Episodes | Metric episodes | Coverage | Socially optimum rate | Socially optimum given consensus | Avg efficiency | Avg global rank, consensus only |
|---|---:|---:|---:|---:|---:|---:|---:|
| negotiation_like | 65 | 65 | 1.000 | 0.123 | 0.211 | 0.504 | 2.842 |
| proposal_following | 54 | 54 | 1.000 | 0.278 | 0.278 | 0.874 | 2.722 |
| thin_candidate_discussion | 50 | 50 | 1.000 | 0.120 | 0.250 | 0.418 | 2.667 |
| instant_consensus | 30 | 26 | 0.867 | 0.423 | 0.423 | 0.929 | 2.115 |
| coordination_theater | 18 | 18 | 1.000 | 0.111 | 0.222 | 0.437 | 2.778 |
| stalled_waiting_loop | 14 | 14 | 1.000 | 0.071 | 0.500 | 0.125 | 2.500 |
| execution_breakdown | 1 | 1 | 1.000 | 0.000 | NA | 0.000 | NA |

Coverage caveat: rows marked non-computable are usually short episodes where one professor never acted, so their full utility vector was not printed in the log. The env could compute those metrics from hidden state, but the log artifact cannot reconstruct them exactly.
