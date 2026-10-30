"""Probes existing integrity checks and reproduces their authority limits."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from project_record.adapters import load_config
from project_record.core import RecordError, policy_satisfied, progress, validate
from project_record.governance import governance_errors

ROOT = Path(__file__).resolve().parents[1]


class PolicyBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.record = load_config(ROOT / 'examples/projects.json', {'standard'})[0]
        self.cases = json.loads((ROOT / 'tests/fixtures/policy/cases.json').read_text())['cases']

    def test_distinct_leaves_count_once_and_duplicate_credit_fails(self):
        case = self.cases[0]
        items = [dict(id=x, state='done', required=True, blocked=False) for x in case['positive']]
        self.assertEqual(progress(items)['done'], 2)
        for item, identity in zip(items, case['negative']):
            item['id'] = identity
        with self.assertRaises(RecordError):
            progress(items)

    def test_pinned_receipt_matches_subject_revision_and_result(self):
        case = self.cases[1]
        receipt = dict(kind='test', subject=case['subject'], revision=case['revision'], result='passed', source='synthetic')
        policy = {'allOf': ['test']}
        self.assertTrue(policy_satisfied(policy, [receipt], case['subject'], case['revision']))
        for change in [dict(subject=case['negativeSubject']), dict(revision='b' * 40), dict(result='failed'), dict(supersededBy='replacement')]:
            with self.subTest(change=change):
                self.assertFalse(policy_satisfied(policy, [{**receipt, **change}], case['subject'], case['revision']))
        self.assertFalse(policy_satisfied({}, [receipt], case['subject'], case['revision']))

    def test_approval_structure_requires_attribution_but_cannot_authenticate_it(self):
        approval = {'id': 'SYNTHETIC', 'status': 'approved', **{k: self.cases[2][k] for k in ['approvedBy', 'approvedAt', 'approvalSource']}}
        self.record['governance']['baselines'].append(approval)
        self.assertEqual(governance_errors(self.record), [])
        # This pass deliberately reproduces the lack of identity authentication.
        self.record['governance']['baselines'][-1].pop('approvalSource')
        self.assertTrue(any('attributed approval' in e for e in governance_errors(self.record)))

    def test_source_revision_drift_rejects_pinned_receipt_but_not_unpinned_call(self):
        case = self.cases[3]
        receipt = dict(kind='test', subject='WRITE', revision=case['observed'], result='passed', source='synthetic')
        self.assertFalse(policy_satisfied({'allOf': ['test']}, [receipt], 'WRITE', case['expected']))
        # This does not implement a source writer or compare-and-swap check.
        self.assertTrue(policy_satisfied({'allOf': ['test']}, [receipt], 'WRITE', None))

    def test_undeclared_work_reference_fails_but_valid_scope_is_not_authorization(self):
        case = self.cases[4]
        package = self.record['governance']['workPackages'][0]
        self.assertIn(case['declared'], package['workItemIds'])
        self.assertEqual(governance_errors(self.record), [])
        package['workItemIds'].append(case['outside'])
        self.assertTrue(any('unknown work' in e for e in governance_errors(self.record)))
        added = deepcopy(self.record['items'][0])
        added.update(id=case['outside'], state='backlog', sourceState='synthetic-unapproved', evidence=[], completionBasis='not-complete')
        self.record['items'].append(added)
        # Valid structure alone does not establish permission to add this scope.
        validate(self.record)
