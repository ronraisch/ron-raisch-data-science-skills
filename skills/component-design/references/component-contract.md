# Component contract v1

JSON is the dependency-free default; YAML may be converted to strict JSON by a local, approved parser. No server is needed. Keep the minimal project record and one component manifest; put per-run evidence under existing runs/. Do not create a second registry.

## Manifest

`schema_version: 1`, `components: [...]`. Each component requires:

- `id`: stable identity, independent of path and architecture.
- `path`: dotted hierarchy; declare parent components. Scope `model.decoder` includes all descendants, never siblings.
- `version`: increasing major.minor.patch; same purpose retains ID. Semantic purpose change creates new ID, including downstream reference updates.
- `purpose`: explicit responsibility. Code review remains necessary to detect undeclared semantic changes.
- `inputs`, `outputs`, `config_schema`: executable JSON schemas; `config`: planned effective values.
- `invariants`: semantic claims, each covered by named `contract_tests` IDs.
- `dependencies`: component IDs. Contracts are checked at every observed boundary, including downstream dependents.
- `sources`: objects with project-relative `path` and optional top-level `symbol`. Used for ownership and extraction, not a one-module rule. Multiple components may map one file; one component may map many files.
- `contract_tests`: nonempty names of actual executable tests. Do not set these true from intent. Call `observe_component` after assertions on actual inputs, outputs, config and invariants. Persist evidence; verification checks samples again.

Schema subset: type, properties, required, additionalProperties=false, items, minItems/maxItems, minimum/maximum, enum, shape (list dimensions, null wildcard), finite and description. Unknown keywords fail; use explicit adapters for tensors or other contracts. Normalize runtime tensors to summaries/small samples, not full training data. Invariants require explicit executable checks; prose is not proof.

`watch` globs scan code, dependency and config files including untracked files. `record_roots` excludes only output/record locations. Mapped sources and resolvable local Python imports remain included. Review scan coverage for native code, packages and dynamic loaders. Changes to coverage require a fresh reviewed baseline. Full-file hashes are deliberately conservative: editing a shared file affects all its owners even if their functions appear unchanged. Refactor the file before freezing the experiment, or obtain expanded approval; do not bypass a failure with narrower mappings.

## Experiment extension

Keep spec schema v1. Add `components` containing:

```json
{
  "manifest": {"path": "components.json", "sha256": "actual file hash"},
  "baseline": {"path": "records/baseline.json", "sha256": "actual file hash"},
  "allowed_changes": ["model.decoder"],
  "approval": {"by": "researcher", "reference": "decisions.md#scope", "scope_sha256": "canonical hash of allowed_changes"},
  "breaking_approvals": {}
}
```

Use `canonical` from tools.experiment_verification.components for hashes of JSON values; use `digest` for file bytes. Approval references are recorded human decisions, not authenticated signatures. An agent must not create approval in place of the decision owner.

A breaking approval keyed by component ID contains by, reference and new_definition_sha256. Source-scope approval alone does not approve a breaking interface. Compatibility checker certifies unchanged contracts and a narrow additive optional-output case; all other changes need explicit review. Runtime evidence and downstream tests are still required.

Before implementation: enumerate owners, intended variables and dependents; freeze hashes and scope. `component_cli check MANIFEST --root PROJECT --baseline BASELINE --scope SCOPE --output REPORT` fails on protected/unmapped edits. After execution: runtime.components contains observed snapshot plus observations from `observe_component`. Core verify combines these checks with existing data, runtime, artifact and metric checks. A failed scope cannot become an accepted ablation. Same shapes do not establish unchanged source/config/dependencies or semantics.

Legacy records remain readable with an explicit unknown component guarantee. New component projects set project.components to the manifest path; all their registered experiments require a scope, including an explicit empty list when nothing changes. Do not retroactively manufacture baseline or approval evidence.

## External artifacts

Default large-artifact storage is organizational NFS. Records contain identity, URI/path, version/revision, SHA-256 and provenance, not binary contents. Mounted NFS uses file:///nfs/... or nfs:///nfs/...; remote NFS hosts require an already provisioned mount. Internal HF uses hf://internal-host/repo plus immutable revision, sha256 and absolute local_path. No network download is implied. Inaccessible bytes remain unverifiable. Do not put credentials in manifests.

## Three guarantees

1. experiment-verify: implemented checks establish intended conditions and authorized scope.
2. production-handoff: isolated extracted inference matches approved research inference on fixtures.
3. production-validator: production meets separately approved quality/behavior criteria.

None implies either of the others.
