# Research summary

Question: Does a one-feature learned classifier improve over the majority baseline for this synthetic sensor dataset?

Observed: validation accuracy 0.8500 versus 0.6250; evidence runs/logistic and runs/majority with verification.json and predictions.csv. Interpretation: the feature is useful on this fixed validation split; robustness and real-world transfer remain unproven. See ablation-review.md and comparison.json for uncertainty.

Negative/failed outcomes: optimizer override and metric reporting injection were detected. These are technical invalidations, not evidence against H1. Synthetic label noise remains an unresolved limit. Final test data was not used for choices or reported results.

Next: repeat with independent paired data seeds, audit error slices, and evaluate once on a sealed final test protocol after model selection. This milestone is paused for that design review.
