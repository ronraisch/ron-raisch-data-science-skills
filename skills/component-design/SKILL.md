---
name: component-design
description: "Define stable research components, contracts, code mappings and authorized experiment scopes. Use before component-controlled experiments or changing pipeline boundaries."
---

Start with: Research question, actual pipeline source, planned experimental variables and decision owner.

## Terms

- **Component**: a stable scientific responsibility, not a Python module.
- **Scope**: explicitly approved component paths; a parent authorizes its descendants.
- **Protected**: every component outside that scope.

## Do

1. Inspect actual source, configuration, dependencies and runtime boundaries. Choose only the nesting useful for planned experiments; include aggregate parents.
2. Write `components.json` using [the contract](references/component-contract.md) and [template](assets/components.json). Map every relevant source/config/dependency file. Map shared utilities to all consumers; one component may span files.
3. Define inputs, outputs, configuration schemas, semantic invariants and named executable contract tests. Test content and semantics, not only shapes. Connect component dependencies by stable ID.
4. Freeze a baseline before edits. Record authorized paths and the researcher's approval bound to that exact list. List direct owners and affected downstream dependencies. Run the scope preflight before implementation and again before execution.
5. Keep identity when purpose stays the same. Increase version for compatible contract/config evolution. A new purpose needs a new ID; incompatible interfaces need explicit approval bound to the new definition and downstream contract tests.
6. Run scope, runtime contract and regression checks through experiment-verify. Preserve unauthorized changes as failed evidence; request expanded approval before editing outside scope. Never auto-repair or self-approve deviations.

Use [experiment-verify](../experiment-verify/SKILL.md) for execution evidence and acceptance.

## Deliver

`components.json`, frozen baseline, approved scope, component-to-code map, contract tests and affected-dependency review. Full-checkout command: `python -m tools.experiment_verification.component_cli snapshot components.json --root PROJECT --output records/baseline.json`.

## Stop

Unknown ownership blocks a controlled-ablation claim. An out-of-scope change fails verification. Renaming a purpose field cannot establish semantic continuity: the researcher must review purpose, actual code and downstream behavior. Snapshot verification is evidence, not authenticated authorization or proof of every possible behavior.
