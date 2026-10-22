import copy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from project_record.adapters import load_config
from project_record.build import build
from project_record.core import RecordError, export_record, summarize
from project_record.delivery import changelog_markdown, delivery_summary, release_readiness
from project_record.governance import governance_errors
from project_record.history import history_errors
from project_record.readme import update_readme
from project_record.scaffold import adoption_plan, initialize
from project_record.timeline import comparison, make_timeline

ROOT = Path(__file__).resolve().parents[1]


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.record = load_config(ROOT / 'examples/projects.json', {'standard'})[0]

    def test_scope_growth_and_state_changes_have_additive_separate_effects(self):
        before = copy.deepcopy(self.record)
        before.pop('governance')
        before.pop('releasePlans')
        after = copy.deepcopy(before)
        pending = next(i for i in after['items'] if i['state'] != 'done')
        pending['state'] = 'done'
        added = copy.deepcopy(after['items'][0])
        added.update(id='ADDED', state='backlog')
        after['items'].append(added)
        result = comparison(before, after)
        bridge = result['bridges']['work']
        self.assertGreater(bridge['stateEffectPP'], 0)
        self.assertLess(bridge['scopeEffectPP'], 0)
        self.assertAlmostEqual(bridge['stateEffectPP'] + bridge['scopeEffectPP'], bridge['totalChangePP'], places=3)
        self.assertEqual(result['added'], ['ADDED'])

    def test_history_rejects_wrong_project_duplicate_and_reverse_observations(self):
        other = copy.deepcopy(self.record)
        other['project']['id'] = 'different'
        with self.assertRaises(RecordError):
            comparison(self.record, other)
        with self.assertRaises(RecordError):
            make_timeline([self.record, self.record])
        other = copy.deepcopy(self.record)
        other['source']['sha256'] = 'a' * 64
        other['source']['observedOn'] = '2026-10-21'
        with self.assertRaises(RecordError):
            make_timeline([self.record, other])

    def test_release_requires_all_kinds_and_exact_applicable_receipts(self):
        revision = 'b' * 40
        plan = {'id':'P', 'component':'cli', 'channel':'registry', 'revision':revision, 'gates':[{'id':'G', 'label':'Owner and test', 'policy':{'allOf':['test','owner-review']}, 'receipts':[{'kind':'test','subject':'G','revision':revision,'result':'passed','source':'test log'}]}]}
        self.assertEqual(release_readiness(self.record, plan)['passed'], 0)
        plan['gates'][0]['receipts'].append({'kind':'owner-review','subject':'G','revision':revision,'result':'passed','source':'attributed review fixture'})
        summary = release_readiness(self.record, plan)
        self.assertEqual(summary['status'], 'ready-for-publication-review')
        self.assertFalse(summary['published'])
        plan['gates'][0]['receipts'][-1]['revision'] = 'c' * 40
        self.assertEqual(release_readiness(self.record, plan)['passed'], 0)

    def test_empty_plan_is_unknown_and_failed_receipt_remains_visible(self):
        plan={'id':'P','component':'cli','channel':'github','revision':'a'*40,'gates':[]}
        self.assertIsNone(release_readiness(self.record, plan)['percent'])
        plan['gates']=[{'id':'G','label':'Check','policy':{'allOf':['test']},'receipts':[{'kind':'test','subject':'G','revision':'a'*40,'result':'failed','source':'failed log'}]}]
        self.assertEqual(release_readiness(self.record, plan)['gates'][0]['status'], 'failed')

    def test_publication_is_component_and_channel_specific_without_fake_deployment(self):
        record=copy.deepcopy(self.record)
        record['deployments']=[]
        record['changes']=[{'id':'C1','component':'cli','type':'feature','summary':'A change.'},{'id':'C2','component':'web','type':'fix','summary':'A second change.'}]
        release={'component':'cli','channel':'github','version':'1.0','revision':'a'*40,'url':'https://example.invalid/release','publishedAt':None,'observedAt':'2026-10-22T12:00:00Z','changeIds':['C1']}
        record['releases']=[release,{**release,'channel':'registry'}]
        self.assertEqual(history_errors(record), [])
        summary=delivery_summary(record)
        self.assertEqual([c['id'] for c in summary['unreleased']], ['C2'])
        self.assertEqual(summary['deployments'], [])
        text=changelog_markdown(record)
        self.assertIn('cli 1.0 / github', text)
        self.assertIn('cli 1.0 / registry', text)
        self.assertIn('Publication time: Unknown', text)

    def test_invalid_release_references_and_unattributed_receipts_fail(self):
        record=copy.deepcopy(self.record)
        record['releasePlans'][0]['workItemIds'].append('MISSING')
        self.assertTrue(history_errors(record))
        record=copy.deepcopy(self.record)
        record['releasePlans'][0]['gates'][0]['receipts']=[{'kind':'test','subject':'G-AUTO','revision':'a'*40,'result':'passed'}]
        self.assertTrue(history_errors(record))

    def test_wbs_mapping_cannot_double_count_or_approve_itself(self):
        record=copy.deepcopy(self.record)
        record['governance']['workPackages'][1]['workItemIds'].append('STD-01')
        self.assertTrue(governance_errors(record))

    def test_malformed_structures_fail_as_record_errors(self):
        for field, value in [('project',[]),('items',[123]),('source',None),('milestones',['invalid'])]:
            with self.subTest(field=field):
                record=copy.deepcopy(self.record)
                record[field]=value
                with self.assertRaises(RecordError):
                    summarize(record)
        record=copy.deepcopy(self.record)
        record['governance']['tailoring']['finance']='invalid'
        with self.assertRaises(RecordError):
            summarize(record)
        record=copy.deepcopy(self.record)
        record['governance']['baselines'][0]['status']='approved'
        self.assertTrue(governance_errors(record))
        record=copy.deepcopy(self.record)
        record['governance']['tailoring'].pop('finance')
        self.assertTrue(governance_errors(record))

    def test_marked_readme_updates_preserve_outside_bytes_and_default_to_preview(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'README.md'
            original='# Existing project\r\n\r\n<!-- project-record:start -->old<!-- project-record:end -->\r\n\r\nBrand and links stay.\r\n'
            path.write_bytes(original.encode())
            module='<!-- project-record:start -->new<!-- project-record:end -->'
            result=update_readme(path,module)
            self.assertTrue(result['changed'])
            self.assertFalse(result['written'])
            self.assertEqual(path.read_bytes(),original.encode())
            update_readme(path,module,True)
            self.assertEqual(path.read_bytes(),original.replace('>old<','>new<').encode())
            self.assertFalse(update_readme(path,module,True)['changed'])
            with self.assertRaises(RecordError):
                update_readme(path,'no markers',True)

    def test_cold_setup_is_unknown_private_and_refuses_existing_content(self):
        with tempfile.TemporaryDirectory() as folder:
            destination=Path(folder)/'new-project'
            initialize(destination,'new-project','A new project','Owner','2026-10-22')
            config=destination/'progress/project-record.json'
            record=load_config(config)[0]
            self.assertIsNone(summarize(record)['metrics']['work']['percent'])
            self.assertEqual(record['project']['visibility'],'private')
            original=(destination/'README.md').read_bytes()
            with self.assertRaises(RecordError):
                initialize(destination,'new-project','Replacement','Owner','2026-10-22')
            self.assertEqual((destination/'README.md').read_bytes(),original)

    def test_hot_inspection_is_idempotent_and_performs_no_source_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            destination=Path(folder)/'project'
            initialize(destination,'example','Example','Owner','2026-10-22')
            config=destination/'progress/project-record.json'
            before={str(p):p.read_bytes() for p in destination.rglob('*') if p.is_file()}
            self.assertEqual(adoption_plan(config),adoption_plan(config))
            self.assertFalse(adoption_plan(config)['writesPerformed'])
            after={str(p):p.read_bytes() for p in destination.rglob('*') if p.is_file()}
            self.assertEqual(before,after)

    def test_host_renderer_keeps_its_site_and_manifest_hashes_match(self):
        record=copy.deepcopy(self.record)
        record['presentation']['renderer']='host'
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'build'
            entries=build([record],ROOT/'examples/projects.json',output,'public',ROOT)
            self.assertFalse((output/'standard/progress.html').exists())
            self.assertNotIn('./progress.html',(output/'standard/README-module.md').read_text())
            for path,digest in entries[0]['sha256'].items():
                self.assertEqual(sha256((output/path).read_bytes()).hexdigest(),digest)

    def test_public_build_rejects_private_supplements_and_stale_output(self):
        record=copy.deepcopy(self.record)
        record['inputVisibility'].append('private')
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'public'
            with self.assertRaises(RecordError):
                build([record],ROOT/'examples/projects.json',output,'public',ROOT)
            self.assertFalse(output.exists())
            output.mkdir()
            (output/'private-old.txt').write_text('private fixture')
            with self.assertRaises(RecordError):
                build([self.record],ROOT/'examples/projects.json',output,'public',ROOT)
            self.assertFalse((output/'standard').exists())

    def test_composite_action_entry_point_handles_paths_and_reports_real_outputs(self):
        with tempfile.TemporaryDirectory(prefix='record build ') as folder:
            destination=Path(folder)/'output with spaces'
            output_file=Path(folder)/'action-output'
            env={**os.environ,'PROJECT_RECORD_CONFIG':str(ROOT/'examples/projects.json'),'PROJECT_RECORD_OUTPUT':str(destination),'PROJECT_RECORD_ONLY':'standard','PROJECT_RECORD_AUDIENCE':'public','GITHUB_OUTPUT':str(output_file)}
            result=subprocess.run([sys.executable,str(ROOT/'tools/run_action.py')],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('manifest=',output_file.read_text())
            self.assertTrue((destination/'standard/delivery.json').is_file())
            self.assertTrue((destination/'standard/CHANGELOG-generated.md').is_file())

    def test_authored_fragments_are_collected_once_and_duplicate_ids_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            destination=Path(folder)/'project'
            initialize(destination,'example','Example','Owner','2026-10-22')
            config=destination/'progress/project-record.json'
            value=json.loads(config.read_text())
            fragment=destination/'progress/change.json'
            fragment.write_text(json.dumps({'id':'C1','component':'cli','type':'feature','summary':'A bounded change.'}))
            metadata={'path':'change.json','visibility':'private','authority':'Authored change fragment','observedOn':'2026-10-22'}
            value['projects'][0]['changeFiles']=[metadata]
            config.write_text(json.dumps(value))
            record=load_config(config)[0]
            self.assertIn('A bounded change.',changelog_markdown(record))
            value['projects'][0]['changeFiles'].append(metadata)
            config.write_text(json.dumps(value))
            with self.assertRaises(RecordError):
                load_config(config)

    def test_action_refuses_existing_output_before_unrelated_files_can_be_uploaded(self):
        with tempfile.TemporaryDirectory() as folder:
            destination=Path(folder)/'existing'
            destination.mkdir()
            sentinel=destination/'unrelated-private.txt'
            sentinel.write_text('must remain outside the generated artifact')
            env={**os.environ,'PROJECT_RECORD_CONFIG':str(ROOT/'examples/projects.json'),'PROJECT_RECORD_OUTPUT':str(destination),'PROJECT_RECORD_ONLY':'standard','PROJECT_RECORD_AUDIENCE':'owner'}
            result=subprocess.run([sys.executable,str(ROOT/'tools/run_action.py')],env=env,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(list(destination.iterdir()),[sentinel])
            self.assertEqual(sentinel.read_text(),'must remain outside the generated artifact')


if __name__ == '__main__':
    unittest.main()
