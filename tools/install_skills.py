"""Copy selected portable skills into a harness' skills directory, without clobbering."""
import argparse
from pathlib import Path
import shutil
import re


def install(names, destination):
    source=Path(__file__).resolve().parents[1]/'skills'
    available={p.name:p for p in source.iterdir() if (p/'SKILL.md').is_file()}
    names=sorted(available) if names==['all'] else names
    if not names or len(set(names)) != len(names):
        raise ValueError('Choose unique skill names or all')
    for name in names:
        if name not in available:raise ValueError(f'Unknown skill: {name}')
    pending=list(names)
    closure=set(names)
    while pending:
        name=pending.pop()
        for dependency in re.findall(r'\]\(\.\./([a-z0-9-]+)/SKILL\.md\)', (available[name]/'SKILL.md').read_text()):
            if dependency not in available:raise ValueError(f'Unknown skill dependency: {dependency}')
            if dependency not in closure:
                closure.add(dependency);pending.append(dependency)
    names=sorted(closure)
    for name in names:
        if (destination/name).exists():raise FileExistsError(destination/name)
    destination.mkdir(parents=True,exist_ok=True)
    for name in names:shutil.copytree(available[name],destination/name,ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return names



def agents_paragraph():
    return (Path(__file__).resolve().parents[1]/'templates/agents-research.md').read_text().strip()


def inspect_agents_file(filename):
    filename=Path(filename)
    if filename.is_symlink() or filename.exists() and not filename.is_file():
        raise ValueError('AGENTS.md must be a regular file; symlinks are not modified')
    content=filename.read_text() if filename.exists() else ''
    begin='<!-- ron-data-science-skills:research-start -->'
    end='<!-- /ron-data-science-skills:research-start -->'
    if (begin in content)!=(end in content) or begin in content and content.index(begin)>content.index(end):
        raise ValueError('Incomplete research skills block in AGENTS.md')
    paragraph=agents_paragraph()
    return content,begin in content or paragraph in content


def append_agents_paragraph(filename):
    filename=Path(filename)
    content,present=inspect_agents_file(filename)
    if present:return False
    paragraph=agents_paragraph()
    begin='<!-- ron-data-science-skills:research-start -->'
    end='<!-- /ron-data-science-skills:research-start -->'
    filename.parent.mkdir(parents=True,exist_ok=True)
    gap=('\n' if content.endswith('\n') else '\n\n') if content else ''
    with filename.open('a') as stream:stream.write(gap+begin+'\n'+paragraph+'\n'+end+'\n')
    return True


if __name__=='__main__':
    import sys
    p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--destination',type=Path,required=True)
    group=p.add_mutually_exclusive_group();group.add_argument('--with-agents',action='store_true');group.add_argument('--no-agents',action='store_true')
    p.add_argument('--agents-md',type=Path,default=Path('AGENTS.md'))
    args=p.parse_args();consent=args.with_agents
    if not args.with_agents and not args.no_agents and sys.stdin.isatty() and sys.stdout.isatty():
        print(f'Optional paragraph for {args.agents_md.resolve()}:\n\n{agents_paragraph()}\n\nThis also installs research-start and its linked skills.')
        consent=input('Append this paragraph? [y/N] ').strip().lower() in ('y','yes')
    if consent:inspect_agents_file(args.agents_md)
    names=args.names
    if consent and names!=['all'] and 'research-start' not in names:names=[*names,'research-start']
    print('\n'.join(install(names,args.destination)))
    if consent:
        print('Research paragraph added.' if append_agents_paragraph(args.agents_md) else 'Existing research paragraph preserved.')
    else:print('AGENTS.md unchanged. Use --with-agents to opt in.')
