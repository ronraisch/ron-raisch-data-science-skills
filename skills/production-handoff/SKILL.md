---
name: production-handoff
description: "Extract approved research inference into one self-contained Jupyter notebook for MLOps. Test isolation and prediction parity before handoff."
---

Start with: Approved inference version, component manifest, source, checkpoint references, representative fixtures and input/output contracts.

## Do

1. Use [component-design](../component-design/SKILL.md) to identify inference components and trace actual transitive code/config dependencies. Inspect the execution path where mappings are incomplete; do not guess.
2. Extract only required imports, decoding, preprocessing, model definition/construction, verified checkpoint loading, forward, postprocessing and output formatting. Inline minimal custom code; preserve algorithms. Exclude training, evaluation, plots, trackers and research helpers.
3. Use established production packages (torch, torchvision, numpy, pandas, sklearn) and stdlib. Obtain researcher approval for extras. Keep checkpoint bytes external, with immutable identity/revision, provenance and content hash.
4. Generate `production_handoff.ipynb` using [extraction instructions](references/extraction.md). No research-repository imports or source-file dependency. Unsupported static extraction requires reviewed manual extraction, then the same isolation/parity gate.
5. Run the original approved inference and every notebook code cell in a separate temporary directory without the research import path. Compare real predictions and output contracts on representative and edge fixtures. Default to strict equivalence; looser criteria require explicit reason and approval before testing.
6. Save fixture hashes, actual outputs/hashes, dependency/artifact manifest and parity report. Deliver the notebook as the single source-code handoff; supporting fixtures/tests/reports remain evidence. MLOps owns deployment.

## Deliver

`production_handoff.ipynb`, `handoff-manifest.json`, `parity-report.json` and supporting fixtures/tests. A verified experiment does not establish notebook parity.

## Stop

Missing source, checkpoint, fixture coverage, isolation or parity blocks verified handoff. Never replace a custom architecture or algorithm to simplify extraction. Do not include research source alongside the notebook to make it run.
