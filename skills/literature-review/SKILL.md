---
name: literature-review
description: "Review scientific literature, compare methods and trace claims. Supports local papers offline."
---

## Inputs

A scoped question, search cutoff, and available papers or search access.

## Definitions

- **Reported result**: a claim read in the source, with page or table.
- **Artifact-checked result**: a reported value checked against supplied code/data/output.
- **Reproduced result**: a value obtained by executing the method and recorded protocol yourself.

## Procedure

1. Define review type and eligibility before searching. Do not call a quick scan systematic.
2. Log source, query, date and counts. Offline: inventory local papers and hashes; state corpus limits.
3. Screen abstracts, then full texts. Record exclusions and unavailable papers; link versions of the same study.
4. Extract method, data/split, pretraining, metric, compute, uncertainty and page/table. Distinguish reported, artifact-checked and independently reproduced findings.
5. Compare protocols before scores. Preserve contradictions; no search hits does not establish novelty.
6. Check citations against actual papers. Recommend baselines and experiments; use curated upstream resources for specialist searches.

## Outputs and evidence

literature.md, sources/search-log.csv, sources/evidence.csv and local-paper hashes.

## Completion criteria

Finish when every included claim has a source location and evidence level, exclusions are logged, and search coverage is stated. An unread paper cannot support a finding. A DOI check establishes identity, not correctness.

## Resources

[Output template](assets/output.md) · [Record format and evidence rules](references/record-contract.md). Work offline by default. Record missing evidence; do not invent it.
