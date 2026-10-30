---
name: research-handoff
description: "Preserve a project so another researcher can continue it after a pause."
---

## Inputs

Full project record, artifacts/access requirements and pause reason.

## Procedure

1. Validate records. Inventory important runs, failures and missing artifacts; flag uncommitted code and inaccessible data.
2. Reconstruct question, hypothesis changes and conclusions. Derive best verified results only within comparable cohorts.
3. Record exact commands, code/environment, data/split digests, checkpoint paths and hardware limits. Separate smoke tests from full replication.
4. Preserve failed approaches and do-not-repeat lessons. Missing history is unknown, not proof that work never happened.
5. State pause date/reason, blockers, restart conditions and next experiments with prerequisites.
6. Follow critical links and cold-run the smallest reproduction in a fresh directory where practical. Record actual outcomes; update manifest and append the pause decision. Never store credentials.

## Outputs and evidence

handoff.md, validated manifest, artifact/access inventory and cold-start result.

## Completion criteria

A new researcher can find evidence, reproduce a smoke run and choose the next step.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
