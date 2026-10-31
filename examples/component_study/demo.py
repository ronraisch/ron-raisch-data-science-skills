"""Real CPU image inference, scope failures, isolated extraction and CV validation.

Generated outputs are a tiny synthetic functional example, not performance evidence.
"""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from tools.experiment_verification.core import save_json, load_json, digest, verify, write_report, aggregate
from tools.experiment_verification.components import snapshot, canonical, verify_scope, observe_component
from tools.experiment_verification.runtime import observe, capture_environment
from tools.production.handoff import build as handoff_build, parity, extract
from tools.production.validator import generate


def manifest():
    array={'type':'array','minItems':1,'items':{'type':'array','minItems':1,'items':{'type':'number','minimum':0,'maximum':1}}}
    output_schema={'type':'object','required':['detections','segmentation'],'additionalProperties':False,
       'properties':{'detections':{'type':'array','items':{'type':'object','required':['box','label','score'],'additionalProperties':False,
          'properties':{'box':{'type':'array','minItems':4,'maxItems':4,'items':{'type':'number'}},'label':{'type':'string','enum':['object']},'score':{'type':'number','minimum':0,'maximum':1}}}},
       'segmentation':{'type':'array','minItems':1,'items':{'type':'array','minItems':1,'items':{'type':'integer','enum':[0,1]}}}}}
    def c(identity,path,purpose,sources,dependencies=(),ins=None,outs=None):
        return {'id':identity,'path':path,'version':'1.0.0','purpose':purpose,
                'inputs':ins or {'type':'object'},'outputs':outs or {'type':'object'},
                'invariants':['Finite inputs/outputs; preserve image dimensions'],
                'config_schema':{'type':'object','additionalProperties':False},'config':{},
                'dependencies':list(dependencies),'sources':sources,'contract_tests':['finite-shape']}
    return {'schema_version':1,'watch':['*.py','*.lock'],'record_roots':['runs','records'],
            'components':[c('model','model','Image detector and segmenter',[],outs=output_schema),
                c('features','model.feature_extraction','Normalize image pixels',[
                    {'path':'features.py','symbol':'extract'},{'path':'common.py','symbol':'clip'}],ins={'type':'array'},outs=array),
                c('decoder','model.decoder','Decode foreground objects and masks',[
                    {'path':'decoder.py','symbol':'decode'},{'path':'common.py','symbol':'clip'}],['features'],ins=array,outs=output_schema),
                c('inference','inference','Load checkpoint and predict',[
                    {'path':'inference.py','symbol':'predict'}],['decoder'],outs=output_schema)]}


def approve_scope(allowed):
    return {'allowed_changes':allowed,'approval':{'by':'example researcher','reference':'decisions.md#scope','scope_sha256':canonical(allowed)}}


def policy(task):
    p={'schema_version':1,'task':task,'strategy':'hybrid','classes':['object'] if task=='detection' else [0,1],
       'files':{'validation-1':{'prediction':'team-results/sample.json','test':'approved/sample.json'}},
       'quality':{'ap50':{'minimum':1.0},'recall':{'minimum':1.0}} if task=='detection' else {'mean_iou':{'minimum':1.0}},
       'reference':{'min_box_iou':0.99,'score_atol':0.001} if task=='detection' else {'min_pixel_agreement':1.0}}
    if task=='detection':p['score_threshold']=0.5
    p['approval']={'by':'demo lead','role':'research-lead','reference':'decisions.md#acceptance','policy_sha256':canonical(p)}
    return p


def invoke(root,inputs,artifacts):
    # Subprocess avoids cross-project module cache contamination.
    code='import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from inference import predict;print(json.dumps(predict(json.loads(Path(sys.argv[2]).read_text()),json.loads(sys.argv[3]))))'
    return json.loads(subprocess.check_output([sys.executable,'-I','-c',code,str(root),str(inputs),json.dumps(artifacts)],text=True))


