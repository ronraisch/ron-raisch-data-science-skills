# CPU research project

Run `python -m examples.demo --output /tmp/new-sensor-study` from the repository root. The output must not already exist. No downloads, dependencies, tracker or GPU needed. The committed sensor-study/ snapshot is for immediate inspection; generated/ is ignored for fresh local runs.

The study uses 180 synthetic readings from 90 independent groups. Group splits are fixed before training. Training-only EDA profiles the score. A majority baseline and centered one-feature logistic model are evaluated on the same 40 validation readings. The 40-row final test is not scored. The learner performs 120 full-batch updates. Labels have controlled synthetic noise; this is a methodology example, not a real-world benchmark.

Outputs include brief, EDA aggregates/figure, hypotheses, roadmap, immutable specs, live runtime evidence, predictions, checkpoint JSON, source digests, losses, verification reports, error IDs/slices/figure, paired group-bootstrap comparison, summary, retrospective, blog draft, decisions, handoff, pause reason and resume report.

Two deliberately incorrect completed executions keep the original intended spec: wrong-optimizer actually uses a lower LR; wrong-metric reports 1.0 despite different predictions. Both must fail verification and remain in the project manifest. The best-verified result ignores them. Unit tests introduce dataset/entity leakage, missing/altered checkpoints, architecture/freeze/step drift, unsupported metrics, missing observations and stale reports.

The example code uses local dataclasses to inspect effective model/preprocessor/optimizer state. Real trainers need their own hooks; the reusable torch-style inspection helpers are in tools/experiment_verification/runtime.py. Do not replace observed values with spec values.

To see resumption survive stale evidence, copy the generated study, alter its logistic checkpoint, then run `python -m tools.experiment_verification resume COPY --output COPY/resume-new.md`. The logistic run must cease to be eligible even if its old verification report says verified. Never modify the original evidence just to obtain a desirable result.
