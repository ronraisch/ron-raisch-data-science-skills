# Verification: wrong-metric

Status: **failed**

| Check | Status | Source | Detail |
| --- | --- | --- | --- |
| dataset.identity | verified | data.csv |  |
| splits.identity | verified | splits.json |  |
| test.duplicate_features | verified | data.csv | Exact x overlap needs domain review; near duplicates not checked. |
| train.duplicate_features | verified | data.csv | Exact x overlap needs domain review; near duplicates not checked. |
| validation.duplicate_features | verified | data.csv | Exact x overlap needs domain review; near duplicates not checked. |
| splits.isolation | verified | splits.json | Checked IDs and declared groups; spatial/temporal/near-duplicate leakage requires adapters. |
| spec.identity | verified | /workspace/scratch/c3cb0966d532/ron-raisch-data-science-skills/examples/sensor-study/specs/logistic.json |  |
| runtime.checkpoint | verified | Classifier initialized from scratch; no weight loader | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.environment | verified | capture_environment | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.hyperparameters | verified | run: active seed/batch locals | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.metric | verified | run: evaluation branch and evaluator | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.model | verified | Classifier.architecture | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.optimizer | verified | SGD.snapshot at start | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.parameters | verified | Classifier.parameters | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.preprocessing | verified | Standardizer.fit(train).snapshot | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.scheduler | verified | run: no scheduler instantiated | Evidence quality depends on the runtime hook; inspect instrumented code. |
| runtime.training | verified | SGD.fit returned history length | Evidence quality depends on the runtime hook; inspect instrumented code. |
| environment.git_provenance | verified | runtime environment hook |  |
| artifact.required.checkpoint.json | verified |  | Required artifact inventory |
| artifact.required.history.json | verified |  | Required artifact inventory |
| artifact.required.source.json | verified |  | Required artifact inventory |
| artifact.required.spec.json | verified |  | Required artifact inventory |
| artifact.0 | verified | runs/wrong-metric/checkpoint.json |  |
| artifact.1 | verified | runs/wrong-metric/history.json |  |
| artifact.2 | verified | runs/wrong-metric/source.json |  |
| artifact.3 | verified | runs/wrong-metric/spec.json |  |
| metric.recomputed | failed | runs/wrong-metric/predictions.csv |  |

## Limits

- Instrumented runtime evidence is not independent attestation.
- CSV adapter checks binary accuracy/MAE, IDs and declared groups only.
- Data semantics, label quality, near duplicates, and uninstrumented behavior remain unproven.

Expected/observed values are preserved in the adjacent JSON report.
