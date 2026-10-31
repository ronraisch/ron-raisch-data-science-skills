"""Standalone JSON CV acceptance engine; generator embeds this source in validator.py.

File mappings and acceptance criteria are project-approved, not a universal layout.
"""
import json
import math
from pathlib import Path


def _finite(x):
    return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)


def _read(root,relative):
    root=Path(root).resolve();path=(root/relative).resolve()
    assert isinstance(relative,str) and relative and not Path(relative).is_absolute() and path.is_relative_to(root), 'Unsafe result path'
    assert path.is_file(), 'Missing result: '+relative
    def duplicate(pairs):
        data={}
        for k,v in pairs:
            assert k not in data, 'Duplicate JSON key'
            data[k]=v
        return data
    return json.loads(path.read_text(),object_pairs_hook=duplicate,parse_constant=lambda x: (_ for _ in ()).throw(AssertionError('Nonfinite JSON')))


def _iou(a,b):
    intersection=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-intersection
    return intersection/union if union else 0.0


def _detections(items,truth=False):
    assert isinstance(items,list), 'Detections must be a list'
    for d in items:
        assert isinstance(d,dict) and set(d)==({'box','label'} if truth else {'box','label','score'}), 'Invalid detection structure'
        box=d['box']
        assert isinstance(box,list) and len(box)==4 and all(_finite(x) for x in box) and box[0]<box[2] and box[1]<box[3], 'Invalid xyxy box'
        assert isinstance(d['label'],str) and d['label'] in POLICY['classes'], 'Unknown class'
        if not truth:assert _finite(d['score']) and 0<=d['score']<=1, 'Invalid confidence'


def _mask(mask):
    assert isinstance(mask,list) and mask and all(isinstance(r,list) and r for r in mask), 'Empty/invalid mask'
    assert all(len(r)==len(mask[0]) for r in mask), 'Ragged mask'
    assert all(isinstance(x,int) and not isinstance(x,bool) and x in POLICY['classes'] for row in mask for x in row), 'Invalid mask label'


def _det_metrics(predictions,truths):
    ap=[];tp=fp=total=0
    for label in POLICY['classes']:
        gt={(i,j):d for i,ds in enumerate(truths) for j,d in enumerate(ds) if d['label']==label}
        ranked=sorted(((d['score'],i,j,d) for i,ds in enumerate(predictions) for j,d in enumerate(ds) if d['label']==label),key=lambda x:(-x[0],x[1],x[2]))
        used=set();curve=[];ctp=cfp=0
        for _,i,_,d in ranked:
            choices=[(_iou(d['box'],g['box']),key) for key,g in gt.items() if key[0]==i and key not in used]
            best=max(choices,default=(0,None))
            hit=best[0]>=0.5
            if hit:used.add(best[1]);ctp+=1
            else:cfp+=1
            curve.append((ctp/len(gt) if gt else 0,ctp/(ctp+cfp)))
            if d['score']>=POLICY['score_threshold']:
                if hit:tp+=1
                else:fp+=1
        total+=len(gt)
        if gt:
            # Explicit protocol: all-point interpolated AP at IoU 0.5, macro over GT-present classes.
            recall=[0.0]+[x[0] for x in curve]+[1.0];precision=[0.0]+[x[1] for x in curve]+[0.0]
            for j in range(len(precision)-2,-1,-1):precision[j]=max(precision[j],precision[j+1])
            ap.append(sum((recall[j]-recall[j-1])*precision[j] for j in range(1,len(recall)) if recall[j]!=recall[j-1]))
    assert total>0, 'No ground-truth positives: recall/AP undefined'
    return {'ap50':sum(ap)/len(ap),'precision':tp/(tp+fp) if tp+fp else 0.0,'recall':tp/total,'false_alarms_per_sample':fp/len(predictions)}


