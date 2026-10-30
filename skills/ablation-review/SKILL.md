---
name: ablation-review
description: "Compare experiments fairly, quantify uncertainty and bound conclusions."
---

Start with: Specs, process/verification states, predictions, seed/unit metadata and decision rules.

## Terms

- **Evaluation cohort**: identical dataset/split digests, evaluation implementation/protocol and metric definition.
- **Controlled ablation**: a cohort comparison with declared changes and fixed budget, seed policy, preprocessing and pretraining controls.
- **Best verified result**: the eligible result maximizing/minimizing the primary metric within one cohort; preserve ties.

## Do

1. Revalidate evidence. Exclude invalid runs from best-verified claims, but retain their existence and failure reasons.
2. Group by data/split digests, evaluation implementation/protocol and metric/split/direction. Use best_runs for these cohorts; audit controls separately.
3. List every changed factor: preprocessing, pretraining, budget, seeds, architecture and settings. Multiple changes support only a bundle-level conclusion; epochs alone do not equal compute.
4. Compute paired effects and justified uncertainty. Resample independent patients/scenes/groups, not correlated rows. Separate seed and sampling variance.
5. Apply the predeclared useful-effect rule. Disclose multiplicity, selection and test reuse; one run cannot establish robustness.
6. Mark hypotheses supported, rejected or inconclusive. Save best results per cohort, negative findings, limitations and the next decisive test.

Use [experiment-verify](../experiment-verify/SKILL.md): Revalidate runs before including them in a cohort.

## Deliver

ablation-review.md, comparison/cohort table, effect sizes/intervals and evidence-linked conclusions. [Template](assets/output.md).

## Stop

Different cohorts cannot share a winner. Multiple changed factors support only a bundle-level conclusion. Report effect size and uncertainty against the predefined useful-effect threshold. Classify support using the design rule, not an after-the-fact narrative.

## Source

Adapted workflow concepts from [KalarisLabs/research-agent-skills — scientific-critical-thinking](https://github.com/KalarisLabs/research-agent-skills/blob/b0ee35abfd7e26428846fbd84f282114560a5fbd/skills/scientific-critical-thinking/SKILL.md) (MIT); specialized for this collection’s local records.
