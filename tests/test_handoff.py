"""Reproduces one pinned synthetic handoff through the existing record reader."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
import unittest

from project_record.adapters import load_config
from project_record.core import RecordError, policy_satisfied, summarize, validate

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/handoff'


class OfflineHandoffTests(unittest.TestCase):
    def setUp(self):
        self.handoff = json.loads((FIXTURE / 'handoff.json').read_text())
        self.record = load_config(FIXTURE / 'projects.json')[0]
        self.leaf = self.record['items'][0]

    def test_exact_reader_contract_and_source_bytes_are_pinned(self):
        pin = self.handoff['pin']
        self.assertEqual(pin['contractVersion'], '0.2.0')
        self.assertEqual(self.record['contractVersion'], pin['contractVersion'])
        self.assertEqual(sha256((FIXTURE / 'ledger.json').read_bytes()).hexdigest(), pin['sourceSha256'])
        self.assertEqual(self.record['source']['sha256'], pin['sourceSha256'])
        self.assertEqual(sha256((FIXTURE / 'projects.json').read_bytes()).hexdigest(), pin['manifestSha256'])
        self.assertEqual(self.record['source']['observedOn'], '2026-10-30')
        self.assertEqual(self.record['source']['kind'], 'file-snapshot')
        self.assertIsNone(self.record['source']['commit'])
        self.assertRegex(pin['toolkitCommit'], r'^[a-f0-9]{40}$')
        for relative, digest in pin['toolkitFiles'].items():
            self.assertEqual(sha256((ROOT / relative).read_bytes()).hexdigest(), digest, relative)

    def test_consumer_and_optional_a2a_ids_do_not_create_accounting_rows(self):
        mapping = self.handoff['mapping']
        self.assertEqual(mapping['projectId'], self.record['project']['id'])
        self.assertEqual(mapping['prsLeafId'], self.leaf['id'])
        self.assertEqual(mapping['consumerTaskId'], self.handoff['consumerTask']['id'])
        self.assertNotEqual(mapping['consumerTaskId'], self.leaf['id'])
        self.assertIsNone(mapping['a2aTaskId'])
        result = summarize(self.record)
        self.assertEqual([i['id'] for i in result['items']], [mapping['prsLeafId']])
        expected = self.handoff['expected']
        self.assertEqual(result['metrics']['work']['done'], expected['requiredDone'])
        self.assertEqual(result['metrics']['work']['total'], expected['requiredTotal'])

    def test_implementation_and_check_do_not_supply_owner_acceptance(self):
        task = self.handoff['consumerTask']
        self.assertEqual(task['status'], 'completed')
        self.assertEqual(task['implementationRevision'], self.leaf['implementationRevision'])
        self.assertEqual(task['receipts'], self.leaf['evidence'])
        args = (self.leaf['evidence'], self.leaf['id'], self.leaf['implementationRevision'])
        self.assertTrue(policy_satisfied(self.handoff['workPolicy'], *args))
        self.assertFalse(policy_satisfied(self.handoff['acceptancePolicy'], *args))
        result = summarize(self.record)
        self.assertIs(result['milestones'][0]['accepted'], False)
        self.assertEqual(result['metrics']['milestones']['done'], self.handoff['expected']['acceptedMilestones'])
        self.assertEqual(result['metrics']['milestones']['total'], self.handoff['expected']['declaredMilestones'])

    def test_offline_replay_is_deterministic_and_preserves_all_input_bytes(self):
        before = {p: p.read_bytes() for p in FIXTURE.iterdir() if p.is_file()}
        original = deepcopy(self.record)
        with patch('socket.socket', side_effect=AssertionError('Offline fixture attempted network')):
            first = summarize(load_config(FIXTURE / 'projects.json')[0])
            second = summarize(load_config(FIXTURE / 'projects.json')[0])
        self.assertEqual(first, second)
        self.assertEqual(self.record, original)
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertTrue(all(value is False for value in self.handoff['permissions'].values()))

    def test_basic_wrong_subject_or_revision_cannot_satisfy_work_policy(self):
        task = self.handoff['consumerTask']
        for subject, revision in [('OTHER', task['implementationRevision']), (self.leaf['id'], 'f' * 40)]:
            with self.subTest(subject=subject, revision=revision):
                self.assertFalse(policy_satisfied(self.handoff['workPolicy'], task['receipts'], subject, revision))

    def test_existing_validator_rejects_duplicate_leaf_and_unknown_contract(self):
        validate(self.record)
        duplicate = deepcopy(self.record)
        duplicate['items'].append(deepcopy(self.leaf))
        with self.assertRaisesRegex(RecordError, 'Duplicate items'):
            validate(duplicate)
        unsupported = deepcopy(self.record)
        unsupported['contractVersion'] = '99.0.0'
        with self.assertRaisesRegex(RecordError, 'Unsupported contractVersion'):
            validate(unsupported)


class AdversarialHandoffTests(unittest.TestCase):
    def setUp(self):
        # Load the explicit fixture without adding a new supported runtime API.
        import importlib.util
        spec = importlib.util.spec_from_file_location('handoff_consumer_fixture', FIXTURE / 'consumer_stub.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assess = module.assess
        self.handoff = json.loads((FIXTURE / 'handoff.json').read_text())
        self.record = load_config(FIXTURE / 'projects.json')[0]
        self.source = deepcopy(self.record['source'])
        self.event = dict(id='synthetic-delivery-01', **self.handoff['mapping'],
                          sourceSha256=self.source['sha256'],
                          implementationRevision=self.handoff['consumerTask']['implementationRevision'],
                          receipts=deepcopy(self.handoff['consumerTask']['receipts']))

    def check_event(self, events=None, **kwargs):
        return self.assess(self.record, self.handoff, [self.event] if events is None else events,
                           self.source, **kwargs)

    def test_retries_and_distinct_delivery_ids_earn_only_one_canonical_credit(self):
        original = deepcopy(self.record)
        first = self.check_event()
        replay = self.check_event([self.event, deepcopy(self.event), {**self.event, 'id': 'synthetic-retry-02'}])
        self.assertEqual(first, replay)
        self.assertEqual(replay['status'], 'pass')
        self.assertEqual(len(replay['proposals']), 2)
        self.assertEqual(replay['metrics']['work']['done'], 1)
        self.assertEqual(replay['metrics']['work']['total'], 1)
        self.assertEqual(self.record, original)
        self.assertFalse(replay['written'])
        self.assertFalse(replay['applicationAuthorized'])

    def test_changed_payload_for_same_event_identity_is_a_conflict(self):
        changed = {**self.event, 'implementationRevision': 'f' * 40}
        result = self.check_event([self.event, changed])
        self.assertEqual(result['status'], 'conflict')
        self.assertIn('event-replay-conflict', result['reasons'])
        self.assertEqual(result['proposals'], [])

    def test_new_source_or_new_implementation_cannot_reuse_old_evidence(self):
        newer = {**self.source, 'sha256': 'e' * 64}
        result = self.assess(self.record, self.handoff, [self.event], newer)
        self.assertEqual(result['status'], 'conflict')
        self.assertIn('current-source-conflict', result['reasons'])
        self.assertEqual(result['source'], self.record['source'])
        self.assertEqual(result['proposals'], [])
        newer_event = {**self.event, 'implementationRevision': 'f' * 40}
        result = self.check_event([newer_event])
        self.assertEqual(result['status'], 'conflict')
        self.assertEqual(result['proposals'], [])
        self.assertFalse(policy_satisfied(self.handoff['workPolicy'], newer_event['receipts'],
                                          newer_event['prsLeafId'], newer_event['implementationRevision']))

    def test_wrong_project_leaf_or_task_correlation_withholds_proposals(self):
        for field in ['projectId', 'prsLeafId', 'consumerTaskId', 'sourceSha256']:
            with self.subTest(field=field):
                result = self.check_event([{**self.event, field: 'wrong'}])
                self.assertEqual(result['status'], 'conflict')
                self.assertEqual(result['proposals'], [])
                self.assertEqual(result['metrics']['work']['total'], 1)

    def test_reopened_issue_is_a_conflict_and_closed_issue_cannot_accept(self):
        reopened = self.check_event(issue={'state': 'open'})
        self.assertEqual(reopened['status'], 'conflict')
        self.assertIn('issue-reopen-conflict', reopened['reasons'])
        self.assertEqual(reopened['proposals'], [])
        closed = self.check_event(issue={'state': 'closed'})
        self.assertEqual(closed['status'], 'pass')
        self.assertEqual(closed['metrics']['milestones']['done'], 0)
        self.assertEqual(reopened['metrics']['work']['done'], 1)

    def test_no_source_is_unknown_and_failed_collection_retains_last_observation(self):
        absent = self.assess(None, self.handoff, [self.event], None)
        self.assertEqual(absent['status'], 'unknown')
        self.assertIsNone(absent['metrics'])
        self.assertIsNone(absent['source'])
        unknown = self.assess(self.record, self.handoff, [self.event], None)
        self.assertEqual(unknown['status'], 'unknown')
        self.assertEqual(unknown['proposals'], [])
        for state, pages, expected in [('failed', 0, None), ('partial', 1, 2), ('success', 1, 2)]:
            with self.subTest(state=state):
                collection = dict(projectId=self.record['project']['id'], status=state,
                                  attemptedAt='2026-10-30T10:00:00Z', source='synthetic-collection-attempt',
                                  coverage=dict(pagesRead=pages, pagesExpected=expected))
                result = self.check_event(collection=collection)
                self.assertEqual(result['status'], 'unknown')
                self.assertEqual(result['freshness']['status'], 'degraded')
                self.assertFalse(result['collection']['complete'])
                self.assertEqual(result['source'], self.source)
                self.assertEqual(result['metrics']['work']['done'], 1)
                self.assertEqual(result['proposals'], [])

    def test_newer_public_render_retains_old_source_date_and_digest(self):
        import tempfile
        from project_record.build import build
        from project_record.status import project_status
        record = deepcopy(self.record)
        # Use the real renderer with the host theme from this toolkit.
        record['presentation']['theme'] = str(ROOT / 'examples/themes/standard.json')
        record['source']['updatedOn'] = record['source']['observedOn']
        with tempfile.TemporaryDirectory() as folder:
            build([record], FIXTURE / 'projects.json', Path(folder) / 'output', 'public', ROOT)
            output = json.loads((Path(folder) / 'output/synthetic-handoff/record.json').read_text())
            self.assertEqual(output['source'], self.source | {'updatedOn': '2026-10-30'})
            status = project_status(output, '2026-11-15')
            self.assertEqual(status['freshness']['status'], 'stale')
            self.assertEqual(status['freshness']['ageDays'], 16)
            self.assertEqual(status['source']['sha256'], self.source['sha256'])
            assessed = self.assess(self.record, self.handoff, [self.event], self.source, as_of='2026-11-15')
            self.assertEqual(assessed['status'], 'unknown')
            self.assertIn('source-freshness-unknown', assessed['reasons'])
            self.assertEqual(assessed['proposals'], [])

    def test_private_project_or_supplement_aborts_entire_public_build_before_output(self):
        import tempfile
        from project_record.build import build
        for private_project in [True, False]:
            record = deepcopy(self.record)
            record['items'][0]['note'] = 'SYNTHETIC_PRIVATE_TASK_SENTINEL'
            record['inputVisibility'] = ['public', 'private']
            if private_project:
                record['project']['visibility'] = 'private'
            with self.subTest(private_project=private_project), tempfile.TemporaryDirectory() as folder:
                destination = Path(folder) / 'public'
                with self.assertRaisesRegex(RecordError, 'Private source'):
                    build([self.record, record], FIXTURE / 'projects.json', destination, 'public', ROOT)
                self.assertFalse(destination.exists())
                self.assertEqual(list(Path(folder).iterdir()), [])

    def test_blocked_prerequisite_and_authored_scope_survive_worker_delivery(self):
        record = deepcopy(self.record)
        leaf = record['items'][0]
        leaf.update(state='ready', blocked=True, dependsOn=['SYNTHETIC-PREREQUISITE'], completionBasis='not-complete')
        prerequisite = deepcopy(leaf)
        prerequisite.update(id='SYNTHETIC-PREREQUISITE', state='backlog', blocked=False, dependsOn=[], evidence=[])
        record['items'].append(prerequisite)
        # A different authored source is a new pin, not permission from a worker.
        record['source']['sha256'] = 'b' * 64
        handoff = deepcopy(self.handoff)
        handoff['pin']['sourceSha256'] = record['source']['sha256']
        event = {**self.event, 'sourceSha256': record['source']['sha256']}
        result = self.assess(record, handoff, [event], record['source'])
        self.assertEqual(result['metrics']['work']['done'], 0)
        self.assertEqual(result['metrics']['work']['blocked'], 1)
        self.assertEqual(leaf['dependsOn'], ['SYNTHETIC-PREREQUISITE'])
        self.assertFalse(result['written'])

    def test_only_authored_cancellation_or_deferral_changes_scope_with_history(self):
        from project_record.timeline import comparison
        for state in ['cancelled', 'deferred']:
            record = deepcopy(self.record)
            leaf = record['items'][0]
            leaf.update(state='cancelled' if state == 'cancelled' else 'backlog',
                        sourceState='synthetic-owner-' + state,
                        required=state == 'cancelled', note='Synthetic owner source change',
                        deferReason='Synthetic owner deferred' if state == 'deferred' else None)
            record['source']['sha256'] = 'c' * 64
            handoff = deepcopy(self.handoff)
            handoff['pin']['sourceSha256'] = record['source']['sha256']
            event = {**self.event, 'sourceSha256': record['source']['sha256']}
            with self.subTest(state=state):
                result = self.assess(record, handoff, [event], record['source'])
                self.assertEqual(result['metrics']['work']['total'], 0)
                self.assertIsNone(result['metrics']['work']['percent'])
                self.assertEqual(len(record['items']), 1)
                self.assertEqual(record['items'][0]['id'], self.record['items'][0]['id'])
                bridge = comparison(self.record, record)
                self.assertEqual(bridge['removed'], [])
                self.assertNotEqual(bridge['sourceRevisions']['before'], bridge['sourceRevisions']['after'])
