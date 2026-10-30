---
name: research-wayfinder
description: "Plan or revise research milestones and prioritize experiments from current evidence."
---

Start with: Brief, hypotheses, existing runs, resource budget and resume report if available.

## Terms

- **Milestone**: a research decision plus the evidence required to make it.
- **Priority**: an ordering justified by decision value, cost, dependencies and uncertainty reduced.
- **Stop rule**: a predefined observation or resource limit that ends an experiment or direction.

## Do

1. Read evidence and decisions. Treat an old roadmap as history, not instructions.
2. For each proposed experiment, name the decision its result could change. Keep required baselines and sanity checks.
3. Compare scientific value, cost, uncertainty reduction and dependencies. Explain estimates; do not disguise judgment as an objective score.
4. Run cheap checks and meaningful baselines first. Reserve budget for replication and error analysis.
5. Set milestone evidence gates, budget caps and stop/pivot rules. Keep a short executable queue; explain deferred work.
6. After new evidence, append the decision and revise the roadmap. If pausing, record why and what would justify restarting.

Use [experiment-design](../experiment-design/SKILL.md): Write specs only for experiments admitted to the queue.

## Deliver

roadmap.md, decisions.md and project.json status/next_experiments. [Template](assets/output.md).

## Stop

Finish with an ordered next-experiment queue. Each entry must name its decision, prerequisites, cost estimate and stop rule. Remove work that cannot change a decision or establish a required baseline/check.

## Source

Adapted workflow concepts from [mattpocock/skills — wayfinder](https://github.com/mattpocock/skills/blob/a496f5513d4a4cf889bc48e189e579f4b0bdf6aa/skills/engineering/wayfinder/SKILL.md) (MIT); specialized for this collection’s local records.
