from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from project_record.core import RecordError

ROOT = Path(__file__).resolve().parents[1]
OBSERVED = '2026-11-05T14:00:00Z'


class InspectorInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'host'
        shutil.copytree(ROOT/'tests/fixtures/inspector',self.root)
        self.selection=json.loads((self.root/'selection.json').read_text())

    def inspect(self, selection=None):
        from project_record.inspector import inspect_inventory
        return inspect_inventory(self.root,self.selection if selection is None else selection,observed_at=OBSERVED)

    def test_cli_surfaces_all_declared_cases_without_scanning_neighbors(self):
        run=subprocess.run([sys.executable,'-m','project_record','inspect-inputs','--root',str(self.root),
                            '--selection',str(self.root/'selection.json'),'--observed-at',OBSERVED],capture_output=True,text=True)
        self.assertEqual(run.returncode,3,run.stderr)
        result=json.loads(run.stdout);rows={r['id']:r for r in result['records']}
        self.assertEqual(rows['REC-1']['status'],'validated')
        self.assertEqual(rows['HIST-1']['status'],'recognized-shape')
        self.assertEqual(rows['INSTALL-1']['status'],'recognized-shape')
        self.assertEqual(rows['MISSING-1']['status'],'missing')
        self.assertEqual(rows['BROKEN-1']['status'],'malformed-json')
        self.assertEqual(rows['FUTURE-1']['status'],'unsupported-kind')
        self.assertFalse(rows['FUTURE-1']['contentRead'])
        self.assertEqual(result['coverage']['declared'],8)
        self.assertEqual(result['coverage']['unselected'],'not-inspected')
        self.assertFalse(result['publishable'])
        self.assertNotIn('personalMemory',run.stdout)
        self.assertNotIn('private-looking text',run.stdout)

    def test_unknown_versions_and_invalid_records_do_not_abort_other_entries(self):
        for version in ['99.0.0', [], {}, True]:
            (self.root/'future-version.json').write_text(json.dumps({'contractVersion':version}))
            row=dict(self.selection['records'][0],id='VERSION',path='future-version.json')
            result=self.inspect({'selectionVersion':1,'records':[row,self.selection['records'][0]]})
            self.assertEqual(result['records'][0]['status'],'unsupported-version')
            self.assertEqual(result['records'][1]['status'],'validated')
        (self.root/'invalid.json').write_text('{"contractVersion":"0.2.0"}')
        row=dict(self.selection['records'][0],path='invalid.json')
        self.assertEqual(self.inspect({'selectionVersion':1,'records':[row]})['records'][0]['status'],'invalid-record')

    def test_only_declared_regular_files_are_read_without_transitive_manifest_reads(self):
        (self.root/'manifest.json').write_text('{"projects":[{"sourceFile":"undeclared-private.json"}]}')
        row=dict(self.selection['records'][0],kind='project-manifest',path='manifest.json')
        original=Path.open;seen=[]
        def guarded(path,*args,**kwargs):
            self.assertEqual(path,self.root/'manifest.json');seen.append(path)
            return original(path,*args,**kwargs)
        with patch.object(Path,'open',guarded),patch.object(Path,'glob',side_effect=AssertionError('No glob scan')),patch.object(Path,'rglob',side_effect=AssertionError('No recursive scan')),patch.object(Path,'iterdir',side_effect=AssertionError('No directory inventory')):
            result=self.inspect({'selectionVersion':1,'records':[row]})
        self.assertEqual(result['records'][0]['status'],'recognized-shape')
        self.assertEqual(len(seen),1)

    def test_source_and_render_times_do_not_refresh_on_inspection(self):
        result=self.inspect()
        self.assertEqual(result['inspectedAt'],OBSERVED)
        row=result['records'][0]
        self.assertEqual(row['sourceObservedOn'],'2026-10-30')
        self.assertIsNone(row['sourceUpdatedOn'])
        self.assertEqual(row['renderedAt'],'2026-11-05T12:00:00Z')
        self.assertTrue(row['synthetic'])
        self.assertEqual(row['producerRevision'],'ebc6afb0b977ff3d7605893c73ac63021775c4d3')

    def test_invalid_selection_fails_before_any_data_read(self):
        for changes in [dict(path='../secret.json'),dict(path='/tmp/secret.json'),dict(path='*.json'),dict(path='./record.json'),dict(path='folder\\record.json'),dict(visibility='unknown')]:
            row=dict(self.selection['records'][0],**changes)
            with self.subTest(changes=changes),patch.object(Path,'open',side_effect=AssertionError('No read before validation')):
                with self.assertRaises((RecordError,ValueError,TypeError)):
                    self.inspect({'selectionVersion':1,'records':[row]})
        with self.assertRaises(RecordError):
            self.inspect({'selectionVersion':True,'records':[]})
        with self.assertRaises(RecordError):
            self.inspect({'selectionVersion':1,'records':[self.selection['records'][0]]*2})

    def test_digest_mismatch_and_oversize_are_partial_not_validated(self):
        row=dict(self.selection['records'][0],expectedSha256='0'*64)
        result=self.inspect({'selectionVersion':1,'records':[row]})
        self.assertEqual(result['records'][0]['status'],'digest-conflict')
        self.assertNotEqual(result['records'][0]['sha256'],'0'*64)
        (self.root/'large.json').write_bytes(b' '*(2*1024*1024+1));row=dict(row,path='large.json',expectedSha256=None)
        result=self.inspect({'selectionVersion':1,'records':[row]})
        self.assertEqual(result['records'][0]['status'],'oversized');self.assertIsNone(result['records'][0]['sha256'])

    def test_symlink_and_nonregular_targets_are_not_read(self):
        (self.root/'linked.json').symlink_to(self.root/'record.json');(self.root/'directory.json').mkdir()
        rows=[dict(self.selection['records'][0],id=i,path=p) for i,p in [('LINK','linked.json'),('DIR','directory.json')]]
        result=self.inspect({'selectionVersion':1,'records':rows})
        self.assertEqual([r['status'] for r in result['records']],['unsafe-path','not-a-regular-file'])
        self.assertTrue(all(not r['contentRead'] for r in result['records']))

    def test_duplicate_members_nonfinite_values_and_bad_utf8_are_malformed(self):
        row=dict(self.selection['records'][0],path='strict.json')
        for data in [b'{"contractVersion":"0.2.0","contractVersion":"99.0.0"}',b'{"bad":NaN}',b'\xff']:
            (self.root/'strict.json').write_bytes(data)
            result=self.inspect({'selectionVersion':1,'records':[row]})
            self.assertEqual(result['records'][0]['status'],'malformed-json')

    def test_shape_only_recognition_does_not_claim_full_schema_validation(self):
        (self.root/'invalid-shape.json').write_text('[]')
        row=dict(self.selection['records'][1],id='INVALID-SHAPE',path='invalid-shape.json')
        result=self.inspect({'selectionVersion':1,'records':[row,self.selection['records'][1]]})
        self.assertEqual(result['records'][0]['status'],'invalid-shape')
        self.assertEqual(result['records'][1]['validation'],'entry-point-shape-only')
        self.assertFalse(result['publishable'])
        self.assertEqual(self.inspect({'selectionVersion':1,'records':[]})['exitCode'],3)

    def test_core_validation_exhaustion_is_unknown_and_does_not_abort_following_rows(self):
        value=json.loads((self.root/'record.json').read_text());template=value['items'][0];items=[]
        for index in range(1200):
            item=deepcopy(template);item['id']='CHAIN-'+str(index);item['dependsOn']=['CHAIN-'+str(index+1)] if index<1199 else [];items.append(item)
        value['items']=items;value['milestones'][0]['gateItemIds']=['CHAIN-0']
        (self.root/'deep-work.json').write_text(json.dumps(value))
        row=dict(self.selection['records'][0],id='DEEP',path='deep-work.json')
        result=self.inspect({'selectionVersion':1,'records':[row,self.selection['records'][0]]})
        self.assertEqual(result['records'][0]['status'],'validation-unavailable')
        self.assertEqual(result['records'][1]['status'],'validated')
        self.assertEqual(result['exitCode'],3)

    def test_deep_or_oversized_selection_is_rejected_without_traceback(self):
        selection=self.root/'bad-selection.json'
        for data in ['['*1400+']'*1400,' '*(128*1024+1)]:
            selection.write_text(data)
            run=subprocess.run([sys.executable,'-m','project_record','inspect-inputs','--root',str(self.root),
                                '--selection',str(selection),'--observed-at',OBSERVED],capture_output=True,text=True)
            self.assertEqual(run.returncode,1)
            self.assertNotIn('Traceback',run.stderr)

    def test_coverage_table_names_only_known_selector_kinds(self):
        from project_record.inspector import KINDS
        catalogue=json.loads((ROOT/'standards/inspector-inventory.json').read_text())
        mapped={r['selectorKind'] for r in catalogue['records'] if r['selectorKind'] is not None}
        self.assertEqual(mapped,KINDS)
        self.assertEqual(len({r['id'] for r in catalogue['records']}),len(catalogue['records']))

    def test_release_smoke_witness_matches_selected_synthetic_files(self):
        from hashlib import sha256
        proof=json.loads((ROOT/'tests/fixtures/inspector/provenance.json').read_text())
        for name,digest in proof['artifactSha256'].items():
            self.assertEqual(sha256((ROOT/'tests/fixtures/inspector'/name).read_bytes()).hexdigest(),digest)

    def test_suite_shape_version_and_unknown_source_fields_stay_honest(self):
        path=self.root/'suite.json';row=dict(self.selection['records'][0],id='SUITE',path='suite.json',kind='skill-suite')
        for version,status in [(1,'recognized-shape'),(True,'unsupported-version'),(2,'unsupported-version')]:
            path.write_text(json.dumps(dict(schemaVersion=version,suiteVersion='0.4.1',contractVersion='0.2.0',skills=['sample'])))
            result=self.inspect({'selectionVersion':1,'records':[row]})
            self.assertEqual(result['records'][0]['status'],status)
        row={k:row[k] for k in ['id','path','kind','visibility']}
        path.write_text('{"schemaVersion":1,"suiteVersion":"0.4.1","contractVersion":"0.2.0","skills":["sample"]}')
        result=self.inspect({'selectionVersion':1,'records':[row]})
        self.assertNotIn('sourceObservedOn',result['records'][0])
        self.assertFalse(result['publishable'])
