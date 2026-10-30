---
name: research-retro
description: "Review the research process and improve future methodology. Use after a milestone, costly failure, or repeated experimental mistakes."
---

# Research Retro

## Inputs

Plans, execution history, verification failures, decisions, time/compute costs and summary.

## Procedure

1. Reconstruct the sequence of decisions from primary records. Judge what was knowable at the time; avoid hindsight blame.
2. Compare intended experiments with executed ones. Separate execution defects, weak design, incorrect assumptions and legitimate negative findings.
3. Identify wasted runs, missing baselines, repeated failures, leakage risks, missing evidence and delays in discovering errors. Quantify cost only where logs support it.
4. For each issue choose a concrete change: deterministic runtime assertion for mechanical errors, design check for confounding, record/template improvement for lost context.
5. Inspect existing checks before adding rules. Prefer executable checks for repeatable mistakes; keep scientific judgment in the relevant skill.
6. Assign a next-use trigger, owner and validation criterion for each action. Record what worked and should be retained. Route open scientific questions back to the roadmap.

## Outputs and evidence

retro.md with evidence/impact/root cause/action/owner/check; methodological decisions appended to decisions.md.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

Actions are specific and checkable; uncertainty about root cause is preserved; no unsupported claims about wasted time or individual intent.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
