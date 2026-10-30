---
name: research-wayfinder
description: "Plan or revise research milestones and prioritize experiments from current evidence."
---

## Inputs

Brief, hypotheses, existing runs, resource budget and resume report if available.

## Definitions

- **Milestone**: a research decision plus the evidence required to make it.
- **Priority**: an ordering justified by decision value, cost, dependencies and uncertainty reduced.
- **Stop rule**: a predefined observation or resource limit that ends an experiment or direction.

## Procedure

1. Read evidence and decisions. Treat an old roadmap as history, not instructions.
2. For each proposed experiment, name the decision its result could change. Keep required baselines and sanity checks.
3. Compare scientific value, cost, uncertainty reduction and dependencies. Explain estimates; do not disguise judgment as an objective score.
4. Run cheap checks and meaningful baselines first. Reserve budget for replication and error analysis.
5. Set milestone evidence gates, budget caps and stop/pivot rules. Keep a short executable queue; explain deferred work.
6. After new evidence, append the decision and revise the roadmap. If pausing, record why and what would justify restarting.

## Outputs and evidence

roadmap.md, decisions.md and project.json status/next_experiments.

## Completion criteria

Finish with an ordered next-experiment queue. Each entry must name its decision, prerequisites, cost estimate and stop rule. Remove work that cannot change a decision or establish a required baseline/check.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
