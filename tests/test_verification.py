import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from examples.demo import build, design, run
from tools.experiment_verification import digest, load_json, save_json, verify
from tools.experiment_verification.core import validate_spec, resolve, aggregate
from tools.experiment_verification.records import validate_project, best_runs, resume_report
from tools.experiment_verification.runtime import assert_frozen, snapshot_model, snapshot_optimizer, checkpoint_evidence
from dashboard.build import render


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=tempfile.TemporaryDirectory()
        with contextlib.redirect_stdout(io.StringIO()):
            cls.study=build(Path(cls.base.name)/"study")

    @classmethod
    def tearDownClass(cls):
        cls.base.cleanup()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/"study"
        shutil.copytree(self.study,self.root)
        self.spec_path=self.root/"specs/logistic.json"
        self.spec=load_json(self.spec_path)
        self.runtime=load_json(self.root/"runs/logistic/runtime.json")

    def report(self):
        return verify(self.spec,self.runtime,self.root,self.spec_path)

    def assertCheck(self,name,status):
        check=next(c for c in self.report()["checks"] if c["name"]==name)
        self.assertEqual(check["status"],status,check)

    def test_good_run_is_verified(self):
        self.assertEqual(self.report()["status"],"verified")

    def test_wrong_optimizer_detected(self):
        r=load_json(self.root/"runs/wrong-optimizer/runtime.json")
        out=verify(self.spec,r,self.root,self.spec_path)
        self.assertEqual(out["status"],"failed")
        self.assertTrue(any(c["name"]=="runtime.optimizer" and c["status"]=="failed" for c in out["checks"]))

    def test_falsified_metric_detected(self):
        r=load_json(self.root/"runs/wrong-metric/runtime.json")
        self.assertEqual(verify(self.spec,r,self.root,self.spec_path)["status"],"failed")

    def test_dataset_changed(self):
        with (self.root/"data.csv").open("a") as f:f.write("extra,newgroup,0.1,1\n")
        self.assertCheck("dataset.identity","failed")

    def test_sample_leakage_even_with_updated_hash(self):
        p=self.root/"splits.json";split=load_json(p)
        split["validation"].append(split["train"][0]);save_json(p,split)
        self.spec["splits"]["sha256"]=digest(p)
        self.assertCheck("splits.isolation","failed")

    def test_group_leakage(self):
        p=self.root/"data.csv";s=p.read_text().replace('s050-0,g050','s050-0,g000');p.write_text(s)
        self.spec["dataset"]["sha256"]=digest(p)
        self.assertCheck("splits.isolation","failed")

    def test_unknown_split_id(self):
        p=self.root/"splits.json";v=load_json(p);v['test'][0]='missing';save_json(p,v)
        self.assertCheck("splits.isolation","failed")

    def test_empty_split(self):
        p=self.root/"splits.json";v=load_json(p);v['test']=[];save_json(p,v)
        self.assertCheck("splits.isolation","failed")

    def test_wrong_checkpoint_bytes(self):
        (self.root/"runs/logistic/checkpoint.json").write_text('{}')
        self.assertCheck("artifact.0","failed")

    def test_missing_required_checkpoint(self):
        self.runtime["artifacts"]=self.runtime["artifacts"][1:]
        self.assertCheck("artifact.required.checkpoint.json","unverifiable")

    def test_missing_observation(self):
        del self.runtime["observations"]["preprocessing"]
        self.assertCheck("runtime.preprocessing","unverifiable")
        self.assertEqual(self.report()["status"],"partially_verified")

    def test_manual_observation_is_partial(self):
        self.runtime["observations"]["model"]["kind"]="manual"
        self.assertCheck("runtime.model","partially_verified")

    def test_unobserved_null_is_not_verified(self):
        del self.runtime["observations"]["checkpoint"]
        self.assertCheck("runtime.checkpoint","unverifiable")

    def test_missing_git_provenance(self):
        self.runtime["observations"]["environment"]["value"]["git_revision"]=None
        self.assertCheck("environment.git_provenance","unverifiable")

    def test_frozen_parameter_mismatch(self):
        self.runtime["observations"]["parameters"]["value"]["trainable_names"]=[]
        self.assertCheck("runtime.parameters","failed")

    def test_architecture_mismatch(self):
        self.runtime["observations"]["model"]["value"]["input_dimension"]=3
        self.assertCheck("runtime.model","failed")

    def test_completed_steps_mismatch(self):
        self.runtime["observations"]["training"]["value"]["completed_steps"]=119
        self.assertCheck("runtime.training","failed")

    def test_predictions_missing(self):
        p=self.root/"runs/logistic/predictions.csv"
        p.write_text('\n'.join(p.read_text().splitlines()[:-1])+'\n')
        self.runtime["predictions"]["sha256"]=digest(p)
        self.assertCheck("metric.recomputed","failed")

    def test_predictions_target_tampering(self):
        import csv
        p=self.root/"runs/logistic/predictions.csv"
        with p.open() as f:rows=list(csv.DictReader(f))
        rows[0]['target']=str(1-int(rows[0]['target']))
        from examples.demo import write_csv
        write_csv(p,rows,['id','target','prediction']);self.runtime['predictions']['sha256']=digest(p)
        self.assertCheck('metric.recomputed','failed')

    def test_unsupported_metric_unverifiable(self):
        self.spec["expected"]["metric"]["name"]="rotated_ap50"
        self.assertCheck("metric.recomputed","unverifiable")

    def test_spec_snapshot_mismatch(self):
        self.runtime["spec_sha256"]="0"*64
        self.assertCheck("spec.identity","failed")

    def test_invalid_spec_rejected(self):
        del self.spec["expected"]["model"]
        with self.assertRaises(ValueError):validate_spec(self.spec)

    def test_null_expected_model_rejected(self):
        self.spec["expected"]["model"]=None
        with self.assertRaises(ValueError):validate_spec(self.spec)

    def test_strict_json(self):
        p=self.root/"bad.json"
        for value in ('{"a": 1,"a": 2}', '{"a":NaN}'):
            p.write_text(value)
            with self.assertRaises(ValueError):load_json(p)

    def test_path_traversal(self):
        with self.assertRaises(ValueError):resolve(self.root,'../outside')
        with self.assertRaises(ValueError):resolve(self.root,'/etc/passwd')

    def test_symlink_escape(self):
        (self.root/"escape").symlink_to(Path(self.temp.name))
        with self.assertRaises(ValueError):resolve(self.root,'escape/outside')

    def test_record_integrity(self):
        _,errors=validate_project(self.root)
        self.assertEqual(errors,[])

    def test_unknown_finding_run(self):
        p=self.root/'project.json';v=load_json(p);v['findings'][0]['run_ids']=['missing'];save_json(p,v)
        self.assertTrue(validate_project(self.root)[1])

    def test_best_excludes_failed_verification(self):
        cohorts=best_runs(self.root)
        self.assertEqual(len(cohorts),1)
        self.assertEqual({r['id'] for r in cohorts[0]['runs']},{'majority','logistic'})

    def test_incomparable_protocol_separates_cohorts(self):
        from tools.experiment_verification.records import cohort_key
        b=copy.deepcopy(self.spec);b['evaluation_protocol']='other'
        self.assertNotEqual(cohort_key(b),cohort_key(self.spec))

    def test_stale_report_not_trusted(self):
        (self.root/'runs/logistic/checkpoint.json').write_text('{}')
        cohorts=best_runs(self.root)
        self.assertEqual(cohorts[0]['best'][0]['id'],'majority')
        self.assertIn('artifact.0: failed',resume_report(self.root))

    def test_resume_finds_unregistered_runs(self):
        (self.root/'runs/forgotten').mkdir()
        self.assertIn('runs/forgotten',resume_report(self.root))
        self.assertIn('Pause reason:',resume_report(self.root))

    def test_dashboard_escapes_html(self):
        p=self.root/'project.json';v=load_json(p);v['title']='<script>alert(1)</script>';save_json(p,v)
        page=render([self.root]);self.assertNotIn('<script>',page);self.assertIn('&lt;script&gt;',page)

    def test_no_overwrite(self):
        with self.assertRaises(FileExistsError):build(self.root)

    def test_cli_exit_and_saved_failed_report(self):
        out=self.root/'report.json'
        cp=subprocess.run([sys.executable,'-m','tools.experiment_verification','verify',str(self.spec_path),str(self.root/'runs/wrong-optimizer/runtime.json'),'--root',str(self.root),'--output',str(out)],capture_output=True,text=True)
        self.assertEqual(cp.returncode,1,cp.stderr);self.assertEqual(load_json(out)['status'],'failed')

    def test_live_frozen_execution_fails(self):
        entry=run(self.root,self.spec_path,'actual-frozen',fault='frozen')
        runtime=load_json(self.root/entry['directory']/'runtime.json')
        report=verify(self.spec,runtime,self.root,self.spec_path)
        self.assertEqual(report['status'],'failed')
        self.assertTrue(any(c['name']=='runtime.parameters' and c['status']=='failed' for c in report['checks']))

    def test_preprocessing_fit_ids_mismatch(self):
        self.runtime['observations']['preprocessing']['value']['fit_ids'].append('s050-0')
        self.assertCheck('runtime.preprocessing','failed')

    def test_mae_adapter_recomputes(self):
        self.spec['expected']['metric']['name']='mae'
        self.runtime['result']=1-self.runtime['result']
        self.assertCheck('metric.recomputed','verified')

    def test_end_to_end_without_network(self):
        from unittest.mock import patch
        with patch('socket.socket.connect',side_effect=AssertionError('Network forbidden')):
            with contextlib.redirect_stdout(io.StringIO()):
                root=build(Path(self.temp.name)/'offline-study')
            self.assertTrue((root/'resume.md').is_file())
            self.assertEqual(len(best_runs(root)),1)

    def test_all_statuses_conservative(self):
        self.assertEqual(aggregate([{'status':'unverifiable'}]),'unverifiable')
        self.assertEqual(aggregate([{'status':'verified'},{'status':'unverifiable'}]),'partially_verified')
        self.assertEqual(aggregate([{'status':'verified'},{'status':'failed'}]),'failed')


