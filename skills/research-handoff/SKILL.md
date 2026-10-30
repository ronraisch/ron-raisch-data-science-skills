---
name: research-handoff
description: "Preserve a project so another researcher can continue it after a pause."
---

## Inputs

Full project record, artifacts/access requirements and pause reason.

## Definitions

- **Handoff**: a record sufficient to locate evidence and execute the next step without the original researcher.
- **Reproduction command**: a command plus exact inputs, code/environment identity and expected checks.
- **Pause condition**: the recorded blocker or decision that suspended work, plus the condition for restarting.

## Procedure

1. Validate records. Inventory important runs, failures and missing artifacts; flag uncommitted code and inaccessible data.
2. Reconstruct question, hypothesis changes and conclusions. Derive best verified results only within comparable cohorts.
3. Record exact commands, code/environment, data/split digests, checkpoint paths and hardware limits. Separate smoke tests from full replication.
4. Preserve failed approaches and do-not-repeat lessons. Missing history is unknown, not proof that work never happened.
5. State pause date/reason, blockers, restart conditions and next experiments with prerequisites.
6. Follow critical links and cold-run the smallest reproduction in a fresh directory when the required code, data and environment are available. Record actual outcomes; update manifest and append the pause decision. Never store credentials.

## Outputs and evidence

handoff.md, validated manifest, artifact/access inventory and cold-start result.

## Completion criteria

Finish only after critical links resolve and a fresh-directory smoke reproduction succeeds. If reproduction is blocked, mark the handoff incomplete and record the exact blocker and missing access/artifact. Keep smoke success separate from scientific replication.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
