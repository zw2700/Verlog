# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_13244.jsonl`
- global_step range: `66` to `75`
- episodes analyzed: `1008`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `67`
- percent of analyzed episodes: `0.066`
- consensus rate: `0.985`
- SO rate: `0.597`
- SO|cons rate: `0.606`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 56 | 0.836 | 1.000 | 0.643 | 0.643 | 0.898 | 1.625 | 83.2 | 2.1 |
| negotiation | 11 | 0.164 | 0.909 | 0.364 | 0.400 | 0.775 | 1.900 | 152.7 | 3.6 |

## only_prof_1_prof_2_share_top

- episodes: `157`
- percent of analyzed episodes: `0.156`
- consensus rate: `0.968`
- SO rate: `0.611`
- SO|cons rate: `0.632`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 132 | 0.841 | 0.992 | 0.682 | 0.687 | 0.956 | 1.519 | 79.6 | 2.1 |
| negotiation | 25 | 0.159 | 0.840 | 0.240 | 0.286 | 0.744 | 2.381 | 143.0 | 3.7 |

## only_prof_1_prof_3_share_top

- episodes: `192`
- percent of analyzed episodes: `0.190`
- consensus rate: `0.995`
- SO rate: `0.495`
- SO|cons rate: `0.497`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 133 | 0.693 | 0.992 | 0.541 | 0.545 | 0.934 | 1.841 | 82.4 | 2.0 |
| negotiation | 59 | 0.307 | 1.000 | 0.390 | 0.390 | 0.899 | 2.254 | 126.5 | 3.4 |

## only_prof_2_prof_3_share_top

- episodes: `194`
- percent of analyzed episodes: `0.192`
- consensus rate: `0.995`
- SO rate: `0.304`
- SO|cons rate: `0.306`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 112 | 0.577 | 1.000 | 0.223 | 0.223 | 0.877 | 2.598 | 85.6 | 2.1 |
| negotiation | 82 | 0.423 | 0.988 | 0.415 | 0.420 | 0.913 | 2.012 | 122.1 | 3.3 |

## no_pair_shares_top

- episodes: `382`
- percent of analyzed episodes: `0.379`
- consensus rate: `0.955`
- SO rate: `0.335`
- SO|cons rate: `0.351`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 232 | 0.607 | 0.996 | 0.328 | 0.329 | 0.918 | 2.407 | 81.6 | 2.1 |
| negotiation | 150 | 0.393 | 0.893 | 0.347 | 0.388 | 0.830 | 2.239 | 131.0 | 3.4 |

## multi_pair_without_all_three_common_top

- episodes: `16`
- percent of analyzed episodes: `0.016`
- consensus rate: `1.000`
- SO rate: `0.438`
- SO|cons rate: `0.438`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 13 | 0.812 | 1.000 | 0.462 | 0.462 | 0.956 | 1.923 | 74.9 | 2.2 |
| negotiation | 3 | 0.188 | 1.000 | 0.333 | 0.333 | 0.954 | 2.000 | 199.3 | 3.7 |

