---
name: eda
description: "Explore data for distributions, anomalies, bias and leakage before modeling."
---

## Inputs

Local data/version, dictionary, target, independent unit and planned splits.

## Definitions

- **Independent unit**: the entity whose observations can vary independently, such as a patient or acquisition.
- **Leakage**: evaluation information entering training, preprocessing fitting or model selection.
- **Finding**: a measured pattern with a denominator, input identity and analysis command.

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

Stop model development if split leakage is found. Save the violating IDs and correct the split under a new version. Finish EDA when aggregates reproduce and each proposed explanation is labeled as a hypothesis.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
