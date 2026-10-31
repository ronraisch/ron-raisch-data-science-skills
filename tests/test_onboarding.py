from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tools.install_skills import append_agents_paragraph,agents_paragraph

ROOT=Path(__file__).resolve().parents[1]

class OnboardingTests(unittest.TestCase):
    def test_append_is_opt_in_preserving_and_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'AGENTS.md';p.write_text('Existing rules')
            self.assertTrue(append_agents_paragraph(p));text=p.read_text()
            self.assertTrue(text.startswith('Existing rules\n\n'));self.assertIn(agents_paragraph(),text)
            self.assertFalse(append_agents_paragraph(p));self.assertEqual(p.read_text(),text)

    def test_symlinks_and_incomplete_blocks_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'AGENTS.md';source=Path(d)/'source';source.write_text('Keep');p.symlink_to(source)
            with self.assertRaises(ValueError):append_agents_paragraph(p)
            self.assertEqual(source.read_text(),'Keep');p.unlink()
            p.write_text('<!-- ron-data-science-skills:research-start -->')
            with self.assertRaises(ValueError):append_agents_paragraph(p)

    def test_python_cli_requires_consent_and_installs_startup_when_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);agents=root/'AGENTS.md'
            base=[sys.executable,'-m','tools.install_skills','eda','--agents-md',str(agents)]
            result=subprocess.run([*base,'--destination',str(root/'first')],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertFalse(agents.exists());self.assertFalse((root/'first/research-start').exists())
            result=subprocess.run([*base,'--destination',str(root/'second'),'--with-agents'],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(agents.exists());self.assertTrue((root/'second/research-start/SKILL.md').exists())

    def test_python_cli_preflights_agents_file_before_copying(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);agents=root/'AGENTS.md';agents.write_text('<!-- ron-data-science-skills:research-start -->')
            target=root/'skills'
            result=subprocess.run([sys.executable,'-m','tools.install_skills','research-start','--destination',str(target),'--with-agents','--agents-md',str(agents)],cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertFalse(target.exists())
