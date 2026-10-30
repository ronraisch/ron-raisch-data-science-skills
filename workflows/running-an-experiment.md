# Running An Experiment

experiment-design → experiment-verify → experiment-run → ablation-review

1. Follow [experiment-design](../skills/experiment-design/SKILL.md). Save specs/ID.json and design note. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.
2. Follow [experiment-verify](../skills/experiment-verify/SKILL.md). Save input preflight and planned runtime hooks; postflight report after execution. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.
3. Follow [experiment-run](../skills/experiment-run/SKILL.md). Save unique runs/ID with actual observations, predictions, artifacts and verification. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.
4. Follow [ablation-review](../skills/ablation-review/SKILL.md). Save ablation-review.md with cohorts, controlled-factor audit and uncertainty. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.

Gate: unresolved missing evidence stays explicit. Scientific conclusions require valid comparable runs; a plan or preflight alone cannot verify execution. Offline use records local-corpus and tooling limits.

Verification has three phases: preflight before execution, live hooks during execution, and postflight after artifacts exist. The arrow sequence is a workflow, not a claim that a completed run can be verified before it occurs. Failed preflight blocks training; failed postflight blocks promotion.
