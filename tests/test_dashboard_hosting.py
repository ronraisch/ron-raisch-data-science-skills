from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from dashboard.serve import handler_for, main
from dashboard.openshift.install import prepare_html


class HostingTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(lambda: b'<html>Snapshot</html>'))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()

    def request(self, path, method='GET'):
        c = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        c.request(method, path)
        response = c.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        c.close()
        return result

    def test_index_and_security_headers(self):
        status, headers, data = self.request('/')
        self.assertEqual(status, 200)
        self.assertEqual(data, b'<html>Snapshot</html>')
        self.assertIn("default-src 'none'", headers['Content-Security-Policy'])
        self.assertEqual(headers['Cache-Control'], 'no-store')

    def test_raw_files_and_traversal_not_served(self):
        for path in ('/project.json', '/data.csv', '/../README.md', '/%2e%2e/etc/passwd', '/snapshot/'):
            self.assertEqual(self.request(path)[0], 404)

    def test_head_and_health(self):
        self.assertEqual(self.request('/healthz')[2], b'ok\n')
        self.assertEqual(self.request('/', 'HEAD')[2], b'')

    def test_snapshot_reopened_after_update(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'index.html'; p.write_bytes(b'first')
            server = ThreadingHTTPServer(('127.0.0.1', 0), handler_for(p.read_bytes))
            t = threading.Thread(target=server.serve_forever, daemon=True);t.start()
            try:
                p.write_bytes(b'updated')
                c=HTTPConnection('127.0.0.1',server.server_port);c.request('GET','/')
                self.assertEqual(c.getresponse().read(),b'updated');c.close()
            finally:
                server.shutdown();server.server_close();t.join()


class InstallTests(unittest.TestCase):
    def test_oversized_snapshot_rejected_before_oc(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'index.html';p.write_bytes(b'x'*(900*1024+1))
            with self.assertRaises(ValueError):prepare_html([],p)

    def test_missing_project_explains_error(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'No project.json'):prepare_html([Path(d)],None)

    def test_snapshot_generated_for_example(self):
        root=Path(__file__).resolve().parents[1]/'examples/sensor-study'
        data=prepare_html([root],None)
        self.assertIn(b'Synthetic sensor classification',data)

    def test_local_launcher_requires_explicit_input(self):
        with self.assertRaises(SystemExit):main([])

    def test_installer_stages_minimal_build_context(self):
        from dashboard.openshift.install import main as install
        import json
        calls=[]
        def fake_oc(*args,input=None):
            calls.append(args)
            if args[:2]==('project','-q'):return 'test-namespace\n'
            if args[0]=='start-build':
                source=Path(next(a.split('=',1)[1] for a in args if a.startswith('--from-dir=')))
                self.assertEqual({str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}, {'dashboard/serve.py','dashboard/Containerfile'})
                self.assertNotIn('index.html',{p.name for p in source.rglob('*')})
            if args[0]=='get':return 'dashboard.example.test'
            return '{}'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'snapshot.html';p.write_text('<html>test</html>')
            with patch('dashboard.openshift.install.oc',side_effect=fake_oc), patch('dashboard.openshift.install.shutil.which',return_value='/bin/oc'):
                self.assertEqual(install(['--html',str(p)]),0)
        self.assertTrue(any(c[0]=='start-build' for c in calls))

    def test_prebuilt_image_skips_build(self):
        from dashboard.openshift.install import main as install
        calls=[]
        def fake_oc(*args,input=None):
            calls.append(args)
            return 'test' if args[0]=='project' else '{}'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'snapshot.html';p.write_text('test')
            with patch('dashboard.openshift.install.oc',side_effect=fake_oc), patch('dashboard.openshift.install.shutil.which',return_value='/bin/oc'):
                install(['--html',str(p),'--image','registry.example/dashboard@sha256:abc'])
        self.assertFalse(any(c[0]=='start-build' for c in calls))
