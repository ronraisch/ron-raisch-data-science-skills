from pathlib import Path
import tempfile
import unittest
from tools.experiment_verification.artifacts import verify_reference, validate_reference
from tools.experiment_verification.core import digest

class ExternalArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.file=self.root/'weights.json';self.file.write_text('{"threshold":0.5}')
        self.ref={'identity':'model','uri':self.file.as_uri(),'version':'1','sha256':digest(self.file),'provenance':'approved source run'}

    def test_provisioned_nfs_and_internal_hf(self):
        self.assertEqual(verify_reference(self.root,self.ref),self.file)
        self.ref.update(uri='nfs://organization/export/weights',local_path=str(self.file))
        self.assertEqual(verify_reference(self.root,self.ref),self.file)
        self.ref.update(uri='hf://internal-host/models/weights',revision='a'*40)
        self.assertEqual(verify_reference(self.root,self.ref),self.file)

    def test_missing_metadata_artifact_or_revision_fail(self):
        for key in ('identity','sha256','provenance'):
            invalid=dict(self.ref);invalid.pop(key)
            with self.assertRaises(ValueError):validate_reference(invalid)
        self.ref.update(uri='hf://internal/model',local_path=str(self.file))
        with self.assertRaises(ValueError):verify_reference(self.root,self.ref)
        self.ref['uri']='file:///nonexistent/missing'
        with self.assertRaises(OSError):verify_reference(self.root,self.ref)

    def test_corrupt_artifact_fails(self):
        self.file.write_text('changed')
        with self.assertRaises(ValueError):verify_reference(self.root,self.ref)
