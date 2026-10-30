"""Serve a research snapshot without exposing project files. Standard library only."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys


def handler_for(snapshot):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.respond(False)

        def do_HEAD(self):
            self.respond(True)

        def respond(self, head):
            path = self.path.split('?', 1)[0]
            if path == '/healthz':
                data, content_type = b'ok\n', 'text/plain; charset=utf-8'
            elif path in ('/', '/index.html'):
                try:
                    data = snapshot()
                except OSError:
                    self.send_error(503, 'Snapshot unavailable')
                    return
                content_type = 'text/html; charset=utf-8'
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
            self.end_headers()
            if not head:
                self.wfile.write(data)
    return Handler


def main(argv=None):
    p = argparse.ArgumentParser(description='Host a read-only research dashboard. No packages or accounts needed.')
    p.add_argument('projects', nargs='*', type=Path, help='One or more project folders containing project.json')
    p.add_argument('--html', type=Path, help='Serve an already generated HTML file instead of project folders')
    p.add_argument('--demo', action='store_true', help='Browse the included synthetic example')
    p.add_argument('--host', default='127.0.0.1', help='Default: local computer only; use 0.0.0.0 for a container')
    p.add_argument('--port', type=int, default=8080)
    args = p.parse_args(argv)
    if sum([bool(args.projects), bool(args.html), args.demo]) != 1:
        p.error('Choose project folders, --html FILE, or --demo')
    if args.demo:
        args.projects = [Path(__file__).resolve().parents[1] / 'examples/sensor-study']
    if args.html:
        try:
            args.html.read_bytes()
        except OSError as exc:
            p.error(str(exc))
        snapshot = args.html.read_bytes  # Reopen for ConfigMap atomic replacement.
    else:
        from dashboard.build import render
        for root in args.projects:
            if not (root / 'project.json').is_file():
                p.error(f'No project.json in {root}; pass the project folder, not the repository root')
        data = render(args.projects).encode('utf-8')
        snapshot = lambda: data
    try:
        server = ThreadingHTTPServer((args.host, args.port), handler_for(snapshot))
    except OSError as exc:
        p.exit(1, f'Cannot listen on {args.host}:{args.port}: {exc}. Try --port 8081.\n')
    print(f'Dashboard: http://{args.host}:{server.server_port}/', flush=True)
    print('Read-only snapshot. Restart to rebuild project records. Press Ctrl+C to stop.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
