"""Component intent, conservative source scope and observed contract checks.

No record-supplied commands are executed. Snapshots are evidence, not attestation.
"""
from __future__ import annotations
import ast
import copy
import json
import math
import re
import subprocess
from pathlib import Path
from .core import load_json, save_json, resolve, digest, check, aggregate


def canonical(value):
    import hashlib
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
        raise ValueError('Component manifest requires schema_version 1')
    items = manifest.get('components')
    if not isinstance(items, list) or not items:
        raise ValueError('Components must be a nonempty list')
    ids, paths = set(), set()
    required = ('id', 'path', 'version', 'purpose', 'inputs', 'outputs', 'invariants',
                'config_schema', 'config', 'dependencies', 'sources', 'contract_tests')
    for c in items:
        if not isinstance(c, dict) or any(k not in c for k in required):
            raise ValueError('Incomplete component definition')
        if not all(isinstance(c[k], str) and c[k].strip() for k in ('id', 'path', 'purpose')):
            raise ValueError('Component id/path/purpose must be nonempty strings')
        if c['id'] in ids or c['path'] in paths or not re.fullmatch(r'[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*', c['path']):
            raise ValueError('Duplicate id/path or invalid hierarchical path')
        if not re.fullmatch(r'\d+\.\d+\.\d+', c['version']):
            raise ValueError('Use major.minor.patch component versions')
        for k in ('inputs', 'outputs', 'config_schema', 'config'):
            if not isinstance(c[k], dict): raise ValueError(f'{k} must be an object')
        for k in ('invariants', 'dependencies', 'sources', 'contract_tests'):
            if not isinstance(c[k], list): raise ValueError(f'{k} must be a list')
        if any(not isinstance(x,str) or not x for x in c['invariants']+c['dependencies']+c['contract_tests']):raise ValueError('Invariant/dependency/test IDs must be nonempty strings')
        if len(set(c['contract_tests']))!=len(c['contract_tests']):raise ValueError('Duplicate test IDs')
        if not c['contract_tests']: raise ValueError('Declare at least one contract test ID')
        if any(not isinstance(s, dict) or not isinstance(s.get('path'), str) for s in c['sources']):
            raise ValueError('Sources require path and optional symbol')
        assert_contract(c['config'], c['config_schema'])
        ids.add(c['id']); paths.add(c['path'])
    by_id = {c['id']: c for c in items}
    def visit(i, stack):
        if i not in by_id: raise ValueError(f'Unknown dependency: {i}')
        if i in stack: raise ValueError('Component dependency cycle')
        for dep in by_id[i]['dependencies']: visit(dep, stack | {i})
    for i in ids: visit(i, set())
    for c in items:
        parent = c['path'].rsplit('.', 1)[0]
        if '.' in c['path'] and parent not in paths:
            raise ValueError(f'Missing parent component: {parent}')
    return manifest


def assert_contract(value, schema, location='$'):
    """Small strict JSON contract subset. Unknown schema keywords fail closed."""
    supported = {'type','properties','required','additionalProperties','items','minItems','maxItems',
                 'minimum','maximum','enum','shape','finite','description'}
    if not isinstance(schema, dict) or set(schema) - supported:
        raise ValueError(f'Unsupported contract schema at {location}')
    types = {'object': dict, 'array': list, 'string': str, 'number': (int,float), 'integer': int,
             'boolean': bool, 'null': type(None)}
    kind = schema.get('type')
    if kind and (kind not in types or not isinstance(value, types[kind]) or
                 kind in ('number','integer') and isinstance(value,bool)):
        raise AssertionError(f'{location}: expected {kind}')
    if isinstance(value, (float,int)) and not isinstance(value,bool):
        if not math.isfinite(value): raise AssertionError(f'{location}: nonfinite number')
        if 'minimum' in schema and value < schema['minimum']: raise AssertionError(f'{location}: below minimum')
        if 'maximum' in schema and value > schema['maximum']: raise AssertionError(f'{location}: above maximum')
    if 'enum' in schema and value not in schema['enum']: raise AssertionError(f'{location}: outside enum')
    if isinstance(value, dict):
        if set(schema.get('required',[])) - value.keys(): raise AssertionError(f'{location}: missing keys')
        props = schema.get('properties',{})
        if schema.get('additionalProperties') is False and value.keys() - props.keys():
            raise AssertionError(f'{location}: extra keys')
        for k,v in value.items():
            if k in props: assert_contract(v,props[k],location+'.'+k)
    if schema.get('shape') and not isinstance(value,list):raise AssertionError(f'{location}: expected shaped array')
    if isinstance(value,list):
        if len(value)<schema.get('minItems',0) or len(value)>schema.get('maxItems',float('inf')):
            raise AssertionError(f'{location}: invalid length')
        shape=schema.get('shape',[])
        if shape and shape[0] is not None and len(value)!=shape[0]: raise AssertionError(f'{location}: shape mismatch')
        for i,v in enumerate(value):
            item=copy.deepcopy(schema.get('items',{}))
            if len(shape)>1:item['shape']=shape[1:]
            assert_contract(v,item,f'{location}[{i}]')


