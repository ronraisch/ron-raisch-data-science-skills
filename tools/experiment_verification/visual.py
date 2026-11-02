"""Hash-linked visual evidence, independent of numerical experiment acceptance."""
from .core import resolve,digest


def visual_evidence(root,run):
    entries=run.get('visual_evidence',[]);errors=[];kinds=set()
    if not entries:errors.append('No visual evidence recorded')
    for item in entries:
        try:
            if item.get('kind') not in ('representative','edge-case'):raise ValueError('Unknown evidence kind')
            if not all(item.get(k) for k in ('sample_id','caption','expected','observed','path','sha256')):raise ValueError('Incomplete visual evidence')
            path=resolve(root,item['path'])
            if path.suffix.lower() not in ('.svg','.png','.jpg','.jpeg'):raise ValueError('Unsupported image format')
            if digest(path)!=item['sha256']:raise ValueError('Visual evidence hash mismatch')
            kinds.add(item['kind'])
        except (KeyError,ValueError,OSError,TypeError) as exc:errors.append(str(exc))
    for kind in ('representative','edge-case'):
        if kind not in kinds:errors.append('Missing '+kind+' examples')
    return {'status':'failed' if errors else 'verified','errors':errors,'entries':entries,
            'limits':'Checks provenance and coverage, not whether a picture demonstrates correctness; researcher inspection is required.'}
