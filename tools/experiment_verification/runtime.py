"""Hooks must observe live objects; never fill them with expected spec values."""
import hashlib
import importlib.metadata
import platform
import subprocess
import sys
from .core import digest


def observe(value, source, stage="start", kind="runtime"):
    if not source or stage not in ("start", "end") or kind not in ("runtime", "manual"):
        raise ValueError("Observation requires source, stage, and valid evidence kind")
    return dict(value=value, source=source, stage=stage, kind=kind)


def assert_frozen(model, expected_trainable):
    """Works with torch-style named_parameters without importing torch."""
    actual = sorted(name for name, p in model.named_parameters() if p.requires_grad)
    if actual != sorted(expected_trainable):
        raise AssertionError(f"Unexpected trainable parameters: {actual}")
    return actual


def snapshot_model(model):
    params = [{"name": n, "shape": list(p.shape), "count": p.numel(), "trainable": bool(p.requires_grad)}
              for n, p in model.named_parameters()]
    return {"class": f"{type(model).__module__}.{type(model).__qualname__}", "structure": repr(model),
            "parameters": params, "total": sum(p["count"] for p in params),
            "trainable": sum(p["count"] for p in params if p["trainable"])}


def snapshot_optimizer(optimizer, model):
    names = {id(p): n for n, p in model.named_parameters()}
    groups = []
    for group in optimizer.param_groups:
        settings = {k: v for k, v in group.items() if k != "params"}
        settings["parameters"] = [names[id(p)] for p in group["params"]]
        groups.append(settings)
    return {"class": f"{type(optimizer).__module__}.{type(optimizer).__qualname__}", "groups": groups}


def checkpoint_evidence(path, load_result, strict):
    """Call only with the result returned by the actual weight loader."""
    return {"sha256": digest(path), "strict": bool(strict),
            "missing_keys": list(load_result.missing_keys),
            "unexpected_keys": list(load_result.unexpected_keys)}


def capture_environment(repo):
    def git(*args):
        try:
            return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError):
            return None
    revision = git("rev-parse", "HEAD")
    status = git("status", "--porcelain")
    patch = git("diff", "HEAD", "--binary")
    packages = sorted({f"{d.metadata['Name']}=={d.version}" for d in importlib.metadata.distributions()})
    return {"python": platform.python_version(), "implementation": sys.implementation.name,
            "packages": packages, "git_revision": revision.decode().strip() if revision else None,
            "git_dirty": bool(status) if status is not None else None,
            "git_diff_sha256": hashlib.sha256(patch).hexdigest() if patch is not None else None,
            "untracked_note": "Hash executed source/data files separately; git diff excludes untracked files."}
