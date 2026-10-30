---
name: experiment-verify
description: "Check intended versus actual execution using runtime evidence and artifacts."
---

## Inputs

Spec, actual data/splits, runtime hooks, predictions, artifacts and code/environment provenance.

## Definitions

- **Intent**: the frozen experiment specification.
- **Observation**: a value captured from the executing object, process or artifact, with source and stage.
- **Verified check**: the implemented check passed against identified evidence; this does not establish untested properties.

## Procedure

1. Read [runtime-contract.md](references/runtime-contract.md). Validate intent; preflight actual data/split hashes, ID coverage and entity leakage before training.
2. Observe live preprocessing and fit IDs, transformed batches, instantiated model and named trainable/frozen parameters. Capture after trainer overrides; never copy expected values into observations.
3. Hash actual pretrained weights and record the real loader result, missing/unexpected keys and strictness. A path or digest does not prove loading.
4. Capture effective optimizer groups, scheduler/LR, hyperparameters, consumed data, completed updates, termination and checkpoints. Start/end snapshots cannot establish every intermediate step.
5. Read artifact bytes and prediction IDs/targets. Recompute supported metrics; custom protocols need audited adapters. Capture Git revision, dirty/source hashes and dependencies. Aggregate mixed verified/unknown checks as partially_verified; all-unknown checks are unverifiable.
6. Run `python -m tools.experiment_verification verify SPEC RUN --root PROJECT --output REPORT`. Retain failures. Mark each check verified, partially_verified, failed or unverifiable; block promotion unless all required checks verify.

## Outputs and evidence

verification.json/.md: expected, observed, source, status, limitations and remediation.

## Completion criteria

Use exactly four check states: verified = check passed; partially_verified = matching claim with incomplete evidence; failed = evidence contradicts intent or protocol; unverifiable = required evidence absent or unsupported. Any failed check fails the run. Only all-verified required checks permit promotion. Retain the original report.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
