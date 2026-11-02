"""Render local file records to a single offline HTML file. No server/JS needed."""
import argparse
from html import escape
from pathlib import Path
from tools.experiment_verification.records import validate_project, inspect_runs, best_runs
from tools.experiment_verification.core import load_json, resolve
from urllib.parse import urlsplit
from tools.experiment_verification.comparison import compare_runs
from tools.experiment_verification.visual import visual_evidence
import base64


def reference_link(value):
    value=str(value or '')
    if urlsplit(value).scheme in ('https','http','file','nfs','hf'):
        return '<a href="'+escape(value,quote=True)+'" rel="noreferrer">'+escape(value)+'</a>'
    return escape(value)


def component_panel(root,project,runs):
    e=lambda v:escape(str(v))
    items=[]
    if project.get('components'):
        m=load_json(resolve(root,project['components']))
        for c in sorted(m['components'],key=lambda c:c['path']):
            items.append('<tr><td>'+e(c['path'])+'</td><td>'+e(c['id'])+'</td><td>'+e(c['version'])+'</td><td>'+e(c['purpose'])+'</td></tr>')
    hierarchy='<table><tr><th>Hierarchy</th><th>Identity</th><th>Version</th><th>Purpose</th></tr>'+''.join(items)+'</table>' if items else '<p>Legacy record: no component hierarchy or controlled-scope guarantee.</p>'
    scopes=[]
    for run in runs:
        detail=run.get('component_verification',{})
        allowed=run.get('specification',{}).get('components',{}).get('allowed_changes','not recorded')
        failures=[c for c in run.get('checks',[]) if c['name'].startswith('components.') and c['status']!='verified']
        trackers=' '.join(reference_link(run.get(k)) for k in ('tracker_url','zenml_url') if run.get(k))
        scopes.append('<details><summary>'+e(run['id'])+' — scope '+e(allowed)+' — '+e(detail.get('status','unknown'))+'</summary><pre>'+e(detail)+'</pre><pre>'+e(failures)+'</pre>'+trackers+'</details>')
    artifacts=''.join('<li>'+e(a.get('identity'))+' '+reference_link(a.get('uri',a.get('path')))+'<br><small>'+e({k:v for k,v in a.items() if k not in ('uri','path')})+'</small></li>' for a in project.get('external_artifacts',[])) or '<li>No external artifact references recorded</li>'
    timeline=''.join('<li>'+e(x.get('date','unknown'))+' — '+e(x.get('event',''))+'</li>' for x in project.get('timeline',[])) or '<li>No dated timeline recorded; inspect research notes.</li>'
    return '<h3>Component hierarchy and versions</h3>'+hierarchy+'<h3>Authorized scopes and verification details</h3>'+''.join(scopes)+'<h3>External artifacts</h3><ul>'+artifacts+'</ul><p>Artifacts remain external. NFS paths require a mounted share; this host serves only the HTML snapshot.</p><h3>Research timeline</h3><ul>'+timeline+'</ul>'


def investigation_panel(root,project,runs):
    comparison=compare_runs(root,project)
    e=lambda x:escape(str(x))
    content='<h3>Many-run tradeoffs</h3><p>All verified runs under matching evaluation conditions; Pareto frontier is descriptive, not a causal claim. Missing cost measurements remain unknown.</p>'
    for cohort in comparison['cohorts']:
        content+='<p>Pareto frontier: '+e(cohort['pareto'])+'; unmeasured objectives: '+e(cohort['missing_objectives'])+'</p><table><tr><th>Run</th><th>Measurements</th><th>Changed scope</th></tr>'+''.join('<tr><td>'+e(r['id'])+'</td><td>'+e(r['values'])+'</td><td>'+e(r['scope'])+'</td></tr>' for r in cohort['runs'])+'</table><details><summary>All pairwise deltas</summary><pre>'+e(cohort['pairs'])+'</pre></details>'
    content+='<h3>Visual proof and edge cases</h3>'
    for run in runs:
        evidence=visual_evidence(root,run.get('runtime',{}))
        content+='<h4>'+e(run['id'])+' — '+e(evidence['status'])+'</h4>'
        for item in evidence['entries']:
            try:
                path=resolve(root,item['path'])
                from tools.experiment_verification.core import digest
                if digest(path)!=item['sha256']:continue
                mime={'.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg'}[path.suffix.lower()]
                data=base64.b64encode(path.read_bytes()).decode()
                # SVG is only an image resource; never inline untrusted SVG markup.
                content+='<figure><img style="max-width:480px;width:100%" src="data:'+mime+';base64,'+data+'" alt="'+escape(item['caption'],quote=True)+'"><figcaption>'+e(item['sample_id'])+' / '+e(item['kind'])+': '+e(item['caption'])+'<br>Expected: '+e(item['expected'])+'<br>Observed: '+e(item['observed'])+'</figcaption></figure>'
            except (OSError,ValueError,KeyError,TypeError):continue
        content+='<p>'+e(evidence['errors'])+'</p>'
    return content


