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
                for section in ('Do','Deliver','Stop'):
                    self.assertIn('## '+section,text)
                self.assertGreaterEqual(len(re.findall(r"^\d+\. ",text,re.M)),4)
                self.assertLess(len(text.splitlines()),500)

    def test_skill_relative_links_resolve(self):
        for path in (ROOT/'skills').rglob('*.md'):
            if 'upstream' in path.parts: continue # Immutable third-party references retain external harness links.
            for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent/target).exists(),f'{path}: {target}')

    def test_bundled_contracts_match(self):
        canonical=(ROOT/'docs/record-contract.md').read_text()
        for p in (ROOT/'skills').glob('*/references/record-contract.md'):
            self.assertEqual(p.read_text(),canonical)

    def test_upstream_sources_are_pinned_at_point_of_use(self):
        import json
        sources=json.loads((ROOT/'docs/upstream-sources.json').read_text())
        for source in sources:
            for path in source['paths']:
                url=source['repository']+'/blob/'+source['revision']+'/'+path
                self.assertTrue(any(url in p.read_text() for p in (ROOT/'skills').glob('*/SKILL.md')), url)

    def test_only_one_portable_record_contract(self):
        self.assertEqual(len(list((ROOT/'skills').glob('*/references/record-contract.md'))),1)

    def test_bundled_upstream_integrity_and_install(self):
        import hashlib, json, tempfile
        from tools.install_skills import install
        manifest=json.loads((ROOT/'docs/upstream-files.json').read_text())
        self.assertEqual(len({row['path'].split('/')[1] for row in manifest}),9)
        with tempfile.TemporaryDirectory() as tmp:
            destination=Path(tmp)
            install(['all'],destination)
            for row in manifest:
                relative=Path(row['path'])
                for file in (ROOT/relative,destination/Path(*relative.parts[1:])):
                    self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),row['sha256'])
