"""External artifact references. Never fetch network data or copy large binaries."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from .core import digest, resolve


def artifact_path(root, ref):
    if ref.get('uri'):
        uri=ref['uri'];p=urlsplit(uri)
        if p.scheme in ('file','nfs'):
            # nfs://host/export is metadata, not an implicit remote mount.
            if p.netloc not in ('','localhost'):
                if not ref.get('local_path'):raise ValueError('Provision NFS mount and record local_path')
                result=Path(ref['local_path'])
            else:result=Path(unquote(p.path))
        elif p.scheme in ('hf','https'):
            result=Path(ref.get('local_path',''))
            if not ref.get('revision'):raise ValueError('Internal HF reference requires immutable revision')
            if not ref.get('local_path'):raise ValueError('Provision artifact locally for offline verification')
        else:raise ValueError('Unsupported artifact URI')
        if not result.is_absolute():raise ValueError('External artifact path must be absolute')
        return result
    return resolve(root,ref['path'])


def validate_reference(ref):
    if not isinstance(ref,dict) or not ref.get('identity') or not (ref.get('uri') or ref.get('path')):
        raise ValueError('Artifact needs identity and path/URI')
    sha=ref.get('sha256','')
    if len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha):raise ValueError('Artifact requires content SHA-256')
    if not ref.get('provenance'):raise ValueError('Artifact requires provenance')
    return ref


def verify_reference(root,ref):
    validate_reference(ref)
    path=artifact_path(root,ref)
    if digest(path)!=ref['sha256']:raise ValueError('Artifact content hash mismatch')
    return path
