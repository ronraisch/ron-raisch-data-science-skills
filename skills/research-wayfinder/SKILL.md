---
name: research-wayfinder
description: "Build or revise an evidence-driven research roadmap. Use to prioritize experiments, plan milestones, or continue after resumption."
---

# Research Wayfinder

## Inputs

Brief, hypotheses, completed runs, uncertainty, resource budget, and any pause/resume report.

## Procedure

1. Reconstruct what is known from verified runs and decisions. Treat stale plans as historical, not current instructions.
2. Identify the decision each proposed experiment can change. Drop experiments whose outcomes cannot affect a decision, unless they establish a required baseline or verification.
3. Estimate cost, uncertainty reduction, dependencies, and scientific value as separate ordinal judgments; explain estimates rather than treating a score as objective truth.
4. Sequence a cheap sanity check and meaningful baseline before expensive comparisons. Allocate replication and failure-analysis budget.
5. Define milestone evidence, resource caps, stop/pivot rules, and a fallback if data or compute is unavailable.
6. Maintain a short current queue with experiment IDs and dependencies, plus a deferred list with reasons. After new evidence, append the decision to decisions.md and revise the queue without erasing old outcomes.
7. If pausing, state why and what event would justify resumption; route to research-handoff.

## Outputs and evidence

roadmap.md with milestones and prioritized experiment IDs; decisions.md update; project.json next_experiments/status.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

The next experiment is executable or has named blockers; each milestone has an evidence gate; priority changes cite evidence.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
