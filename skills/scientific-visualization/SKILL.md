---
name: scientific-visualization
description: "Create reproducible scientific figures from actual data and model outputs."
---

## Inputs

Source artifacts, intended claim, audience, metric definitions and uncertainty method.

## Procedure

1. Name the question each figure answers. Choose the chart for the variables; never generate numerical evidence as an AI image.
2. Save source tables and plotting code with input hashes, filters, joins, units, seed and environment.
3. Show observations/distributions and appropriate uncertainty. Label denominators and whether intervals describe samples, groups or seeds.
4. Use readable labels and accessible colors. Disclose truncation, logs, normalization, omissions and smoothing; retain raw learning curves.
5. For CV overlays, distinguish predictions/annotations and record coordinates, thresholds and protocol. For embeddings, record encoder/projection settings; visual clusters do not prove separability.
6. Compare valid cohorts. Export SVG/PDF or PNG as appropriate; inspect rendering. Write captions linking evidence and limits; use upstream guidance for specialist layouts.

## Outputs and evidence

figures/: script, source tables, exports, captions and input/method manifest.

## Completion criteria

Figures regenerate and support only the stated claim; axes, selection and uncertainty are clear.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
