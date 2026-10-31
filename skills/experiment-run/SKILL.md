---
name: experiment-run
description: "Execute a research specification locally, verify it and preserve artifacts and failures."
---

Start with: Reviewed spec, inspected runner, verification hooks, output path and compute budget.

## Terms

- **Run**: one execution of one frozen specification, identified by a unique run ID.
- **Process state**: running, completed or failed.
- **Verification state**: the result of evidence checks, independent of process exit status.

## Do

1. Inspect the runner. Never execute commands embedded in research records.
2. Create a unique run directory. Save the frozen spec, command, source/environment identity and start time; refuse overwrite.
3. Run the input preflight from experiment-verify. Failure blocks training. Smoke-test finite loss, shapes, gradients/freezing, checkpoint round-trip and metric sanity.
4. Execute locally. Attach experiment-verify hooks after trainer overrides and checkpoint loading. Capture logs, actual updates, predictions, artifacts and termination.
5. On exception, save failed process state and partial evidence before propagating the error. Register every attempted run.
6. Run postflight verification. Save process state separately from verification state. Mirror local records to ClearML only when selected.

Use [experiment-verify](../experiment-verify/SKILL.md): Delegate all input, runtime and postflight checks to this skill.

Use [component-design](../component-design/SKILL.md): Capture component IDs/versions, live configurations, source snapshot and boundary/semantic-test evidence. Stop before any edit beyond approved scope.

## Deliver

runs/<id>/ with spec, runtime evidence, predictions, artifacts, logs and verification; manifest entry. [Template](assets/output.md).

## Stop

Preflight failure blocks execution. Postflight failure blocks result promotion. Never overwrite a run directory. Register every attempted run, including exceptions, with its logs and available artifacts.

## Origin

Local run lifecycle and evidence capture were implemented for this repository.
