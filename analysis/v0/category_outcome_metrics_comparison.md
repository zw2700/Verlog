# Category Outcome Metrics Comparison

These tables are computed only on episodes with a visible full utility matrix.

## First 10 Base-Policy Steps

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

## Final 10 Train Steps

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
