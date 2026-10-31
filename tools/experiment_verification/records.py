"""Validate continuity records; rank only reverified, comparable completed runs."""
from __future__ import annotations
from pathlib import Path
from .core import load_json, resolve, verify


def validate_project(root):
    root = Path(root)
    p = load_json(root / "project.json")
    errors = []
    if p.get("schema_version") != 1:
        errors.append("Unsupported project schema_version")
    for field in ("id", "title", "objective", "question"):
        if not isinstance(p.get(field), str) or not p[field].strip():
            errors.append(f"Missing {field}")
    if p.get("status") not in ("active", "paused", "resumed", "completed"):
        errors.append("Invalid project status")
    if p.get("status") == "paused" and not p.get("pause_reason"):
        errors.append("Paused project needs pause_reason")
    for field in ("hypotheses", "runs", "findings", "next_experiments", "documents"):
        if not isinstance(p.get(field), list):
            errors.append(f"{field} must be a list")
    if errors:
        return p, errors
    component_ids=set()
    if p.get("components"):
        try:
            from .components import validate_manifest
            component_manifest=validate_manifest(load_json(resolve(root,p['components'])))
            component_ids={c['id'] for c in component_manifest['components']}
        except (OSError, ValueError, AssertionError, TypeError, KeyError) as exc:
            errors.append(f'Component manifest: {exc}')
    for artifact in p.get('external_artifacts',[]):
        try:
            from .artifacts import validate_reference
            validate_reference(artifact)
        except (ValueError,TypeError) as exc: errors.append(str(exc))
    hypotheses, run_ids, finding_ids = set(), set(), set()
    def unique(items, seen, label):
        for item in items:
            if not isinstance(item, dict) or not item.get("id") or item["id"] in seen:
                errors.append(f"Duplicate/missing {label} id")
            else:
                seen.add(item["id"])
    unique(p["hypotheses"], hypotheses, "hypothesis")
    unique(p["runs"], run_ids, "run")
    unique(p["findings"], finding_ids, "finding")
    def exists(path):
        try:
            if not resolve(root, path).exists():
                errors.append(f"Missing path: {path}")
        except (ValueError, TypeError) as exc:
            errors.append(str(exc))
    for h in p["hypotheses"]:
        if h.get("status") not in ("proposed", "supported", "rejected", "inconclusive") or not h.get("statement"):
            errors.append(f"Invalid hypothesis: {h.get('id')}")
    for run in p["runs"]:
        if run.get("status") not in ("completed", "failed", "running"):
            errors.append(f"Invalid run status: {run.get('id')}")
        for field in ("directory", "spec"):
            exists(run.get(field))
        try:
            spec = load_json(resolve(root, run["spec"]))
            if p.get('components') and not spec.get('components'):
                errors.append(f'Component project requires explicit scope for {run["id"]}')
            if spec.get("hypothesis_id") not in hypotheses:
                errors.append(f"Unknown hypothesis for {run['id']}")
        except (ValueError, OSError, KeyError) as exc:
            errors.append(f"Spec error: {exc}")
    for entry in p['runs']+p['findings']:
        if any(identity not in component_ids for identity in entry.get('component_ids',[])):
            errors.append(f'Unknown component reference: {entry.get("id")}')
    for finding in p["findings"]:
        if finding.get("kind") not in ("observation", "interpretation", "negative-result") or not finding.get("claim"):
            errors.append(f"Invalid finding: {finding.get('id')}")
        if not isinstance(finding.get("evidence"), list) or not finding["evidence"]:
            errors.append(f"Finding lacks evidence: {finding.get('id')}")
        for path in finding.get("evidence", []):
            exists(path)
        for rid in finding.get("run_ids", []):
            if rid not in run_ids:
                errors.append(f"Unknown run reference: {rid}")
    for path in p["documents"]:
        exists(path)
    return p, errors


def inspect_runs(root, project):
    """Never trust a cached verification status after a pause."""
    root = Path(root)
    results = []
    for entry in project["runs"]:
        item = dict(entry)
        try:
            spec_path = resolve(root, entry["spec"])
            spec = load_json(spec_path)
            runtime = load_json(resolve(root, entry["directory"]) / "runtime.json")
            report = verify(spec, runtime, root, spec_path)
            if runtime["run_id"] != entry["id"]:
                raise ValueError("Manifest/runtime run ID mismatch")
            item.update(specification=spec, runtime=runtime, verification=report["status"], checks=report["checks"], component_verification=report["components"])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            item.update(verification="unverifiable", error=str(exc))
        results.append(item)
    return results


