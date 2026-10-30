"""Local tabular verifier. Runtime observations are evidence, not attestation."""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

CATEGORIES = ("preprocessing", "model", "checkpoint", "parameters", "optimizer",
              "scheduler", "hyperparameters", "training", "metric", "environment")
STATUSES = ("verified", "partially_verified", "failed", "unverifiable")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"Duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json(path):
    def invalid(value):
        raise ValueError(f"Nonfinite JSON number: {value}")
    return json.loads(Path(path).read_text(), object_pairs_hook=_unique, parse_constant=invalid)


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def resolve(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError(f"Expected a nonempty relative path: {relative!r}")
    root = Path(root).resolve()
    p = (root / relative).resolve()
    if not p.is_relative_to(root):
        raise ValueError(f"Path escapes project: {relative}")
    return p


def validate_spec(spec):
    if not isinstance(spec, dict) or spec.get("schema_version") != 1:
        raise ValueError("Unsupported or missing spec schema_version")
    for key in ("id", "hypothesis_id", "decision_rule", "evaluation_protocol"):
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            raise ValueError(f"Missing spec field: {key}")
    for key in ("dataset", "splits"):
        item = spec.get(key)
        if not isinstance(item, dict) or not item.get("path"):
            raise ValueError(f"Missing {key}.path")
        sha = item.get("sha256", "")
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError(f"Invalid {key}.sha256")
    expected = spec.get("expected")
    if not isinstance(expected, dict) or set(expected) != set(CATEGORIES):
        raise ValueError(f"expected must contain exactly {CATEGORIES}")
    for key in ("preprocessing", "model", "parameters", "hyperparameters", "training", "environment"):
        if not isinstance(expected[key], dict) or not expected[key]:
            raise ValueError(f"expected.{key} must be a nonempty object")
    for key in ("checkpoint", "optimizer", "scheduler"):
        if expected[key] is not None and not isinstance(expected[key], dict):
            raise ValueError(f"expected.{key} must be an object or explicit null")
    required = spec.get("required_artifacts")
    if not isinstance(required, list) or not required or len(set(required)) != len(required) or any(not isinstance(x, str) or not x for x in required):
        raise ValueError("Specify unique required_artifacts basenames")
    metric = expected["metric"]
    if not isinstance(metric, dict) or set(metric) != {"name", "split", "direction"}:
        raise ValueError("metric needs name, split, direction")
    if metric["direction"] not in ("maximize", "minimize"):
        raise ValueError("Invalid metric direction")
    if metric["split"] not in ("validation", "test"):
        raise ValueError("Evaluation split must be validation or test")
    return spec


def check(name, status, expected=None, observed=None, source=None, detail=""):
    return dict(name=name, status=status, expected=expected, observed=observed,
                source=source, detail=detail)


def aggregate(checks):
    states = {c["status"] for c in checks}
    if "failed" in states:
        return "failed"
    if states == {"verified"}:
        return "verified"
    if states == {"unverifiable"} or not states:
        return "unverifiable"
    return "partially_verified"


def read_dataset(root, spec):
    with resolve(root, spec["dataset"]["path"]).open(newline="") as f:
        reader = csv.DictReader(f)
        if not {"id", "group", "x", "target"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV adapter needs id,group,x,target columns")
        rows = list(reader)
    ids = [r["id"] for r in rows]
    if not rows or any(not x for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("Dataset IDs must be unique and nonempty")
    if any(not r["group"] for r in rows):
        raise ValueError("Dataset groups must be nonempty")
    for row in rows:
        if not all(math.isfinite(float(row[k])) for k in ("x", "target")):
            raise ValueError("Dataset has nonfinite numeric values")
    return rows


def preflight(spec, root):
    """Verify actual input bytes and split identity, group isolation and coverage."""
    validate_spec(spec)
    checks = []
    for key in ("dataset", "splits"):
        try:
            actual = digest(resolve(root, spec[key]["path"]))
            status = "verified" if actual == spec[key]["sha256"] else "failed"
            checks.append(check(f"{key}.identity", status, spec[key]["sha256"], actual, spec[key]["path"]))
        except (OSError, ValueError) as exc:
            checks.append(check(f"{key}.identity", "unverifiable", source=spec[key]["path"], detail=str(exc)))
    try:
        rows = read_dataset(root, spec)
        splits = load_json(resolve(root, spec["splits"]["path"]))
        if not isinstance(splits, dict) or set(splits) != {"train", "validation", "test"}:
            raise ValueError("Splits must contain train, validation and test")
        by_id = {r["id"]: r for r in rows}
        seen_ids, seen_groups, seen_features = set(), set(), set()
        for name, ids in splits.items():
            if not isinstance(ids, list) or not ids or any(not isinstance(i, str) for i in ids):
                raise ValueError(f"Invalid or empty split: {name}")
            if len(ids) != len(set(ids)) or not set(ids).issubset(by_id):
                raise ValueError(f"Duplicate or unknown sample IDs in {name}")
            groups = {by_id[i]["group"] for i in ids}
            # Exact feature duplicate detection is a warning needing review, not
            # proof of leakage (e.g. discrete features can legitimately repeat).
            features = {by_id[i]["x"] for i in ids}
            if seen_ids.intersection(ids) or seen_groups.intersection(groups):
                raise ValueError(f"Sample/entity leakage involving {name}")
            overlap = seen_features.intersection(features)
            checks.append(check(f"{name}.duplicate_features", "partially_verified" if overlap else "verified",
                                observed=len(overlap), source=spec["dataset"]["path"],
                                detail="Exact x overlap needs domain review; near duplicates not checked."))
            seen_ids.update(ids); seen_groups.update(groups); seen_features.update(features)
        if seen_ids != set(by_id):
            raise ValueError("Splits do not cover the dataset exactly")
        checks.append(check("splits.isolation", "verified", source=spec["splits"]["path"],
                            detail="Checked IDs and declared groups; spatial/temporal/near-duplicate leakage requires adapters."))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        checks.append(check("splits.isolation", "failed", detail=str(exc)))
    return checks


def _metric_check(spec, run, root):
    metric = spec["expected"]["metric"]
    try:
        if run.get("evaluation_split") != metric["split"]:
            raise ValueError("Wrong evaluation split")
        rows = read_dataset(root, spec)
        labels = {r["id"]: float(r["target"]) for r in rows}
        splits = load_json(resolve(root, spec["splits"]["path"]))
        ids = splits[metric["split"]]
        prediction_path = run["predictions"]["path"]
        if digest(resolve(root, prediction_path)) != run["predictions"]["sha256"]:
            raise ValueError("Prediction artifact hash mismatch")
        with resolve(root, prediction_path).open(newline="") as f:
            predictions = list(csv.DictReader(f))
        pred_ids = [r["id"] for r in predictions]
        if len(set(pred_ids)) != len(pred_ids) or set(pred_ids) != set(ids):
            raise ValueError("Predictions missing, duplicated, or not the evaluation split")
        values = []
        for r in predictions:
            y, p = float(r["target"]), float(r["prediction"])
            if not math.isfinite(y) or not math.isfinite(p) or y != labels[r["id"]]:
                raise ValueError("Nonfinite predictions or target differs from actual dataset")
            if metric["name"] == "accuracy":
                if y not in (0, 1) or p not in (0, 1):
                    raise ValueError("Accuracy adapter accepts binary class labels only")
                values.append(float(y == p))
            elif metric["name"] == "mae":
                values.append(abs(y-p))
            else:
                return check("metric.recomputed", "unverifiable", detail="Unsupported metric; add audited adapter")
        value = sum(values) / len(values)
        reported = run.get("result")
        if not isinstance(reported, (int, float)) or isinstance(reported, bool) or not math.isfinite(reported):
            raise ValueError("Missing or nonfinite result")
        return check("metric.recomputed", "verified" if math.isclose(value, reported, rel_tol=1e-10, abs_tol=1e-12) else "failed",
                     reported, value, prediction_path)
    except (OSError, ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
        return check("metric.recomputed", "failed", detail=str(exc))


def verify(spec, run, root, spec_path=None):
    """Compare intent to instrumented observations plus independently read bytes."""
    checks = preflight(spec, root)
    if not isinstance(run, dict) or not isinstance(run.get("observations", {}), dict):
        raise ValueError("Runtime record and observations must be objects")
    if run.get("schema_version") != 1 or not run.get("run_id"):
        checks.append(check("run.schema", "failed", detail="Missing run_id/schema version"))
    if spec_path is not None:
        sha = digest(spec_path)
        checks.append(check("spec.identity", "verified" if sha == run.get("spec_sha256") else "failed",
                            sha, run.get("spec_sha256"), str(spec_path)))
    else:
        checks.append(check("spec.identity", "unverifiable", detail="Provide original spec_path to hash intent"))
    for key, expected in spec["expected"].items():
        observation = run.get("observations", {}).get(key)
        if not isinstance(observation, dict) or "value" not in observation:
            checks.append(check(f"runtime.{key}", "unverifiable", expected, detail="No runtime observation"))
            continue
        actual = observation["value"]
        # JSON normalized comparison avoids tuple/list differences without numeric coercion.
        equal = json.dumps(expected, sort_keys=True, allow_nan=False) == json.dumps(actual, sort_keys=True, allow_nan=False)
        backed = observation.get("source") and observation.get("stage") in ("start", "end")
        status = ("failed" if not equal else "verified" if backed and observation.get("kind") == "runtime"
                  else "partially_verified")
        checks.append(check(f"runtime.{key}", status, expected, actual, observation.get("source"),
                            "Evidence quality depends on the runtime hook; inspect instrumented code."))
    env = run.get("observations", {}).get("environment", {}).get("value", {})
    if not isinstance(env, dict) or not env.get("git_revision"):
        checks.append(check("environment.git_provenance", "unverifiable", detail="No observed Git revision; source snapshots need separate review"))
    else:
        checks.append(check("environment.git_provenance", "verified", observed=env["git_revision"], source="runtime environment hook"))
    artifacts = run.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        checks.append(check("artifacts", "unverifiable", detail="No artifacts recorded"))
    else:
        names = {Path(a.get("path", "")).name for a in artifacts if isinstance(a, dict)}
        for required in spec["required_artifacts"]:
            checks.append(check(f"artifact.required.{required}", "verified" if required in names else "unverifiable",
                                expected=required, observed=sorted(names), detail="Required artifact inventory"))
        for index, artifact in enumerate(artifacts):
            try:
                actual = digest(resolve(root, artifact["path"]))
                checks.append(check(f"artifact.{index}", "verified" if actual == artifact["sha256"] else "failed",
                                    artifact["sha256"], actual, artifact["path"]))
            except (OSError, ValueError, KeyError, TypeError) as exc:
                checks.append(check(f"artifact.{index}", "unverifiable", detail=str(exc)))
    checks.append(_metric_check(spec, run, root))
    return {"schema_version": 1, "run_id": run.get("run_id"), "status": aggregate(checks), "checks": checks,
            "limitations": ["Instrumented runtime evidence is not independent attestation.",
                            "CSV adapter checks binary accuracy/MAE, IDs and declared groups only.",
                            "Data semantics, label quality, near duplicates, and uninstrumented behavior remain unproven."]}


def write_report(path, report):
    save_json(path, report)
    lines = [f"# Verification: {report['run_id']}", "", f"Status: **{report['status']}**", "",
             "| Check | Status | Source | Detail |", "| --- | --- | --- | --- |"]
    for c in report["checks"]:
        clean = lambda s: str(s or "").replace("|", "\\|").replace("\n", " ")
        lines.append("| " + " | ".join(clean(c[k]) for k in ("name", "status", "source", "detail")) + " |")
    lines += ["", "## Limits", "", *[f"- {s}" for s in report["limitations"]], "",
              "Expected/observed values are preserved in the adjacent JSON report."]
    Path(path).with_suffix(".md").write_text("\n".join(lines)+"\n")
