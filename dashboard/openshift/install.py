"""One-command OpenShift installation. Requires an existing oc login/project."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def oc(*args, input=None):
    stream = args and args[0] in ('start-build', 'rollout')
    result = subprocess.run(['oc', *args], input=input, text=True, check=True, stdout=None if stream else subprocess.PIPE)
    return result.stdout or ''


def prepare_html(projects, html):
    if html:
        data = html.read_bytes()
    else:
        from dashboard.build import render
        for root in projects:
            if not (root / 'project.json').is_file():
                raise ValueError(f'No project.json in {root}')
        data = render(projects).encode('utf-8')
    if len(data) > 900 * 1024:
        raise ValueError('Snapshot exceeds the safe ConfigMap size (900 KiB). Select fewer projects or shorten embedded notes.')
    return data


def main(argv=None):
    p = argparse.ArgumentParser(description='Install/update the static dashboard in the current OpenShift project')
    p.add_argument('projects', nargs='*', type=Path)
    p.add_argument('--html', type=Path)
    p.add_argument('--image', help='Use a prebuilt image; skip the in-cluster build. Prefer a pinned digest.')
    p.add_argument('--base-image', default='python:3.12-slim', help='Python 3.11+ base image; use an internal mirror in disconnected clusters')
    args = p.parse_args(argv)
    if bool(args.projects) == bool(args.html):
        p.error('Choose project folders or --html FILE')
    try:
        data = prepare_html(args.projects, args.html)
        if not shutil.which('oc'):
            raise ValueError('Install the OpenShift oc CLI, run oc login, then oc project YOUR_PROJECT')
        namespace = oc('project', '-q').strip()
        if not namespace:
            raise ValueError('Select a project with oc project YOUR_PROJECT')
        repo = Path(__file__).resolve().parents[2]
        image = args.image or f'image-registry.openshift-image-registry.svc:5000/{namespace}/research-records:latest'
        print(f'Installing research-records into OpenShift project {namespace}', flush=True)
        with tempfile.TemporaryDirectory(prefix='research-dashboard-') as tmp:
            stage = Path(tmp)
            (stage / 'index.html').write_bytes(data)
            print('Uploading HTML snapshot...', flush=True)
            manifest = oc('create', 'configmap', 'research-records-html', f'--from-file=index.html={stage / "index.html"}', '--dry-run=client', '-o', 'json')
            oc('apply', '-f', '-', input=manifest)
            print('Applying workload and HTTPS Route...', flush=True)
            resources = oc('process', '-f', str(repo / 'dashboard/openshift/template.yaml'), '-p', f'IMAGE={image}', '-p', f'BASE_IMAGE={args.base_image}')
            oc('apply', '-f', '-', input=resources)
            if not args.image:
                # Upload ONLY server + Containerfile, never research files, Git or credentials.
                context = stage / 'build' / 'dashboard'
                context.mkdir(parents=True)
                for name in ('serve.py', 'Containerfile'):
                    shutil.copyfile(repo / 'dashboard' / name, context / name)
                print('Building the hosting image (no research data in image)...', flush=True)
                oc('start-build', 'research-records', f'--from-dir={context.parent}', '--follow', '--wait')
            print('Waiting for the dashboard...', flush=True)
            oc('rollout', 'restart', 'deployment/research-records')
            oc('rollout', 'status', 'deployment/research-records', '--timeout=180s')
            host = oc('get', 'route', 'research-records', '-o', 'jsonpath={.spec.host}').strip()
            print(f'Dashboard: https://{host}/')
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        p.exit(1, f'Installation stopped: {exc}\nLocal project files were not modified. Fix the reported issue and rerun.\n')


if __name__ == '__main__':
    raise SystemExit(main())
