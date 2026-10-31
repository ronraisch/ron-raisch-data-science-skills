---
name: scientific-visualization
description: "Create reproducible scientific figures from actual data and model outputs."
---

Start with: Source artifacts, intended claim, audience, metric definitions and uncertainty method.

## Terms

- **Uncertainty band**: an interval with a stated method and resampling/replication unit.

## Do

1. Name the question each figure answers. Choose the chart for the variables; never generate numerical evidence as an AI image.
2. Save source tables and plotting code with input hashes, filters, joins, units, seed and environment.
3. Show observations/distributions and appropriate uncertainty. Label denominators and whether intervals describe samples, groups or seeds.
4. Use readable labels and accessible colors. Disclose truncation, logs, normalization, omissions and smoothing; retain raw learning curves.
5. For CV overlays, distinguish predictions/annotations and record coordinates, thresholds and protocol. For embeddings, record encoder/projection settings; visual clusters do not prove separability.
6. Compare valid cohorts. Export SVG/PDF or PNG for the target publication or viewer; inspect rendering. Write captions linking evidence and limits.

Use [ablation-review](../ablation-review/SKILL.md): Use its approved cohorts and uncertainty calculations for method comparisons.

## Deliver

figures/: script, source tables, exports, captions and input/method manifest. [Template](assets/output.md).

## Stop

Reject figures without source data and regeneration code. Label units, filters, scales and uncertainty. Inspect the rendered export. Embedding separation is a visualization outcome, not proof of generalization.

## Attribution

Scientific workflow adapted from K-Dense-AI/scientific-agent-skills (MIT).
