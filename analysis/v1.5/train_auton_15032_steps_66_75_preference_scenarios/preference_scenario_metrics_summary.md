# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_15032.jsonl`
- global_step range: `66` to `75`
- episodes analyzed: `532`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `6`
- percent of analyzed episodes: `0.011`
- consensus rate: `1.000`
- SO rate: `1.000`
- SO|cons rate: `1.000`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 4 | 0.667 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 74.0 | 2.0 |
| negotiation | 2 | 0.333 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 118.5 | 3.0 |

## only_prof_1_prof_2_share_top

- episodes: `67`
- percent of analyzed episodes: `0.126`
- consensus rate: `0.985`
- SO rate: `0.507`
- SO|cons rate: `0.515`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 44 | 0.657 | 1.000 | 0.682 | 0.682 | 0.974 | 1.568 | 78.5 | 1.8 |
| negotiation | 23 | 0.343 | 0.957 | 0.174 | 0.182 | 0.864 | 2.909 | 211.4 | 4.3 |

## only_prof_1_prof_3_share_top

- episodes: `63`
- percent of analyzed episodes: `0.118`
- consensus rate: `0.984`
- SO rate: `0.556`
- SO|cons rate: `0.565`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 44 | 0.698 | 0.977 | 0.568 | 0.581 | 0.951 | 1.837 | 148.9 | 3.3 |
| instant_decision | 19 | 0.302 | 1.000 | 0.526 | 0.526 | 0.971 | 1.684 | 143.6 | 1.8 |

## only_prof_2_prof_3_share_top

- episodes: `41`
- percent of analyzed episodes: `0.077`
- consensus rate: `0.951`
- SO rate: `0.561`
- SO|cons rate: `0.590`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 37 | 0.902 | 0.973 | 0.568 | 0.583 | 0.940 | 1.667 | 145.7 | 3.5 |
| instant_decision | 4 | 0.098 | 0.750 | 0.500 | 0.667 | 0.746 | 1.333 | 217.8 | 1.8 |

## no_pair_shares_top

- episodes: `350`
- percent of analyzed episodes: `0.658`
- consensus rate: `0.909`
- SO rate: `0.283`
- SO|cons rate: `0.311`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 263 | 0.751 | 0.901 | 0.274 | 0.304 | 0.846 | 2.401 | 240.7 | 4.3 |
| instant_decision | 87 | 0.249 | 0.931 | 0.310 | 0.333 | 0.871 | 2.494 | 227.2 | 1.6 |

## multi_pair_without_all_three_common_top

- episodes: `5`
- percent of analyzed episodes: `0.009`
- consensus rate: `1.000`
- SO rate: `0.400`
- SO|cons rate: `0.400`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 4 | 0.800 | 1.000 | 0.250 | 0.250 | 0.940 | 1.750 | 96.2 | 3.0 |
| instant_decision | 1 | 0.200 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 76.0 | 2.0 |

