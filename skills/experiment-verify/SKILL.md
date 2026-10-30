---
name: experiment-verify
description: "Check whether the intended experiment actually executed, using runtime observations and artifacts. Use before expensive runs, at runtime, and after execution; never trust config alone."
---

# Experiment Verify

## Inputs

Experiment spec, data and split manifests, instrumented runtime evidence, predictions, checkpoint/artifact files, code/environment provenance.

## Procedure

1. Read docs/verification.md in the full checkout, or this skill's references/runtime-contract.md if installed alone. Locate the reusable Python verifier; copy the checkout for executable support if absent.
2. Validate the spec. Before training, hash actual data and split files; check row IDs, content/entity overlap, coverage, and labels used by preprocessing. Halt on leakage or wrong identity.
3. Observe live objects after checkpoint loading and trainer/framework overrides: model structure, named parameters/requires_grad, optimizer groups, scheduler state and effective hyperparameters. Record source hook and stage for each observation; do not copy expected values into observations.
4. Check checkpoint bytes and loading outcome (missing/unexpected keys, strictness); compare trainable names and counts, not only total parameters. A supplied path or hash cannot prove weights were loaded.
5. Capture preprocessing from executed transform objects and representative transformed batches; log fitted statistics and fit IDs. Capture runtime values at start and end; instrument per-step changes when needed.
6. Record actual completed steps, update counts, termination, checkpoint hashes, evaluation sample IDs and predictions. Recompute supported metrics from predictions and actual labels; for custom metrics supply an audited adapter and record its source digest.
7. Run `python -m tools.experiment_verification verify SPEC RUN --root PROJECT --output REPORT`. Retain nonzero exit reports. Investigate failures without deleting the original evidence.
8. Assign every requirement verified, partially_verified, failed, or unverifiable. Missing observations are unverifiable; descriptive assertions without executable evidence are partial; contradictions are failures. Aggregate conservatively.
9. Report residual limits: runtime telemetry is instrumented evidence, not cryptographic proof of honest execution; data hashes do not prove label correctness; no universal hook proves all preprocessing or distributed execution semantics.

## Outputs and evidence

verification.json and verification.md with expected/observed values, source locations, status, limitations and remedial actions.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

Every required check is accounted for; failures block promotion; partial/unverifiable results cannot be called fully verified; original evidence remains accessible.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
