import json
from pathlib import Path
import tempfile
import unittest

from project_record.adapters import load_config
from project_record.core import percentage, summarize
from project_record.delivery import release_readiness
from project_record.scaffold import initialize


class PercentageTests(unittest.TestCase):
    def test_half_tenth_rounds_up_consistently_for_leaf_and_candidate_ratios(self):
        self.assertEqual(percentage(13, 16), 81.3)
        self.assertIsNone(percentage(0, 0))
        revision = 'b' * 40
        gates = [{'id': str(i), 'label': str(i), 'policy': {'allOf': ['test']},
                  'receipts': [{'kind': 'test', 'subject': str(i), 'revision': revision,
                                'result': 'passed', 'source': 'fixture receipt'}] if i < 13 else []}
                 for i in range(16)]
        self.assertEqual(release_readiness({'items': []}, {'id': 'P', 'component': 'cli', 'channel': 'source', 'revision': revision, 'gates': gates})['percent'], 81.3)

    def test_equal_milestone_mean_uses_unrounded_shares_and_the_same_rounding(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'project'
            initialize(root, 'example', 'Example', 'Owner', '2026-10-22')
            ledger = root / 'progress/ledger.json'
            value = json.loads(ledger.read_text())
            for identity, total, done in [('A', 1, 1), ('B', 8, 5)]:
                value['groups'].append({'id': identity, 'title': identity, 'panel': 'Example'})
                value['milestones'].append({'id': identity, 'title': identity, 'goal': 'Test checkpoint', 'horizon': 'Now', 'groupIds': [identity], 'gateItemIds': [identity + '-0'], 'unscopedWork': [], 'acceptanceRule': 'all-gate-items'})
                for i in range(total):
                    state = 'done' if i < done else 'backlog'
                    value['items'].append({'id': f'{identity}-{i}', 'title': 'Fixture work', 'groupId': identity, 'milestoneId': identity, 'state': state, 'sourceState': state, 'completionBasis': 'fixture', 'kind': 'implementation', 'required': True, 'blocked': False, 'dependsOn': [], 'evidence': []})
            ledger.write_text(json.dumps(value))
            record = summarize(load_config(root / 'progress/project-record.json')[0])
            self.assertEqual(record['metrics']['work']['percent'], 66.7)
            self.assertEqual(record['metrics']['roadmapMean']['percent'], 81.3)


if __name__ == '__main__':
    unittest.main()