def build(output):
    root=Path(output).resolve()
    if root.exists():raise FileExistsError(root)
    root.mkdir(parents=True)
    for p in Path(__file__).with_name('source').glob('*.py'):shutil.copy2(p,root/p.name)
    (root/'decisions.md').write_text('# Scope\nExample researcher authorizes model.decoder only.\n\n# Acceptance\nDemo lead approves exact toy outputs and perfect quality for this functional fixture. These are not operational thresholds.\n')
    m=manifest();baseline=snapshot(root,m);save_json(root/'records/baseline.json',baseline)
    # Authorized code change is local to decoder; no protected implementation changes.
    p=root/'decoder.py';p.write_text(p.read_text().replace('value >= threshold','value >= threshold - 0.05'))
    m['components'][2]['version']='1.0.1';save_json(root/'components.json',m)
    scope=approve_scope(['model.decoder']);checks,current,owners=verify_scope(root,m,baseline,scope)
    if aggregate(checks)!='verified':raise AssertionError(checks)
    save_json(root/'records/scope.json',{'status':aggregate(checks),'checks':checks,'affected_sources':owners})
    # External artifact stands in for mounted NFS; never place model bytes in Git records.
    artifact_root=root.parent/(root.name+'-nfs');artifact_root.mkdir(exist_ok=False)
    save_json(artifact_root/'checkpoint.json',{'threshold':0.6})
    checkpoint={'identity':'toy-threshold-model','uri':(artifact_root/'checkpoint.json').as_uri(),'version':'1',
                'sha256':digest(artifact_root/'checkpoint.json'),'provenance':'CPU demo synthetic fixed parameter, no training'}
    data=[]
    for i in range(3):
        pixels=[[10+i for _ in range(6)] for _ in range(6)]
        for y in range(1,4):
            for x in range(2,5):pixels[y][x]=210+i
        data.append({'id':['train-1','validation-1','test-1'][i],'group':str(i),'pixels':pixels,'target':1})
    save_json(root/'data/images.json',data);save_json(root/'data/splits.json',dict(train=['train-1'],validation=['validation-1'],test=['test-1']))
    sample=data[1];save_json(root/'data/fixture.json',{'pixels':sample['pixels']})
    prediction=invoke(root,root/'data/fixture.json',{'checkpoint':str(artifact_root/'checkpoint.json')})
    for scenario,filename,old,new in [('unauthorized-extractor','features.py','255.0','254.0'),('shared-utility','common.py','1.0','0.9')]:
        path=root/filename;original=path.read_bytes();path.write_text(original.decode().replace(old,new))
        try:
            bad,_,_=verify_scope(root,m,baseline,scope)
            save_json(root/f'records/{scenario}.json',{'status':aggregate(bad),'checks':bad})
            if aggregate(bad)!='failed':raise AssertionError('Unauthorized scenario passed')
        finally:path.write_bytes(original)
    env=lambda:{'python':sys.version.split()[0],'git_revision':capture_environment(Path(__file__).resolve().parents[2])['git_revision']}
    expected={'preprocessing':{'scale':255.0},'model':{'decoder':'decode'},'checkpoint':{'sha256':checkpoint['sha256']},
              'parameters':{'trainable':0},'optimizer':None,'scheduler':None,'hyperparameters':{'threshold':0.6},
              'training':{'steps':0,'mode':'inference-only'},'metric':{'name':'accuracy','split':'validation','direction':'maximize'},'environment':env()}
    spec={'schema_version':1,'id':'decoder-v1','hypothesis_id':'H1','decision_rule':'Functional smoke only; quality/generalization remain untested',
          'evaluation_protocol':'binary object presence v1, sealed test; CV quality is independently checked at production validation',
          'dataset':{'path':'data/images.json','sha256':digest(root/'data/images.json'),'format':'cv-json'},
          'splits':{'path':'data/splits.json','sha256':digest(root/'data/splits.json')},'required_artifacts':['predictions.csv'],'expected':expected,
          'components':dict(scope,baseline={'path':'records/baseline.json','sha256':digest(root/'records/baseline.json')},manifest={'path':'components.json','sha256':digest(root/'components.json')})}
    save_json(root/'specs/decoder.json',spec)
    run_dir=root/'runs/decoder';run_dir.mkdir(parents=True)
    with (run_dir/'predictions.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['id','target','prediction']);w.writerow([sample['id'],sample['target'],int(bool(prediction['detections']))])
    # Runtime observations are taken from the executed source/output/checkpoint, not copied from expected.
    actual={'preprocessing':{'scale':255.0},'model':{'decoder':'decode'},'checkpoint':{'sha256':digest(artifact_root/'checkpoint.json')},'parameters':{'trainable':0},'optimizer':None,'scheduler':None,'hyperparameters':load_json(artifact_root/'checkpoint.json'),'training':{'steps':0,'mode':'inference-only'},'metric':{'name':'accuracy','split':'validation','direction':'maximize'},'environment':env()}
    # Observe boundaries by executing the same original functions in a fresh process.
    boundary_code='''import sys,json;sys.path.insert(0,sys.argv[1]);from features import extract;from decoder import decode;data=json.loads(sys.argv[2]);f=extract(data);o=decode(f,0.6);print(json.dumps([f,o]))'''
    features,out=json.loads(subprocess.check_output([sys.executable,'-I','-c',boundary_code,str(root),json.dumps(sample['pixels'])],text=True))
    if prediction!=out:raise AssertionError('Boundary and pipeline disagree')
    pairs=[({'pixels':sample['pixels']},prediction),(sample['pixels'],features),(features,out),({'pixels':sample['pixels']},prediction)]
    observations=[]
    for c,(inp,outp) in zip(m['components'],pairs):
        # Executable semantic guard independent of schema: complete HxW coverage and actual binary mask.
        valid=len(prediction['segmentation'])==len(sample['pixels']) and all(len(a)==len(b) for a,b in zip(prediction['segmentation'],sample['pixels'])) and all(x in (0,1) for row in prediction['segmentation'] for x in row)
        observations.append(observe_component(c,inp,outp,{}, {'finite-shape':valid}))
    predref={'path':'runs/decoder/predictions.csv','sha256':digest(run_dir/'predictions.csv')}
    run={'schema_version':1,'run_id':'decoder','spec_sha256':digest(root/'specs/decoder.json'),'observations':{k:observe(v,'CPU inference instrumented entry') for k,v in actual.items()},'artifacts':[predref,checkpoint],'predictions':predref,'evaluation_split':'validation','result':1.0,
         'components':{'snapshot':snapshot(root,m),'observations':observations}}
    save_json(run_dir/'runtime.json',run);report=verify(spec,run,root,root/'specs/decoder.json');write_report(run_dir/'verification.json',report)
    if report['status']!='verified':raise AssertionError(report)
    handoff={'entry':{'path':'inference.py','symbol':'predict'},'component_ids':['inference'],'artifacts':{'checkpoint':checkpoint},'fixtures':[{'path':'data/fixture.json','sha256':digest(root/'data/fixture.json')}],'output_schema':{'type':'object','required':['detections','segmentation']}}
    _,provenance=extract(root,m,handoff['entry'],handoff['component_ids'])
    handoff['inference_approval']={'by':'example researcher','reference':'decisions.md#scope',
         'inference_sha256':canonical({'manifest':canonical(m),'source':provenance,'entry':handoff['entry'],'artifacts':handoff['artifacts']})}
    save_json(root/'records/handoff-config.json',handoff)
    nb=handoff_build(root,m,handoff,root/'production');parity_report=parity(root,nb,handoff)
    if parity_report['status']!='verified':raise AssertionError(parity_report)
    for task,key in [('detection','detections'),('segmentation','segmentation')]:
        folder=root/'production'/task;folder.mkdir();generate(policy(task),folder/'validator.py')
        save_json(folder/'outputs/team-results/sample.json',{'id':sample['id'],'prediction':prediction[key]})
        truth=[{'box':[2,1,5,4],'label':'object'}] if task=='detection' else [[int(2<=x<5 and 1<=y<4) for x in range(6)] for y in range(6)]
        save_json(folder/'tests/approved/sample.json',{'id':sample['id'],'reference':prediction[key],'truth':truth})
        code='import importlib.util,sys;sp=importlib.util.spec_from_file_location("validator",sys.argv[1]);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert m.validate(sys.argv[2],sys.argv[3]) is None'
        subprocess.run([sys.executable,'-I','-c',code,str(folder/'validator.py'),str(folder/'outputs'),str(folder/'tests')],check=True)
    project={'schema_version':1,'id':'component-cv','title':'Component-controlled CPU image study','objective':'Demonstrate authorized inference extraction','question':'Can decoder-only changes preserve the protected feature extractor?','status':'paused','pause_reason':'Functional example complete; operational data and thresholds not supplied','components':'components.json','external_artifacts':[checkpoint],
             'hypotheses':[{'id':'H1','statement':'Decoder changes can be isolated from feature extraction','status':'supported'}],
             'runs':[{'id':'decoder','spec':'specs/decoder.json','directory':'runs/decoder','status':'completed'}],
             'findings':[{'id':'F1','kind':'observation','claim':'Authorized decoder edit verified; extractor/shared utility edits rejected. Toy inference parity passed. No generalization claim.','evidence':['records/scope.json','records/unauthorized-extractor.json','records/shared-utility.json','production/parity-report.json'],'run_ids':['decoder'],'component_ids':['decoder']}],
             'next_experiments':['Approve real dataset and production acceptance criteria'], 'documents':['decisions.md'],
             'timeline':[{'date':'2026-10-31','event':'Controlled scope, isolated extraction and toy production validation executed'}]}
    save_json(root/'project.json',project)
    return root


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(build(a.output))

if __name__=='__main__':main()
