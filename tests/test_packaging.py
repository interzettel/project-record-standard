from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from project_record.agents import install_skills
from tools.package_standard import package


class DistributionTests(unittest.TestCase):
    def test_archive_is_deterministic_checksums_match_and_owner_sources_are_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            first,second=Path(folder)/'a.zip',Path(folder)/'b.zip'
            package(first)
            package(second)
            self.assertEqual(first.read_bytes(),second.read_bytes())
            with ZipFile(first) as archive:
                names=archive.namelist()
                self.assertFalse(any('/portfolio/' in n or '/dist/' in n or '/audit/' in n or '__pycache__' in n for n in names))
                root='project-record-standard/'
                config=json.loads(archive.read(root+'examples/projects.json'))
                self.assertTrue(all(e['project']['visibility']=='public' for e in config['projects']))
                checksums=archive.read(root+'checksums.sha256').decode().splitlines()
                for line in checksums:
                    digest,name=line.split('  ',1)
                    self.assertEqual(sha256(archive.read(root+name)).hexdigest(),digest)

    def test_distributed_toolkit_installs_the_same_skills_and_preserves_brand_rules(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            destination = root / 'standard.zip'
            package(destination)
            with ZipFile(destination) as archive:
                archive.extractall(root / 'unpacked')
            toolkit = root / 'unpacked/project-record-standard'
            project = root / 'project'
            project.mkdir()
            (project / 'AGENTS.md').write_text('# Loomglass\n\nPreserve burgundy serif branding.\n')
            result = install_skills(toolkit, project, apply=True)
            self.assertTrue(result['written'])
            self.assertIn('Preserve burgundy serif branding.', (project / 'AGENTS.md').read_text())
            manifest = json.loads((toolkit / 'skills/manifest.json').read_text())
            for name in manifest['skills']:
                self.assertEqual((toolkit / 'skills' / name / 'SKILL.md').read_bytes(), (project / '.agents/skills' / name / 'SKILL.md').read_bytes())
            self.assertEqual(install_skills(toolkit, project, apply=True)['changes'], [])


if __name__=='__main__':
    unittest.main()
