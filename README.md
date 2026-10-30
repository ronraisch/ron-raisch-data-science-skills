# Ron's Data Science Skills


Nine skills now use bundled, pinned methods from K-Dense, Kalaris and Matt Pocock through concise local entry points. Seven skills retain local verification and continuity workflows. See [source selection](docs/curation.md). Install once; the methods and supporting files remain available offline. For local models, invoke one skill and load only the method sections it names.

A small collection of practical, reusable research skills for data scientists, ML researchers, and coding agents. Use them to ask better questions, run the experiment you intended, understand failures, and leave enough evidence to resume a project months later.

**The skills are the product.** Python utilities, file records, a CPU example, optional ClearML integration, and a small read-only dashboard support them. No database, server, paid model, or NVIDIA GPU is required.

## Choose a skill

| Stage | Skill | Durable output |
| --- | --- | --- |
| Understand | [research-grill](skills/research-grill/SKILL.md) | Question, assumptions, constraints and success criteria |
| Understand | [literature-review](skills/literature-review/SKILL.md) | Search log, source evidence, competing methods |
| Explore | [eda](skills/eda/SKILL.md) | Reproducible profiles, figures, leakage/bias findings |
| Explain | [hypothesis-generation](skills/hypothesis-generation/SKILL.md) | Rival explanations and falsifiable predictions |
| Plan | [research-wayfinder](skills/research-wayfinder/SKILL.md) | Evidence-driven milestones and next experiments |
| Design | [experiment-design](skills/experiment-design/SKILL.md) | Controlled comparison and machine-readable specification |
| Verify | [experiment-verify](skills/experiment-verify/SKILL.md) | Intended-versus-observed evidence report |
| Run | [experiment-run](skills/experiment-run/SKILL.md) | Run artifacts, process state and verification |
| Investigate | [failure-analysis](skills/failure-analysis/SKILL.md) | Error slices, label issues and discriminating tests |
| Compare | [ablation-review](skills/ablation-review/SKILL.md) | Comparable cohorts, uncertainty and bounded conclusions |
| Show | [scientific-visualization](skills/scientific-visualization/SKILL.md) | Source tables, scripts, figures and captions |
| Preserve | [research-summary](skills/research-summary/SKILL.md) | Claim-to-evidence summary, including negative findings |
| Improve | [research-retro](skills/research-retro/SKILL.md) | Methodological improvements and executable guards |
| Explain | [research-blog](skills/research-blog/SKILL.md) | Readable internal article with evidence |
| Pause | [research-handoff](skills/research-handoff/SKILL.md) | Cold-start instructions, failures and pause reasons |
| Resume | [research-resume](skills/research-resume/SKILL.md) | Reconstructed history, best comparable results and evidence gaps |

