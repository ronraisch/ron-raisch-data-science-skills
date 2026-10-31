from pathlib import Path
import tempfile
import unittest
from tools.install_skills import install


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

    def test_clearml_infrastructure_is_removed(self):
        root=Path(__file__).resolve().parents[1]
        self.assertFalse((root/'tools/clearml').exists())
        self.assertFalse((root/'docs/clearml.md').exists())
        self.assertNotIn('clearml', (root/'pyproject.toml').read_text().lower())