class HookTests(unittest.TestCase):
    def setUp(self):
        class Parameter:
            def __init__(self,trainable):self.requires_grad=trainable;self.shape=(2,3)
            def numel(self):return 6
        class Model:
            def __init__(self):self.a=Parameter(False);self.b=Parameter(True)
            def named_parameters(self):return [('backbone',self.a),('head',self.b)]
        self.model=Model()

    def test_freeze_assertion(self):
        self.assertEqual(assert_frozen(self.model,['head']),['head'])
        with self.assertRaises(AssertionError):assert_frozen(self.model,[])

    def test_live_model_counts(self):
        v=snapshot_model(self.model);self.assertEqual(v['total'],12);self.assertEqual(v['trainable'],6)

    def test_live_optimizer_groups(self):
        class Optimizer:pass
        o=Optimizer();o.param_groups=[{'params':[self.model.b],'lr':.03}]
        v=snapshot_optimizer(o,self.model);self.assertEqual(v['groups'][0]['parameters'],['head']);self.assertEqual(v['groups'][0]['lr'],.03)

    def test_checkpoint_loading_evidence(self):
        class Result:missing_keys=['head'];unexpected_keys=[]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'weights';p.write_bytes(b'checkpoint')
            v=checkpoint_evidence(p,Result(),False)
            self.assertEqual(v['sha256'],digest(p));self.assertEqual(v['missing_keys'],['head'])


if __name__=='__main__':unittest.main()
