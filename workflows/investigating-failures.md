# Investigating Failures

failure-analysis → hypothesis-generation → experiment-design

1. Follow [failure-analysis](../skills/failure-analysis/SKILL.md). Save failure-analysis.md, errors.csv and slice tables. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.
2. Follow [hypothesis-generation](../skills/hypothesis-generation/SKILL.md). Save hypotheses.json with discriminating predictions. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.
3. Follow [experiment-design](../skills/experiment-design/SKILL.md). Save a new immutable spec ID tied to the discovered failure. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.

Gate: unresolved missing evidence stays explicit. Scientific conclusions require valid comparable runs; a plan or preflight alone cannot verify execution. Offline use records local-corpus and tooling limits.
