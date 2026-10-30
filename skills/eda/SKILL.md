---
name: eda
description: "Explore data for distributions, anomalies, bias and leakage before modeling."
---

## Inputs

Local data/version, dictionary, target, independent unit and planned splits.

## Procedure

1. Hash inputs. Profile schema, units, missingness, label coverage, duplicates, groups and timestamps; preserve raw files.
2. Audit leakage by entity, time, scene, near duplicates and target-derived features. Rows may not be independent.
3. Explore training data and validation metadata separately. Keep test labels sealed during tuning; disclose any test access.
4. Plot distributions, correlations, tails and subgroup differences with denominators, missing-value policy and sampling seed. Associations are exploratory, not causal.
5. Inspect anomalies alongside normal examples, including images/annotations where relevant. Separate rare valid cases from suspected data or label errors; never silently drop them.
6. Save the analysis script, tables, figures and environment. Turn findings into hypotheses; use curated upstream inspectors for additional formats.

## Outputs and evidence

eda.md, reproducible analysis, input hashes, aggregate tables, figures and leakage/bias findings.

## Completion criteria

Aggregates reproduce; sampling limits, suspicious examples and next hypotheses are recorded.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
