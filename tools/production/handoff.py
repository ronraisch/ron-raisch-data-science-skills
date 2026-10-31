"""Conservative static inference extraction and isolated notebook parity.

Explicit supported boundary: top-level Python symbols, normal imports and JSON I/O.
Dynamic imports, reflection and ambiguous bindings stop extraction for manual review.
"""
from __future__ import annotations
import ast
import builtins
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from tools.experiment_verification.core import load_json, save_json, resolve, digest
from tools.experiment_verification.components import validate_manifest, canonical, assert_contract
from tools.experiment_verification.artifacts import verify_reference

DEFAULT_PACKAGES={'torch','torchvision','numpy','pandas','sklearn'}
BANNED_CALLS={'eval','exec','__import__','compile','globals','locals','getattr','setattr'}


def extract(root, manifest, entry, component_ids, extra_packages=None):
    validate_manifest(manifest);root=Path(root)
    by_id={c['id']:c for c in manifest['components']};selected=set()
    def include(i):
        if i in selected:return
        if i not in by_id:raise ValueError('Unknown inference component '+i)
        selected.add(i)
        for d in by_id[i]['dependencies']:include(d)
    for i in component_ids:include(i)
    mappings=[s for i in selected for s in by_id[i]['sources']]
    modules={};emitted={};ordered=[];imports=set();visiting=set();provenance=[]
    def parse(file):
        if file in modules:return modules[file]
        tree=ast.parse(resolve(root,file).read_text());nodes={};bindings={}
        for n in tree.body:
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                names=[n.name]
            elif isinstance(n,(ast.Assign,ast.AnnAssign)):
                names=[x.id for x in (n.targets if isinstance(n,ast.Assign) else [n.target]) if isinstance(x,ast.Name)]
            elif isinstance(n,(ast.Import,ast.ImportFrom)):
                for alias in n.names:
                    if alias.name=='*':raise ValueError('Star import needs manual extraction')
                    name=alias.asname or (alias.name.split('.')[0] if isinstance(n,ast.Import) else alias.name)
                    bindings[name]=(n,alias)
                continue
            else:continue
            for name in names:
                if name in nodes:raise ValueError('Ambiguous top-level binding '+name)
                nodes[name]=n
        modules[file]=(nodes,bindings);return nodes,bindings
    def module_file(file,node):
        if node.level:
            base=Path(file).parent
            for _ in range(node.level-1):base=base.parent
            return (base/((node.module or '').replace('.','/')+'.py')).as_posix()
        return (node.module or '').replace('.','/')+'.py'
    def add(file,name):
        key=(file,name)
        if key in emitted:return
        if key in visiting:raise ValueError('Recursive source dependencies require reviewed manual extraction')
        if not any(s['path']==file and (not s.get('symbol') or s['symbol']==name) for s in mappings):
            raise ValueError(f'Inference dependency missing from selected component mappings: {file}:{name}')
        nodes,bindings=parse(file)
        if name not in nodes:raise ValueError('Cannot resolve source symbol '+name)
        node=nodes[name];visiting.add(key)
        if isinstance(node,ast.AsyncFunctionDef):raise ValueError('Async entry requires explicit adapter')
        local={a.arg for a in ast.walk(node) if isinstance(a,ast.arg)}|{x.id for x in ast.walk(node) if isinstance(x,ast.Name) and isinstance(x.ctx,(ast.Store,ast.Param))}
        local.add(name)
        for call in (x for x in ast.walk(node) if isinstance(x,ast.Call)):
            if isinstance(call.func,ast.Name) and call.func.id in BANNED_CALLS:raise ValueError('Dynamic source needs manual extraction')
        for dep in sorted({x.id for x in ast.walk(node) if isinstance(x,ast.Name) and isinstance(x.ctx,ast.Load)}-local-set(dir(builtins))):
            if dep in nodes:add(file,dep)
            elif dep in bindings:
                imp,alias=bindings[dep]
                if isinstance(imp,ast.ImportFrom) and resolve(root,module_file(file,imp)).is_file():
                    add(module_file(file,imp),alias.name)
                    if alias.asname and alias.asname!=alias.name:raise ValueError('Local aliased import needs explicit extraction adapter')
                else:
                    module=(imp.module or '') if isinstance(imp,ast.ImportFrom) else alias.name
                    base=module.split('.')[0]
                    if (root/base).is_dir() or (root/(base+'.py')).is_file():raise ValueError('Research module import must be extracted, never packaged as a dependency')
                    if base not in sys.stdlib_module_names|DEFAULT_PACKAGES|set(extra_packages or []):
                        raise ValueError('Unapproved production dependency '+module)
                    if base in {'importlib','runpy'}:raise ValueError('Dynamic module loading is unsupported')
                    imports.add(ast.unparse(imp))
            else:raise ValueError('Unresolved inference dependency '+dep)
        code=ast.get_source_segment(resolve(root,file).read_text(),node)
        if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.decorator_list:
            raise ValueError('Decorated symbols need reviewed manual extraction')
        if any(n==name and f!=file for f,n in emitted):raise ValueError('Colliding source symbols '+name)
        visiting.remove(key);emitted[key]=code;ordered.append(code)
        provenance.append({'path':file,'symbol':name,'file_sha256':digest(resolve(root,file))})
    add(entry['path'],entry['symbol'])
    return '\n'.join(sorted(imports))+'\n\n'+'\n\n'.join(ordered)+'\n',provenance


