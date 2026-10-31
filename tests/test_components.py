import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from examples.component_study.demo import manifest, approve_scope
from tools.experiment_verification.components import snapshot, verify_scope, assert_contract, canonical, observe_component, validate_manifest
from tools.experiment_verification.core import aggregate, save_json

SOURCE=Path(__file__).resolve().parents[1]/'examples/component_study/source'

class ComponentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        for p in SOURCE.glob('*.py'):shutil.copy2(p,self.root/p.name)
        self.m=manifest();self.base=snapshot(self.root,self.m);self.scope=approve_scope(['model.decoder'])

    def status(self):return aggregate(verify_scope(self.root,self.m,self.base,self.scope)[0])

    def edit(self,name):
        p=self.root/name;p.write_text(p.read_text()+'\n# implementation change\n')

    def test_authorized_decoder(self):
        self.edit('decoder.py');self.assertEqual(self.status(),'verified')

    def test_protected_extractor(self):
        self.edit('features.py');checks,_,owners=verify_scope(self.root,self.m,self.base,self.scope)
        self.assertEqual(aggregate(checks),'failed');self.assertIn('model.feature_extraction',owners['features.py'])

    def test_shared_utility_protects_all_owners(self):
        self.edit('common.py');checks,_,owners=verify_scope(self.root,self.m,self.base,self.scope)
        self.assertEqual(aggregate(checks),'failed');self.assertEqual(len(owners['common.py']),2)

    def test_contract_violation(self):
        c=self.m['components'][1]
        with self.assertRaises(AssertionError):observe_component(c,[[255]],[[2.0]],{}, {'finite-shape':True})
        with self.assertRaises(AssertionError):assert_contract([[1]],{'type':'array','shape':[2,2]})

    def test_compatible_version_evolution(self):
        c=self.m['components'][2]
        c['outputs']=copy.deepcopy(c['outputs']);c['outputs']['additionalProperties']=True
        self.base=snapshot(self.root,self.m)
        c['version']='1.1.0';c['outputs']['properties']['optional_score']={'type':'number'}
        self.assertEqual(self.status(),'verified')

    def test_changed_definition_requires_version_increase(self):
        self.m['components'][2]['config']={'depth':4};self.m['components'][2]['config_schema']={'type':'object'}
        self.assertEqual(self.status(),'failed')

    def test_semantic_change_needs_new_identity(self):
        self.m['components'][2].update(purpose='Segmentation only',version='2.0.0')
        self.assertEqual(self.status(),'failed')
        self.m['components'][2]['id']='segmenter'
        self.m['components'][3]['dependencies']=['segmenter']
        self.m['components'][3]['version']='1.0.1'
        self.scope=approve_scope(['model.decoder','inference'])
        self.assertEqual(self.status(),'verified')

    def test_same_purpose_cannot_arbitrarily_replace_identity(self):
        self.m['components'][2]['id']='new-decoder';self.m['components'][3]['dependencies']=['new-decoder']
        self.scope=approve_scope(['model.decoder','inference']);self.assertEqual(self.status(),'failed')

    def test_nested_mapping(self):
        child=copy.deepcopy(self.m['components'][2]);child.update(id='regression',path='model.decoder.regression',sources=[{'path':'regression.py'}],dependencies=[])
        (self.root/'regression.py').write_text('x=1\n');self.m['components'].append(child);self.base=snapshot(self.root,self.m)
        self.edit('regression.py');self.assertEqual(self.status(),'verified')
        self.scope=approve_scope(['model.decoder.regression']);self.edit('decoder.py');self.assertEqual(self.status(),'failed')

    def test_component_spans_multiple_files(self):
        for path in ('decoder.py','decoder_extra.py'):
            if not (self.root/path).exists():(self.root/path).write_text('x=1\n')
        self.m['components'][2]['sources'].append({'path':'decoder_extra.py'})
        self.base=snapshot(self.root,self.m);self.edit('decoder_extra.py');self.assertEqual(self.status(),'verified')

    def test_config_and_dependency_files_protected(self):
        p=self.root/'runtime.lock';p.write_text('numpy==1\n')
        for c in self.m['components']:c['sources'].append({'path':'runtime.lock'})
        self.base=snapshot(self.root,self.m);p.write_text('numpy==2\n');self.assertEqual(self.status(),'failed')

    def test_untracked_or_deleted_source_detected(self):
        (self.root/'new.py').write_text('x=1');self.assertEqual(self.status(),'failed')
        (self.root/'new.py').unlink();(self.root/'features.py').unlink()
        self.assertEqual(self.status(),'failed')

    def test_scope_approval_bound_to_exact_scope(self):
        self.scope['allowed_changes'].append('model.feature_extraction');self.assertEqual(self.status(),'failed')

    def test_breaking_contract_approval_and_downstream_runtime_required(self):
        c=self.m['components'][2];c['version']='2.0.0';c['outputs']={'type':'array'}
        self.assertEqual(self.status(),'failed')
        self.scope['breaking_approvals']={'decoder':{'by':'lead','reference':'decision-3','new_definition_sha256':canonical(c)}}
        self.assertEqual(self.status(),'verified') # only scope stage; runtime checks remain mandatory.

    def test_cannot_hide_changes_by_scanning_policy(self):
        self.edit('features.py');self.m['watch']=['decoder.py'];self.assertEqual(self.status(),'failed')

    def test_invalid_manifest_and_schema(self):
        self.m['components'][1]['dependencies']=['inference']
        with self.assertRaises(ValueError):validate_manifest(self.m)
        with self.assertRaises(ValueError):assert_contract(1,{'typ':'number'})

    def test_runtime_settings_of_protected_component_fail(self):
        self.m['components'][1]['config_schema']={'type':'object'}
        self.m['components'][1]['config']={'normalization':250};self.m['components'][1]['version']='1.0.1'
        self.assertEqual(self.status(),'failed')

    def test_dependency_definition_of_protected_component_fails(self):
        self.m['components'][3]['dependencies']=[];self.m['components'][3]['version']='1.0.1'
        self.assertEqual(self.status(),'failed')

    def test_default_scan_excludes_manifest_and_project_records(self):
        self.m.pop('watch');self.m.pop('record_roots')
        save_json(self.root/'components.json',self.m)
        save_json(self.root/'project.json',{'runs':[]})
        self.base=snapshot(self.root,self.m)
        save_json(self.root/'records/baseline.json',self.base)
        self.m['components'][2]['version']='1.0.1'
        save_json(self.root/'components.json',self.m)
        save_json(self.root/'project.json',{'runs':['new-run']})
        self.assertEqual(self.status(),'verified')
        (self.root/'settings.json').write_text('{"normalization":250}')
        self.assertEqual(self.status(),'failed') # arbitrary config remains watched.
        (self.root/'settings.json').unlink()
        save_json(self.root/'nested/project.json',{'decoder_config':'unexpected'})
        self.assertEqual(self.status(),'failed') # only conventional ROOT metadata is excluded.

    def test_input_contract_narrowing_requires_breaking_approval(self):
        c=self.m['components'][2];c['version']='1.1.0'
        c['inputs']={'type':'object','properties':{},'additionalProperties':True}
        self.base=snapshot(self.root,self.m)
        c['version']='1.2.0';c['inputs']['properties']['optional']={'type':'number'}
        self.assertEqual(self.status(),'failed')
