# Resume: Synthetic sensor classification

Question: Does a learned sensor-score classifier improve over a majority baseline?

Status: paused
Pause reason: Demo milestone complete; multi-seed robustness study needs a new design.

## Hypotheses

- H1: Learned score improves accuracy by at least 0.10 — recorded status inconclusive (interpretation, not auto-inferred)

## Registered runs (verification recomputed from present artifacts)

| Run | Process | Verification | Result |
| --- | --- | --- | --- |
| majority | completed | verified | 0.625 |
| logistic | completed | verified | 0.85 |
| wrong-optimizer | completed | failed | 0.85 |
| wrong-metric | completed | failed | 1.0 |

## Best verified results by comparison cohort

- Cohort 1: {'direction': 'maximize', 'name': 'accuracy', 'split': 'validation'}; best: [{'id': 'logistic', 'value': 0.85}]. Audit budget/seeds/factors before causal conclusions.

## Evidence gaps and failures

- wrong-optimizer: runtime.optimizer: failed
- wrong-metric: metric.recomputed: failed
- Unregistered run directories: none found

## Findings (recorded claims; inspect cited evidence)

- F1 [observation]: Fixed-split classifier and baseline results are recorded; interpretation is limited to one seed. Evidence: comparison.json, summary.md
- F2 [negative-result]: Wrong optimizer and reported metric invalidate those executions, not H1. Evidence: runs/wrong-optimizer/verification.json, runs/wrong-metric/verification.json

## Recommended next experiments (recorded, not auto-approved)

- Parameterize the fixed generator seed and predeclare paired independent data-seed replication
- Controlled noise versus nonlinear-boundary experiment

## Required cold-start work

Read handoff/decisions and original artifacts; audit runtime hooks. Reproduce the smallest run in a new output directory. Check current data/environment access. Reassess old interpretations before changing status. Offline literature cutoff and absent records remain unknown.

This report inventories evidence. It does not reconstruct missing conversations or infer scientific support from a score.
