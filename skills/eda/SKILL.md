---
name: eda
description: "Explore data for distributions, anomalies, bias and leakage before modeling."
---

Start with: Local data/version, dictionary, target, independent unit and planned splits.

## Terms

- **Independent unit**: the entity whose observations can vary independently, such as a patient or acquisition.
- **Leakage**: evaluation information entering training, preprocessing fitting or model selection.

## Do

1. Hash inputs. Profile schema, units, missingness, label coverage, duplicates, groups and timestamps; preserve raw files.
2. Audit leakage by entity, time, scene, near duplicates and target-derived features. Rows may not be independent.
3. Explore training data and validation metadata separately. Keep test labels sealed during tuning; disclose any test access.
4. Plot distributions, correlations, tails and subgroup differences with denominators, missing-value policy and sampling seed. Associations are exploratory, not causal.
5. Inspect anomalies alongside normal examples, including images/annotations where relevant. Separate rare valid cases from suspected data or label errors; never silently drop them.
6. Save the analysis script, tables, figures and environment. Turn findings into hypotheses; use curated upstream inspectors for additional formats.

Use [experiment-verify](../experiment-verify/SKILL.md): Use its input/split checks; inspect domain leakage that the adapter does not cover.

## Deliver

eda.md, reproducible analysis, input hashes, aggregate tables, figures and leakage/bias findings. [Template](assets/output.md).

## Stop

Stop model development if split leakage is found. Save the violating IDs and correct the split under a new version. Finish EDA when aggregates reproduce and each proposed explanation is labeled as a hypothesis.

## Source

Adapted workflow concepts from [K-Dense-AI/scientific-agent-skills — exploratory-data-analysis](https://github.com/K-Dense-AI/scientific-agent-skills/blob/5f2bc0341354fd5590aef76a533ada1e1e5b4e62/skills/exploratory-data-analysis/SKILL.md) (MIT); specialized for this collection’s local records.
