import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.research_pipeline import Component,Pipeline
from tools.experiment_verification.comparison import compare_runs
from tools.experiment_verification.visual import visual_evidence
from tools.experiment_verification.core import digest

class PipelineWorkflowTests(unittest.TestCase):
    def test_python_authoring_roundtrip(self):
        pipeline=Pipeline((Component('data','data','Load samples'),))
        with tempfile.TemporaryDirectory() as d:
            p=pipeline.export(Path(d)/'evidence.json')
            from tools.experiment_verification.core import load_json
            self.assertEqual(load_json(p),pipeline.manifest())

    def test_multi_run_pareto_and_pairs_not_fixed_reference(self):
        def run(name,score,cost,baseline):
            return {'id':name,'status':'completed','verification':'verified','runtime':{'result':score,'tradeoffs':{'latency_ms':cost}},'specification':{'dataset':{'sha256':'data'},'splits':{'sha256':'split'},'evaluation_protocol':'v1','expected':{'metric':{'name':'ap50','direction':'maximize','split':'validation'}},'components':{'baseline':baseline,'allowed_changes':['decoder']}}}
        runs=[run('fast',0.7,1,'a'),run('accurate',0.9,5,'b'),run('dominated',0.6,4,'c')]
        with patch('tools.experiment_verification.comparison.inspect_runs',return_value=runs):result=compare_runs('.',{})
        cohort=result['cohorts'][0];self.assertEqual(set(cohort['pareto']),{'fast','accurate'});self.assertEqual(len(cohort['pairs']),3)
        self.assertEqual(cohort['missing_objectives'],['parameters'])
        runs[2]['specification']['evaluation_protocol']='different'
        with patch('tools.experiment_verification.comparison.inspect_runs',return_value=runs):self.assertEqual(len(compare_runs('.',{})['cohorts']),2)

    def test_visual_missing_category_and_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'image.svg';p.write_text('<svg/>')
            item={'sample_id':'s','kind':'representative','path':'image.svg','sha256':digest(p),'caption':'Overlay','expected':'box','observed':'box'}
            self.assertEqual(visual_evidence(root,{'visual_evidence':[item]})['status'],'failed')
            edge=dict(item,kind='edge-case');run={'visual_evidence':[item,edge]}
            self.assertEqual(visual_evidence(root,run)['status'],'verified');p.write_text('changed')
            self.assertEqual(visual_evidence(root,run)['status'],'failed')
