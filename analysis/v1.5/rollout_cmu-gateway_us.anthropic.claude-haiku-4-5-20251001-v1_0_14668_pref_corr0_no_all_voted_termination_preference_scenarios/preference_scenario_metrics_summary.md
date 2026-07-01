# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_rollout_cmu-gateway_us.anthropic.claude-haiku-4-5-20251001-v1_0_14668_pref_corr0_no_all_voted_termination.jsonl`
- global_step range: `None` to `None`
- episodes analyzed: `100`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## only_prof_1_prof_2_share_top

- episodes: `16`
- percent of analyzed episodes: `0.160`
- consensus rate: `1.000`
- SO rate: `0.688`
- SO|cons rate: `0.688`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 15 | 0.938 | 1.000 | 0.733 | 0.733 | 0.987 | 1.333 | 37.3 | 2.0 |
| negotiation | 1 | 0.062 | 1.000 | 0.000 | 0.000 | 1.000 | 2.000 | 218.0 | 5.0 |

## only_prof_1_prof_3_share_top

- episodes: `16`
- percent of analyzed episodes: `0.160`
- consensus rate: `1.000`
- SO rate: `0.562`
- SO|cons rate: `0.562`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 16 | 1.000 | 1.000 | 0.562 | 0.562 | 0.986 | 1.750 | 70.9 | 3.0 |

## only_prof_2_prof_3_share_top

- episodes: `6`
- percent of analyzed episodes: `0.060`
- consensus rate: `1.000`
- SO rate: `0.667`
- SO|cons rate: `0.667`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 5 | 0.833 | 1.000 | 0.600 | 0.600 | 0.973 | 1.800 | 102.8 | 5.2 |
| instant_decision | 1 | 0.167 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 36.0 | 3.0 |

## no_pair_shares_top

- episodes: `62`
- percent of analyzed episodes: `0.620`
- consensus rate: `0.935`
- SO rate: `0.565`
- SO|cons rate: `0.603`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 62 | 1.000 | 0.935 | 0.565 | 0.603 | 0.907 | 1.603 | 304.0 | 13.4 |

