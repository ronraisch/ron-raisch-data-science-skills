---
name: literature-review
description: "Review scientific literature, compare methods and trace claims. Supports local papers offline."
---

## Inputs

A scoped question, search cutoff, and available papers or search access.

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

Claims have source locations and evidence levels; coverage and inaccessible evidence are explicit.

## Resources

Use the [output template](assets/output.md). Consult the [record contract](references/record-contract.md) for IDs, paths and evidence rules. Keep work local/offline unless another tool is explicitly selected. Never fabricate evidence; preserve failures and separate observation from interpretation.
