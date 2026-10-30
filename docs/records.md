# Research continuity records

Use the lightweight v1 [record contract](record-contract.md). Start with templates/project.json and the Markdown templates. The generated example and committed examples/sensor-study directory demonstrate a complete record. No database migration or service is involved.

`project.json` is the index, not the only truth. Keep immutable experiment specifications, unique run directories with evidence, a dated append-only decision history, and a human handoff. Keep technical process failure separate from verification failure and scientific rejection. Large artifacts may live in an approved artifact store, but preserve content hashes and an access/recovery note; the bundled verifier only reads local artifacts, so materialize external files before verification.

```bash
python -m tools.experiment_verification records PROJECT
python -m tools.experiment_verification resume PROJECT --output PROJECT/resume-new.md
```

The validator checks schema essentials, IDs, references, run status, hypothesis references and required local evidence paths. It does not prove every prose claim or enforce an exhaustive schema for future scientific domains. Resume recomputes current run verification and lists unregistered run directories. It never treats old verification.json as a permanent certificate. Missing or altered files disqualify a run from best-verified results.

Comparison cohorts use dataset digest, split digest, evaluation protocol and metric (name/split/direction). Ties are preserved. Only completed, currently verified runs can be best. **This grouping is necessary but insufficient for a controlled ablation**: the skill also audits budget, seed policy, preprocessing, pretraining and changed factors. The same metric string cannot rescue a different evaluation implementation; encode its digest/version in evaluation_protocol. Never compare AP50 to mAP50:95 or rotated to horizontal boxes merely because a chart labels both “AP”.

Pausing: update status/pause_reason, handoff, next_experiments, and a decision. Run the validator and a cold-start smoke reproduction. Resuming: revalidate available bytes, read original decisions, identify old versus current conclusions, check changed constraints, and recommend a new immutable experiment. Keep project status paused until continuation actually begins. Unknown history stays unknown.