def _tracked_files(root, manifest):
    # Include untracked Python and dependency/config files, not only Git's tracked diff.
    patterns=manifest.get('watch', ['**/*.py', '**/*.json', '**/*.yaml', '**/*.yml', '**/*.toml', '**/*requirements*.txt', '**/*.lock'])
    ignored=manifest.get('record_roots', ['runs','specs','records','artifacts','.git','.venv','__pycache__'])
    files=set()
    for pattern in patterns:
        for p in Path(root).glob(pattern):
            rel=p.relative_to(root)
            if (p.is_file() and rel.as_posix() not in ('components.json','project.json')
                    and not any(part in ignored for part in rel.parts)): files.add(rel.as_posix())
    # Mapped files must never disappear behind exclusion patterns.
    files.update(s['path'] for c in manifest['components'] for s in c['sources'])
    return sorted(files)


def _source_owners(root, manifest):
    """Follow local Python imports; stop at declared component dependency boundaries.

    Shared utilities are attributed to their real consumers even when an author
    omitted a redundant shared source mapping. Dynamic imports remain unsupported.
    """
    components={c['id']:c for c in manifest['components']}
    direct={}
    for c in components.values():
        for source in c['sources']:direct.setdefault(source['path'],set()).add(c['id'])
    owners={p:set(ids) for p,ids in direct.items()}
    def deps(identity):
        result=set()
        def walk(i):
            for d in components[i]['dependencies']:
                if d not in result:result.add(d);walk(d)
        walk(identity);return result
    for c in components.values():
        boundaries=deps(c['id']);pending=[s['path'] for s in c['sources']];seen=set()
        while pending:
            path=pending.pop()
            if path in seen:continue
            seen.add(path);owners.setdefault(path,set()).add(c['id'])
            if not path.endswith('.py') or not resolve(root,path).is_file():continue
            tree=ast.parse(resolve(root,path).read_text())
            for node in ast.walk(tree):
                candidates=[]
                if isinstance(node,ast.Import):candidates=[a.name.replace('.','/')+'.py' for a in node.names]
                elif isinstance(node,ast.ImportFrom):
                    base=Path(path).parent if node.level else Path('.')
                    for _ in range(max(0,node.level-1)):base=base.parent
                    module=(node.module or '').replace('.','/')
                    candidates=[(base/(module+'.py')).as_posix(),(base/module/'__init__.py').as_posix()]
                    candidates.extend((base/module/(a.name+'.py')).as_posix() for a in node.names)
                for dep in candidates:
                    if resolve(root,dep).is_file() and not direct.get(dep,set()).intersection(boundaries):pending.append(dep)
    return {p:sorted(components[i]['path'] for i in ids) for p,ids in sorted(owners.items())}


def snapshot(root, manifest, allow_missing=False):
    root=Path(root).resolve(); validate_manifest(manifest)
    source_owners=_source_owners(root,manifest)
    files={p:(digest(resolve(root,p)) if resolve(root,p).is_file() else None) for p in sorted(set(_tracked_files(root,manifest)) | source_owners.keys())}
    if not allow_missing and any(v is None for v in files.values()):raise ValueError('Missing mapped source cannot establish baseline')
    try: revision=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],stderr=subprocess.DEVNULL).decode().strip()
    except (OSError,subprocess.CalledProcessError): revision=None
    return {'schema_version':1,'manifest':copy.deepcopy(manifest),'manifest_sha256':canonical(manifest),
            'files':files,'source_owners':source_owners,'git_revision':revision}


def _within(path, scope): return any(path==s or path.startswith(s+'.') for s in scope)


