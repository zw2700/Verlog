# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_16403.jsonl`
- episode_log files read: `1`
- global_step range: `66` to `75`
- episodes analyzed: `728`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `37`
- percent of analyzed episodes: `0.051`
- consensus rate: `1.000`
- SO rate: `0.946`
- SO given consensus rate: `0.946`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |       36 | 0.973 |     1.000 | 0.944 |         0.944 |   0.984 |    1.111 |       53.8 |       1.9 |
| negotiation      |        1 | 0.027 |     1.000 | 1.000 |         1.000 |   1.000 |    1.000 |       82.0 |       3.0 |

## only_prof_1_prof_2_share_top

- episodes: `126`
- percent of analyzed episodes: `0.173`
- consensus rate: `0.992`
- SO rate: `0.738`
- SO given consensus rate: `0.744`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |      111 | 0.881 |     1.000 | 0.811 |         0.811 |   0.989 |    1.225 |       49.0 |       2.0 |
| negotiation      |       15 | 0.119 |     0.933 | 0.200 |         0.214 |   0.832 |    2.357 |      170.3 |       4.9 |

## only_prof_1_prof_3_share_top

- episodes: `156`
- percent of analyzed episodes: `0.214`
- consensus rate: `0.968`
- SO rate: `0.647`
- SO given consensus rate: `0.669`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision             |       81 | 0.519 |     1.000 | 0.741 |         0.741 |   0.973 |    1.420 |       68.3 |       1.8 |
| negotiation                  |       74 | 0.474 |     0.946 | 0.554 |         0.586 |   0.892 |    1.714 |      136.7 |       3.8 |
| stalled_coordination_failure |        1 | 0.006 |     0.000 | 0.000 |            NA |   0.000 |       NA |      516.0 |      43.0 |

## only_prof_2_prof_3_share_top

- episodes: `121`
- percent of analyzed episodes: `0.166`
- consensus rate: `1.000`
- SO rate: `0.579`
- SO given consensus rate: `0.579`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation      |       67 | 0.554 |     1.000 | 0.746 |         0.746 |   0.976 |    1.373 |      104.3 |       3.3 |
| instant_decision |       54 | 0.446 |     1.000 | 0.370 |         0.370 |   0.906 |    2.130 |       66.4 |       1.9 |

## no_pair_shares_top

- episodes: `279`
- percent of analyzed episodes: `0.383`
- consensus rate: `0.903`
- SO rate: `0.391`
- SO given consensus rate: `0.433`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |      147 | 0.527 |     0.946 | 0.422 |         0.446 |   0.891 |    2.007 |       94.5 |       1.8 |
| negotiation      |      132 | 0.473 |     0.856 | 0.356 |         0.416 |   0.801 |    2.168 |      197.8 |       4.6 |

## multi_pair_without_all_three_common_top

- episodes: `9`
- percent of analyzed episodes: `0.012`
- consensus rate: `1.000`
- SO rate: `0.333`
- SO given consensus rate: `0.333`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |        6 | 0.667 |     1.000 | 0.500 |         0.500 |   0.927 |    2.000 |       59.2 |       1.8 |
| negotiation      |        3 | 0.333 |     1.000 | 0.000 |         0.000 |   0.892 |    2.667 |       99.3 |       3.0 |

