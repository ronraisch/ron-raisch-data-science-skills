# Optional ZenML

Standalone scripts remain the default. This adapter uses the open-source Python SDK and default local orchestrator/artifact store; it requires no paid feature, external AI service or cloud account. ZenML itself keeps local metadata; the research record remains ordinary files and does not require ZenML's database/server.

Tested with ZenML 0.98.0. Install only when selected:

```
uv sync --extra zenml
ZENML_ANALYTICS_OPT_IN=false uv run python -m tools.zenml.pipeline --output /tmp/new-zenml-study
```

Use a new output path. To keep test configuration separate, set ZENML_CONFIG_PATH to a writable local directory. The default SDK local stack initializes itself. For offline deployment, prepare pinned wheels/transitive dependencies for the target OS/Python and provision the stack locally; see offline.md. No downloads are made by the example pipeline itself.

Two cache-disabled steps execute the existing component CPU study and reverify its file evidence. Outputs are JSON dictionaries with experiment-spec hashes, component identities/scopes, external artifact references and verification outcomes; ZenML materializes them with lineage. Nested scientific components need not each become an orchestration step. `records/zenml.json` preserves actual pipeline/step/stack IDs after execution. Large checkpoints remain external. Configure a project-specific zenml_url only when an actual server link is available; never invent a URL from a local ID.

Caching is disabled because source/filesystem integrity must be rechecked, not inferred from a cached step. Both steps call the same standalone tools. ZenML is not needed for component enforcement.

Primary sources reviewed: [pipeline/step API and caching](https://docs.zenml.io/concepts/steps_and_pipelines/advanced_features), [official source and license](https://github.com/zenml-io/zenml). The installed SDK declares Apache-2.0. This integration does not promise ZenML Cloud or commercial capabilities.