def compatible(old, new):
    """Conservative compatibility: unchanged contracts or additive optional object outputs.

    Other evolution requires reviewed breaking-change approval, never inferred compatibility.
    """
    if old==new:return True
    if old.get('type')=='object' and new.get('type')=='object':
        return (old.get('required',[])==new.get('required',[]) and
                old.get('additionalProperties',True) is not False and
                all(new.get('properties',{}).get(k)==v for k,v in old.get('properties',{}).items()) and
                {k:v for k,v in old.items() if k!='properties'}=={k:v for k,v in new.items() if k!='properties'})
    return False


def verify_scope(root, manifest, baseline, scope):
    """Diff current bytes and definitions. Shared-file edits affect every mapped owner."""
    validate_manifest(manifest); validate_manifest(baseline['manifest'])
    if baseline.get('manifest_sha256')!=canonical(baseline['manifest']): raise ValueError('Corrupt baseline manifest')
    allowed=scope.get('allowed_changes')
    if not isinstance(allowed,list) or any(not isinstance(x,str) for x in allowed): raise ValueError('Explicit allowed_changes list required')
    old={c['id']:c for c in baseline['manifest']['components']};new={c['id']:c for c in manifest['components']}
    paths={c['path'] for c in list(old.values())+list(new.values())}
    if any(x not in paths for x in allowed):raise ValueError('Unknown allowed component path')
    approval=scope.get('approval',{})
    checks=[check('components.authorization','verified' if approval.get('by') and approval.get('reference') and
                  approval.get('scope_sha256')==canonical(allowed) else 'failed', detail='Scope approval must bind the exact allowed_changes list; record is not an authenticated signature.')]
    now=snapshot(root,manifest,allow_missing=True)
    changed=sorted(p for p in set(baseline['files'])|set(now['files']) if baseline['files'].get(p)!=now['files'].get(p))
    owners={p:sorted(set(baseline.get('source_owners',{}).get(p,[])) | set(now['source_owners'].get(p,[]))) for p in changed}
    for p,affected in owners.items():
        protected=[x for x in affected if not _within(x,allowed)]
        checks.append(check('components.source.'+p,'failed' if protected or not affected else 'verified',
                            baseline['files'].get(p),now['files'].get(p),p,
                            f'Affected: {affected or "UNMAPPED"}; protected: {protected}. Shared files are conservative: split source mappings/code or obtain scope approval.'))
    # A watch/exclusion policy change cannot hide source edits.
    for field in ('watch','record_roots'):
        if baseline['manifest'].get(field)!=manifest.get(field): checks.append(check('components.scan_policy','failed',detail='Changing scan coverage requires a new reviewed baseline'))
    evolution=scope.get('breaking_approvals',{})
    for identity in sorted(set(old)|set(new)):
        a,b=old.get(identity),new.get(identity);c=b or a
        if a==b:continue
        authorized=_within(c['path'],allowed) and (not a or _within(a['path'],allowed))
        checks.append(check('components.definition.'+identity,'verified' if authorized else 'failed',a,b,detail='Definition/config/dependency/source mapping changes require scope authorization'))
        if a and b:
            if a['purpose']!=b['purpose']:
                checks.append(check('components.identity.'+identity,'failed',detail='Purpose changed: create a new component identity'))
            if b['version']==a['version'] or tuple(map(int,b['version'].split('.')))<=tuple(map(int,a['version'].split('.'))):
                checks.append(check('components.version.'+identity,'failed',detail='Changed definition requires increasing version'))
            good=(a['inputs']==b['inputs'] and a['config_schema']==b['config_schema'] and
                  compatible(a['outputs'],b['outputs']) and a['invariants']==b['invariants'])
            approval=evolution.get(identity,{})
            approved=approval.get('by') and approval.get('reference') and approval.get('new_definition_sha256')==canonical(b)
            checks.append(check('components.compatibility.'+identity,'verified' if good or approved else 'failed',detail='Conservative contract compatibility; incompatible/unknown evolution requires approval bound to new definition plus downstream tests'))
        elif b and any(x['purpose']==b['purpose'] and x['path']==b['path'] for x in old.values()):
            checks.append(check('components.identity.'+identity,'failed',detail='Same purpose/path: retain existing identity and increment version'))
    if not changed:checks.append(check('components.sources','verified',detail='No source byte changes'))
    return checks,now,owners


