---
name: hypothesis-generation
description: "Turn observations into falsifiable hypotheses and discriminating experiments."
---

## Inputs

Observations with evidence, existing hypotheses and constraints.

## Procedure

1. State the observation and its uncertainty. Separate measurements from impressions or reported claims.
2. Propose rival explanations, including a null and measurement/data error. Distinguish causal from predictive claims.
3. Define measurable variables, independent unit, direction and minimum useful effect.
4. Build a prediction matrix: what would each rival predict under each intervention? Drop tests where all rivals predict the same outcome.
5. Name confounders and controls. Define support, falsification and inconclusive regions; non-significance alone does not establish the null.
6. Choose the cheapest discriminating test. Keep exploratory hypotheses exploratory until tested on new evidence.

## Outputs and evidence

hypotheses.json and hypotheses.md: IDs, provenance, rivals, predictions and next tests.

## Completion criteria

Each hypothesis can fail and has a test that separates it from a rival.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