def build(root,manifest,config,output):
    output=Path(output)
    if output.exists():raise FileExistsError(output)
    extras=config.get('extra_packages',[])
    if extras:
        approval=config.get('package_approval',{})
        if not approval.get('by') or not approval.get('reference') or approval.get('packages_sha256')!=canonical(extras):
            raise ValueError('Additional packages require approval')
    code,provenance=extract(root,manifest,config['entry'],config['component_ids'],extras)
    refs=config.get('artifacts',{})
    approved_identity=canonical({'manifest':canonical(manifest),'source':provenance,'entry':config['entry'],'artifacts':refs})
    approval=config.get('inference_approval',{})
    if not approval.get('by') or not approval.get('reference') or approval.get('inference_sha256')!=approved_identity:
        raise ValueError('Researcher approval must bind the exact inference source, manifest and artifacts')
    for ref in refs.values():verify_reference(root,ref)
    # Artifact integrity checks live in the notebook too, immediately before inference.
    runner='''import hashlib
import json
from pathlib import Path

def predict_from_files(input_path, output_path, artifact_paths):
    expected = ARTIFACT_HASHES
    if set(artifact_paths) != set(expected):
        raise AssertionError("Artifact inventory differs")
    for name, filename in artifact_paths.items():
        hasher = hashlib.sha256()
        with open(filename, "rb") as stream:
            for chunk in iter(lambda: stream.read(1048576), b""):
                hasher.update(chunk)
        if hasher.hexdigest() != expected[name]:
            raise AssertionError("Checkpoint/artifact hash mismatch: " + name)
    inputs = json.loads(Path(input_path).read_text())
    result = ENTRY(inputs, artifact_paths)
    Path(output_path).write_text(json.dumps(result, allow_nan=False))
'''.replace('ENTRY',config['entry']['symbol'])
    runner='ARTIFACT_HASHES = '+repr({k:v['sha256'] for k,v in refs.items()})+'\n'+runner
    invocation='''# Minimal invocation: provision input and external artifacts, then run:
# predict_from_files("input.json", "predictions.json", {"checkpoint": "/nfs/model/checkpoint"})
'''
    def cell(source):return {'cell_type':'code','execution_count':None,'metadata':{},'id':canonical(source)[:12],'outputs':[],'source':source.splitlines(True)}
    nb={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},
        'cells':[cell(code),cell(runner),cell(invocation)]}
    output.mkdir(parents=True);save_json(output/'production_handoff.ipynb',nb)
    packages=sorted({(n.module or '').split('.')[0] if isinstance(n,ast.ImportFrom) else a.name.split('.')[0]
                     for n in ast.walk(ast.parse(code)) if isinstance(n,(ast.Import,ast.ImportFrom)) for a in n.names})
    versions={}
    for name in packages:
        try:versions[name]=importlib.metadata.version('scikit-learn' if name=='sklearn' else name)
        except importlib.metadata.PackageNotFoundError:versions[name]='stdlib or unavailable; provision before parity'
    record={'schema_version':1,'entry':config['entry'],'component_ids':config['component_ids'],
            'source':provenance,'manifest_sha256':canonical(manifest),'artifacts':refs,'packages':versions,
            'notebook_sha256':digest(output/'production_handoff.ipynb'),'config_sha256':canonical(config),'status':'unverifiable'}
    save_json(output/'handoff-manifest.json',record)
    return output/'production_handoff.ipynb'


def compare(expected,actual,atol=0.0,rtol=0.0):
    import math
    if isinstance(expected,bool) or expected is None or isinstance(expected,str):
        if type(expected)!=type(actual) or expected!=actual:raise AssertionError('Output value/type differs')
    elif isinstance(expected,(int,float)):
        if isinstance(actual,bool) or not isinstance(actual,(int,float)) or not math.isfinite(actual) or not math.isfinite(expected) or not math.isclose(expected,actual,abs_tol=atol,rel_tol=rtol):raise AssertionError('Numeric parity failure')
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(expected)!=len(actual):raise AssertionError('Output shape differs')
        for x,y in zip(expected,actual):compare(x,y,atol,rtol)
    elif isinstance(expected,dict):
        if not isinstance(actual,dict) or expected.keys()!=actual.keys():raise AssertionError('Output keys differ')
        for k in expected:compare(expected[k],actual[k],atol,rtol)
    else:raise AssertionError('Unsupported output type')


