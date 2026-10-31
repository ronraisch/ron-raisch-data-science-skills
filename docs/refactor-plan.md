# Component research refactor

Baseline: GitHub main ffa15b1, tree fb2efad; local Python 63/63 and Node 8/8 passed on 2026-10-31. Existing APIs: verify/spec/runtime schema v1 and four statuses; records/resume; Python/Node installers and recursive sibling links; static render/serve/OpenShift; optional ClearML. Preserve these interfaces and all upstream bundle bytes.

Extend core.verify and records with optional component fields. Add component snapshots/contract checks in experiment_verification, production extraction and validator generation, three skills, one additional CPU CV example, optional ZenML and HTML investigation panels. Keep standalone scripts the default. No required packages, service, DB or new frontend.

Compatibility: v1 records remain valid. New controlled-ablation claims require a frozen component baseline and approved scope; legacy runs explicitly lack that guarantee. New validators use a project-specific declared file mapping, not a mandated MLOps directory structure. Unmapped source changes fail closed; shared files are conservatively protected. Record approvals are evidence references, not authenticated signatures.

Tests: preserve original suites; add hostile/degraded fixtures, scope/contract/evolution cases, isolated notebook execution and parity, detection/segmentation validator boundaries, package/offline checks and original/new CPU demos. Exercise optional ZenML if SDK available; identify unavailable cluster/server checks separately in validation.md.
