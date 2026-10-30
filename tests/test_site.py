import json
from pathlib import Path
import tempfile
import unittest

from project_record.adapters import load_config
from project_record.build import build
from project_record.core import RecordError
from tools.build_site import build_site

ROOT = Path(__file__).resolve().parents[1]


class SiteTests(unittest.TestCase):
    def test_site_copies_only_public_manifest_files_and_keeps_brand_examples(self):
        with tempfile.TemporaryDirectory() as folder:
            records, site = Path(folder)/'records', Path(folder)/'site'
            build(load_config(ROOT/'examples/projects.json'), ROOT/'examples/projects.json', records, 'public', ROOT)
            (records/'unlisted-private.txt').write_text('must not publish')
            result = build_site(records, site)
            self.assertEqual(result['audience'], 'public')
            self.assertTrue((site/'guide/STANDARD.html').exists())
            self.assertTrue((site/'guide/READINESS.html').exists())
            self.assertTrue((site/'guide/WORK-MODEL.html').exists())
            for guide in ['ARCHITECTURE', 'POLICY', 'COMPATIBILITY', 'RECORDS', 'FEEDBACK']:
                self.assertTrue((site / 'guide' / (guide + '.html')).is_file())
            home = (site/'index.html').read_text()
            self.assertIn('Project records that keep up with the work', home)
            self.assertIn('Available now', home)
            self.assertIn('Planned next', home)
            self.assertIn('standard/progress.html', home)
            self.assertIn('github-release', home)
            self.assertIn('0.4.1', home)
            self.assertIn('WORK-MODEL.html', (site/'guide/START-HERE.html').read_text())
            self.assertIn('READINESS.html', (site/'guide/START-HERE.html').read_text())
            self.assertFalse((site/'unlisted-private.txt').exists())
            self.assertIn('Prehnite', (site/'prehnite/progress.html').read_text())
            self.assertIn('Standard website', (site/'index.html').read_text())

    def test_modified_input_and_private_manifest_fail_before_any_site_write(self):
        for private in [False, True]:
            with self.subTest(private=private), tempfile.TemporaryDirectory() as folder:
                records, site = Path(folder)/'records', Path(folder)/'site'
                build(load_config(ROOT/'examples/projects.json'), ROOT/'examples/projects.json', records, 'public', ROOT)
                if private:
                    path=records/'build-manifest.json'
                    manifest=json.loads(path.read_text())
                    manifest[0]['audience']='owner'
                    path.write_text(json.dumps(manifest))
                else:
                    (records/'standard/progress.html').write_text('modified after review')
                with self.assertRaises(RecordError):
                    build_site(records,site)
                self.assertFalse(site.exists())
