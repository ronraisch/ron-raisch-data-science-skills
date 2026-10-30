---
name: research-handoff
description: "Preserve enough context to pause a project or transfer it to another researcher. Use before inactivity, personnel changes or compute handoffs."
---

# Research Handoff

## Inputs

Entire project record, code/data access requirements, run inventory, conclusions and reason for pausing.

## Procedure

1. Validate records and inventory all important runs, including failures and negative results. Flag missing artifacts, inaccessible data, uncommitted code and unverified results.
2. Write the original question, hypothesis history, current conclusions and scope changes with evidence links. Compute best results only within comparable verified cohorts.
3. Record exact reproduction commands, Python/dependency setup, dataset/split digests, checkpoint paths, hardware limits and expected smoke-test outputs. Separate CPU smoke tests from full scientific replication.
4. Explain failed approaches and why not to repeat them. Preserve unknowns; a missing log is not proof an experiment never ran.
5. State status, pause date/reason, blockers and conditions for restarting. Recommend the next few experiments with rationale and prerequisites.
6. Perform a cold read: follow every critical link and run the smallest reproduction command in a fresh output directory where practical. Record what was actually tested.
7. Update project.json handoff/status/next_experiments and append a pause decision. Use local paths or stable IDs; keep credentials out of records.

## Outputs and evidence

handoff.md; validated project.json; artifact/access inventory; cold-read reproduction result; pause decision.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

A new researcher can locate evidence, identify the strongest comparable result, reproduce a smoke run and understand the next step and blockers.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
