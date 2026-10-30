---
name: scientific-visualization
description: "Create reproducible scientific figures from actual data and model outputs."
---

## Inputs

Source artifacts, intended claim, audience, metric definitions and uncertainty method.

## Definitions

- **Figure**: a deterministic mapping from named source data to visual marks.
- **Uncertainty band**: an interval with a stated method and resampling/replication unit.
- **Caption**: the claim, population, protocol, denominator and interpretation needed to read the figure.

## Procedure

1. Name the question each figure answers. Choose the chart for the variables; never generate numerical evidence as an AI image.
2. Save source tables and plotting code with input hashes, filters, joins, units, seed and environment.
3. Show observations/distributions and appropriate uncertainty. Label denominators and whether intervals describe samples, groups or seeds.
4. Use readable labels and accessible colors. Disclose truncation, logs, normalization, omissions and smoothing; retain raw learning curves.
5. For CV overlays, distinguish predictions/annotations and record coordinates, thresholds and protocol. For embeddings, record encoder/projection settings; visual clusters do not prove separability.
6. Compare valid cohorts. Export SVG/PDF or PNG for the target publication or viewer; inspect rendering. Write captions linking evidence and limits; use upstream guidance for specialist layouts.

## Outputs and evidence

figures/: script, source tables, exports, captions and input/method manifest.

## Completion criteria

Reject figures without source data and regeneration code. Label units, filters, scales and uncertainty. Inspect the rendered export. Embedding separation is a visualization outcome, not proof of generalization.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
