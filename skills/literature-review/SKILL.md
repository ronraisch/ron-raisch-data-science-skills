---
name: literature-review
description: "Search, screen, compare, and trace scientific literature, including local papers offline. Use for evidence synthesis, method selection, baselines, and research gaps."
---

# Literature Review

## Inputs

A scoped question, inclusion/exclusion criteria, local papers or authorized search access, and time cutoff.

## Procedure

1. Fix the question, date range, eligible populations/tasks, and review type (bounded narrative, scoping, systematic). Do not label a quick web scan systematic.
2. Record each database/query/date/result count in sources/search-log.csv. Offline: enumerate local files and SHA-256 hashes, record extraction commands, and explicitly bound coverage to that collection.
3. Screen titles and full texts separately; record exclusion reasons. Link preprint/journal versions as one study; do not double count benchmarks or cohorts.
4. Extract method, data/version/split, pretraining, supervision, metric definition, compute, uncertainty, and source page/table into sources/evidence.csv. Mark missing full text and inaccessible results.
5. Separate author-reported results, results checked against supplied artifacts, and independently reproduced results. A valid DOI verifies identity, not the result.
6. Compare only aligned evaluation protocols. Explain differences in task, leakage risk, labels, and compute before declaring a method stronger. Distinguish an unsearched area from an established research gap.
7. Recommend baselines and discriminating experiments. Keep unresolved contradictions. Follow the curated upstream references for domain searches and systematic-review details; do not invoke optional paid services by default.

## Outputs and evidence

literature.md; sources/search-log.csv; sources/evidence.csv; local-paper hashes and a method comparison with source locations.

Use stable project/hypothesis/experiment/run IDs and relative evidence paths. Preserve failed attempts. Never fabricate missing measurements, citations or verification. Keep observed facts separate from interpretation.

## Completion criteria

Every substantive finding has a source location and evidence level; screening/coverage limits are clear; missing papers and competing explanations remain visible.

## Resources

Read [the record contract](references/record-contract.md) for durable outputs and [the skill template](assets/output.md) to start the deliverable. These are bundled so the skill remains usable when copied alone. Full-checkout tools and examples are optional; humans or other local tools may produce the same record format.
