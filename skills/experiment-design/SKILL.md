---
name: experiment-design
description: "Design controlled experiments and write executable specifications before running."
---

## Inputs

Hypothesis ID, data/version, baseline, confounders and budget.

## Definitions

- **Baseline**: a named reference method evaluated under the same protocol.
- **Controlled comparison**: only declared treatment factors vary; all listed controls stay fixed.
- **Ablation**: a controlled comparison that removes or changes a declared component.

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

Do not run with unknown input hashes, undefined primary metric, absent baseline or unfilled runtime settings. Freeze the spec before execution. Any change to intent requires a new experiment ID and amendment reason.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
