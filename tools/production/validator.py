"""Generate a single standalone validator.py from explicit approved criteria."""
from pathlib import Path
import ast
import json
from tools.experiment_verification.components import canonical
from tools.experiment_verification.core import save_json, digest


def validate_policy(policy):
    if policy.get('schema_version')!=1 or policy.get('task') not in ('detection','segmentation'):
        raise ValueError('Unsupported validation task/schema')
    if policy.get('strategy') not in ('ground_truth','reference','hybrid','invariants'):
        raise ValueError('Choose explicit validation strategy')
    if not isinstance(policy.get('files'),dict) or not policy['files']:raise ValueError('Nonempty project-specific sample/file map required')
    pred_paths=[];test_paths=[]
    for sample,paths in policy['files'].items():
        if not isinstance(sample,str) or not sample or not isinstance(paths,dict):raise ValueError('Invalid sample map')
        for name,store in [('prediction',pred_paths),('test',test_paths)]:
            p=paths.get(name)
            if not isinstance(p,str) or not p or Path(p).is_absolute() or '..' in Path(p).parts:raise ValueError('Unsafe sample path')
            store.append(p)
    if len(set(pred_paths))!=len(pred_paths) or len(set(test_paths))!=len(test_paths):raise ValueError('File mappings must be one-to-one')
    if not policy.get('classes') or len(set(policy['classes']))!=len(policy['classes']):raise ValueError('Declare unique classes')
    if policy['task']=='detection' and any(not isinstance(x,str) for x in policy['classes']):raise ValueError('Detection classes are names')
    if policy['task']=='segmentation' and any(not isinstance(x,int) or isinstance(x,bool) for x in policy['classes']):raise ValueError('Segmentation classes are integer labels')
    def bounded(x,lo=0,hi=1):
        import math
        if not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) or not lo<=x<=hi:raise ValueError('Invalid threshold')
    if policy['task']=='detection':bounded(policy.get('score_threshold'))
    if policy['strategy'] in ('ground_truth','hybrid'):
        if not policy.get('quality'):raise ValueError('Quality thresholds required')
        allowed={'ap50','precision','recall','false_alarms_per_sample'} if policy['task']=='detection' else {'mean_iou'}
        for name,bounds in policy['quality'].items():
            if name not in allowed or not bounds or set(bounds)-{'minimum','maximum'}:raise ValueError('Invalid metric bounds')
            for x in bounds.values():bounded(x,0,float('inf') if name=='false_alarms_per_sample' else 1)
            if bounds.get('minimum',0)>bounds.get('maximum',float('inf')):raise ValueError('Inverted threshold')
    if policy['strategy'] in ('reference','hybrid'):
        keys=['min_box_iou','score_atol'] if policy['task']=='detection' else ['min_pixel_agreement']
        for k in keys:bounded(policy.get('reference',{}).get(k))
        if policy['task']=='detection' and policy['reference']['min_box_iou']==0:raise ValueError('Box matching requires positive IoU')
    for rule in policy.get('metamorphic',[]):
        if rule.get('relation') not in ('horizontal_flip','duplicate_input') or rule.get('base') not in policy['files'] or rule.get('transformed') not in policy['files'] or rule['base']==rule['transformed']:
            raise ValueError('Invalid metamorphic sample pair/relation')
        if policy['task']=='detection':
            bounded(rule.get('min_box_iou'));bounded(rule.get('score_atol'))
            if rule['min_box_iou']<=0:raise ValueError('Metamorphic box IoU must be positive')
            if rule['relation']=='horizontal_flip':bounded(rule.get('width'),1,float('inf'))
        else:bounded(rule.get('min_pixel_agreement'))
    approval=policy.get('approval',{})
    intent={k:v for k,v in policy.items() if k!='approval'}
    if not all(approval.get(k) for k in ('by','role','reference')) or approval['role'] not in ('research-lead','product-stakeholder') or approval.get('policy_sha256')!=canonical(intent):
        raise ValueError('Research lead/product approval must bind the proposed policy, not observed results')
    return policy


def generate(policy,output):
    validate_policy(policy);output=Path(output)
    if output.exists():raise FileExistsError(output)
    source=Path(__file__).with_name('validator_runtime.py').read_text()
    source='POLICY = '+repr(policy)+'\n\n'+source
    ast.parse(source);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(source)
    save_json(output.with_name('validator-manifest.json'),{'schema_version':1,'validator_sha256':digest(output),'policy':policy,
              'protocol':'xyxy continuous boxes, one-to-one class matching, all-point interpolated macro AP50 on GT-present classes; segmentation macro IoU on union-present declared classes',
              'limits':'Axis-aligned boxes / dense integer masks only. OBB, void labels, partial annotations, custom layouts need reviewed adapters and tests.'})
    return output


def main():
    import argparse
    from tools.experiment_verification.core import load_json
    p=argparse.ArgumentParser();p.add_argument('policy',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    print(generate(load_json(a.policy),a.output))

if __name__=='__main__':main()
