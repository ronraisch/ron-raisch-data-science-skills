import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from examples.component_study.demo import build, policy, manifest
from tools.experiment_verification.core import load_json, save_json, digest, verify
from tools.experiment_verification.components import canonical
from tools.production.handoff import extract, parity, build as export
from tools.production.validator import generate


def load_module(path):
    s=importlib.util.spec_from_file_location('standalone_validator',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

class ProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=build(Path(cls.tmp.name)/'cv')
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.work=Path(self.temp.name)
        self.project=self.work/'project';shutil.copytree(self.root,self.project)

    def test_extraction_only_inference_and_transitive_shared_symbols(self):
        code,prov=extract(self.project,manifest(),{'path':'inference.py','symbol':'predict'},['inference'])
        self.assertEqual({x['symbol'] for x in prov},{'predict','extract','decode','clip'})
        self.assertNotIn('from features import',code);self.assertNotIn('from decoder import',code)
        self.assertNotIn('tools.',code)

    def test_notebook_isolated_strict_parity(self):
        result=parity(self.project,self.project/'production/production_handoff.ipynb',load_json(self.project/'records/handoff-config.json'))
        self.assertEqual(result['status'],'verified',result)

    def test_missing_mapping_refuses_extraction(self):
        m=manifest();m['components'][1]['sources']=[]
        with self.assertRaises(ValueError):extract(self.project,m,{'path':'inference.py','symbol':'predict'},['inference'])

    def test_unapproved_package_and_dynamic_code_rejected(self):
        path=self.project/'features.py';path.write_text('import mystery_package\ndef extract(pixels):\n    return mystery_package.predict(pixels)\n')
        with self.assertRaises(ValueError):extract(self.project,manifest(),{'path':'inference.py','symbol':'predict'},['inference'])
        path.write_text('def extract(pixels):\n    return eval("pixels")\n')
        with self.assertRaises(ValueError):extract(self.project,manifest(),{'path':'inference.py','symbol':'predict'},['inference'])

    def test_parity_fails_if_notebook_source_changes(self):
        nb=self.project/'production/production_handoff.ipynb';x=load_json(nb);x['cells'][0]['source']=['raise RuntimeError("broken")'];save_json(nb,x)
        r=parity(self.project,nb,load_json(self.project/'records/handoff-config.json'));self.assertEqual(r['status'],'failed')

    def test_parity_detects_wrong_extraction_even_with_updated_notebook_digest(self):
        nb=self.project/'production/production_handoff.ipynb';x=load_json(nb)
        x['cells'][0]['source']=[s.replace('value >= threshold - 0.05','value < threshold - 0.05') for s in x['cells'][0]['source']];save_json(nb,x)
        record=load_json(nb.parent/'handoff-manifest.json');record['notebook_sha256']=digest(nb);save_json(nb.parent/'handoff-manifest.json',record)
        r=parity(self.project,nb,load_json(self.project/'records/handoff-config.json'));self.assertEqual(r['status'],'failed',r)

    def test_missing_checkpoint_and_loosening_parity_fail(self):
        cfg=load_json(self.project/'records/handoff-config.json');cfg['tolerance']={'atol':0.1,'rtol':0}
        self.assertEqual(parity(self.project,self.project/'production/production_handoff.ipynb',cfg)['status'],'failed')
        cfg.pop('tolerance');cfg['fixtures']=[]
        self.assertEqual(parity(self.project,self.project/'production/production_handoff.ipynb',cfg)['status'],'failed')

    def test_component_violations_block_original_verifier(self):
        spec=load_json(self.project/'specs/decoder.json');run=load_json(self.project/'runs/decoder/runtime.json')
        (self.project/'features.py').write_text('def extract(pixels):return pixels\n')
        self.assertEqual(verify(spec,run,self.project,self.project/'specs/decoder.json')['status'],'failed')

    def test_runtime_contract_and_config_corruption_fail(self):
        spec=load_json(self.project/'specs/decoder.json');run=load_json(self.project/'runs/decoder/runtime.json')
        run['components']['observations'][1]['outputs']=[[2.0]]
        self.assertEqual(verify(spec,run,self.project,self.project/'specs/decoder.json')['status'],'failed')

    def test_legacy_report_has_explicit_scope_gap(self):
        from tools.experiment_verification.components import component_checks
        checks,report=component_checks({}, {}, self.project)
        self.assertEqual(checks,[]);self.assertEqual(report['status'],'unverifiable')

    def test_isolation_blocks_hidden_source_reads(self):
        nb=self.project/'production/production_handoff.ipynb';x=load_json(nb)
        x['cells'][0]['source'].append('\nfrom pathlib import Path\n_HIDDEN = Path('+repr(str(self.project/'features.py'))+').read_text()\n')
        save_json(nb,x);record=load_json(nb.parent/'handoff-manifest.json');record['notebook_sha256']=digest(nb);save_json(nb.parent/'handoff-manifest.json',record)
        result=parity(self.project,nb,load_json(self.project/'records/handoff-config.json'))
        self.assertEqual(result['status'],'failed');self.assertIn('research repository access',result['error'])

    def test_external_artifact_hash_corruption_blocks_parity(self):
        cfg=load_json(self.project/'records/handoff-config.json')
        # Use a forged reference with the original config binding updated by an attacker.
        cfg['artifacts']['checkpoint']['sha256']='0'*64
        nb=self.project/'production/production_handoff.ipynb';record=load_json(nb.parent/'handoff-manifest.json')
        record['artifacts']=cfg['artifacts'];record['config_sha256']=canonical(cfg);save_json(nb.parent/'handoff-manifest.json',record)
        self.assertEqual(parity(self.project,nb,cfg)['status'],'failed')


    def test_missing_malformed_or_unregistered_component_evidence_blocks_verification(self):
        spec=load_json(self.project/'specs/decoder.json');original=load_json(self.project/'runs/decoder/runtime.json')
        for bad in (None, [], {'observations':['invalid']}, {'observations':[{'id':'undeclared'}]}):
            run=copy.deepcopy(original);run['components']=bad
            self.assertNotEqual(verify(spec,run,self.project,self.project/'specs/decoder.json')['status'],'verified')

    def test_same_shapes_do_not_hide_failed_semantic_regression(self):
        spec=load_json(self.project/'specs/decoder.json');run=load_json(self.project/'runs/decoder/runtime.json')
        run['components']['observations'][1]['tests']['finite-shape']=False
        report=verify(spec,run,self.project,self.project/'specs/decoder.json')
        self.assertEqual(report['status'],'failed')
        self.assertTrue(any(c['name']=='components.behavior.features' and c['status']=='failed' for c in report['checks']))


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)

    def setup_case(self,task='detection',strategy='hybrid'):
        p=policy(task);p['strategy']=strategy
        p['approval']['policy_sha256']=canonical({k:v for k,v in p.items() if k!='approval'})
        generate(p,self.root/'validator.py');self.validator=load_module(self.root/'validator.py');self.p=p
        self.pred=self.root/'pred';self.test=self.root/'test'
        output=[{'box':[0,0,2,2],'label':'object','score':0.9}] if task=='detection' else [[0,1],[0,1]]
        truth=[{'box':[0,0,2,2],'label':'object'}] if task=='detection' else [[0,1],[0,1]]
        save_json(self.pred/'team-results/sample.json',{'id':'validation-1','prediction':output})
        save_json(self.test/'approved/sample.json',{'id':'validation-1','truth':truth,'reference':output})
        return output

    def change(self,**fields):
        p=self.pred/'team-results/sample.json';x=load_json(p);x.update(fields);save_json(p,x)

    def test_acceptable_detection_returns_none(self):
        self.setup_case();self.assertIsNone(self.validator.validate(str(self.pred),str(self.test)))

    def test_degraded_detection_fails(self):
        self.setup_case();self.change(prediction=[])
        with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_missing_results_fail(self):
        self.setup_case();(self.pred/'team-results/sample.json').unlink()
        with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_sample_mismatch_fails(self):
        self.setup_case();self.change(id='different')
        with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_invalid_structures_nonfinite_and_duplicate_boxes_fail(self):
        output=self.setup_case()
        for bad in ({},[{'box':[0,0,0,0],'label':'object','score':1}],output+output):
            self.change(prediction=bad)
            with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_allowed_numeric_difference(self):
        output=self.setup_case();output[0]['score']+=0.0005;self.change(prediction=output)
        self.assertIsNone(self.validator.validate(self.pred,self.test))

    def test_ground_truth_boundary_and_degradation(self):
        output=self.setup_case(strategy='ground_truth');self.assertIsNone(self.validator.validate(self.pred,self.test))
        output[0]['box']=[0,0,0.1,0.1];self.change(prediction=output)
        with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_reference_score_tolerance_rejects_larger_difference(self):
        output=self.setup_case();output[0]['score']+=0.002;self.change(prediction=output)
        with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_segmentation_accepts_correct_and_rejects_degraded(self):
        self.setup_case('segmentation');self.assertIsNone(self.validator.validate(self.pred,self.test))
        self.change(prediction=[[0,0],[0,0]])
        with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_segmentation_rejects_shape_and_label_errors(self):
        self.setup_case('segmentation')
        for bad in ([],[[1]],[[0,3],[0,1]],[[0],[0,1]]):
            self.change(prediction=bad)
            with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_empty_mapping_and_unapproved_policy_cannot_generate(self):
        p=policy('detection');p['files']={}
        with self.assertRaises(ValueError):generate(p,self.root/'validator.py')
        p=policy('detection');p['quality']['ap50']['minimum']=0.5
        with self.assertRaises(ValueError):generate(p,self.root/'validator.py')

    def test_missing_ground_truth_or_reference_fails(self):
        self.setup_case();save_json(self.test/'approved/sample.json',{'id':'validation-1'})
        with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_metamorphic_flip_pass_and_negative_control(self):
        p=policy('segmentation');p['strategy']='invariants'
        p['files']['flip']={'prediction':'flipped/mask.json','test':'checks/flip.json'}
        p['metamorphic']=[{'relation':'horizontal_flip','base':'validation-1','transformed':'flip','min_pixel_agreement':1.0}]
        p['approval']['policy_sha256']=canonical({k:v for k,v in p.items() if k!='approval'})
        generate(p,self.root/'validator.py');v=load_module(self.root/'validator.py')
        pred=self.root/'pred';test=self.root/'test'
        save_json(pred/'team-results/sample.json',{'id':'validation-1','prediction':[[0,1]]})
        save_json(pred/'flipped/mask.json',{'id':'flip','prediction':[[1,0]]})
        save_json(test/'approved/sample.json',{'id':'validation-1'})
        save_json(test/'checks/flip.json',{'id':'flip'})
        self.assertIsNone(v.validate(pred,test))
        save_json(pred/'flipped/mask.json',{'id':'flip','prediction':[[0,1]]})
        with self.assertRaises(AssertionError):v.validate(pred,test)

    def test_ap50_matching_boundary_is_inclusive(self):
        self.setup_case(strategy='ground_truth')
        # Box intersection 2, union 4: IoU exactly .5 must count as a match.
        self.change(prediction=[{'box':[0,0,1,2],'label':'object','score':0.5}])
        self.assertIsNone(self.validator.validate(self.pred,self.test))
        self.change(prediction=[{'box':[0,0,0.999,2],'label':'object','score':0.5}])
        with self.assertRaises(AssertionError):self.validator.validate(self.pred,self.test)

    def test_segmentation_approved_numeric_quality_boundary(self):
        p=policy('segmentation');p['quality']={'mean_iou':{'minimum':(0.75+2/3)/2}};p['reference']={'min_pixel_agreement':0.875}
        p['approval']['policy_sha256']=canonical({k:v for k,v in p.items() if k!='approval'})
        generate(p,self.root/'validator.py');v=load_module(self.root/'validator.py');pred=self.root/'pred';test=self.root/'test'
        reference=[[0,0,0,0],[0,1,1,1]]
        save_json(test/'approved/sample.json',{'id':'validation-1','truth':reference,'reference':reference})
        save_json(pred/'team-results/sample.json',{'id':'validation-1','prediction':[[0,0,0,0],[0,0,1,1]]})
        # IoU background 5/6, foreground 2/3; approved bound is looser, pixel agreement exactly .875.
        self.assertIsNone(v.validate(pred,test))

    def test_detection_metamorphic_flip(self):
        p=policy('detection');p['strategy']='invariants'
        p['files']['flip']={'prediction':'flipped/boxes.json','test':'checks/flip.json'}
        p['metamorphic']=[{'relation':'horizontal_flip','base':'validation-1','transformed':'flip','width':10,'min_box_iou':1.0,'score_atol':0.0}]
        p['approval']['policy_sha256']=canonical({k:v for k,v in p.items() if k!='approval'})
        generate(p,self.root/'validator.py');v=load_module(self.root/'validator.py');pred=self.root/'pred';test=self.root/'test'
        base=[{'box':[1,1,3,3],'label':'object','score':0.9}];flipped=[{'box':[7,1,9,3],'label':'object','score':0.9}]
        save_json(pred/'team-results/sample.json',{'id':'validation-1','prediction':base})
        save_json(pred/'flipped/boxes.json',{'id':'flip','prediction':flipped})
        save_json(test/'approved/sample.json',{'id':'validation-1'});save_json(test/'checks/flip.json',{'id':'flip'})
        self.assertIsNone(v.validate(pred,test))
        save_json(pred/'flipped/boxes.json',{'id':'flip','prediction':base})
        with self.assertRaises(AssertionError):v.validate(pred,test)
