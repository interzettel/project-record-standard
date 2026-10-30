"""Exercises worked evidence cases using the existing record/policy boundaries."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from project_record.adapters import load_config
from project_record.core import policy_satisfied, summarize, validate

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/evidence_stages/cases.json'


class EvidenceStageTests(unittest.TestCase):
    def setUp(self):
        self.cases = {c['id']: c for c in json.loads(FIXTURE.read_text())['cases']}

    def read_case(self, identity):
        """Loads one unchanged authored fixture through the native adapter."""
        case = self.cases[identity]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            raw = (json.dumps(case['ledger'], indent=2) + '\n').encode()
            (root / 'ledger.json').write_bytes(raw)
            entry = dict(adapter='normalized-v1', sourceFile='ledger.json',
                         project=case['project'], source=case['source'],
                         presentation=dict(renderer='host'))
            (root / 'projects.json').write_text(json.dumps(dict(projects=[entry])))
            record = load_config(root / 'projects.json')[0]
        self.assertEqual(record['source']['sha256'], sha256(raw).hexdigest())
        validate(record)
        return record

    def test_all_cases_retain_criteria_states_dependencies_and_denominators(self):
        for identity, case in self.cases.items():
            with self.subTest(case=identity):
                record = self.read_case(identity)
                self.assertEqual(record['items'], case['ledger']['items'])
                result = summarize(record)
                expected = case['expected']
                self.assertEqual(result['metrics']['work']['done'], expected['requiredDone'])
                self.assertEqual(result['metrics']['work']['total'], expected['requiredTotal'])
                self.assertEqual(result['metrics']['milestones']['done'], expected['acceptedMilestones'])
                for leaf in record['items']:
                    satisfied = policy_satisfied(case['policies'][leaf['id']], leaf['evidence'],
                                                 leaf['id'], leaf['implementationRevision'])
                    self.assertEqual(satisfied, leaf['state'] == 'done')

    def test_built_and_verified_unmerged_artifact_does_not_satisfy_remaining_gates(self):
        record = self.read_case('loomglass')
        leaf = record['items'][0]
        self.assertTrue(policy_satisfied({'allOf': ['implementation', 'test']},
                                        leaf['evidence'], leaf['id'], leaf['implementationRevision']))
        for kind in ['integration', 'owner-review', 'publication', 'deployment']:
            self.assertFalse(policy_satisfied({'allOf': [kind]}, leaf['evidence'],
                                             leaf['id'], leaf['implementationRevision']))
        self.assertEqual(summarize(record)['metrics']['work']['done'], 0)

    def test_passing_old_revision_and_old_publication_do_not_verify_current_artifact(self):
        record = self.read_case('obsidian')
        leaf = record['items'][0]
        self.assertTrue(policy_satisfied({'allOf': ['test']}, leaf['evidence'], leaf['id'], 'a' * 40))
        self.assertFalse(policy_satisfied({'allOf': ['test']}, leaf['evidence'], leaf['id'], leaf['implementationRevision']))
        self.assertNotEqual(self.cases['obsidian']['publication']['revision'], leaf['implementationRevision'])
        self.assertEqual(leaf['state'], 'active')

    def test_bounded_exception_preserves_original_edge_and_incomplete_criteria(self):
        record = self.read_case('caldera')
        before = deepcopy(record)
        build = record['items'][0]
        self.assertTrue(policy_satisfied({'allOf': ['implementation', 'test']},
                                        build['evidence'], build['id'], build['implementationRevision']))
        self.assertEqual(build['dependsOn'], ['ACCEPT'])
        self.assertTrue(build['blocked'])
        self.assertEqual(summarize(record)['metrics']['work']['done'], 0)
        self.assertEqual(summarize(record)['metrics']['work']['total'], 2)
        self.assertEqual(record, before)

    def test_negative_research_can_be_done_without_publication_or_owner_acceptance(self):
        record = self.read_case('basalt')
        leaf = record['items'][0]
        self.assertEqual(self.cases['basalt']['measurement']['outcome'], 'no-improvement')
        self.assertIsNone(self.cases['basalt']['publication'])
        self.assertEqual(summarize(record)['metrics']['work']['done'], 1)
        self.assertFalse(policy_satisfied({'allOf': ['owner-review']}, leaf['evidence'], leaf['id'], leaf['implementationRevision']))
        # A different improvement criterion would not pass these observations.
        self.assertFalse(policy_satisfied({'allOf': ['improvement']}, leaf['evidence'], leaf['id'], leaf['implementationRevision']))

    def test_staging_deployment_does_not_supply_missing_owner_acceptance(self):
        record = self.read_case('tuff')
        deployment = self.cases['tuff']['deployment']
        leaf = record['items'][0]
        self.assertEqual(deployment['revision'], leaf['implementationRevision'])
        self.assertEqual(deployment['authorizedScope'], 'staging-only')
        self.assertIsNone(self.cases['tuff']['publication'])
        self.assertEqual(summarize(record)['metrics']['work']['done'], 0)
        self.assertIs(summarize(record)['milestones'][0]['accepted'], False)

    def test_structural_validation_does_not_interpret_criteria_or_authenticate_exceptions(self):
        record = self.read_case('caldera')
        leaf = record['items'][0]
        leaf.update(state='done', blocked=False)
        validate(record)
        self.assertEqual(summarize(record)['metrics']['work']['done'], 1)
        # This passing structural check exposes a limit, not authorized completion.
        self.assertFalse(policy_satisfied(self.cases['caldera']['policies']['BUILD'],
                                         leaf['evidence'], leaf['id'], leaf['implementationRevision']))