def parity(root,notebook,config):
    """Run original and extracted code independently; persist failed reports as well."""
    root=Path(root).resolve();notebook=Path(notebook).resolve();report={'status':'failed','stage':'production-handoff','fixtures':[]}
    try:
        nb=load_json(notebook);record=load_json(notebook.parent/'handoff-manifest.json')
        if canonical(config)!=record['config_sha256']:raise AssertionError('Handoff configuration/approval changed after extraction')
        if (root/'components.json').exists() and canonical(load_json(root/'components.json'))!=record['manifest_sha256']:raise AssertionError('Component manifest changed after extraction')
        if digest(notebook)!=record['notebook_sha256']:raise AssertionError('Notebook changed after extraction')
        for item in record['source']:
            if digest(resolve(root,item['path']))!=item['file_sha256']:raise AssertionError('Research source changed after extraction')
        tol=config.get('tolerance',{'atol':0.0,'rtol':0.0})
        if any(tol.get(k,0)!=0 for k in ('atol','rtol')):
            a=config.get('parity_approval',{})
            if not a.get('by') or not a.get('reference') or not a.get('reason') or a.get('tolerance_sha256')!=canonical(tol):raise AssertionError('Non-strict parity requires explicit approved justification')
        if not config.get('fixtures'):raise AssertionError('No parity fixtures')
        artifacts={k:str(verify_reference(root,v)) for k,v in record['artifacts'].items()}
        code='\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code')
        for fixture in config['fixtures']:
            source=resolve(root,fixture['path'])
            if digest(source)!=fixture['sha256']:raise AssertionError('Fixture hash mismatch')
            with tempfile.TemporaryDirectory(prefix='isolated-inference-') as tmp:
                tmp=Path(tmp);data=tmp/'input.json';data.write_bytes(source.read_bytes());expected=tmp/'reference.json';actual=tmp/'actual.json'
                # Original executes the approved entry, preserving real local imports.
                original='import sys,json,importlib;from pathlib import Path;sys.path.insert(0,'+repr(str(root))+');fn=getattr(importlib.import_module('+repr(config['entry']['path'][:-3].replace('/','.'))+'),'+repr(config['entry']['symbol'])+');Path('+repr(str(expected))+').write_text(json.dumps(fn(json.loads(Path('+repr(str(data))+').read_text()),'+repr(artifacts)+'),allow_nan=False))'
                subprocess.run([sys.executable,'-I','-c',original],cwd=tmp,check=True,capture_output=True,timeout=120)
                guard='import sys,os\n_RESEARCH_ROOT = '+repr(str(root))+'\ndef _deny_research_access(event, args):\n    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):\n        filename = os.path.realpath(os.fsdecode(args[0]))\n        if filename == _RESEARCH_ROOT or filename.startswith(_RESEARCH_ROOT + os.sep):\n            raise RuntimeError("Notebook attempted research repository access: " + filename)\nsys.addaudithook(_deny_research_access)\n'
                script=tmp/'inference.py';script.write_text(guard+code+'\npredict_from_files('+repr(str(data))+','+repr(str(actual))+','+repr(artifacts)+')\n')
                env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME')}
                # -I + temporary cwd removes checkout imports. This is import isolation, not a security sandbox.
                result=subprocess.run([sys.executable,'-I',str(script)],cwd=tmp,env=env,capture_output=True,text=True,timeout=120)
                if result.returncode:raise AssertionError('Isolated inference failed: '+result.stderr[-2000:])
                want=load_json(expected);got=load_json(actual)
                if config.get('output_schema'):assert_contract(got,config['output_schema'])
                compare(want,got,**tol)
                report['fixtures'].append({'path':fixture['path'],'sha256':fixture['sha256'],'reference_sha256':digest(expected),'isolated_output_sha256':digest(actual),'status':'verified'})
        report.update(status='verified',isolation='python -I, temporary cwd, no research import path, audit guard denies research file reads',notebook_sha256=digest(notebook),
                      tolerance=tol,limitations=['Static extraction supports explicit top-level symbols only.','Parity covers supplied fixtures and environment, not every future input.','Execution requires reviewed trusted source; isolation is not a security sandbox.'])
    except (OSError,ValueError,KeyError,AssertionError,subprocess.SubprocessError) as exc:report['error']=str(exc)
    save_json(notebook.parent/'parity-report.json',report)
    return report


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('command',choices=['build','parity']);p.add_argument('root',type=Path);p.add_argument('manifest',type=Path);p.add_argument('config',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();config=load_json(a.config)
    if a.command=='build':print(build(a.root,load_json(a.manifest),config,a.output));return 0
    result=parity(a.root,a.output/'production_handoff.ipynb',config);print(result['status']);return int(result['status']!='verified')

if __name__=='__main__':raise SystemExit(main())
