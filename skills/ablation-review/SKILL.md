---
name: ablation-review
description: "Compare experiments fairly, quantify uncertainty and bound conclusions."
---

## Inputs

Specs, process/verification states, predictions, seed/unit metadata and decision rules.

## Definitions

- **Evaluation cohort**: identical dataset/split digests, evaluation implementation/protocol and metric definition.
- **Controlled ablation**: a cohort comparison with declared changes and fixed budget, seed policy, preprocessing and pretraining controls.
- **Best verified result**: the eligible result maximizing/minimizing the primary metric within one cohort; preserve ties.

## Procedure

1. Revalidate evidence. Exclude invalid runs from best-verified claims, but retain their existence and failure reasons.
2. Group by data/split digests, evaluation implementation/protocol and metric/split/direction. Use best_runs for these cohorts; audit controls separately.
3. List every changed factor: preprocessing, pretraining, budget, seeds, architecture and settings. Multiple changes support only a bundle-level conclusion; epochs alone do not equal compute.
4. Compute paired effects and justified uncertainty. Resample independent patients/scenes/groups, not correlated rows. Separate seed and sampling variance.
5. Apply the predeclared useful-effect rule. Disclose multiplicity, selection and test reuse; one run cannot establish robustness.
6. Mark hypotheses supported, rejected or inconclusive. Save best results per cohort, negative findings, limitations and the next decisive test.

## Outputs and evidence

ablation-review.md, comparison/cohort table, effect sizes/intervals and evidence-linked conclusions.

## Completion criteria

Different cohorts cannot share a winner. Multiple changed factors support only a bundle-level conclusion. Report effect size and uncertainty against the predefined useful-effect threshold. Classify support using the design rule, not an after-the-fact narrative.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
