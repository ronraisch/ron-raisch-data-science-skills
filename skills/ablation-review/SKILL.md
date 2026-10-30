---
name: ablation-review
description: "Compare completed experiments fairly, quantify uncertainty, and bound conclusions. Use for ablations, model selection, baseline comparisons and result promotion."
---

# Ablation Review

## Inputs

Run specs, verification reports, prediction artifacts, metrics, seed/unit metadata and predeclared decision rule.

## Procedure

1. Check verification status and completion independently. Exclude failed/unverifiable runs from best-verified claims, but include their existence and reasons in the review.
2. Construct comparison cohorts from dataset digest, split digest, preprocessing/evaluation protocol, metric/split/direction, training budget and allowed varying factors. Use best_runs for strict metric/evaluation cohorts, then manually audit experimental controls.
3. List every changed factor. When multiple factors differ, attribute only to the bundle; do not call it a controlled ablation. Equal epochs may hide unequal updates, examples, compute or pretraining.
4. Compute paired differences on matched seeds or independent units. Use a justified interval/test; resample patients/scenes rather than correlated rows when applicable. State seed variance and sampling variance separately.
5. Compare effect size and uncertainty against the minimum useful effect, not only p-values. Disclose multiple comparisons, validation selection, and test reuse. One run cannot establish robustness.
6. Mark each hypothesis supported, rejected, or inconclusive using its predeclared rule. Missing evidence stays inconclusive. Do not rank incomparable metrics together.
7. Update best-results by cohort with report/artifact links and limitations. Preserve negative results and the next decisive experiment.

## Outputs and evidence

ablation-review.md; cohort comparison table with changed factors, deltas/intervals, evidence and bounded conclusions; project finding updates.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

No unsupported causal attribution or incomparable winner; uncertainty and exclusions are visible; each conclusion links to runs.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
