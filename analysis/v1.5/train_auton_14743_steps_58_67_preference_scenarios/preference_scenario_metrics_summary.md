# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_14743.jsonl`
- global_step range: `58` to `67`
- episodes analyzed: `719`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `24`
- percent of analyzed episodes: `0.033`
- consensus rate: `1.000`
- SO rate: `0.750`
- SO|cons rate: `0.750`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 17 | 0.708 | 1.000 | 0.765 | 0.765 | 0.977 | 1.235 | 89.1 | 1.8 |
| negotiation | 7 | 0.292 | 1.000 | 0.714 | 0.714 | 0.964 | 1.429 | 144.9 | 3.0 |

## only_prof_1_prof_2_share_top

- episodes: `100`
- percent of analyzed episodes: `0.139`
- consensus rate: `1.000`
- SO rate: `0.520`
- SO|cons rate: `0.520`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 56 | 0.560 | 1.000 | 0.643 | 0.643 | 0.964 | 1.786 | 107.9 | 1.9 |
| negotiation | 44 | 0.440 | 1.000 | 0.364 | 0.364 | 0.922 | 2.523 | 158.8 | 3.7 |

## only_prof_1_prof_3_share_top

- episodes: `99`
- percent of analyzed episodes: `0.138`
- consensus rate: `1.000`
- SO rate: `0.525`
- SO|cons rate: `0.525`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 68 | 0.687 | 1.000 | 0.485 | 0.485 | 0.931 | 2.529 | 144.6 | 3.3 |
| instant_decision | 31 | 0.313 | 1.000 | 0.613 | 0.613 | 0.958 | 1.677 | 135.5 | 1.6 |

## only_prof_2_prof_3_share_top

- episodes: `106`
- percent of analyzed episodes: `0.147`
- consensus rate: `0.991`
- SO rate: `0.519`
- SO|cons rate: `0.524`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 76 | 0.717 | 1.000 | 0.474 | 0.474 | 0.938 | 2.355 | 168.2 | 3.8 |
| instant_decision | 30 | 0.283 | 0.967 | 0.633 | 0.655 | 0.913 | 2.000 | 124.4 | 1.7 |

## no_pair_shares_top

- episodes: `386`
- percent of analyzed episodes: `0.537`
- consensus rate: `0.969`
- SO rate: `0.355`
- SO|cons rate: `0.366`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 273 | 0.707 | 0.967 | 0.344 | 0.356 | 0.892 | 3.170 | 183.8 | 3.8 |
| instant_decision | 113 | 0.293 | 0.973 | 0.381 | 0.391 | 0.921 | 2.536 | 161.6 | 1.7 |

## multi_pair_without_all_three_common_top

- episodes: `4`
- percent of analyzed episodes: `0.006`
- consensus rate: `1.000`
- SO rate: `0.750`
- SO|cons rate: `0.750`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 3 | 0.750 | 1.000 | 0.667 | 0.667 | 0.992 | 1.333 | 203.7 | 2.0 |
| negotiation | 1 | 0.250 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 119.0 | 3.0 |

