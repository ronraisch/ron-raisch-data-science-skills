---
name: research-retro
description: "Review a research process and turn methodological mistakes into concrete improvements."
---

## Inputs

Plans, execution history, verification failures, decisions, costs and summary.

## Definitions

- **Process defect**: a repeatable failure of planning, execution, verification or record keeping.
- **Root cause**: an explanation supported by the event history, not inferred intent.
- **Action**: a change with an owner, trigger and pass/fail check.

## Procedure

1. Reconstruct decisions from records. Judge what was knowable then; avoid hindsight blame.
2. Compare intended and executed experiments. Separate execution bugs, weak design, wrong assumptions and legitimate negative findings.
3. Find avoidable runs, missing baselines, repeated failures, leakage and lost evidence. Quantify cost only where logs support it.
4. Inspect existing checks before adding rules. Turn mechanical failures into executable assertions; leave judgment in the relevant skill.
5. For each change, name evidence, impact, root-cause confidence, owner, next-use trigger and validation criterion.
6. Save what worked and what should change. Append methodological decisions; return scientific questions to the roadmap.

## Outputs and evidence

retro.md with concrete actions and checks; decisions.md update.

## Completion criteria

Every proposed improvement needs an observed incident and a validation check. Mechanical mistakes require executable guards. Mark unmeasured costs as estimates. Do not rewrite a legitimate negative result as a process failure.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
