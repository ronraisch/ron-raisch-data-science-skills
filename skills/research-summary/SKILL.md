---
name: research-summary
description: "Summarize a research milestone with evidence-linked findings, negative results and open questions. Use after an investigation or before stakeholder reporting."
---

# Research Summary

## Inputs

Question, hypotheses, run inventory including failures, verification reports, decisions and current status.

## Procedure

1. Read records and evidence, not only the latest presentation. State the original question and whether scope changed.
2. Build a claim-to-evidence table with run IDs, metric protocol, verification status and limitations. Distinguish direct measurements, interpretation and speculation.
3. Summarize strongest results within comparable cohorts. Include meaningful baselines, effect size/uncertainty and relevant compute.
4. Include failed approaches and negative results with what they ruled out. Distinguish technical failure from scientific rejection.
5. Explain decisions and unresolved questions. Reconcile contradictions or explicitly leave them open.
6. Update project.json findings and hypotheses without erasing history. Run the record validator, and save a dated summary linked from the manifest.

## Outputs and evidence

summary.md; findings with evidence/run IDs; current status, limitations and next experiments.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

Every conclusion is traceable; failures are represented; readers can tell what was measured versus inferred.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
