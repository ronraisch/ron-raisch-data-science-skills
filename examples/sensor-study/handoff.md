# Handoff

This is a reproducible synthetic study, not a real sensor result. Start with brief.md, hypotheses.json, summary.md and ablation-review.md. specs/ preserves intent; runs/ includes completed valid and intentionally invalid executions. Each run has its own spec snapshot and provenance. The strongest eligible run is derived by the resume utility within a single validation cohort; do not compare its score to another dataset/split.

Reproduce from the repository root with Python 3.11+: `python -m examples.demo --output /tmp/fresh-sensor-study`. No dependencies or GPU needed. The command refuses an existing destination. Run the verification and resumption commands in README. Check the source/environment fields from the new execution instead of expecting an identical Git revision after code edits.

Smoke check: two eligible runs, wrong optimizer and metric failures, valid project records. Actual tested commands/results are recorded in docs/validation.md in the delivered repository. Data is generated locally with seed 17; no access credentials or downloads. Relative artifact paths and content hashes are preserved. Source hashes are in each run's source.json. Checkpoints store live fitted weight/bias as JSON, not pickle.

Paused because the demo milestone is complete and H1 needs multi-seed follow-up. Do not repeat the invalid runs as scientific evidence. Next: paired group/data-seed replication, controlled label-noise experiment, then frozen test evaluation. Domain validation is a separate question.
