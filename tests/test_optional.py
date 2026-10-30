from pathlib import Path
import tempfile
import unittest
from tools.install_skills import install
from tools.clearml.log_run import log_run
from tools.experiment_verification import save_json


class OptionalTests(unittest.TestCase):
    def test_selected_skill_install_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'skills';install(['research-resume'],out)
            self.assertTrue((out/'research-summary/references/record-contract.md').exists())
            self.assertTrue((out/'research-handoff/SKILL.md').exists())
            self.assertTrue((out/'experiment-verify/SKILL.md').exists())
            with self.assertRaises(FileExistsError):install(['research-resume'],out)

    def test_installer_preflights_all_names(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'skills'
            with self.assertRaises(ValueError):install(['research-resume','unknown'],out)
            self.assertFalse(out.exists())

    def test_clearml_adapter_without_server(self):
        class Logger:
            def report_scalar(self,**kw):self.scalar=kw
        class FakeTask:
            offline=False
            @classmethod
            def set_offline(cls,offline_mode):cls.offline=offline_mode
            @classmethod
            def init(cls,**kw):cls.instance=cls();return cls.instance
            def __init__(self):self.id='task-id';self.logger=Logger();self.connections=[];self.artifacts=[];self.closed=False
            def connect(self,params,**kw):self.connections.append((params,kw))
            def get_logger(self):return self.logger
            def upload_artifact(self,**kw):self.artifacts.append(kw)
            def close(self):self.closed=True
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);spec=root/'spec.json';run=root/'runtime.json'
            save_json(spec,{'id':'spec','dataset':{'sha256':'data'},'splits':{'sha256':'split'},'evaluation_protocol':'v1','expected':{'metric':{'name':'accuracy','split':'validation'}}})
            save_json(run,{'run_id':'r1','observations':{'optimizer':{'value':{'lr':.1}}},'result':.7,'artifacts':[]})
            result=log_run(root,spec,run,FakeTask,offline=True)
            self.assertEqual(result,'task-id');self.assertTrue(FakeTask.offline)
            self.assertTrue(FakeTask.instance.closed)
            self.assertTrue(all(kw['ignore_remote_overrides'] for _,kw in FakeTask.instance.connections))
            self.assertEqual(FakeTask.instance.logger.scalar['value'],.7)
