import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from project_record.adapters import load_config
from project_record.build import build, render_readme
from project_record.core import RecordError, summarize

ROOT = Path(__file__).resolve().parents[1]


class ReadmeProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'host'
        shutil.copytree(ROOT / 'tests/fixtures/readme-only', self.root)
        self.config = self.root / 'projects.json'
        shutil.rmtree(self.root/'assets')
        readme=self.root/'README.md';text=readme.read_bytes();start=b'<!-- project-record:start -->';end=b'<!-- project-record:end -->'
        readme.write_bytes(text[:text.index(start)+len(start)]+b'\nIntentionally stale test region.\n'+text[text.index(end):])

    def command(self, *extra):
        return subprocess.run([sys.executable, '-m', 'project_record', 'readme-profile', '--config', str(self.config),
                               '--only', 'readme-only', '--readme', str(self.root/'README.md'),
                               '--image', str(self.root/'assets/progress.svg'), *extra], capture_output=True, text=True)

    def test_readme_contains_granular_semantics_source_and_no_site_requirement(self):
        record = summarize(load_config(self.config)[0])
        svg, markdown = render_readme(record, json.loads((self.root/'theme.json').read_text()))
        self.assertIn('DOC-1', markdown)
        self.assertIn('DOC-2', markdown)
        self.assertIn('DOC-3', markdown)
        self.assertIn('P2', markdown)
        self.assertIn('Blocked', markdown)
        self.assertIn('Deferred', markdown)
        self.assertIn('./evidence/check.txt', markdown)
        self.assertIn(record['source']['sha256'], markdown)
        self.assertIn('1/2 · 50.0%', markdown)
        self.assertIn('0/1 · 0.0%', markdown)
        self.assertNotIn('Interactive route', markdown)
        self.assertNotIn('progress.html', markdown)
        self.assertIn(record['source']['sha256'], svg)
        tree = ET.fromstring(svg)
        self.assertEqual(tree.attrib['role'], 'img')
        self.assertTrue(tree.find('{http://www.w3.org/2000/svg}desc').text)

    def test_public_build_needs_no_html_javascript_or_pages(self):
        output=self.root/'generated'
        result=build(load_config(self.config), self.config, output, 'public', ROOT)
        self.assertEqual(len(result), 1)
        self.assertTrue((output/'readme-only/README-module.md').is_file())
        self.assertFalse(list(output.rglob('*.html')))
        self.assertFalse(list(output.rglob('*.js')))
        self.assertFalse((self.root/'.github').exists())

    def test_cli_apply_rerun_and_stale_text_image_and_source_detection(self):
        original=(self.root/'README.md').read_bytes()
        version=(self.root/'pyproject.toml').read_bytes()
        stale=self.command('--check')
        self.assertEqual(stale.returncode, 1, stale.stderr)
        self.assertEqual((self.root/'README.md').read_bytes(), original)
        self.assertFalse((self.root/'assets').exists())
        applied=self.command('--write')
        self.assertEqual(applied.returncode, 0, applied.stderr)
        current=(self.root/'README.md').read_bytes()
        start=b'<!-- project-record:start -->';end=b'<!-- project-record:end -->'
        self.assertEqual(current.split(start)[0], original.split(start)[0])
        self.assertEqual(current.split(end)[1], original.split(end)[1])
        self.assertEqual((self.root/'pyproject.toml').read_bytes(), version)
        self.assertEqual(self.command('--check').returncode, 0)
        self.assertEqual(self.command('--write').returncode, 0)
        self.assertEqual((self.root/'README.md').read_bytes(), current)
        (self.root/'assets/progress.svg').write_text('stale')
        self.assertEqual(self.command('--check').returncode, 1)
        self.assertEqual(self.command('--write').returncode, 0)
        data=json.loads((self.root/'ledger.json').read_text());data['items'][1]['title']='Changed source title'
        (self.root/'ledger.json').write_text(json.dumps(data))
        self.assertEqual(self.command('--check').returncode, 1)
        self.assertEqual(self.command('--write').returncode, 0)
        self.assertIn('Changed source title', (self.root/'README.md').read_text())
        text=(self.root/'README.md').read_text().replace('Changed source title','stale text')
        (self.root/'README.md').write_text(text)
        self.assertEqual(self.command('--check').returncode, 1)

    def test_other_declared_sources_cannot_be_replaced_by_graphic(self):
        from project_record.readme_profile import sync_readme
        path=self.root/'assets/progress.svg';path.parent.mkdir();path.write_bytes((self.root/'ledger.json').read_bytes())
        before=path.read_bytes();config=json.loads(self.config.read_text())
        other=json.loads(json.dumps(config['projects'][0]));other['project']['id']='other';other['sourceFile']='assets/progress.svg'
        config['projects'].append(other);self.config.write_text(json.dumps(config))
        with self.assertRaises(RecordError):
            sync_readme(self.config,'readme-only',self.root/'README.md',path,write=True)
        self.assertEqual(path.read_bytes(),before)

    def test_literal_work_and_project_text_cannot_inject_markup(self):
        config=json.loads(self.config.read_text());config['projects'][0]['project']['name']='Small <img src=x> ](javascript:alert(1))'
        self.config.write_text(json.dumps(config))
        raw=json.loads((self.root/'ledger.json').read_text());raw['items'][0]['title']='Literal | <script>alert(1)</script>'
        raw['items'][0]['evidence'][0]['source']='javascript:alert(1)';(self.root/'ledger.json').write_text(json.dumps(raw))
        record=summarize(load_config(self.config)[0]);svg,text=render_readme(record,json.loads((self.root/'theme.json').read_text()))
        self.assertNotIn('<script>',text);self.assertNotIn('<img',text)
        import markdown
        rendered=markdown.markdown(text,extensions=['tables'])
        self.assertNotIn('href="javascript:',rendered);self.assertNotIn('<script>',rendered);self.assertNotIn('src=x',rendered.replace('&lt;img src=x&gt;', 'literal'))
        self.assertIn('Literal \\| &lt;script&gt;',text)

    def test_private_inputs_missing_markers_and_conflicting_modes_fail_without_writes(self):
        original=(self.root/'README.md').read_bytes();config=json.loads(self.config.read_text())
        config['projects'][0]['project']['visibility']='private';self.config.write_text(json.dumps(config))
        self.assertNotEqual(self.command('--write').returncode,0)
        self.assertEqual((self.root/'README.md').read_bytes(),original);self.assertFalse((self.root/'assets').exists())
        config['projects'][0]['project']['visibility']='public';self.config.write_text(json.dumps(config))
        (self.root/'README.md').write_text('No generated markers here')
        self.assertNotEqual(self.command('--write').returncode,0);self.assertFalse((self.root/'assets').exists())
        (self.root/'README.md').write_bytes(original)
        config['projects'][0]['presentation']['progressUrl']='https://example.org/site';self.config.write_text(json.dumps(config))
        self.assertNotEqual(self.command('--write').returncode,0);self.assertFalse((self.root/'assets').exists())

    def test_source_labels_are_literal_and_unsafe_evidence_is_not_a_link(self):
        config=json.loads(self.config.read_text());config['projects'][0]['source']['path']='ledger` <script>alert(1)</script>.json'
        self.config.write_text(json.dumps(config));record=summarize(load_config(self.config)[0])
        _,text=render_readme(record,json.loads((self.root/'theme.json').read_text()))
        import markdown
        rendered=markdown.markdown(text,extensions=['tables'])
        self.assertNotIn('<script>',rendered);self.assertIn('&lt;script&gt;',rendered)

    def test_interrupted_output_pair_is_detected_and_repaired(self):
        import project_record.readme_profile as profile
        atomic=profile._atomic
        def fail_readme(path,data):
            if path==self.root/'README.md':
                raise OSError('synthetic second replacement failure')
            return atomic(path,data)
        before=(self.root/'README.md').read_bytes()
        with patch.object(profile,'_atomic',side_effect=fail_readme):
            with self.assertRaises(OSError):
                profile.sync_readme(self.config,'readme-only',self.root/'README.md',self.root/'assets/progress.svg',write=True)
        self.assertEqual((self.root/'README.md').read_bytes(),before)
        self.assertEqual(self.command('--check').returncode,1)
        self.assertEqual(self.command('--write').returncode,0)
        self.assertEqual(self.command('--check').returncode,0)

    def test_empty_required_scope_is_not_measured_and_symlink_output_is_refused(self):
        raw=json.loads((self.root/'ledger.json').read_text())
        for item in raw['items']:
            item.update(required=False,deferReason='Retained optional fixture scope')
        raw['milestones'][0]['gateItemIds']=[];(self.root/'ledger.json').write_text(json.dumps(raw))
        record=summarize(load_config(self.config)[0]);_,text=render_readme(record,json.loads((self.root/'theme.json').read_text()))
        self.assertIn('0/0 · Not measured',text)
        (self.root/'assets').mkdir();(self.root/'assets/progress.svg').symlink_to(self.root/'pyproject.toml')
        version=(self.root/'pyproject.toml').read_bytes()
        self.assertNotEqual(self.command('--write').returncode,0)
        self.assertEqual((self.root/'pyproject.toml').read_bytes(),version)

    def test_cooperating_prs_suite_drift_is_rejected_without_rewriting_host_version(self):
        from tools.check_skills import check_suite
        toolkit=self.root/'toolkit';toolkit.mkdir();shutil.copytree(ROOT/'skills',toolkit/'skills');shutil.copyfile(ROOT/'pyproject.toml',toolkit/'pyproject.toml')
        check_suite(toolkit)
        file=toolkit/'skills/manifest.json';manifest=json.loads(file.read_text());manifest['suiteVersion']='9.9.9';file.write_text(json.dumps(manifest))
        with self.assertRaises(RecordError):
            check_suite(toolkit)
        self.assertIn('version = "2.8.0"',(self.root/'pyproject.toml').read_text())

    def test_checked_in_minimal_host_fixture_is_current(self):
        base=ROOT/'tests/fixtures/readme-only'
        run=subprocess.run([sys.executable,'-m','project_record','readme-profile','--config',str(base/'projects.json'),
                            '--only','readme-only','--readme',str(base/'README.md'),'--image',str(base/'assets/progress.svg'),'--check'],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr+run.stdout)