def render(roots):
    cards=[]
    for root in roots:
        root=Path(root)
        try:
            project,errors=validate_project(root)
            if errors:
                raise ValueError("; ".join(errors))
            runs=inspect_runs(root,project)
            e=lambda v:escape(str(v))
            rows="".join(f"<tr><td>{e(r['id'])}</td><td>{e(r['status'])}</td><td>{e(r['verification'])}</td><td>{e(r.get('runtime',{}).get('result','unknown'))}</td></tr>" for r in runs)
            findings="".join(f"<li><strong>{e(f['kind'])}</strong>: {e(f['claim'])}<br><small>Evidence: {e(', '.join(f['evidence']))}</small></li>" for f in project["findings"])
            hypotheses="".join(f"<li>{e(h['id'])}: {e(h['statement'])} — {e(h['status'])}</li>" for h in project["hypotheses"])
            nexts="".join(f"<li>{e(n)}</li>" for n in project["next_experiments"])
            bests="".join(f"<li>{e(b['metric'])}: {e(b['best'])}</li>" for b in best_runs(root,project)) or '<li>No eligible verified results</li>'
            docs=[]
            # Embed human notes as escaped text; never render record HTML or execute links.
            for name in project["documents"]:
                from tools.experiment_verification.core import resolve
                path=resolve(root,name)
                if path.suffix in (".md", ".json"):
                    docs.append(f"<details><summary>{e(name)}</summary><pre>{e(path.read_text())}</pre></details>")
            cards.append(f'''<article><h2>{e(project['title'])}</h2><p class="status">{e(project['status'])}</p>
<p><strong>Objective:</strong> {e(project['objective'])}</p><p><strong>Question:</strong> {e(project['question'])}</p>
<p><strong>Pause reason:</strong> {e(project.get('pause_reason') or 'not recorded')}</p>
<h3>Hypotheses (recorded interpretation)</h3><ul>{hypotheses}</ul>
<h3>Runs (verification recomputed at build)</h3><table><thead><tr><th>Run</th><th>Process</th><th>Verification</th><th>Result</th></tr></thead><tbody>{rows}</tbody></table>
<h3>Best verified by evaluation cohort</h3><ul>{bests}</ul><p>Audit budget, seeds and changed factors before attributing a gain.</p>
<h3>Findings and negative results</h3><ul>{findings}</ul><h3>Next experiments</h3><ul>{nexts}</ul>
{component_panel(root,project,runs)}{investigation_panel(root,project,runs)}<h3>Research notes</h3>{''.join(docs)}</article>''')
        except (OSError,ValueError,KeyError,TypeError) as exc:
            cards.append(f'<article><h2>Invalid/unavailable project</h2><p>{escape(str(root))}: {escape(str(exc))}</p></article>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'">
<title>Research records</title><style>body{font:16px system-ui;background:#f3f6f8;color:#182b38;max-width:1050px;margin:40px auto;padding:0 20px}article{background:white;padding:28px;margin:24px 0;border:1px solid #ccd7df;border-radius:10px}h1,h2{color:#163e56}h3{margin-top:28px}table{border-collapse:collapse;width:100%;overflow:auto;display:block}td,th{padding:10px;border-bottom:1px solid #dde5ea;text-align:left}.status{font-weight:700;color:#694b0a}li{margin:9px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px ui-monospace;background:#f4f6f8;padding:16px}summary{padding:12px;cursor:pointer}small{color:#435764}</style>
<h1>Research records</h1><p>Local snapshot of research questions, evidence, failures, pause reasons and next steps. Rebuild after files change. No tracker or account required.</p>'''+''.join(cards)+"</html>\n"


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("projects",nargs="+",type=Path);p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(render(args.projects));print(args.output)
