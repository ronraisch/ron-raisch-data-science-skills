---
name: failure-analysis
description: "Investigate false positives, false negatives, error clusters and dataset problems. Use when aggregate metrics hide failure modes or experiments regress."
---

# Failure Analysis

## Inputs

Predictions keyed by sample ID, actual labels and annotation coverage, split definition, metadata, baseline predictions and verification reports.

## Procedure

1. Verify prediction/label joins are one-to-one and cover the specified evaluation set. Preserve missing predictions as failures rather than dropping rows.
2. Fix the operating threshold and metric protocol before categorizing errors. For detection record IoU, rotated/horizontal boxes, class mapping, duplicate handling and unlabeled-positive policy.
3. Compute confusion counts, per-class rates, denominators and uncertainty. Slice by meaningful features (size, scene, sensor, subgroup, missingness) and inspect both errors and matched successes.
4. Cluster error representations only as an exploratory aid; report feature choice, distance, seed and sample coverage. Validate clusters against representative examples.
5. Audit a sample of apparent errors for ambiguous/missing labels, corrupt input, distribution shift and preprocessing differences. Keep suspected annotation issues separate from confirmed model errors.
6. Compare baseline/candidate on the same examples. Quantify whether a gain trades one error type or subgroup for another. Treat post-hoc slices as hypotheses, not confirmatory discoveries.
7. Propose a ranked set of experiments that distinguish explanations. Link each recommendation to error evidence and expected improvement; keep raw IDs local when sensitive.

## Outputs and evidence

failure-analysis.md; error table with sample IDs/type/slice/evidence; aggregate rates and recommended hypothesis IDs.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

Findings have denominators and examples; data/annotation/model explanations are separated; proposed fixes have discriminating tests.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
