# Curation decisions — reviewed 2026-10-30

Read the pinned upstream skill files in upstream-sources.json, their root licenses, and Kalaris' third-party notices. Revisions are audit snapshots, not promises that later upstream behavior stays the same.

| Local skills | Existing source | Reuse / deliberate change |
| --- | --- | --- |
| literature-review | K-Dense literature-review | Adapt search/screen/extract/synthesize/citation workflow; retain reported-versus-reproduced distinction. Reference upstream for discipline-specific queries and systematic reviews. Omit paid search and generated schematics. |
| eda | K-Dense exploratory-data-analysis | Adapt local profiling, independent units, missingness/leakage and sampling limits. Reference its format-specific inspectors rather than rebuilding broad format support. Local demo is CSV only. |
| hypothesis-generation | K-Dense hypothesis-generation | Adapt rival predictions, operationalization and falsification. Use a small record contract instead of bundling its complete schema/tool suite. |
| scientific-visualization | K-Dense scientific-visualization | Retain reproducible source tables, accessible figures and uncertainty. Reference upstream for specialized publication layouts and plotting ecosystems. |
| experiment-design, ablation-review | Kalaris experimental-design and scientific-critical-thinking | Adapt randomization/blocking, independent replication and bias critique; specialize for ML splits, runtime settings and comparable cohorts. Use upstream for factorial DOE matrices and study-design tools. Kalaris credits K-Dense for these scientific materials. |
| research-grill, research-wayfinder, research-retro | Matt Pocock grilling, wayfinder, retro | Adapt focused questioning, evolving decision records and executable guardrails. Avoid mandatory harness commands, relentless interviewing or a platform dependency. |
| experiment-verify/run and continuity skills | New implementation for this collection | Add instrumented observations versus intent, local records, evidence revalidation and pause/resume reconstruction. |

Use the pinned repository/path URLs in upstream-sources.json to inspect specialized tooling. Review per-file licenses and dependencies before copying anything new; retain notices and document modifications. Avoid installing both upstream and local skills with the same trigger name unless the harness supports explicit selection.

Optional services are not part of the offline workflow. Literature reviews in an offline environment must describe local-corpus coverage and cutoff rather than claim current or exhaustive search.
