# Fully offline use

The 20 skills can be followed by a human or local coding model with filesystem access. No network calls, paid AI API, embeddings service, database or tracker are made by the core tools. Python 3.11+ and a local copy of this repository suffice. Run commands from the repository root; imports use the checkout, not an installed package.

On a connected machine, obtain a repository archive or Git bundle and Python/uv installers for the offline OS/architecture. Transfer them through your approved mechanism. If the offline machine already has Python, use `python -m unittest discover -s tests -v` and `python -m examples.demo --output /tmp/new-study` directly. These commands need no pip/uv dependency resolution. `uv run --no-project --offline python ...` is also usable if uv already has that Python interpreter available. Optional extras require prepared wheels.

For optional plotting or ZenML, prepare an OS/Python-specific wheelhouse and a pinned lock/environment in advance, transfer it, and install with `uv pip install --no-index --find-links /media/wheels PACKAGE==VERSION`. Include transitive dependencies and hashes. Remote workers need local Git/data/package mirrors and preloaded container images if used; disabling internet is not enough to make missing assets available.

Literature review: put local PDF/text papers under sources/papers/, record file hashes and page-level evidence, and label the corpus cutoff. Use locally installed PDF extraction tooling if needed. The skill does not claim exhaustive or current coverage from a local corpus. Never send unpublished data to online services as an implicit fallback.

Copy selected skills with tools/install_skills.py or copy entire directories manually. The installer copies referenced sibling skills transitively. research-summary owns the portable record contract; templates remain with their skill. Manual copies must include referenced siblings. Executable verification needs the full checkout or an explicitly reviewed equivalent implementation; it is not secretly bundled into each prompt.

Component verification, notebook extraction/isolation and generated CV validators use only stdlib. Full-checkout tools must be provisioned with the skills when executable checks are needed. Stage checkpoint bytes on mounted NFS or local external storage before parity; internal Hugging Face references need immutable revisions and local copies. Extraction never fetches artifacts. ZenML needs a separately prepared wheelhouse/local stack; no server is required for standalone research.

Skill procedures are directly in SKILL.md. Long upstream methods remain an optional unchanged archive; agents are not directed to load them. ORIGIN.json carries source attribution without adding a reading prerequisite.
