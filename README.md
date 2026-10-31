# Ron's Data Science Skills


Twenty concise research skills with explicit inputs, procedures, deliverables and stop rules. Scientific workflows retain their K-Dense, Kalaris and Matt Pocock provenance. No skill requires loading a long upstream method. Optional offline utilities and source archives remain bundled; [source selection](docs/curation.md) records attribution.

A small collection of practical, reusable research skills for data scientists, ML researchers, and coding agents. Use them to ask better questions, run the experiment you intended, understand failures, and leave enough evidence to resume a project months later.

**The skills are the product.** Python utilities, file records, a CPU example, optional ZenML integration, and a small read-only dashboard support them. No database, server, paid model, or NVIDIA GPU is required.

## Choose a skill

| Stage | Skill | Durable output |
| --- | --- | --- |
| Start | [research-start](skills/research-start/SKILL.md) | Route a new idea through question clarification, component design and planning |
| Understand | [research-grill](skills/research-grill/SKILL.md) | Question, assumptions, constraints and success criteria |
| Understand | [literature-review](skills/literature-review/SKILL.md) | Search log, source evidence, competing methods |
| Explore | [eda](skills/eda/SKILL.md) | Reproducible profiles, figures, leakage/bias findings |
| Explain | [hypothesis-generation](skills/hypothesis-generation/SKILL.md) | Rival explanations and falsifiable predictions |
| Plan | [research-wayfinder](skills/research-wayfinder/SKILL.md) | Evidence-driven milestones and next experiments |
| Structure | [component-design](skills/component-design/SKILL.md) | Stable hierarchy, contracts, code mappings and approved change scope |
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
| Transfer | [production-handoff](skills/production-handoff/SKILL.md) | One standalone inference notebook and isolated parity evidence |
| Accept | [production-validator](skills/production-validator/SKILL.md) | Standalone validator.py and approved production validation data |

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

For offline transfer, run `npm pack` in a connected checkout, transfer the `.tgz`, then `npm install --global --offline ./ron-raisch-data-science-skills-0.5.0.tgz`. Run `ron-raisch-data-science-skills install ...` locally. The tarball includes the skills, licenses and optional Python tools; no external packages need fetching. GitHub-based npx needs Git and network on first use.

From a source checkout, `npm test` tests the Node CLI and `npm start` opens the demo host (Python required). Existing Python commands remain supported.

## Trigger the right skill

Start with `npx --yes github:ronraisch/ron-raisch-data-science-skills install research-start`. Then tell your agent: **“Use research-start to begin this research project.”** Compatible harnesses can also discover it from requests such as “start a research project” or “explore this research idea.” Automatic selection depends on the harness/model; explicit invocation is the reliable fallback. No AGENTS.md change is required.

research-start inspects existing records, resumes paused work when appropriate, or routes new work through research-grill → component-design → research-wayfinder. It loads the next skill for the current phase rather than repeating all procedures. Literature review and EDA enter the plan when their evidence is needed.

The interactive `npx … install` command previews an optional [short research paragraph](templates/agents-research.md) and asks before appending it to the current project's AGENTS.md. Default is **No**. Accepting also installs research-start and its linked skills. Existing content and previously added blocks are preserved. For scripts:

```bash
# Explicitly opt in (also works without a terminal):
npx --yes github:ronraisch/ron-raisch-data-science-skills install all --with-agents
# Skip the prompt and leave AGENTS.md untouched:
npx --yes github:ronraisch/ron-raisch-data-science-skills install research-start --no-agents
# Choose another project's instruction file:
npx --yes github:ronraisch/ron-raisch-data-science-skills install research-start --with-agents --agents-md /path/to/project/AGENTS.md
```

`npx --yes` only approves downloading the package; it does not consent to AGENTS.md changes. Python installation supports the same --with-agents, --no-agents and --agents-md options. Installing only a specialist skill does not silently add the startup workflow unless you accept the paragraph. Skill descriptions provide routing hints, not an enforcement guarantee; component scope and verification remain executable gates.

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

## Controlled component experiments

A scientific experiment changes an explicitly approved part of a stable component hierarchy. Define `components.json` with component-design, freeze a source baseline, and declare `allowed_changes` in the experiment spec. Before editing, identify shared-file owners and affected dependencies. Any additional scope needs explicit researcher approval **before** modification. Verification fails protected source/config/contract changes and rejects the result as a controlled ablation.

Component identity follows purpose, not module layout. Multiple components may share files; components may span files. Same purpose retains ID with version evolution; a new purpose requires a new ID. Full-file hashing is conservative about shared utilities. See [the component contract](skills/component-design/references/component-contract.md) and [migration guidance](docs/migration.md).

```bash
python -m examples.component_study.demo --output /tmp/new-component-study
python -m tools.experiment_verification records /tmp/new-component-study
python -m dashboard.build /tmp/new-component-study --output /tmp/components.html
```

This additional CPU image example preserves the original sensor example. It runs actual inference, accepts a decoder-only edit, rejects extractor/shared-utility edits, extracts inference into one notebook, runs strict isolated parity and exercises standalone detection/segmentation validators. Its tiny synthetic fixtures are functional demonstrations, not model-quality claims. Large checkpoints belong on organizational NFS or an internal Hugging Face server; records hold immutable identities and hashes.

Three separate guarantees: **experiment-verify** checks intended execution and authorized changes; **production-handoff** checks extraction parity and independence; **production-validator** checks production against separately approved behavioral/quality criteria. MLOps owns deployment. [Production tools and limits](docs/production.md).

## Preserve research between sessions

Keep `project.json`, hypotheses, immutable specs, run folders, decisions, summaries and handoff notes together. The record validator checks references. Resume recomputes verification from present artifacts, discovers unregistered run directories, and derives best results **within evaluation cohorts**. Controlled ablations require additional budget/seed/factor review. No tracker is needed. See [records](docs/records.md), [templates](templates/README.md), and [five compositions](workflows/README.md).

## Optional tools

- [ZenML](docs/zenml.md): optional open-source local pipelines and artifact lineage around the same standalone scripts. Components and scope enforcement work without ZenML.
- [Dashboard](dashboard/README.md): static offline research continuity views of questions, hypotheses, findings, failures, pause reasons and next steps. It reads file records and remains independent of experiment trackers.

## Sources, contribution and license

| Source | Role in this collection |
| --- | --- |
| [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills) | Literature, EDA, hypotheses and scientific figures |
| [Kalaris Research Agent Skills](https://github.com/KalarisLabs/research-agent-skills) | Experimental design and critical appraisal |
| [Matt Pocock Skills](https://github.com/mattpocock/skills) | Questioning, decision-driven planning and retrospectives |

Each adapted skill includes ORIGIN.json with the reviewed source URL and pinned revision; SKILL.md names its source without directing the agent to load the original. Original local skills are labeled as such. Nine skills adapt the pinned scientific procedures into direct instructions. Unchanged upstream resources remain an optional offline archive, not a required reading chain.


Reviewed K-Dense Scientific Agent Skills, Kalaris Research Agent Skills and Matt Pocock's Skills. Bundled selected methods and resources without copying entire catalogs. [Curation decisions](docs/curation.md), [pinned sources](docs/upstream-sources.json), and [retained notices](THIRD_PARTY_NOTICES.md) explain provenance.

MIT for this repository; upstream notices in `LICENSES/`. Contribute small skills, realistic evidence fixtures and deterministic checks; see [CONTRIBUTING.md](CONTRIBUTING.md). All contributions must preserve scientific uncertainty and failed outcomes.

To publish this prepared repository, follow [the GitHub instructions](docs/publish.md).
