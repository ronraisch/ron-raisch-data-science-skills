import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from examples.component_study.demo import build, manifest, approve_scope
from tools.experiment_verification.core import load_json, save_json, preflight, aggregate
from tools.experiment_verification.components import snapshot, verify_scope
from tools.experiment_verification.records import validate_project, resume_report
from dashboard.build import render, reference_link

class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=build(Path(cls.tmp.name)/'cv')
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_component_records_and_resume(self):
        _,errors=validate_project(self.root);self.assertEqual(errors,[])
        report=resume_report(self.root);self.assertIn('Components and artifact provenance',report);self.assertIn('verified',report)

    def test_dashboard_keeps_old_panels_and_adds_components(self):
        html=render([self.root])
        for text in ['Component hierarchy','model.feature_extraction','1.0.1','Authorized scopes','External artifacts','Research timeline','Best verified by evaluation cohort','Pause reason']:
            self.assertIn(text,html)
        self.assertNotIn('<a href="javascript:',reference_link('javascript:alert(1)'))
        self.assertIn('&lt;',reference_link('<script>'))

    def test_preflight_enforces_scope(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'copy';shutil.copytree(self.root,root)
            (root/'features.py').write_text('def extract(x):return x\n')
            self.assertEqual(aggregate(preflight(load_json(root/'specs/decoder.json'),root)),'failed')

    def test_real_import_analysis_finds_missing_shared_mapping(self):
        import shutil
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for p in (Path(__file__).resolve().parents[1]/'examples/component_study/source').glob('*.py'):shutil.copy2(p,root/p.name)
            m=manifest();m['components'][1]['sources']=[{'path':'features.py','symbol':'extract'}]
            baseline=snapshot(root,m);(root/'common.py').write_text('def clip(x):return x\n')
            checks,_,owners=verify_scope(root,m,baseline,approve_scope(['model.decoder']))
            self.assertIn('model.feature_extraction',owners['common.py']);self.assertEqual(aggregate(checks),'failed')

    def test_validator_refuses_optimized_python(self):
        folder=self.root/'production/detection'
        code='import importlib.util; s=importlib.util.spec_from_file_location("v",'+repr(str(folder/'validator.py'))+');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.validate("missing","missing")'
        r=subprocess.run([sys.executable,'-O','-I','-c',code],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('without Python -O',r.stderr)

    def test_legacy_records_remain_usable(self):
        root=Path(__file__).resolve().parents[1]/'examples/sensor-study'
        self.assertEqual(validate_project(root)[1],[])
        self.assertIn('Legacy record',render([root]))
