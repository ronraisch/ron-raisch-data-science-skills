"""Evidence-based verification; see docs/verification.md for supported scope."""
from .core import verify, validate_spec, preflight, digest, load_json, save_json

__all__ = ["verify", "validate_spec", "preflight", "digest", "load_json", "save_json"]