Each skill follows the [open Agent Skills format](https://agentskills.io/specification): a `SKILL.md` with name/description and optional bundled assets/references. Read it as a human, ask an agent to follow it, or copy selected directories into your harness' skill location. Skills are independently usable; full-checkout Python tools are optional and deliberately scoped.

## Install with npm / npx

Node 18+ is enough to install the skills. Run from your target project:

```bash
npx --yes github:ronraisch/ron-raisch-data-science-skills list
npx --yes github:ronraisch/ron-raisch-data-science-skills install research-resume --agent codex
# Claude Code:
npx --yes github:ronraisch/ron-raisch-data-science-skills install research-grill --agent claude
# All skills, or a custom location:
npx --yes github:ronraisch/ron-raisch-data-science-skills install all --destination ./my-skills
```

The installer includes referenced skills, preserves their assets, and refuses existing directories. It has no runtime dependencies, Python requirement or install hooks. The package is available from GitHub; it has **not** been published to the npm registry. Pin a Git commit with `github:ronraisch/ron-raisch-data-science-skills#COMMIT` for repeatable installation.

Optional dashboard commands use the same package, but require Python 3.11+ (`PYTHON` selects the executable); OpenShift also requires `oc`:

```bash
npx --yes github:ronraisch/ron-raisch-data-science-skills serve --demo
npx --yes github:ronraisch/ron-raisch-data-science-skills serve /path/to/my-study
npx --yes github:ronraisch/ron-raisch-data-science-skills deploy /path/to/my-study
```

For offline transfer, run `npm pack` in a connected checkout, transfer the `.tgz`, then `npm install --global --offline ./ron-raisch-data-science-skills-0.2.0.tgz`. Run `ron-raisch-data-science-skills install ...` locally. The tarball includes the skills, licenses and optional Python tools; no external packages need fetching. GitHub-based npx needs Git and network on first use.

From a source checkout, `npm test` tests the Node CLI and `npm start` opens the demo host (Python required). Existing Python commands remain supported.

## Start locally

Python 3.11+ and Git are enough. Core tooling has **zero third-party dependencies**. With uv:

```bash
uv run --no-project python -m unittest discover -s tests -v
uv run --no-project python -m examples.demo --output examples/generated/sensor-study
uv run --no-project python -m tools.experiment_verification records examples/generated/sensor-study
uv run --no-project python -m tools.experiment_verification resume examples/generated/sensor-study --output examples/generated/resume.md
uv run --no-project python -m dashboard.build examples/generated/sensor-study --output dashboard/generated/index.html
```

Or replace `uv run --no-project python` with `python`. The example refuses an existing output directory; choose a new path for another execution. Open the generated dashboard HTML directly in your browser.

The example generates synthetic sensor observations, runs train-only EDA, freezes group splits, compares majority and logistic classifiers on validation, records real runtime observations, injects wrong optimizer and metric executions, analyzes errors, writes summaries/handoff, pauses the project, and reconstructs it. A sealed test split is not scored. Generated numbers are actual local computations, not external benchmark results. See [the example guide](examples/README.md).

A committed [example record](examples/sensor-study/project.json) is included for browsing without running Python. Re-execute the example to create a fresh run with your environment/Git provenance. Read [validation results and limits](docs/validation.md).

## Host the dashboard quickly

```bash
python -m dashboard --demo
# Your own research records:
python -m dashboard /path/to/my-study
# OpenShift (after oc login and oc project):
python -m dashboard.openshift.install /path/to/my-study
```

Local hosting opens at http://127.0.0.1:8080; the OpenShift installer prints the Route URL. No pip packages are needed. Both serve only the generated HTML. See [dashboard setup](dashboard/README.md) for existing HTML files, disconnected clusters, prebuilt images and updates.

## Use with coding agents

From a complete checkout, an agent can simply read a named `skills/<name>/SKILL.md`. To copy selected portable skills into a project:

```bash
# Common Agent Skills project location, including Codex-compatible harnesses:
python -m tools.install_skills research-grill experiment-design experiment-verify research-resume --destination /path/to/project/.agents/skills
# Claude Code's project location:
python -m tools.install_skills research-resume --destination /path/to/project/.claude/skills
```

Check your harness' discovery location/version. Cursor, Copilot, Gemini and other systems can consume the Markdown instructions or Agent Skills directories where supported; no universal plugin registration is assumed. The installer includes the sibling skills linked by the selected workflows, including transitive links, and refuses to overwrite existing directories. Read the printed skill list after installation. No model API or harness-specific tool call is required. Avoid duplicate upstream/local trigger names. More in [installation and offline use](docs/offline.md).

Example request: “Follow research-resume on `my-study/`. Revalidate available evidence, distinguish old conclusions from current evidence, and propose the next experiment. Use local files only.”

## Verify what actually ran

```bash
python -m tools.experiment_verification verify \
  examples/generated/sensor-study/specs/logistic.json \
  examples/generated/sensor-study/runs/logistic/runtime.json \
  --root examples/generated/sensor-study \
  --output examples/generated/sensor-study/runs/logistic/recheck.json
```

Exit 0 means all implemented required checks verified; exit 1 means a failed, partial, or unverifiable report; exit 2 means invalid input. Reports preserve expected/observed values, sources and limitations. Never equate a process exit with scientific validity.

The supplied adapter checks CSV dataset/split identity and group isolation, live runtime observations versus intent, required artifact hashes, exact prediction coverage and targets, and recomputed binary accuracy or MAE. Runtime helpers observe torch-style parameters/optimizer groups without requiring torch. Integrate hooks after trainer overrides and checkpoint loading. Unsupported domains/metrics need explicit adapters; telemetry cannot prove honest execution or label correctness. See [verification scope and integration](docs/verification.md).

## Preserve research between sessions

Keep `project.json`, hypotheses, immutable specs, run folders, decisions, summaries and handoff notes together. The record validator checks references. Resume recomputes verification from present artifacts, discovers unregistered run directories, and derives best results **within evaluation cohorts**. Controlled ablations require additional budget/seed/factor review. No tracker is needed. See [records](docs/records.md), [templates](templates/README.md), and [five compositions](workflows/README.md).

## Optional tools

- [ClearML](docs/clearml.md): SDK logging, parameter/metric/artifact tracking, dataset digests, comparison, and remote CPU task registration/execution. Existing ClearML experiment comparison is reused. SDK/Agent: Apache-2.0; Server: SSPL-1.0, source-available rather than OSI-approved open source. Nothing here requires a server.
- [Dashboard](dashboard/README.md): static offline research continuity views of questions, hypotheses, findings, failures, pause reasons and next steps. It reads file records and does not duplicate ClearML's monitoring UI.

## Sources, contribution and license

| Source | Role in this collection |
| --- | --- |
| [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills) | Literature, EDA, hypotheses and scientific figures |
| [Kalaris Research Agent Skills](https://github.com/KalarisLabs/research-agent-skills) | Experimental design and critical appraisal |
| [Matt Pocock Skills](https://github.com/mattpocock/skills) | Questioning, decision-driven planning and retrospectives |

Relevant skills link directly to the reviewed upstream file at its pinned revision. Original local skills are labeled as such. These are concept adaptations, not vendored upstream implementations.


Reviewed K-Dense Scientific Agent Skills, Kalaris Research Agent Skills and Matt Pocock's Skills. Adapted selected workflow concepts and referenced specialized tooling rather than copying their catalogs. [Curation decisions](docs/curation.md), [pinned sources](docs/upstream-sources.json), and [retained notices](THIRD_PARTY_NOTICES.md) explain provenance.

MIT for this repository; upstream notices in `LICENSES/`. Contribute small skills, realistic evidence fixtures and deterministic checks; see [CONTRIBUTING.md](CONTRIBUTING.md). All contributions must preserve scientific uncertainty and failed outcomes.

To publish this prepared repository, follow [the GitHub instructions](docs/publish.md).
