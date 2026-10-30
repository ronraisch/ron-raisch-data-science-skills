---
name: failure-analysis
description: "Investigate model errors, error clusters and dataset or annotation problems."
---

## Inputs

Verified predictions, labels/coverage, metadata, evaluation protocol and baseline predictions.

## Procedure

1. Check one-to-one prediction/label joins and evaluation coverage. Missing predictions remain errors.
2. Fix threshold and protocol. Detection needs IoU, box type, class mapping, duplicates and unlabeled-positive policy.
3. Compute FP/FN/confusion counts, subgroup rates, denominators and uncertainty. Slice by meaningful data characteristics; inspect matched successes too.
4. If clustering errors, record features, distance, seed and coverage. Validate clusters against examples; post-hoc slices are hypotheses.
5. Audit labels, corruption, shift and preprocessing. Separate suspected annotation problems from confirmed model errors; compare baseline and candidate on the same samples.
6. Rank experiments that distinguish explanations. Link each recommendation to error evidence and expected change; keep sensitive sample IDs local.

## Outputs and evidence

failure-analysis.md, error/slice tables, representative examples and proposed hypothesis IDs.

## Completion criteria

Findings have denominators and examples; proposed fixes test an explanation.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
