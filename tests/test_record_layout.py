"""Exercises optional mappings, privacy selection and non-destructive lookup."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from project_record.core import RecordError
from project_record.record_layout import CLASSES, git_paths, layout_index, migration_preview, resolve_record, validate_layout

ROOT = Path(__file__).resolve().parents[1]


class RecordLayoutTests(unittest.TestCase):
    def profile(self, name='shared-repository'):
        return json.loads((ROOT / 'tests/fixtures/record_layout' / (name + '.json')).read_text())

    def test_three_hosts_resolve_all_classes_without_renaming(self):
        for name in ['readme-research', 'private-agent', 'shared-repository']:
            with self.subTest(host=name):
                profile = self.profile(name)
                before = deepcopy(profile)
                validate_layout(profile)
                self.assertEqual({s['class'] for s in profile['stores']}, CLASSES)
                self.assertEqual(resolve_record(profile, 'work', 'R1')['path'], next(s for s in profile['stores'] if s['class'] == 'work')['home']['path'])
                self.assertEqual(profile, before)

    def test_missing_class_and_competing_writer_fail(self):
        profile = self.profile()
        profile['stores'].pop()
        with self.assertRaises(RecordError):
            validate_layout(profile)
        profile = self.profile()
        profile['stores'].append(deepcopy(profile['stores'][0]))
        with self.assertRaises(RecordError):
            validate_layout(profile)

    def test_plan_cannot_own_work_state(self):
        profile = self.profile()
        next(s for s in profile['stores'] if s['class'] == 'plan')['owns'] = ['work.state']
        with self.assertRaises(RecordError):
            validate_layout(profile)

    def test_scoped_ids_are_distinct_and_duplicate_identity_fails(self):
        profile = self.profile()
        self.assertNotEqual(resolve_record(profile, 'work', 'R1')['path'], resolve_record(profile, 'knowledge', 'R1')['path'])
        profile['records'].append(deepcopy(profile['records'][0]))
        with self.assertRaises(RecordError):
            validate_layout(profile)

    def test_public_index_omits_private_locators_values_and_totals(self):
        for name in ['shared-repository', 'private-agent']:
            profile = self.profile(name)
            profile['privateTotal'] = 787878
            profile['records'][0]['secret'] = 'SECRET-SENTINEL'
            result = layout_index(profile)
            output = json.dumps(result)
            for secret in ['synthetic-private', '787878', 'SECRET-SENTINEL', 'reference', 'retention']:
                self.assertNotIn(secret, output)
        self.assertEqual(layout_index(self.profile('private-agent')), [])

    def test_private_and_transient_export_refused_even_with_git_approval(self):
        for kind in ['personal-memory', 'session-context', 'generated']:
            profile = self.profile()
            store = next(s for s in profile['stores'] if s['class'] == kind)
            store.update(publicIndex=True, gitApproval={'by':'synthetic owner','source':'synthetic grant','reason':'test'})
            with self.assertRaises(RecordError):
                validate_layout(profile)

    def test_private_repo_git_requires_explicit_decision(self):
        profile = self.profile()
        store = next(s for s in profile['stores'] if s['class'] == 'personal-memory')
        store.update(home={'kind':'repo','path':'private-memory.md','scope':'file'}, git=True)
        with self.assertRaises(RecordError):
            validate_layout(profile)
        store['gitApproval'] = {'by':'synthetic owner','source':'synthetic decision','reason':'private backup'}
        validate_layout(profile)
        self.assertNotIn('private-memory.md', json.dumps(layout_index(profile)))

    def test_stale_recall_and_superseded_decision_remain_explicit(self):
        result = resolve_record(self.profile(), 'decisions', 'ADR-1', 'old-revision')
        self.assertTrue(result['staleRecall'])
        self.assertEqual(result['status'], 'superseded')
        self.assertEqual(result['supersededBy'], 'ADR-2')
        self.assertEqual(resolve_record(self.profile(), 'work', 'MISSING'), {'status':'unknown'})

    def test_supersession_cycles_and_missing_successors_fail(self):
        for successor in ['MISSING', 'ADR-1']:
            profile = self.profile()
            profile['records'][2]['supersededBy'] = successor
            with self.assertRaises(RecordError):
                validate_layout(profile)

    def test_move_preview_retains_identity_alias_and_input_bytes(self):
        before = self.profile()
        after = deepcopy(before)
        item = after['records'][4]
        previous = item['path']
        item.update(path='Existing.evidence/experiment-renamed.md', previousPaths=[previous])
        original = deepcopy((before, after))
        result = migration_preview(before, after)
        self.assertEqual(len(result), 1)
        self.assertFalse(result[0]['applied'])
        self.assertEqual(resolve_record(after, 'evidence', previous)['id'], 'EXP-1')
        self.assertEqual((before, after), original)
        item.pop('previousPaths')
        with self.assertRaises(RecordError):
            migration_preview(before, after)

    def test_shared_file_lookup_is_ambiguous_without_an_id(self):
        profile = self.profile('readme-research')
        path = profile['records'][2]['path']
        self.assertEqual(resolve_record(profile, 'decisions', path), {'status':'ambiguous'})
        self.assertEqual(resolve_record(profile, 'decisions', 'ADR-2')['status'], 'current')

    def test_directory_with_dot_and_path_escapes(self):
        profile = self.profile()
        validate_layout(profile)
        for path in ['/outside', '../outside', 'Existing.evidence/../outside', 'C:\\outside', 'docs/%2e%2e/x']:
            broken = deepcopy(profile)
            broken['records'][4]['path'] = path
            with self.assertRaises(RecordError):
                validate_layout(broken)

    def test_empty_generated_directory_does_not_create_records(self):
        profile = self.profile()
        self.assertFalse(any(x['className'] == 'generated' for x in layout_index(profile, 'owner')))
        profile['records'] = []
        self.assertEqual(layout_index(profile), [])

    def test_removed_mapping_is_a_hold_not_a_delete(self):
        before = self.profile()
        after = deepcopy(before)
        after['records'].pop()
        report = migration_preview(before, after)
        self.assertEqual(report[0]['action'], 'unmapped-hold')
        self.assertFalse(report[0]['applied'])

    def test_git_selection_is_explicit_and_policy_changes_hold(self):
        before = self.profile('private-agent')
        self.assertEqual(git_paths(before), [])
        after = deepcopy(before)
        store = next(s for s in after['stores'] if s['class'] == 'work')
        store['git'] = True
        self.assertEqual(git_paths(after), ['Bestehend/Arbeit.json'])
        self.assertEqual(migration_preview(before, after)[0]['action'], 'policy-change-hold')

    def test_malformed_host_metadata_fails_as_record_error(self):
        for field, value in [('class', []), ('supersededBy', [])]:
            profile = self.profile()
            profile['records'][0][field] = value
            with self.assertRaises(RecordError):
                validate_layout(profile)
        profile = self.profile()
        profile['layoutVersion'] = True
        with self.assertRaises(RecordError):
            validate_layout(profile)

    def test_private_section_cannot_hide_inside_a_selected_git_file(self):
        profile = self.profile('readme-research')
        store = next(s for s in profile['stores'] if s['class'] == 'personal-memory')
        store['home'] = {'kind':'repo', 'path':'README.md#private-memory', 'scope':'file'}
        with self.assertRaises(RecordError):
            git_paths(profile)

    def test_second_move_preserves_all_historical_aliases(self):
        before = self.profile()
        before['records'][4]['previousPaths'] = ['old-experiment.md']
        after = deepcopy(before)
        item = after['records'][4]
        item.update(path='Existing.evidence/new.md', previousPaths=[item['path']])
        with self.assertRaises(RecordError):
            migration_preview(before, after)

    def test_transient_and_grant_changes_are_validated_and_held(self):
        before = self.profile()
        after = deepcopy(before)
        store = next(s for s in after['stores'] if s['class'] == 'generated')
        store['transient'] = 'true'
        with self.assertRaises(RecordError):
            validate_layout(after)
        store['transient'] = False
        self.assertEqual(migration_preview(before, after)[0]['action'], 'policy-change-hold')
        store['transient'] = True
        store['gitApproval'] = {'by':'changed', 'source':'synthetic', 'reason':'test'}
        self.assertEqual(migration_preview(before, after)[0]['action'], 'policy-change-hold')

    def test_indirect_missing_successor_is_a_record_error(self):
        profile = self.profile()
        profile['records'][3]['supersededBy'] = 'MISSING'
        with self.assertRaises(RecordError):
            validate_layout(profile)
