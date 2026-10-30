from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]


class SkillTests(unittest.TestCase):
    def test_sixteen_valid_skills(self):
        paths=list((ROOT/'skills').glob('*/SKILL.md'))
        self.assertEqual(len(paths),16)
        for path in paths:
            with self.subTest(skill=path.parent.name):
                text=path.read_text();front=text.split('---',2)[1]
                self.assertIn('name: '+path.parent.name,front)
                self.assertRegex(path.parent.name,r'^[a-z0-9]+(-[a-z0-9]+)*$')
                self.assertIn('description: ',front)
                for section in ('Inputs','Procedure','Outputs and evidence','Completion criteria','Resources'):
                    self.assertIn('## '+section,text)
                self.assertGreaterEqual(len(re.findall(r"^\d+\. ",text,re.M)),6)
                self.assertLess(len(text.splitlines()),500)

    def test_skill_relative_links_resolve(self):
        for path in (ROOT/'skills').rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/target).exists(),f'{path}: {target}')

    def test_bundled_contracts_match(self):
        canonical=(ROOT/'docs/record-contract.md').read_text()
        for p in (ROOT/'skills').glob('*/references/record-contract.md'):
            self.assertEqual(p.read_text(),canonical)
