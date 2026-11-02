"""Many-run descriptive comparison; a reference run is optional, never privileged."""
import math
from .records import inspect_runs


def compare_runs(root,project,objectives=None):
    automatic=objectives is None
    objectives=objectives or {'result':'maximize','latency_ms':'minimize','parameters':'minimize'}
    if not objectives or any(v not in ('maximize','minimize') for v in objectives.values()):raise ValueError('Invalid objectives')
    groups={};excluded=[]
    for run in inspect_runs(root,project):
        if run['status']!='completed' or run['verification']!='verified':
            excluded.append({'id':run['id'],'reason':run['verification']});continue
        spec=run['specification'];metric=spec['expected']['metric']
        key=(spec['dataset']['sha256'],spec['splits']['sha256'],spec['evaluation_protocol'],str(sorted(metric.items())))
        runtime=run['runtime'];values={'result':runtime['result'],**runtime.get('tradeoffs',{})}
        # Missing measurements stay unknown; never impute zero cost.
        values={k:v for k,v in values.items() if k in objectives and isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)}
        if automatic:objectives=dict(objectives,result=metric['direction'])
        groups.setdefault(key,[]).append({'id':run['id'],'values':values,'scope':spec.get('components',{}).get('allowed_changes'),
                                         'result_direction':metric['direction'],'note':'Descriptive tradeoff, not proof of isolated causal effect'})
    cohorts=[]
    for rows in groups.values():
        if automatic:objectives=dict(objectives,result=rows[0]['result_direction'])
        available=[k for k in objectives if all(k in r['values'] for r in rows)]
        def dominates(a,b):
            def gain(k):return (a['values'][k]-b['values'][k])*(1 if objectives[k]=='maximize' else -1)
            return bool(available) and all(gain(k)>=0 for k in available) and any(gain(k)>0 for k in available)
        frontier=[r['id'] for r in rows if not any(dominates(other,r) for other in rows)]
        pairs=[{'left':a['id'],'right':b['id'],'delta_right_minus_left':{k:b['values'][k]-a['values'][k] for k in available}} for i,a in enumerate(rows) for b in rows[i+1:]]
        cohorts.append({'runs':rows,'objectives':{k:objectives[k] for k in available},'pareto':frontier,'pairs':pairs,
                        'missing_objectives':sorted(set(objectives)-set(available))})
    return {'cohorts':cohorts,'excluded':excluded}
