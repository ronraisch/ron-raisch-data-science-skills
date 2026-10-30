---
name: hypothesis-generation
description: "Turn observations into falsifiable hypotheses and experiments that distinguish rival explanations. Use after EDA, literature review, or failure analysis."
---

# Hypothesis Generation

## Inputs

Observed findings and their evidence, current hypotheses, constraints, plausible mechanisms and alternatives.

## Procedure

1. Quote each observation with its file/run/source and uncertainty. Label informal impressions and author claims explicitly.
2. Generate a small set of rival explanations, including a measurement/data error explanation and a simple null. Separate causal hypotheses from predictive associations.
3. Define operational variables, the independent unit, expected direction and minimum useful effect for each hypothesis.
4. Build a prediction matrix: what each explanation predicts under each intervention/control. Reject proposed experiments where all rivals predict the same outcome.
5. Identify confounders, selection bias, label noise, and train/test contamination. Specify controls and what remains unidentifiable.
6. Choose the least costly discriminating experiment. Predefine support, rejection, and inconclusive regions; lack of statistical significance alone does not establish the null.
7. Save hypothesis IDs, provenance, predictions, and proposed tests. Exploratory hypotheses stay exploratory until assessed on new evidence.

## Outputs and evidence

hypotheses.json; hypothesis matrix in hypotheses.md; evidence links and proposed discriminating experiments.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

Each hypothesis has a rival, measurable prediction, falsification condition and next test; causal scope matches the design.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
