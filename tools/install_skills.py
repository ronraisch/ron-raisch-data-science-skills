"""Copy selected portable skills into a harness' skills directory, without clobbering."""
import argparse
from pathlib import Path
import shutil


def install(names, destination):
    source=Path(__file__).resolve().parents[1]/'skills'
    available={p.name:p for p in source.iterdir() if (p/'SKILL.md').is_file()}
    names=sorted(available) if names==['all'] else names
    if not names or len(set(names)) != len(names):
        raise ValueError('Choose unique skill names or all')
    for name in names:
        if name not in available:raise ValueError(f'Unknown skill: {name}')
        if (destination/name).exists():raise FileExistsError(destination/name)
    destination.mkdir(parents=True,exist_ok=True)
    for name in names:shutil.copytree(available[name],destination/name)
    return names


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--destination',type=Path,required=True)
    args=p.parse_args();print('\n'.join(install(args.names,args.destination)))
