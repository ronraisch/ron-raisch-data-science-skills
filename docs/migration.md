# Compatible migration to component research (0.4)

Existing v1 project/spec/runtime JSON, verifier CLI, four verification states, installs and dashboard commands remain supported. No conversion is required to browse or resume an old project. Legacy reports now explicitly describe missing component scope; their old verified status applies only to old implemented checks.

To start new component-controlled work:

1. Follow component-design on actual code. Keep scientific responsibilities stable; map shared files, relevant configs/lockfiles, imports and contract tests. Use JSON without adding dependencies.
2. Set project.components to components.json. Freeze a baseline before changes and place it under records/. New registered experiments in that project require explicit component scopes, even an empty allowed_changes list.
3. Record the researcher's approved scope and hash in the new immutable spec. Record incompatible-interface approval separately. Never manufacture retroactive approvals or pretend that a baseline captured after an old run proves what ran.
4. Attach observe_component at actual boundaries; save source snapshot plus identity/version, actual config, input/output samples and executed semantic test outcomes. Core verify checks these with existing execution checks. Run downstream tests for contract evolution.
5. Keep checkpoints outside Git; add external_artifacts identities/URIs/revisions/SHA-256/provenance. HF bytes must be provisioned locally offline. Missing external bytes remain unverifiable.

Conservative full-file ownership can reject a decoder edit in a file shared with a protected extractor. Move code before freezing the experiment, or obtain explicit expanded scope. Do not narrow mappings after a rejection. Watch-coverage changes need a new reviewed baseline. Source/version/contract checks cannot automatically detect an undeclared semantic purpose change; preserve human review and executable behavior tests.

Production handoff/validation are new optional workflows, not migrations of research-handoff. A standalone inference notebook is the source-code handoff to MLOps; validator.py is a separate acceptance tool. Existing research continuity files remain intact. ZenML is opt-in. npm package 0.5.0 is GitHub-installable; no npm registry release is implied.

## 0.5: research startup and ClearML removal

ClearML SDK/Agent configuration, adapter scripts, package extra and setup guide have been removed at the maintainer's request. Existing records containing clearml_url remain readable; the dashboard no longer exposes that integration. Use tracker_url for an ordinary external research link, or zenml_url for ZenML. Old Git revisions retain historical ClearML code if migration context is needed. No other experiment, dashboard or deployment feature is removed.

A new research-start skill routes startup/continuation through the existing lifecycle skills. npm/Python installation can optionally append templates/agents-research.md to a project AGENTS.md. Interactive terminals ask first; noninteractive installs require --with-agents. --no-agents skips the offer. Explicit opt-in includes research-start and its linked skills, even for a partial installation. Existing prose and already-installed research blocks are preserved.