def _seg_metrics(predictions,truths):
    intersections={c:0 for c in POLICY['classes']};unions=intersections.copy()
    for p,t in zip(predictions,truths):
        assert len(p)==len(t) and len(p[0])==len(t[0]), 'Mask shape differs'
        for pr,tr in zip(p,t):
            for a,b in zip(pr,tr):
                for c in POLICY['classes']:
                    intersections[c]+=int(a==c and b==c);unions[c]+=int(a==c or b==c)
    values=[intersections[c]/unions[c] for c in POLICY['classes'] if unions[c]]
    assert values, 'No labeled pixels'
    return {'mean_iou':sum(values)/len(values)}


def _reference(pred,ref,criteria=None):
    criteria=POLICY['reference'] if criteria is None else criteria
    if POLICY['task']=='segmentation':
        assert len(pred)==len(ref) and len(pred[0])==len(ref[0]), 'Reference mask shape differs'
        agreement=sum(a==b for pr,rr in zip(pred,ref) for a,b in zip(pr,rr))/(len(ref)*len(ref[0]))
        assert agreement>=criteria['min_pixel_agreement'], 'Reference pixel agreement below threshold'
    else:
        assert len(pred)==len(ref), 'Reference detection count differs'
        # Find a complete threshold-compatible pairing. Greedy best-IoU pairing
        # can reject valid reordered/overlapping detections when one box has
        # two valid partners and another has only one.
        edges=[[j for j,r in enumerate(ref) if d['label']==r['label'] and
                abs(d['score']-r['score'])<=criteria['score_atol'] and
                _iou(d['box'],r['box'])>=criteria['min_box_iou']] for d in pred]
        matched={}
        def augment(i,seen):
            for j in edges[i]:
                if j in seen:continue
                seen.add(j)
                if j not in matched or augment(matched[j],seen):
                    matched[j]=i
                    return True
            return False
        for i in sorted(range(len(pred)),key=lambda i:len(edges[i])):
            assert augment(i,set()), 'Reference detections differ'



def validate(output_pred, output_test):
    if not __debug__:raise RuntimeError('Run validation without Python -O; assertions are required')
    assert POLICY['files'], 'No files to validate'
    predictions=[];truths=[];seen=set();by_sample={}
    for sample,mapping in POLICY['files'].items():
        pred=_read(output_pred,mapping['prediction']);test=_read(output_test,mapping['test'])
        assert isinstance(pred,dict) and set(pred)=={'id','prediction'}, 'Invalid output structure'
        assert isinstance(test,dict) and test.get('id')==sample and pred['id']==sample and sample not in seen, 'Sample identity mismatch'
        seen.add(sample);p=pred['prediction']
        checker=_mask if POLICY['task']=='segmentation' else _detections
        checker(p);predictions.append(p);by_sample[sample]=p
        if POLICY['strategy'] in ('reference','hybrid'):
            assert 'reference' in test, 'Missing reference output'
            checker(test['reference']);_reference(p,test['reference'])
        if POLICY['strategy'] in ('ground_truth','hybrid'):
            assert 'truth' in test, 'Missing ground truth'
            if POLICY['task']=='detection':_detections(test['truth'],truth=True)
            else:_mask(test['truth'])
            truths.append(test['truth'])
    if truths:
        metrics=_det_metrics(predictions,truths) if POLICY['task']=='detection' else _seg_metrics(predictions,truths)
        for name,bounds in POLICY['quality'].items():
            assert name in metrics, 'Unknown quality metric'
            if 'minimum' in bounds:assert metrics[name]>=bounds['minimum'], name+' below approved minimum'
            if 'maximum' in bounds:assert metrics[name]<=bounds['maximum'], name+' above approved maximum'
    for rule in POLICY.get('metamorphic',[]):
        base=by_sample[rule['base']];transformed=by_sample[rule['transformed']]
        if rule['relation']=='horizontal_flip':
            if POLICY['task']=='segmentation':expected=[list(reversed(row)) for row in base]
            else:
                width=rule['width']
                expected=[dict(d,box=[width-d['box'][2],d['box'][1],width-d['box'][0],d['box'][3]]) for d in base]
        else:expected=base # duplicate_input: approved deterministic invariance
        _reference(transformed,expected,rule)
    # Structural/finite/class/shape invariants always apply, including invariants-only strategy.
    return None
