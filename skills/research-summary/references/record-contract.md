# File-based research record contract (v1)

Keep records in a project directory. JSON is strict (no NaN/Infinity), UTF-8, with schema_version: 1. Paths are relative to that project; reject paths escaping it. Missing values mean unknown, never zero. Record observations separately from interpretation. The full checkout contains tools and detailed templates.

- project.json: id, title, objective, question, status (active/paused/resumed/completed), pause_reason, hypotheses, runs, findings, next_experiments, documents. A hypothesis has id, statement, status (proposed/supported/rejected/inconclusive). A run has id, spec, directory, status (completed/failed/running), optional clearml_url. A finding has id, claim, evidence (relative paths), run_ids and kind (observation/interpretation/negative-result).
- brief.md: objective, scientific question, constraints, minimum useful effect, baseline, assumptions, non-goals.
- hypotheses.json / hypotheses.md: stable IDs, rival explanations, predictions, support/falsification/inconclusive conditions and confounders.
- specs/<id>.json: immutable intent, input digests, expected runtime fields, protocol and decision rule. Change intent under a new ID.
- runs/<id>/: spec snapshot, runtime.json (observed values with source/stage/kind), predictions, artifacts, verification.json/.md, logs. Preserve failures, exit status and partial evidence.
- decisions.md: append dated decision, evidence, alternatives, rationale and consequences. Keep superseded decisions.
- roadmap.md, summary.md, handoff.md, resume.md: link back to run IDs and artifacts. State what is unverified and why paused.
- sources/: queries and evidence tables, local paper digests and source locations.
- figures/: deterministic script, source tables, exports and captions.

Best results are derived within dataset/split/evaluation/metric cohorts, never one global score. Fully verified means the implemented checks passed for instrumented evidence, not absolute scientific truth. For a controlled ablation also audit budget, seeds, preprocessing, pretraining and changed factors.

Every deliverable must identify inputs, commands/method, observations, interpretations, limitations, failed/negative outcomes, and the next decision. Leave unavailable sections explicitly unknown. Offline use needs only local files and a local model or a human; no server or paid service is part of this contract.

## Optional component extension (compatible with v1)

project.components points to components.json; new component projects require components scope in every registered spec. The shared component contract belongs to component-design/references/component-contract.md. Runtime evidence carries component snapshot and observations; verification adds a component section. Legacy verification keeps its old narrower meaning and explicitly reports unknown component scope. Do not manufacture historic approvals.

Optional external_artifacts contain identity, URI/path, version/revision, sha256 and provenance. Default large storage is mounted organizational NFS; internal HF references need immutable revision and provisioned local_path offline. No large binaries enter Git. Run tracker links may include clearml_url and zenml_url; findings may name component_ids. Optional timeline entries preserve dated decisions and pause/resume events. These fields add no mandatory service.
