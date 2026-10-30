# Pausing And Resuming

research-handoff → research-resume → research-wayfinder

1. Follow [research-handoff](../skills/research-handoff/SKILL.md). Save handoff.md, pause_reason, inventory and cold-start command. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.
2. Follow [research-resume](../skills/research-resume/SKILL.md). Save resume.md with revalidated evidence, history and unknowns. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.
3. Follow [research-wayfinder](../skills/research-wayfinder/SKILL.md). Save revised roadmap.md, new experiment IDs and a dated decision. Pass the saved outputs and evidence paths to the next step; do not rely on chat memory.

Gate: unresolved missing evidence stays explicit. Scientific conclusions require valid comparable runs; a plan or preflight alone cannot verify execution. Offline use records local-corpus and tooling limits.

Run `python -m tools.experiment_verification records PROJECT` before pausing and `python -m tools.experiment_verification resume PROJECT --output PROJECT/resume-new.md` on return. Re-read original records, check stale artifacts, then reproduce a smoke run in a new directory. Only mark resumed when continuation begins.
