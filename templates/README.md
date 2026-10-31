# Templates

Copy only what the current skill needs into your project. project.json is a minimal index; hypotheses.json is a richer hypothesis ledger. experiment.json contains **intentional placeholders** and is not runnable until filled with actual digests and expected runtime objects. validate_spec rejects its placeholder hashes. For a runnable spec, generate the CPU demo or inspect examples/sensor-study/specs/.

Each skill has a task-specific Markdown output template here and bundled in its assets/ directory. Use headings as prompts for evidence, not as permission to fabricate a filled report. Omit inapplicable sections with a reason. All summaries, blog posts and handoffs must keep observation, interpretation and uncertainty separate.

Use search-log.csv/evidence.csv for literature provenance; decisions.md is append-only in spirit. See docs/record-contract.md for IDs, statuses and path rules. Preserve unknowns as null/text explanations, not zeros. No paid tool, running server or model API is required to use these templates.

For component projects, start with components.json plus component-scope.json; fill actual source mappings, versions, executable contracts and researcher approval before freezing baseline. component-design owns the detailed contract. external-artifact.json is a metadata-only NFS/HF reference. production-handoff.json describes the approved inference entry and fixtures; acceptance-policy.json proposes validator criteria for stakeholder approval, not runnable thresholds. The additional CPU CV example provides filled demonstration records.
