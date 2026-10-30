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
