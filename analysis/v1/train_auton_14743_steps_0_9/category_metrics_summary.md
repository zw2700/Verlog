# Category Metrics Summary

- episode_log: `logs/episode_log_train_auton_14743.jsonl`
- global_step range: `0` to `9`
- episodes analyzed: `7168`
- overall consensus rate: `0.685`
- overall SO rate: `0.138`
- overall SO given consensus rate: `0.201`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |     5917 | 0.825 |     0.655 | 0.125 |         0.191 |   0.557 |    4.357 |      308.6 |      13.7 |
| instant_decision             |     1014 | 0.141 |     0.991 | 0.239 |         0.241 |   0.854 |    4.118 |       38.8 |       3.1 |
| stalled_coordination_failure |      236 | 0.033 |     0.114 | 0.021 |         0.185 |   0.096 |    4.074 |      487.4 |      27.2 |
| malformed_or_other           |        1 | 0.000 |     1.000 | 0.000 |         0.000 |   0.716 |    2.000 |      274.0 |      15.0 |
