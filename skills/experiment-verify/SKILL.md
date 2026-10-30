---
name: experiment-verify
description: "Check intended versus actual execution using runtime evidence and artifacts."
---

## Inputs

Spec, actual data/splits, runtime hooks, predictions, artifacts and code/environment provenance.

## Procedure

1. Read [runtime-contract.md](references/runtime-contract.md). Validate intent; preflight actual data/split hashes, ID coverage and entity leakage before training.
2. Observe live preprocessing and fit IDs, transformed batches, instantiated model and named trainable/frozen parameters. Capture after trainer overrides; never copy expected values into observations.
3. Hash actual pretrained weights and record the real loader result, missing/unexpected keys and strictness. A path or digest does not prove loading.
4. Capture effective optimizer groups, scheduler/LR, hyperparameters, consumed data, completed updates, termination and checkpoints. Start/end snapshots cannot establish every intermediate step.
5. Read artifact bytes and prediction IDs/targets. Recompute supported metrics; custom protocols need audited adapters. Capture Git revision, dirty/source hashes and dependencies.
6. Run `python -m tools.experiment_verification verify SPEC RUN --root PROJECT --output REPORT`. Retain failures. Mark each check verified, partially_verified, failed or unverifiable; block promotion unless all required checks verify.

## Outputs and evidence

verification.json/.md: expected, observed, source, status, limitations and remediation.

## Completion criteria

Every requirement is accounted for. Missing evidence stays unknown; instrumented telemetry is not independent proof of honest execution or label correctness.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
