# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_17323`
- episode_log files read: `32`
- global_step range: `66` to `75`
- episodes analyzed: `826`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `73`
- percent of analyzed episodes: `0.088`
- consensus rate: `1.000`
- SO rate: `0.918`
- SO given consensus rate: `0.918`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |       71 | 0.973 |     1.000 | 0.915 |         0.915 |   0.989 |    1.099 |       34.7 |       1.9 |
| negotiation      |        2 | 0.027 |     1.000 | 1.000 |         1.000 |   1.000 |    1.000 |       90.5 |       4.0 |

## only_prof_1_prof_2_share_top

- episodes: `155`
- percent of analyzed episodes: `0.188`
- consensus rate: `1.000`
- SO rate: `0.748`
- SO given consensus rate: `0.748`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |      148 | 0.955 |     1.000 | 0.743 |         0.743 |   0.981 |    1.358 |       33.2 |       1.9 |
| negotiation      |        7 | 0.045 |     1.000 | 0.857 |         0.857 |   1.000 |    1.143 |       55.4 |       3.4 |

## only_prof_1_prof_3_share_top

- episodes: `143`
- percent of analyzed episodes: `0.173`
- consensus rate: `1.000`
- SO rate: `0.797`
- SO given consensus rate: `0.797`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |      102 | 0.713 |     1.000 | 0.873 |         0.873 |   0.990 |    1.176 |       39.1 |       1.9 |
| negotiation      |       41 | 0.287 |     1.000 | 0.610 |         0.610 |   0.969 |    1.634 |       66.4 |       3.2 |

## only_prof_2_prof_3_share_top

- episodes: `149`
- percent of analyzed episodes: `0.180`
- consensus rate: `1.000`
- SO rate: `0.436`
- SO given consensus rate: `0.436`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |      107 | 0.718 |     1.000 | 0.355 |         0.355 |   0.901 |    2.243 |       39.3 |       2.0 |
| negotiation      |       42 | 0.282 |     1.000 | 0.643 |         0.643 |   0.964 |    1.595 |       64.2 |       3.2 |

## no_pair_shares_top

- episodes: `296`
- percent of analyzed episodes: `0.358`
- consensus rate: `0.929`
- SO rate: `0.328`
- SO given consensus rate: `0.353`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |      206 | 0.696 |     0.990 | 0.325 |         0.328 |   0.914 |    2.338 |       40.6 |       1.9 |
| negotiation      |       90 | 0.304 |     0.789 | 0.333 |         0.423 |   0.733 |    2.085 |      159.9 |       3.7 |

## multi_pair_without_all_three_common_top

- episodes: `10`
- percent of analyzed episodes: `0.012`
- consensus rate: `1.000`
- SO rate: `0.300`
- SO given consensus rate: `0.300`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |        9 | 0.900 |     1.000 | 0.222 |         0.222 |   0.950 |    1.889 |       28.4 |       1.7 |
| negotiation      |        1 | 0.100 |     1.000 | 1.000 |         1.000 |   1.000 |    1.000 |       79.0 |       3.0 |

