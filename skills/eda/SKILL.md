---
name: eda
description: "Explore local data reproducibly for distributions, correlations, anomalies, bias and leakage. Use before modeling or when a dataset changes."
---

# Eda

## Inputs

Dataset paths/version, data dictionary, observational unit, intended splits, target and intended deployment population.

## Procedure

1. Hash inputs and inventory schema, dimensions, units, missingness, label coverage, duplicates, groups, and timestamps. Preserve raw data; use derived copies for transformations.
2. Determine the independent unit (patient, scene, acquisition, user), not merely the row. Audit shared entities, near duplicates, spatial/temporal neighbors, and target-derived features across splits.
3. Profile train/validation metadata separately. Keep test labels sealed during exploratory tuning; report any authorized test access as a deviation.
4. Plot distributions, missingness, target balance, stratified relationships, and suspicious tails with denominators. Examine small and underrepresented groups; record sample selection and seed.
5. Compute correlations and associations with an explicit missing-value policy and multiplicity caveat. Inspect whether a relationship disappears after grouping; do not infer causality.
6. Inspect representative and extreme examples, including CV images/annotations where relevant. Separate plausible rare cases from annotation/data errors; propose corrections without silently deleting them.
7. Save executable analysis, aggregate tables, figures, environment, and a finding-to-hypothesis table. The CPU example demonstrates stdlib profiling; use curated upstream EDA tooling for additional file formats.

## Outputs and evidence

eda.md; reproducible analysis script/notebook; input hashes; aggregate tables and figures; leakage/bias findings with counts.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

Another researcher can reproduce aggregates; sampling limits and test access are disclosed; anomalies are linked to examples and hypotheses rather than removed without justification.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
