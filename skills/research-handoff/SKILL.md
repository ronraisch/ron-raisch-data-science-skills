---
name: research-handoff
description: "Preserve a project so another researcher can continue it after a pause."
---

Start with: Full project record, artifacts/access requirements and pause reason.

## Terms

- **Handoff**: a record sufficient to locate evidence and execute the next step without the original researcher.
- **Reproduction command**: a command plus exact inputs, code/environment identity and expected checks.

## Do

1. Validate the manifest and inventory code, data, specs, runs and artifacts. Flag inaccessible or uncommitted inputs.
2. Reuse research-summary for conclusions and ablation-review for cohort winners. Add the hypothesis/decision chronology.
3. Record exact commands, versions/digests, checkpoint locations, access requirements and hardware limits. Store no credentials.
4. List failed approaches and why they should not be repeated. State pause date, cause, restart condition and next experiments.
5. Execute the smallest reproduction in a fresh directory. Record the command and observed checks. Missing access or artifacts makes the handoff incomplete.
6. Update manifest status/pause_reason and append the pause decision. Preserve the previous handoff.

Use [research-summary](../research-summary/SKILL.md): Reuse the current evidence summary instead of rewriting conclusions.

Use [ablation-review](../ablation-review/SKILL.md) for comparable results.

## Deliver

handoff.md, validated manifest, artifact/access inventory and cold-start result. [Template](assets/output.md).

## Stop

Finish only after critical links resolve and a fresh-directory smoke reproduction succeeds. If reproduction is blocked, mark the handoff incomplete and record the exact blocker and missing access/artifact. Keep smoke success separate from scientific replication.

## Origin

The handoff protocol was designed for independently owned, paused projects.
