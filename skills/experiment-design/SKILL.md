---
name: experiment-design
description: "Design controlled ML or scientific experiments with falsification rules and machine-readable specs. Use before data collection, training, ablation, or evaluation."
---

# Experiment Design

## Inputs

Hypothesis ID, baseline, data/version, resource limits, measurement plan, and known confounders.

## Procedure

1. Define the independent unit, estimand, population, primary metric, direction and minimum useful effect before running. Separate secondary/exploratory metrics.
2. Specify a simple baseline and strongest feasible relevant baseline. Hold splits, preprocessing, evaluation implementation, budget and seed policy fixed for a controlled comparison.
3. Freeze dataset and split manifests by digest. Split by entity/time/scene where needed. Fit preprocessing on training data only. State how unlabeled positives and incomplete annotations are evaluated.
4. Choose controlled factors and ablations; include interaction tests when factors may interact. Treat an architecture+augmentation change as a bundle, not evidence for either alone.
5. Plan replication at the independent unit, paired seeds/samples, uncertainty and multiplicity policy. Record a power/sensitivity justification or explicitly state exploratory limitations.
6. Specify actual model structure, checkpoint digest and loading policy, frozen/trainable parameters, optimizer, scheduler, runtime hyperparameters, step budget, artifact outputs and environment.
7. Copy the spec template, fill expected observations, generate hashes, and validate with the verifier's validate_spec function. Never leave placeholders in a runnable spec.
8. Define support/falsification/inconclusive outcomes and stopping rules. Seal the test protocol; use validation for choices. Amend specs under a new ID with a reason; do not rewrite intent after seeing results.

## Outputs and evidence

specs/<experiment-id>.json; preregistration/design note with baselines, ablations, replication plan and decision rules.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

A runnable spec has immutable inputs, measurable predictions and comparison controls; scientific protocol and executable settings agree.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
