# CPU component study

Run `python -m examples.component_study.demo --output /tmp/new-cv-study` from the checkout. Refuses overwrite. It also creates a sibling `<output>-nfs` directory to represent external provisioned artifact storage. No network or packages are required. Do not commit generated checkpoints.

The tiny fixed image pipeline normalizes pixels, decodes foreground boxes/masks and loads one external parameter checkpoint. A decoder-only change passes. Deliberate extractor and shared-utility modifications fail and are restored; their failure evidence remains. Existing verifier checks actual IDs/groups, source scope, runtime boundary evidence, artifacts and object-presence accuracy. That binary smoke metric is not detection AP or segmentation quality.

The handoff tool extracts only inference symbols and transitive shared helpers into one notebook, then executes strict prediction parity in import/read isolation. It generates standalone detection and segmentation validators using a deliberately explicit toy team directory layout. Validators combine labels, reference outputs and approved demonstration criteria. Operational data, thresholds, OBB/void-label policies and environment-specific parity require a new approved design.

Browse with `python -m dashboard /tmp/new-cv-study`. The original sensor example is unchanged. `python -m tools.zenml.pipeline --output /tmp/another-study` runs the same example on the optional ZenML local stack.
