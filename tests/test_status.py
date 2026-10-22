import copy
from pathlib import Path
import unittest

from project_record.adapters import load_config
from project_record.core import RecordError
from project_record.scaffold import initialize
from project_record.status import project_status
import tempfile

ROOT = Path(__file__).resolve().parents[1]


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.record = load_config(ROOT / 'examples/projects.json', {'prehnite'})[0]

    def test_status_exposes_named_counts_and_does_not_change_observation(self):
        original = copy.deepcopy(self.record)
        value = project_status(self.record, '2026-10-25', 2)
        self.assertEqual(value['metrics']['work']['done'], 60)
        self.assertEqual(value['metrics']['work']['total'], 80)
        self.assertEqual(value['metrics']['work']['percent'], 75)
        self.assertEqual(value['metrics']['milestones']['percent'], 11.1)
        self.assertEqual(value['freshness']['ageDays'], 3)
        self.assertEqual(value['freshness']['status'], 'stale')
        self.assertEqual(self.record, original)

    def test_failed_partial_collection_cannot_refresh_or_replace_last_success(self):
        observation = {'projectId': 'prehnite', 'attemptedAt': '2026-10-25T12:00:00Z', 'status': 'failed', 'coverage': {'pagesRead': 1, 'pagesExpected': 3}, 'error': 'quota', 'source': 'operator log'}
        value = project_status(self.record, '2026-10-25', 7, observation)
        self.assertEqual(value['freshness']['status'], 'degraded')
        self.assertEqual(value['source']['observedOn'], '2026-10-22')
        self.assertEqual(value['metrics']['work']['done'], 60)
        self.assertEqual(value['collection']['coverage']['pagesRead'], 1)
        self.assertFalse(value['collection']['complete'])

    def test_claimed_success_with_partial_coverage_is_degraded(self):
        observation = {'projectId': 'prehnite', 'attemptedAt': '2026-10-25T12:00:00Z', 'status': 'success', 'coverage': {'pagesRead': 1, 'pagesExpected': 3}, 'source': 'operator log'}
        value = project_status(self.record, '2026-10-25', 7, observation)
        self.assertEqual(value['freshness']['status'], 'degraded')
        self.assertEqual(value['source']['observedOn'], '2026-10-22')

    def test_future_observation_wrong_project_and_invalid_coverage_fail(self):
        with self.assertRaises(RecordError):
            project_status(self.record, '2026-10-21', 7)
        for patch in [{'projectId': 'other'}, {'attemptedAt': '2026-10-25'}, {'coverage': []}, {'coverage': {'pagesRead': 4, 'pagesExpected': 3}}, {'coverage': {'pagesRead': True, 'pagesExpected': 3}}]:
            receipt = {'projectId': 'prehnite', 'attemptedAt': '2026-10-25T12:00:00Z', 'status': 'success', 'coverage': {'pagesRead': 3, 'pagesExpected': 3}, 'source': 'log', **patch}
            with self.subTest(patch=patch), self.assertRaises(RecordError):
                project_status(self.record, '2026-10-25', 7, receipt)

    def test_empty_scope_stays_unmeasured_with_no_forecast(self):
        with tempfile.TemporaryDirectory() as folder:
            initialize(Path(folder) / 'new', 'new', 'New', 'Owner', '2026-10-22')
            record = load_config(Path(folder) / 'new/progress/project-record.json')[0]
            value = project_status(record, '2026-10-22', 7)
            self.assertIsNone(value['metrics']['work']['percent'])
            self.assertEqual(value['freshness']['status'], 'within-threshold')
            self.assertEqual(value['blockers'], [])
            self.assertEqual(value['collection']['status'], 'not-reconciled')


if __name__ == '__main__':
    unittest.main()
