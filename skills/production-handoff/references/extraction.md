# Extraction and parity

Full-checkout tools:

```
python -m tools.production.handoff build PROJECT components.json handoff-config.json OUTPUT
python -m tools.production.handoff parity PROJECT components.json handoff-config.json OUTPUT
```

The supplied adapter supports explicit top-level Python symbols with normal imports and JSON input/output. Entry signature: `predict(inputs, artifacts)`, where inputs is decoded JSON and artifacts maps names to locally provisioned absolute paths. Write an approved thin I/O adapter for other research interfaces; do not alter model logic. Static tracing follows top-level symbol references and local from-imports through declared inference-component dependencies. It extracts referenced functions/classes/constants, not whole modules. Dynamic loading, reflection, decorators, recursive definitions, star/ambiguous imports and name collisions stop for review. This is deliberately narrower than a universal Python slicer.

Record `inference_approval` with by/reference/inference_sha256, binding canonical({manifest: canonical(manifest), source: extracted provenance list, entry, artifacts}). This must represent the researcher's exact approved inference, not an agent-generated operational approval. Config: entry `{path, symbol}`, component_ids, artifacts keyed by name, fixtures `[{path, sha256}]`, output_schema. Artifact references follow component-design's contract. Extra packages require `package_approval` with by/reference/packages_sha256. Nonzero tolerance `{atol,rtol}` requires `parity_approval` with by/reference/reason/tolerance_sha256. The default is strict numerical equivalence and identical keys, lengths, labels and types. A task requiring order-independent matching or stochastic equivalence needs a reviewed task-specific comparator; do not weaken array checks after observing a failure.

The notebook contains only extracted inference, integrity checks, JSON I/O and a minimal invocation. Dependencies and checkpoint bytes are external. Import isolation uses python -I, a temporary cwd and no research import path, plus an audit guard denying research-file reads; it is not a hostile-code sandbox. Review trusted code before execution. Parity is fixture/environment evidence, not a universal behavioral proof.

The CPU component example exercises actual extraction and isolated execution. For GPU/custom production packages, run parity in the intended approved environment and preserve its package versions and fixture outputs. Check package availability separately from approval.
