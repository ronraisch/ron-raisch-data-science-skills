---
name: production-validator
description: "Generate standalone production acceptance checks and validation data for MLOps using approved quality, reference and invariant criteria."
---

Start with: Team output-directory convention, approved task/protocol, reference predictions, labeled data, required invariants and decision owner.

## Do

1. Inspect the team's existing directory convention. Declare sample-to-file mappings and output schemas; preserve its layout. Ask for the convention if it is unavailable. Never infer success from an empty search.
2. Propose ground-truth metrics, reference similarity and required invariants. Prefer hybrid validation when labels and reference outputs exist. Specify hardware/precision/quantization/stochastic tolerances and class/annotation policy before measuring acceptance.
3. Obtain research-lead or product-stakeholder approval bound to the exact proposed thresholds and protocol. Record rationale. Never derive approval from observed model performance.
4. Generate one standalone `validator.py` exposing exactly `validate(output_pred, output_test)`. Both arguments are directories. Assert on failure; return nothing. Inline helper code and approved policy; no research imports, tracker or required result object.
5. Test independently: acceptable/degraded predictions, missing files, wrong samples, malformed outputs, threshold boundaries, allowed numerical differences and unacceptable quality loss. For stochastic outputs, use an approved distributional protocol with adequate repetitions.
6. Deliver validation data outside Git on NFS with identities, revisions/hashes and provenance. Record tests and limits. Use [the adapter guide](references/validation.md) for supported detection/segmentation examples.

Use [production-handoff](../production-handoff/SKILL.md) for reference inference; its parity report does not approve production thresholds.

## Deliver

`validator.py`, approved policy, validation dataset/reference inventory, integrity manifest and independent pass/fail test evidence.

## Stop

No approved thresholds, missing results, invalid sample identities, empty evaluation or failed negative controls blocks delivery as verified. Run without Python -O. Experiment integrity, notebook parity and production acceptance are separate guarantees.
