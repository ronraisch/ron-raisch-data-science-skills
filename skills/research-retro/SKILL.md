---
name: research-retro
description: "Review a research process and turn methodological mistakes into concrete improvements."
---

Start with: Plans, execution history, verification failures, decisions, costs and summary.

## Terms

- **Process defect**: a repeatable failure of planning, execution, verification or record keeping.
- **Action**: a change with an owner, trigger and pass/fail check.

## Do

1. Reconstruct decisions from records. Judge what was knowable then; avoid hindsight blame.
2. Compare intended and executed experiments. Separate execution bugs, weak design, wrong assumptions and legitimate negative findings.
3. Find avoidable runs, missing baselines, repeated failures, leakage and lost evidence. Quantify cost only where logs support it.
4. Inspect existing checks before adding rules. Turn mechanical failures into executable assertions; leave judgment in the relevant skill.
5. For each change, name evidence, impact, root-cause confidence, owner, next-use trigger and validation criterion.
6. Save what worked and what should change. Append methodological decisions; return scientific questions to the roadmap.

Use [research-wayfinder](../research-wayfinder/SKILL.md): Return unresolved scientific decisions to the roadmap.

## Deliver

retro.md with concrete actions and checks; decisions.md update. [Template](assets/output.md).

## Stop

Every proposed improvement needs an observed incident and a validation check. Mechanical mistakes require executable guards. Mark unmeasured costs as estimates. Do not rewrite a legitimate negative result as a process failure.

## Source

Adapted workflow concepts from [mattpocock/skills — retro](https://github.com/mattpocock/skills/blob/a496f5513d4a4cf889bc48e189e579f4b0bdf6aa/skills/engineering/retro/SKILL.md) (MIT); specialized for this collection’s local records.
