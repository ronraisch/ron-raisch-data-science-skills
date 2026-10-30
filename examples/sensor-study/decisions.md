# Decisions

1. Before execution: use synthetic group-split sensor data for a CPU methodology demo, not a domain benchmark. Compare majority and a one-feature logistic learner, validation only.
2. After execution: retain deliberately wrong optimizer/metric runs; exclude them from scientific comparisons because verification fails. Evidence: their verification.json files.
3. Pause after the demonstration: robustness is inconclusive with one seed. Resume with independent data seeds and controlled noise tests before accessing final test outcomes.
