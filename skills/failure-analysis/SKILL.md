---
name: failure-analysis
description: "Investigate model errors, error clusters and dataset or annotation problems."
---

Start with: Verified predictions, labels/coverage, metadata, evaluation protocol and baseline predictions.

## Terms

- **False positive/negative**: an error under the recorded threshold, matching rule and annotation policy.
- **Error slice**: samples selected by one explicit predicate, with total and error counts.
- **Annotation defect**: an error established by review of the input and labeling specification.

## Do

1. Check one-to-one prediction/label joins and evaluation coverage. Missing predictions remain errors.
2. Fix threshold and protocol. Detection needs IoU, box type, class mapping, duplicates and unlabeled-positive policy.
3. Compute FP/FN/confusion counts, subgroup rates, denominators and uncertainty. Slice by meaningful data characteristics; inspect matched successes too.
4. If clustering errors, record features, distance, seed and coverage. Validate clusters against examples; post-hoc slices are hypotheses.
5. Audit labels, corruption, shift and preprocessing. Separate suspected annotation problems from confirmed model errors; compare baseline and candidate on the same samples.
6. Rank experiments that distinguish explanations. Link each recommendation to error evidence and expected change; keep sensitive sample IDs local.

Use [hypothesis-generation](../hypothesis-generation/SKILL.md): Convert the error explanations into discriminating tests.

Use [component-design](../component-design/SKILL.md): Associate a failure hypothesis with component IDs only when error evidence supports that attribution; propose a scoped discriminating change.

## Deliver

failure-analysis.md, error/slice tables, representative examples and proposed hypothesis IDs. [Template](assets/output.md).

## Stop

Do not call an apparent model error an annotation defect without review evidence. Every reported error rate needs a denominator. Every recommended fix needs a discriminating experiment. Missing predictions remain in the evaluation denominator.

## Origin

Prediction-to-error investigation is specific to this collection.
