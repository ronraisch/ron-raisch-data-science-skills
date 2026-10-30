---
name: research-retro
description: "Review a research process and turn methodological mistakes into concrete improvements."
---

## Inputs

Plans, execution history, verification failures, decisions, costs and summary.

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

Actions are testable; suspected causes and estimated costs are labeled.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
