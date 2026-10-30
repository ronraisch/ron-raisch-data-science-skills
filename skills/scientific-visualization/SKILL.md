---
name: scientific-visualization
description: "Create reproducible scientific figures for distributions, predictions, embeddings, learning curves and comparisons. Use for analysis and research communication."
---

# Scientific Visualization

## Inputs

Immutable data/run artifacts, audience, intended claim, metric definitions, uncertainty method and export requirements.

## Procedure

1. State the question and claim each plot should assess. Select a chart matching the variable types; do not use generated images for numerical evidence.
2. Load source artifacts with explicit joins, units and filtering. Save a tidy aggregate table and plotting script; record hashes, seed, library versions and selection rules.
3. Plot raw observations or distributions when feasible. Add meaningful uncertainty and denominators; label whether bands reflect samples, independent groups or seeds. Do not imply interpolation is observed evidence.
4. Use comparable scales and clear labels, accessible colors and readable type. Disclose truncated axes, log transforms, smoothing, omitted data and normalization. Keep a raw learning curve alongside smoothing.
5. CV: draw predictions and annotations distinctly on the same coordinate system; include scale, threshold, IoU/protocol and representative failures. Embeddings: record encoder and projection settings; neighborhood pictures do not prove class separability.
6. Compare methods within valid cohorts. Use uncertainty-aware paired differences when that is the question rather than only bars of means.
7. Export vector SVG/PDF where appropriate and PNG for previews. Inspect rendered output for clipped labels, illegible legends and hidden uncertainty. Follow curated upstream visualization guidance for specialized publication layouts.

## Outputs and evidence

figures/ with exported figures, source tables, script and captions linking to artifacts; figure manifest with methods and hashes.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

Each plot regenerates from recorded inputs; labels/units/uncertainty and selection policy are visible; the caption supports only the plotted evidence.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
