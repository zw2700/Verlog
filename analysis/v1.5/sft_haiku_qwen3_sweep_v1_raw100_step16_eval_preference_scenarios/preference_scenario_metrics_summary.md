# Preference Scenario Metrics Summary

- episode_log: `outputs/sft/evaluations/haiku_qwen3_sweep_v1/raw100_step16/episodes.jsonl`
- episode_log files read: `1`
- global_step range: `None` to `None`
- episodes analyzed: `500`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `47`
- percent of analyzed episodes: `0.094`
- consensus rate: `0.979`
- SO rate: `0.723`
- SO given consensus rate: `0.739`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |       28 | 0.596 |     1.000 | 0.893 |         0.893 |   0.988 |    1.179 |       58.6 |       2.2 |
| negotiation      |       19 | 0.404 |     0.947 | 0.474 |         0.500 |   0.800 |    1.889 |      165.0 |       4.7 |

## only_prof_1_prof_2_share_top

- episodes: `80`
- percent of analyzed episodes: `0.160`
- consensus rate: `1.000`
- SO rate: `0.613`
- SO given consensus rate: `0.613`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation      |       42 | 0.525 |     1.000 | 0.500 |         0.500 |   0.926 |    1.833 |      161.0 |       4.8 |
| instant_decision |       38 | 0.475 |     1.000 | 0.737 |         0.737 |   0.972 |    1.342 |       53.2 |       2.0 |

## only_prof_1_prof_3_share_top

- episodes: `105`
- percent of analyzed episodes: `0.210`
- consensus rate: `0.962`
- SO rate: `0.667`
- SO given consensus rate: `0.693`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation      |       79 | 0.752 |     0.949 | 0.658 |         0.693 |   0.911 |    1.573 |      173.0 |       5.1 |
| instant_decision |       26 | 0.248 |     1.000 | 0.692 |         0.692 |   0.948 |    1.423 |       45.3 |       2.2 |

## only_prof_2_prof_3_share_top

- episodes: `97`
- percent of analyzed episodes: `0.194`
- consensus rate: `0.959`
- SO rate: `0.629`
- SO given consensus rate: `0.656`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation      |       73 | 0.753 |     0.945 | 0.658 |         0.696 |   0.908 |    1.435 |      175.8 |       4.8 |
| instant_decision |       24 | 0.247 |     1.000 | 0.542 |         0.542 |   0.961 |    1.750 |       47.1 |       2.3 |

## no_pair_shares_top

- episodes: `168`
- percent of analyzed episodes: `0.336`
- consensus rate: `0.905`
- SO rate: `0.375`
- SO given consensus rate: `0.414`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |      116 | 0.690 |     0.862 | 0.302 |         0.350 |   0.799 |    2.340 |      234.8 |       6.5 |
| instant_decision             |       51 | 0.304 |     1.000 | 0.549 |         0.549 |   0.951 |    1.843 |       49.5 |       2.1 |
| stalled_coordination_failure |        1 | 0.006 |     1.000 | 0.000 |         0.000 |   0.967 |    2.000 |      328.0 |      33.0 |

## multi_pair_without_all_three_common_top

- episodes: `3`
- percent of analyzed episodes: `0.006`
- consensus rate: `1.000`
- SO rate: `0.000`
- SO given consensus rate: `0.000`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision |        2 | 0.667 |     1.000 | 0.000 |         0.000 |   0.938 |    2.000 |       36.5 |       2.5 |
| negotiation      |        1 | 0.333 |     1.000 | 0.000 |         0.000 |   0.985 |    2.000 |      105.0 |       3.0 |

