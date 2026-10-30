---
name: research-grill
description: "Clarify and challenge a research question before committing to experiments. Use for vague requests, assumptions, scientific versus product goals, and success criteria."
---

# Research Grill

## Inputs

An idea or request; available data, compute, deployment constraints, and existing decisions.

## Procedure

1. Read existing project records before interviewing. Extract facts already available from code and data; ask only for decisions or information you cannot obtain.
2. Write the business objective separately from the scientific question. Translate “improve detection” into a population, comparison, outcome, and deployment constraint.
3. Map assumptions: data represents deployment; labels are reliable; the metric measures value; compute is available. Mark each as evidence-backed, assumed, or unknown.
4. Challenge the cheapest-to-disprove assumption first. Ask a small round of dependent questions; offer a concrete recommendation and its tradeoff. Do not keep interviewing once an experiment can resolve the uncertainty.
5. Specify a useful baseline, minimum useful effect, error costs, resource limit, and an explicit stop rule. Name who can decide product tradeoffs.
6. List non-goals and unresolved questions with an owner or an experiment. Do not turn a product wish into a scientific fact.

## Outputs and evidence

brief.md using the brief template; project.json question/objective; an assumptions table with evidence and a measurable success criterion.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

The question is answerable; product objective and hypothesis are distinct; blockers and provisional assumptions are explicit; the next skill can work without guessing the metric.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
