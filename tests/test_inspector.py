from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
import json
import re
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from project_record.core import RecordError
from project_record import inspector

ROOT = Path(__file__).resolve().parents[1]
TIME = '2026-11-06T00:15:00+01:00'


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids = set(); self.links = []; self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.add(attrs['id'])
        if tag == 'a': self.links.append(attrs.get('href', ''))


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'host'
        shutil.copytree(ROOT / 'tests/fixtures/inspector', self.root)
        self.selection = json.loads((self.root / 'selection.json').read_text())

    def model(self, selection=None):
        self.assertTrue(hasattr(inspector, 'inspector_model'), 'offline semantic model is not implemented')
        return inspector.inspector_model(self.root, selection or self.selection, observed_at=TIME)

    def declare(self, kind, value, identity='EXTRA'):
        path = identity + '.json'; (self.root / path).write_text(json.dumps(value))
        return dict(id=identity, path=path, kind=kind, visibility='private')

    def test_shared_metrics_ignore_cached_values_and_never_aggregate_snapshots(self):
        record = json.loads((self.root / 'record.json').read_text())
        record['metrics']['work']['done'] = 999
        record['items'][0]['evidence'] = [dict(kind='test', result='failed', source='ci/run', subject='WORK-1')]
        a = self.declare('project-record', record, 'A'); b = self.declare('project-record', record, 'B')
        result = self.model(dict(selectionVersion=1, records=[a, b]))
        self.assertNotIn('metrics', result)
        self.assertFalse(result['publishable'])
        for row in result['artifacts']:
            work = next(v for v in row['views'] if v['role'] == 'work')
            self.assertEqual(work['metrics']['work']['done'], 0)
            self.assertEqual(work['metrics']['work']['total'], 1)
            self.assertEqual(work['items'][0]['id'], 'WORK-1')
            self.assertFalse(work['milestones'][0]['accepted'])

    def test_selected_bodies_read_once_unknown_fallback_and_private_neighbor_untouched(self):
        original = Path.open; reads = []
        def guarded(path, *args, **kwargs):
            self.assertNotEqual(path.name, 'undeclared-private.json')
            if path.parent == self.root: reads.append(path.name)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'open', guarded), patch.object(Path, 'rglob', side_effect=AssertionError('no scan')):
            result = self.model()
        self.assertEqual(reads.count('record.json'), 1)
        future = next(r for r in result['artifacts'] if r['id'] == 'FUTURE-1')
        self.assertEqual(future['views'][0]['role'], 'uninterpreted')
        self.assertEqual(future['status'], 'unsupported-kind')
        self.assertEqual(next(r for r in result['artifacts'] if r['id'] == 'MISSING-1')['status'], 'missing')
        self.assertEqual(next(r for r in result['artifacts'] if r['id'] == 'BROKEN-1')['status'], 'malformed-json')
        self.assertEqual(result['inspectedAt'], TIME)
        self.assertEqual(result['artifacts'][0]['sourceObservedOn'], '2026-10-30')
        self.assertEqual(result['artifacts'][0]['renderedAt'], '2026-11-05T12:00:00Z')

    def test_assessment_views_are_explicit_shape_only_and_preserve_negative_claims(self):
        rows = [self.declare('discovery', {'projectId': 'toy', 'sources': [{'coverage': 'partial'}], 'cleanupQueue': [], 'unresolvedDecisions': []}, 'D'),
                self.declare('readiness-assessment', {'recordKind': 'repository-readiness-assessment', 'readinessLevel': 'L5', 'dimensions': {}, 'autonomy': {'promotionAuthorized': False}}, 'R'),
                self.declare('evidence-record', {'receipts': [{'result': 'failed', 'kind': 'test', 'revision': 'a'*40}]}, 'E'),
                self.declare('collection-observation', {'projectId': 'toy', 'status': 'failed', 'attemptedAt': '2026-11-05T15:00:00Z', 'source': 'toy', 'coverage': {'pagesRead': 0, 'pagesExpected': None}}, 'O')]
        model = self.model(dict(selectionVersion=1, records=rows))
        self.assertEqual([r['views'][0]['role'] for r in model['artifacts']], ['discovery', 'readiness', 'evidence', 'operations'])
        self.assertTrue(all(r['validation'] == 'entry-point-shape-only' for r in model['artifacts']))
        self.assertEqual(model['artifacts'][1]['value']['autonomy']['promotionAuthorized'], False)
        bad = self.declare('readiness-assessment', {'readinessLevel': 'L5'}, 'BAD')
        self.assertEqual(self.model(dict(selectionVersion=1, records=[bad]))['artifacts'][0]['views'][0]['role'], 'uninterpreted')

    def test_render_has_closed_source_joins_and_escapes_hostile_data(self):
        row = self.declare('future', {'a/b~c': '<script>alert(1)</script>', 'url': 'javascript:alert(2)'})
        model = self.model(dict(selectionVersion=1, records=[row, self.selection['records'][0]]))
        from project_record.inspector_views import render_inspector
        text = render_inspector(model); dom = Document(text)
        self.assertNotIn('<script>alert(1)</script>', text)
        self.assertIn('&lt;script&gt;', text)
        self.assertTrue(all(x.startswith('#') for x in dom.links))
        self.assertTrue(all(x[1:] in dom.ids for x in dom.links))
        self.assertIn('/a~1b~0c', text)
        self.assertIn('Uninterpreted', text)
        self.assertNotIn('personalMemory', text)

    def test_all_catalogue_families_have_explicit_view_or_fallback_mapping(self):
        model = self.model()
        self.assertEqual(len(model['coverageTable']), 32)
        self.assertTrue(all(r['view'] and r['familyId'] for r in model['coverageTable']))
        self.assertEqual(next(r for r in model['coverageTable'] if r['familyId'] == 'F-RECEIPTS')['view'], 'uninterpreted')

    def test_digest_conflict_symlink_complexity_and_empty_sets_stay_readable(self):
        bad = dict(self.selection['records'][0], expectedSha256='0'*64)
        self.assertNotIn('value', self.model(dict(selectionVersion=1, records=[bad]))['artifacts'][0])
        (self.root / 'linked.json').symlink_to(self.root / 'record.json')
        linked = dict(bad, path='linked.json')
        self.assertEqual(self.model(dict(selectionVersion=1, records=[linked]))['artifacts'][0]['status'], 'unsafe-path')
        broad = self.declare('future', list(range(5001)), 'BROAD')
        result = self.model(dict(selectionVersion=1, records=[broad, self.selection['records'][0]]))
        self.assertEqual(result['artifacts'][0]['status'], 'render-limit')
        self.assertNotIn('value', result['artifacts'][0])
        self.assertEqual(result['artifacts'][1]['status'], 'validated')
        self.assertEqual(self.model(dict(selectionVersion=1, records=[]))['exitCode'], 3)

    def test_cli_requires_owner_local_new_output_and_never_changes_input(self):
        before = {p.name: sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir() if p.is_file()}
        out = Path(self.temp.name) / 'view'
        args = [sys.executable, '-m', 'project_record', 'inspector', '--root', str(self.root), '--selection', str(self.root/'selection.json'), '--observed-at', TIME, '--output', str(out)]
        refused = subprocess.run(args, capture_output=True, text=True)
        self.assertNotEqual(refused.returncode, 0); self.assertFalse(out.exists())
        run = subprocess.run(args+['--owner-local'], capture_output=True, text=True)
        self.assertEqual(run.returncode, 3, run.stderr)
        self.assertEqual(sorted(p.name for p in out.iterdir()), ['index.html'])
        again = subprocess.run(args+['--owner-local'], capture_output=True, text=True)
        self.assertEqual(again.returncode, 1)
        self.assertEqual(before, {p.name: sha256(p.read_bytes()).hexdigest() for p in self.root.iterdir() if p.is_file()})

    def test_large_nested_keys_and_missing_newer_views_are_bounded(self):
        value = {'x'*40000: {'y'*40000: 'text'}}
        row = self.declare('future', value, 'KEYS')
        result = self.model(dict(selectionVersion=1, records=[row]))
        self.assertEqual(result['artifacts'][0]['status'], 'render-limit')

    def test_semantic_history_preserves_exact_observations_and_candidate_failure(self):
        from project_record.inspector_views import render_inspector
        row = self.declare('history', {'coverage': 'partial', 'snapshots': [{'observedOn': '2026-10-01', 'metrics': {'work': {'done': 2, 'total': 3, 'percent': 66.7}}}], 'comparisons': []}, 'H')
        model = self.model(dict(selectionVersion=1, records=[row]))
        text = render_inspector(model)
        self.assertIn('2026-10-01', text)
        self.assertIn('66.7', text)
        self.assertNotIn('&quot;observedOn&quot;:', text, 'semantic history should use labelled fields rather than a serialized JSON blob')

    def test_failed_candidate_gate_stays_not_ready_and_dependency_links_are_local(self):
        from project_record.inspector_views import render_inspector
        record = json.loads((self.root/'record.json').read_text())
        second = deepcopy(record['items'][0]); second.update(id='WORK-2', dependsOn=['WORK-1'])
        record['items'].append(second)
        record['releasePlans'] = [dict(id='P', component='cli', channel='github', revision='a'*40,
            gates=[dict(id='G', label='Check', policy={'allOf':['test']}, receipts=[dict(kind='test', subject='G', revision='a'*40, result='failed', source='toy failed log')])])]
        row = self.declare('project-record', record)
        model = self.model(dict(selectionVersion=1, records=[row]))
        view = next(v for v in model['artifacts'][0]['views'] if v['role']=='delivery')
        self.assertEqual(view['summary']['plans'][0]['status'], 'not-ready')
        self.assertFalse(view['summary']['plans'][0]['published'])
        text = render_inspector(model)
        self.assertIn('Prerequisite WORK-1', text)

    def test_private_all_views_fixture_renders_each_original_content_role(self):
        root = ROOT/'tests/fixtures/inspector-views'
        self.assertTrue((root/'selection.json').is_file(), 'combined safe semantic fixture is missing')
        model = inspector.inspector_model(root, json.loads((root/'selection.json').read_text()), observed_at=TIME)
        roles = {v['role'] for a in model['artifacts'] for v in a['views']}
        self.assertTrue({'work','provenance','discovery','readiness','evidence','history','delivery','operations','uninterpreted'} <= roles)
        self.assertTrue(all(a['synthetic'] for a in model['artifacts']))
        from project_record.inspector_views import render_inspector
        text = render_inspector(model)
        self.assertIn('toy failed run', text)
        self.assertIn('Synthetic unavailable collector', text)
        doc = Document(text)
        self.assertTrue(all(x[1:] in doc.ids for x in doc.links))

    def test_output_render_failure_leaves_no_directory_or_partial_artifact(self):
        out = Path(self.temp.name)/'too-large'
        self.assertTrue(hasattr(inspector, 'build_inspector'))
        with patch('project_record.inspector_views.render_inspector', return_value='x'*(32*1024*1024+1)):
            with self.assertRaises(RecordError):
                inspector.build_inspector(self.root, self.root/'selection.json', out, observed_at=TIME)
        self.assertFalse(out.exists())

    def test_unrenderable_unicode_cannot_suppress_later_records_or_crash_output(self):
        for value in [{'extra':'\ud800'}, {'\ud800':'extra'}]:
            row = self.declare('future', value, 'UNICODE')
            (self.root/'selection-local.json').write_text(json.dumps(dict(selectionVersion=1, records=[row,self.selection['records'][0]])))
            out = Path(self.temp.name)/('unicode-'+str(len(value.keys()))+'-'+str('\ud800' in value))
            result = inspector.build_inspector(self.root, self.root/'selection-local.json', out, observed_at=TIME)
            self.assertEqual(result['exitCode'], 3)
            self.assertIn('WORK-1', (out/'index.html').read_text())
            self.assertIn('unrenderable-unicode', (out/'index.html').read_text())
        bad = dict(self.selection['records'][0], path='\ud800.json')
        with self.assertRaises(RecordError):
            self.model(dict(selectionVersion=1, records=[bad]))

    def test_present_null_joins_its_exact_field_and_raw_json_types_remain_distinct(self):
        from project_record.inspector_views import render_inspector
        row = self.declare('future', {'nullValue':None, 'nullString':'null', 'falseValue':False, 'falseString':'false', 'oneValue':1, 'oneString':'1'})
        text = render_inspector(self.model(dict(selectionVersion=1, records=[self.selection['records'][0],row])))
        source = re.search(r'class="source-field" id="([^"]+)"><code>/items/0/implementationRevision</code>', text)
        link = re.search(r'href="#([^"]+)">Basis /items/0/implementationRevision</a>', text)
        self.assertEqual(source.group(1), link.group(1))
        for expected in ['&quot;null&quot;', '&quot;false&quot;', '&quot;1&quot;']:
            self.assertIn(expected, text)
        self.assertIn('<code>/nullValue</code> <span>null</span>',text)

    def test_calculated_gates_link_decisive_work_states_and_exact_plan_fields(self):
        from project_record.inspector_views import render_inspector
        record = json.loads((self.root/'record.json').read_text())
        record['milestones'][0]['acceptanceRule']='all-gate-items'
        record['releasePlans']=[dict(id='P',component='cli',channel='github',revision='a'*40,workItemIds=['WORK-1'],gates=[])]
        text=render_inspector(self.model(dict(selectionVersion=1,records=[self.declare('project-record',record)])))
        for label in ['Gate input /items/0/state','Gate input /releasePlans/0/workItemIds/0','Gate input /milestones/0/gateItemIds/0']:
            self.assertIn(label,text)
            pointer=label.removeprefix('Gate input ')
            target=re.search(r'class="source-field" id="([^"]+)"><code>'+re.escape(pointer)+'</code>',text)
            link=re.search(r'href="#([^"]+)">'+re.escape(label)+'</a>',text)
            self.assertEqual(target.group(1),link.group(1))

    def test_derived_delivery_does_not_repeat_large_work_receipts_per_plan(self):
        from project_record.inspector_views import render_inspector
        record=json.loads((self.root/'record.json').read_text())
        record['items'][0]['completionBasis']='&'*30000
        record['releasePlans']=[dict(id='P'+str(n),component='cli',channel='github',revision='a'*40,workItemIds=['WORK-1'],gates=[]) for n in range(32)]
        text=render_inspector(self.model(dict(selectionVersion=1,records=[self.declare('project-record',record)])))
        self.assertLess(len(text.encode()),1024*1024)

    @unittest.skipUnless(os.name=='posix','POSIX filesystem mode check')
    def test_private_output_is_owner_only_even_under_permissive_umask(self):
        out=Path(self.temp.name)/'private-output'
        old=os.umask(0)
        try:
            inspector.build_inspector(self.root,self.root/'selection.json',out,observed_at=TIME)
        finally:
            os.umask(old)
        self.assertEqual(out.stat().st_mode & 0o777,0o700)
        self.assertEqual((out/'index.html').stat().st_mode & 0o777,0o600)

    def test_unchecked_embedded_extras_cannot_inherit_core_validation(self):
        record=json.loads((self.root/'record.json').read_text())
        record.update(discovery='CERTIFIED',operations={'status':'healthy'},history='CERTIFIED')
        row=self.declare('project-record',record)
        model=self.model(dict(selectionVersion=1,records=[row]))
        extras=[v for v in model['artifacts'][0]['views'] if v['pointer'] in {'/discovery','/operations','/history'}]
        self.assertTrue(extras)
        self.assertTrue(all(v['role']=='uninterpreted' and v['validation']=='unvalidated-extra' for v in extras))

    def test_page_expansion_limit_refuses_before_creating_output(self):
        rows=[self.declare('future', {'s'+str(k):'&'*30000 for k in range(8)}, 'B'+str(n)) for n in range(30)]
        (self.root/'many.json').write_text(json.dumps(dict(selectionVersion=1,records=rows)))
        out=Path(self.temp.name)/'expansion'
        with self.assertRaises(RecordError):
            inspector.build_inspector(self.root,self.root/'many.json',out,observed_at=TIME)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
