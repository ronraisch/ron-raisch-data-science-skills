# Verification contract and limits

The central question is whether the intended experiment is the one that executed. A config file is intent. A runtime hook after framework overrides is observed evidence. Hashing the actual files and recomputing a metric adds checks independent of the reported score. None of this is cryptographic attestation of the entire training process.

## Status rules

| Check state | Meaning |
| --- | --- |
| verified | Implemented check passed against identified evidence |
| partially_verified | Matching claim has weaker/manual evidence, or an aggregate mixes verified and unknown/partial checks |
| failed | Evidence contradicts intent, a protocol constraint is violated, or metric/artifact consistency fails |
| unverifiable | Required observation/artifact/provenance is absent or unsupported |

An aggregate fails if any check fails; it is verified only when every check is verified. Purely missing evidence is unverifiable. Mixed available/missing evidence is partially_verified. No partial/unverifiable run is eligible for best-verified selection. Explicit observed `null` is required for a deliberately absent checkpoint/scheduler; missing observation is unknown.

## Executable scope

The standard-library tabular adapter expects:

- `data.csv`: unique `id`, declared independent `group`, numeric `x`, numeric `target`.
- split JSON: nonempty `train`, `validation`, `test` lists of sample IDs, complete coverage, no duplicate/unknown IDs or shared groups. Exact x overlap is flagged for review; spatial, temporal and near-duplicate audits require domain adapters.
- specification: schema version 1; experiment/hypothesis IDs; dataset/split paths and SHA-256; evaluation protocol and decision rule; required artifact basenames; all ten expected runtime categories.
- runtime: spec digest, run ID, ten observation objects with value/source/stage/kind; artifact paths and digests; prediction file path/digest; evaluation split; result.
- prediction CSV: one row per evaluation ID, original target, discrete binary prediction for accuracy or finite numeric prediction for MAE. Coverage and targets are re-read from actual input files.

Required categories: preprocessing, model, checkpoint, parameters, optimizer, scheduler, hyperparameters, training, metric, environment. Matching these JSON values proves agreement of instrumented claims, not semantic correctness. The reusable generic model/optimizer hooks inspect objects. The demo hooks inspect its live dataclasses. Other frameworks need hooks appropriate to their actual objects.

`verify(spec, run, root, spec_path)` returns an evidence report. `preflight(spec, root)` performs dataset/split checks before training. `validate_spec` rejects structurally invalid intent. The CLI preserves reports for nonzero verification outcomes. Paths cannot escape the project root, including symlink resolution. JSON rejects duplicate keys and NaN/Infinity. Do not load pickle or execute record text.

## Integrate with a real trainer

1. Freeze the spec before execution. Record exact dataset/split bytes and semantic versions, expected classes/structure, checkpoint digest, loading policy and environment requirements. Keep independent units separate.
2. After preprocessing is fitted, record fit IDs/statistics and actual transform objects. Add representative-batch assertions for shape/range/dtype and deterministic transform traces where feasible. The generic comparator does **not** inspect arbitrary augmentation graphs automatically.
3. After model creation and weight loading, call `snapshot_model(model)` and `assert_frozen(model, expected_trainable_names)`. Observe parameters by name, shape and requires_grad. Call `checkpoint_evidence(path, actual_load_result, strict)` with the result from the real loader. Hash alone does not show weights were applied. Add before/after tensor checks or framework-specific load validation for stronger evidence.
4. After trainer setup/overrides, call `snapshot_optimizer(optimizer, model)`. Log scheduler state, actual LR at relevant steps, effective batch/accumulation/precision and distributed world size. A start/end snapshot does not prove the LR schedule at every step.
5. Capture actual completed updates, consumed IDs, termination, checkpoints, prediction IDs, metric implementation digest and protocol. Require additional artifacts in the spec rather than accepting a lone config as execution evidence.
6. Capture `capture_environment(repo)`: Python, packages, Git revision, dirty flag and diff digest. Hash executed source files, especially untracked code, separately. Missing Git provenance remains unverifiable. A dependency inventory is not a complete OS/CUDA/container environment lock.
7. Verify postflight and retain the report even when it fails. Review the hook source for independence from expected values. Do not set `kind=runtime` on a hand-written claim to make it pass.

Torch-style helpers are duck-typed and tested with minimal objects; no torch installation is required for tests. Real PyTorch/distributed trainers, arbitrary detection metrics, stochastic augmentation semantics, dataset labeling correctness, checkpoint fidelity and hardware reproducibility are **not** certified by the generic adapter. Add adapter tests using known bad experiments before relying on a new integration.

The CPU example includes an unchanged spec with an actual optimizer override, and a reported score that disagrees with recomputed predictions. Unit tests also exercise leakage, freezing, steps, architecture, missing evidence, targets, paths and stale reports. See docs/validation.md for what was executed.

## Component extension

The existing verify/preflight functions and CLI now accept spec.components. Scope preflight hashes current source/config/dependency files, including untracked watched files and resolved local Python imports. It compares definitions and full-file ownership against a frozen baseline. Protected or unmapped edits fail; shared utility edits affect all owners. Code mappings remain many-to-many. Changed scan coverage cannot hide a diff. Explicit dependency boundaries identify downstream consumers for contract testing; those consumers need not produce identical predictions.

Reports distinguish components.authorization/source/definition, compatibility, runtime identity/config, contracts and behavior. Contract samples and named semantic/regression tests are observed at runtime, never filled from expected config. Unknown component evidence blocks a new component run from all-verified status. Prose invariants and stable shapes alone establish no semantic guarantee. Static import analysis cannot establish hidden native/dynamic dependencies; enumerate them in mappings/watch policy and review coverage.

Core data checks additionally support the CPU example's cv-json pixels/IDs/groups format; the metric adapter remains binary accuracy/MAE. Object-presence accuracy is a smoke check, not detection AP or segmentation IoU. Production CV acceptance uses separate approved protocols.

Legacy specs remain accepted and have components.mode=legacy with unverifiable component scope. Their old verification status is unchanged; it must never be described as a component-controlled ablation. See migration.md and component-design's shared contract.
