# Production transfer and acceptance

Use production-handoff for one inference-only notebook; use production-validator for separately approved production behavior. See the concise skills and their bundled references for procedures and schemas. The research team does not implement deployment here.

The extraction adapter resolves top-level Python symbols through component mappings and normal local imports, with explicit limitations. It includes custom functions/classes and required constants; it does not copy entire research modules. It rejects unresolved dependencies and dynamic patterns instead of claiming universal source slicing. Add a reviewed thin JSON I/O adapter where needed. Custom architectures remain custom; established packages are approved by default, extras require a recorded researcher decision. The inference approval binds exact source, manifest and artifact identities.

The generated notebook hashes provisioned checkpoint bytes before loading and contains a minimal invocation. It imports no project code. Parity executes the original source separately and all notebook code in python -I with a temporary cwd and a guard denying research-file reads. This tests import/read independence for trusted code; it is not a hostile-code sandbox. Fixtures, source/config hashes, actual output hashes, output contracts and strict/default numerical comparison are recorded. Nonzero tolerance requires approved justification before extraction. Absent isolation/parity evidence cannot be called verified.

The validator generator embeds its runtime and approved policy directly into one validator.py. `validate(output_pred, output_test)` accepts directories, asserts on failure and returns None on success. An explicit sample-to-path map accommodates team directory conventions; provide a reviewed parser for formats unlike the example JSON adapter. The detection adapter specifies continuous xyxy AP50/precision/recall/false alarms and reference IoU/score tolerances. The segmentation adapter specifies macro IoU, pixel agreement and shape/class invariants. Approved metamorphic pairs support horizontal-flip or duplicate-input relations. OBB, void labels, incomplete annotations and stochastic distribution tests need explicit task adapters, approved protocols and negative controls.

No thresholds are inferred from predictions. Research-lead/product approval hashes the policy. Run without -O. Empty sets, absent samples, mismatched IDs, malformed/invalid values and failed quality/reference/metamorphic checks fail. An approval record binds content but is not an authenticated signature. Data integrity is recorded through external artifact manifests; operational access/retention stays with the organization.

Run the complete CPU workflow:

```
python -m examples.component_study.demo --output /tmp/cv-study
python -m tools.production.handoff parity /tmp/cv-study /tmp/cv-study/components.json /tmp/cv-study/records/handoff-config.json /tmp/cv-study/production
```

The example uses tiny synthetic images and an external locally provisioned checkpoint standing in for NFS. It emits both detection and segmentation validator.py modules plus test data. Example approvals apply only to toy functional checks; they do not approve operational quality. Do not copy its thresholds into production. Tests exercise deliberately incorrect source, notebooks and predictions. No NVIDIA GPU is required.