def observe_component(component, inputs, outputs, config, test_results):
    """Call at the actual component boundary. Exceptions block evidence creation."""
    assert_contract(inputs,component['inputs']);assert_contract(outputs,component['outputs'])
    assert_contract(config,component['config_schema'])
    if set(test_results)!=set(component['contract_tests']) or not all(v is True for v in test_results.values()):
        raise AssertionError('Missing or failed named semantic/contract tests')
    return {'id':component['id'],'version':component['version'],'definition_sha256':canonical(component),
            'config':config,'inputs':inputs,'outputs':outputs,'tests':test_results,'source':'instrumented component boundary'}


def scope_preflight(spec, root):
    config=spec['components']
    try:
        baseline=resolve(root,config['baseline']['path']);manifest=resolve(root,config['manifest']['path'])
        if digest(baseline)!=config['baseline']['sha256'] or digest(manifest)!=config['manifest']['sha256']:
            raise ValueError('Frozen baseline/manifest identity mismatch')
        return verify_scope(root,load_json(manifest),load_json(baseline),config)[0]
    except (OSError,ValueError,KeyError,TypeError,AssertionError,SyntaxError) as exc:
        return [check('components.preflight','failed',detail=str(exc))]


def component_checks(spec, run, root):
    config=spec.get('components')
    if config is None:
        # Compatibility: legacy verified remains the old narrow guarantee.
        return [], {'mode':'legacy','status':'unverifiable','detail':'No component scope evidence; not eligible for component-controlled ablation'}
    checks=[]
    try:
        baseline_path=resolve(root,config['baseline']['path'])
        if digest(baseline_path)!=config['baseline']['sha256']:raise ValueError('Baseline hash mismatch')
        manifest_path=resolve(root,config['manifest']['path'])
        if digest(manifest_path)!=config['manifest']['sha256']:raise ValueError('Manifest hash mismatch')
        baseline=load_json(baseline_path);manifest=load_json(manifest_path)
        checks,current,owners=verify_scope(root,manifest,baseline,config)
        evidence=run.get('components',{})
        if not isinstance(evidence,dict):raise ValueError('Component runtime evidence must be an object')
        recorded=evidence.get('snapshot')
        content=lambda value: {k:v for k,v in value.items() if k!='git_revision'} if isinstance(value,dict) else None
        checks.append(check('components.runtime.sources','verified' if content(recorded)==content(current) else 'failed',
                            current,evidence.get('snapshot'),detail='Re-read source bytes, definitions and ownership must match execution. Git revision is retained as provenance; a metadata-only commit is not a source change.'))
        observed=evidence.get('observations',[])
        if not isinstance(observed,list) or any(not isinstance(x,dict) for x in observed):raise ValueError('Component observations must be objects')
        if any(x.get('id') not in {c['id'] for c in manifest['components']} for x in observed):raise ValueError('Unregistered component executed')
        if len({x.get('id') for x in observed})!=len(observed):raise ValueError('Duplicate component observations')
        by_id={x.get('id'):x for x in observed}
        for c in manifest['components']:
            o=by_id.get(c['id'])
            if o is None:
                checks.append(check('components.runtime.'+c['id'],'unverifiable',detail='No boundary evidence'));continue
            runtime_ok=(o.get('version'),o.get('definition_sha256'),o.get('config'))==(c['version'],canonical(c),c['config']) and bool(o.get('source'))
            checks.append(check('components.runtime.'+c['id'],'verified' if runtime_ok else 'failed',source=o.get('source'),detail='Observed identity/version/config must match frozen definition'))
            try:
                assert_contract(o['inputs'],c['inputs']);assert_contract(o['outputs'],c['outputs'])
            except (KeyError,ValueError,AssertionError,TypeError) as exc:status='failed';detail=str(exc)
            else:status='verified';detail='Boundary samples satisfy declared schemas'
            checks.append(check('components.contracts.'+c['id'],status,source=o.get('source'),detail=detail))
            tests=o.get('tests',{})
            passed=isinstance(tests,dict) and set(tests)==set(c['contract_tests']) and all(x is True for x in tests.values())
            checks.append(check('components.behavior.'+c['id'],'verified' if passed else 'failed',source=o.get('source'),detail='Named executable semantic/regression tests; instrumented evidence is not attestation'))
        return checks,{'mode':'component','status':aggregate(checks),
                       'allowed_changes':config['allowed_changes'],'affected_sources':owners,
                       'components':[{'id':c['id'],'path':c['path'],'version':c['version']} for c in manifest['components']]}
    except (OSError,ValueError,KeyError,TypeError,AssertionError,SyntaxError) as exc:
        checks.append(check('components.evidence','failed',detail=str(exc)))
        return checks,{'mode':'component','status':'failed','detail':str(exc)}
