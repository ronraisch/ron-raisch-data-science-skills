"""Render local file records to a single offline HTML file. No server/JS needed."""
import argparse
from html import escape
from pathlib import Path
from tools.experiment_verification.records import validate_project, inspect_runs, best_runs


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
                if path.suffix==".md":
                    docs.append(f"<details><summary>{e(name)}</summary><pre>{e(path.read_text())}</pre></details>")
            cards.append(f'''<article><h2>{e(project['title'])}</h2><p class="status">{e(project['status'])}</p>
<p><strong>Objective:</strong> {e(project['objective'])}</p><p><strong>Question:</strong> {e(project['question'])}</p>
<p><strong>Pause reason:</strong> {e(project.get('pause_reason') or 'not recorded')}</p>
<h3>Hypotheses (recorded interpretation)</h3><ul>{hypotheses}</ul>
<h3>Runs (verification recomputed at build)</h3><table><thead><tr><th>Run</th><th>Process</th><th>Verification</th><th>Result</th></tr></thead><tbody>{rows}</tbody></table>
<h3>Best verified by evaluation cohort</h3><ul>{bests}</ul><p>Audit budget, seeds and changed factors before attributing a gain.</p>
<h3>Findings and negative results</h3><ul>{findings}</ul><h3>Next experiments</h3><ul>{nexts}</ul>
<h3>Research notes</h3>{''.join(docs)}</article>''')
        except (OSError,ValueError,KeyError,TypeError) as exc:
            cards.append(f'<article><h2>Invalid/unavailable project</h2><p>{escape(str(root))}: {escape(str(exc))}</p></article>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; base-uri 'none'; form-action 'none'">
<title>Research records</title><style>body{font:16px system-ui;background:#f3f6f8;color:#182b38;max-width:1050px;margin:40px auto;padding:0 20px}article{background:white;padding:28px;margin:24px 0;border:1px solid #ccd7df;border-radius:10px}h1,h2{color:#163e56}h3{margin-top:28px}table{border-collapse:collapse;width:100%;overflow:auto;display:block}td,th{padding:10px;border-bottom:1px solid #dde5ea;text-align:left}.status{font-weight:700;color:#694b0a}li{margin:9px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px ui-monospace;background:#f4f6f8;padding:16px}summary{padding:12px;cursor:pointer}small{color:#435764}</style>
<h1>Research records</h1><p>Local snapshot of research questions, evidence, failures, pause reasons and next steps. Rebuild after files change. No tracker or account required.</p>'''+''.join(cards)+"</html>\n"


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("projects",nargs="+",type=Path);p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(render(args.projects));print(args.output)