def cohort_key(spec):
    import json
    return json.dumps([spec["dataset"]["sha256"], spec["splits"]["sha256"],
                       spec["evaluation_protocol"], spec["expected"]["metric"],
                       {k:spec.get('components',{}).get(k) for k in ('baseline','allowed_changes')}], sort_keys=True)


def best_runs(root, project=None):
    if project is None:
        project, errors = validate_project(root)
        if errors:
            raise ValueError("; ".join(errors))
    cohorts = {}
    for run in inspect_runs(root, project):
        if run["status"] != "completed" or run["verification"] != "verified":
            continue
        spec = run["specification"]
        key = cohort_key(spec)
        value = run["runtime"]["result"]
        bucket = cohorts.setdefault(key, {"metric": spec["expected"]["metric"], "runs": [], "best": []})
        bucket["runs"].append({"id": run["id"], "value": value})
    for bucket in cohorts.values():
        select = max if bucket["metric"]["direction"] == "maximize" else min
        best_value = select(r["value"] for r in bucket["runs"])
        bucket["best"] = [r for r in bucket["runs"] if r["value"] == best_value]
    return list(cohorts.values())


def resume_report(root):
    project, errors = validate_project(root)
    if errors:
        raise ValueError("; ".join(errors))
    runs = inspect_runs(root, project)
    lines = [f"# Resume: {project['title']}", "", f"Question: {project['question']}", "",
             f"Status: {project['status']}", f"Pause reason: {project.get('pause_reason') or 'not recorded'}", "",
             "## Hypotheses", ""]
    lines += [f"- {h['id']}: {h['statement']} — recorded status {h['status']} (interpretation, not auto-inferred)" for h in project["hypotheses"]]
    lines += ["", "## Registered runs (verification recomputed from present artifacts)", "",
              "| Run | Process | Verification | Result |", "| --- | --- | --- | --- |"]
    for r in runs:
        lines.append(f"| {r['id']} | {r['status']} | {r['verification']} | {r.get('runtime', {}).get('result', 'unknown')} |")
    lines += ["", "## Best verified results by comparison cohort", ""]
    for index, c in enumerate(best_runs(root, project), 1):
        lines.append(f"- Cohort {index}: {c['metric']}; best: {c['best']}. Audit budget/seeds/factors before causal conclusions.")
    if not best_runs(root, project):
        lines.append("No currently eligible verified results.")
    registered = {resolve(root, r["directory"]) for r in project["runs"]}
    unregistered = sorted(str(p.relative_to(root)) for p in (Path(root)/"runs").glob("*") if p.is_dir() and p.resolve() not in registered)
    lines += ["", "## Evidence gaps and failures", ""]
    for run in runs:
        if run["verification"] != "verified":
            details = run.get("error") or "; ".join(c["name"]+": "+c["status"] for c in run.get("checks", []) if c["status"] != "verified")
            lines.append(f"- {run['id']}: {details}")
    lines += [f"- Unregistered run directories: {unregistered or 'none found'}", "",
              "## Findings (recorded claims; inspect cited evidence)", ""]
    lines += [f"- {f['id']} [{f['kind']}]: {f['claim']} Evidence: {', '.join(f['evidence'])}" for f in project["findings"]]
    lines += ["", "## Recommended next experiments (recorded, not auto-approved)", ""]
    lines += [f"- {x}" for x in project["next_experiments"]]
    lines += ["", "## Components and artifact provenance", "",
              str(project.get("components", "Legacy project: component scope unknown")),
              str(project.get("external_artifacts", [])), "", "## Required cold-start work", "",
              "Read handoff/decisions and original artifacts; audit runtime hooks. Reproduce the smallest run in a new output directory. Check current data/environment access. Reassess old interpretations before changing status. Offline literature cutoff and absent records remain unknown.", "",
              "This report inventories evidence. It does not reconstruct missing conversations or infer scientific support from a score."]
    return "\n".join(lines)+"\n"
