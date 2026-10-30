---
name: hypothesis-generation
description: "Turn observations into falsifiable hypotheses and discriminating experiments."
---

## Inputs

Observations with evidence, existing hypotheses and constraints.

## Definitions

- **Hypothesis**: a statement whose predefined measurement can contradict it.
- **Rival**: an alternative explanation of the same observation.
- **Discriminating test**: an experiment for which rivals predict different outcomes.

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

Reject hypotheses without a measurable falsification rule. Reject tests whose outcomes cannot separate rivals. Finish with one selected test, its controls and predefined support/rejection/inconclusive regions.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
