---
name: experiment-design
description: "Design controlled experiments and write executable specifications before running."
---

## Inputs

Hypothesis ID, data/version, baseline, confounders and budget.

## Procedure

1. Define population, independent unit, estimand, primary metric/direction and useful effect. Separate exploratory metrics.
2. Choose simple and relevant strong baselines. Hold splits, preprocessing, evaluation, budget and seed policy fixed; label bundled changes.
3. Freeze data/split digests. Split by entity/time/scene as needed; fit preprocessing on training only. State incomplete-label and unlabeled-positive policy.
4. Plan controlled ablations and interactions. Replicate independent units; predeclare uncertainty, multiplicity and sensitivity/power limits.
5. Specify architecture, checkpoint/loading policy, trainability, optimizer, scheduler, runtime settings, steps, artifacts and environment. Fill the machine-readable template; run validate_spec.
6. Predeclare support, falsification, inconclusive and stopping rules. Keep final test sealed. Amend intent under a new experiment ID.

## Outputs and evidence

specs/<id>.json and design note with controls, replication and decision rules.

## Completion criteria

Intent is executable, immutable and capable of falsifying the hypothesis.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
