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
                self.assertIn(root + 'CHANGELOG.md', names)
                self.assertIn(root + 'INSTALL.md', names)
                self.assertIn(root + 'LICENSE', names)
                self.assertIn(root + 'src/project_record/record_layout.py', names)
                self.assertIn(root + 'src/project_record/pins.py', names)
                self.assertIn(root + 'src/project_record/execution.py', names)
                self.assertIn(root + 'src/project_record/policy.py', names)
                self.assertIn(root + 'src/project_record/policy_ci.py', names)
                self.assertIn(root + 'tools/run_policy_ci.py', names)
                self.assertIn(root + '.github/prs-policy.json', names)
                self.assertIn(root + 'tests/test_policy_ci.py', names)
                self.assertIn(root + 'src/project_record/reconcile.py', names)
                self.assertIn(root + 'tests/test_reconcile.py', names)
                self.assertIn(root + 'templates/work-result.example.json', names)
                self.assertIn(root + 'templates/reconciliation-profile.example.json', names)
                self.assertIn(root + 'tools/check_policy.py', names)
                self.assertIn(root + 'templates/policy-request.example.json', names)
                for name in ['projects.json','ledger.json','profile.json','issues.json']:
                    self.assertIn(root + 'tests/fixtures/execution/' + name, names)
                self.assertIn(root + 'templates/adoption-pin.example.json', names)
                self.assertIn(root + 'tests/test_pins.py', names)
                self.assertIn(root + 'tests/test_handoff.py', names)
                self.assertIn(root + 'tests/test_evidence_stages.py', names)
                self.assertIn(root + 'tests/fixtures/evidence_stages/cases.json', names)
                for name in ['projects.json', 'ledger.json', 'handoff.json', 'consumer_stub.py']:
                    self.assertIn(root + 'tests/fixtures/handoff/' + name, names)
                self.assertIn(root + 'templates/record-layout.example.json', names)
                self.assertIn(root + 'tests/test_record_layout.py', names)
                for host in ['readme-research', 'private-agent', 'shared-repository']:
                    self.assertIn(root + 'tests/fixtures/record_layout/' + host + '.json', names)
                for guide in ['ARCHITECTURE', 'POLICY', 'COMPATIBILITY', 'HANDOFF', 'RECORDS', 'FEEDBACK']:
                    self.assertIn(root + 'standards/' + guide + '.md', names)
                self.assertIn(root + 'standards/WORK-MODEL.md', names)
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
            readiness = project / '.agents/skills/use-project-records/references/readiness-contract.md'
            self.assertTrue(readiness.is_file())
            template = json.loads((project / '.agents/skills/use-project-records/references/readiness-assessment.json').read_text())
            self.assertEqual(template['readinessLevel'], 'L0')
            self.assertEqual(len(template['dimensions']), 10)
            self.assertTrue(all(d['status'] == 'unknown' for d in template['dimensions'].values()))
            self.assertFalse(template['autonomy']['promotionAuthorized'])
            self.assertTrue((toolkit / 'standards/READINESS.md').is_file())
            self.assertEqual(install_skills(toolkit, project, apply=True)['changes'], [])


if __name__=='__main__':
    unittest.main()
