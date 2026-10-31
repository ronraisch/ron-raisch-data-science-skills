"""Explicit developer commands; never execute commands from a manifest."""
import argparse
from pathlib import Path
from .core import load_json, save_json, aggregate
from .components import snapshot, verify_scope


def main():
    p=argparse.ArgumentParser(description='Snapshot or preflight component scope')
    p.add_argument('command',choices=['snapshot','check']);p.add_argument('manifest',type=Path)
    p.add_argument('--root',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--baseline',type=Path);p.add_argument('--scope',type=Path)
    a=p.parse_args()
    try:
        m=load_json(a.manifest)
        if a.command=='snapshot':save_json(a.output,snapshot(a.root,m));return 0
        if not a.baseline or not a.scope:p.error('check needs --baseline and --scope')
        checks,_,owners=verify_scope(a.root,m,load_json(a.baseline),load_json(a.scope))
        save_json(a.output,{'status':aggregate(checks),'checks':checks,'affected_sources':owners})
        return int(aggregate(checks)!='verified')
    except (OSError,ValueError,AssertionError,KeyError,TypeError) as exc:p.exit(2,str(exc)+'\n')

if __name__=='__main__':raise SystemExit(main())
