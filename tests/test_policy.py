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


class SharedPolicyInterfaceTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.record = load_config(ROOT / 'tests/fixtures/handoff/projects.json')[0]
        self.source = self.folder / 'ledger.json'
        self.source.write_bytes((ROOT / 'tests/fixtures/handoff/ledger.json').read_bytes())
        leaf = self.record['items'][0]
        self.request = dict(policyVersion=1, record=self.record, before=deepcopy(self.record),
                            requiredRules=['PRS-EVIDENCE-01','PRS-SOURCE-01','PRS-HISTORY-01','PRS-SCOPE-01'],
                            gates=[dict(subject=leaf['id'], revision=leaf['implementationRevision'],
                                        policy=dict(allOf=['implementation','test']), receipts=deepcopy(leaf['evidence']))],
                            source=dict(path=str(self.source), expectedSha256=self.record['source']['sha256']),
                            audience='public', output=dict(path=str(self.folder / 'new-output')), changes=[])

    def evaluate(self, request=None):
        from project_record.policy import evaluate
        return evaluate(self.request if request is None else request)

    def result(self, report, rule):
        return next(r for r in report['checks'] if r['ruleId'] == rule)

    def test_explicit_required_subset_passes_without_certifying_unknown_mechanisms_or_writing(self):
        before = self.source.read_bytes()
        report = self.evaluate()
        self.assertEqual(report['overall'], 'pass')
        self.assertEqual(report['exitCode'], 0)
        self.assertEqual(len(report['checks']), 17)
        self.assertEqual(self.result(report, 'PRS-HOST-01')['status'], 'unknown')
        self.assertFalse(report['operationAuthorized'])
        self.assertFalse(report['written'])
        self.assertEqual(self.source.read_bytes(), before)
        self.assertFalse((self.folder / 'new-output').exists())

    def test_duplicate_credit_fails_even_if_accounting_was_not_listed_as_required(self):
        request = deepcopy(self.request)
        request['record']['items'].append(deepcopy(request['record']['items'][0]))
        report = self.evaluate(request)
        self.assertEqual(report['exitCode'], 1)
        self.assertEqual(self.result(report, 'PRS-ACCOUNT-01')['status'], 'fail')
        self.assertTrue(self.result(report, 'PRS-ACCOUNT-01')['required'])

    def test_wrong_revision_proof_fails_and_missing_proof_is_unknown(self):
        request = deepcopy(self.request)
        request['gates'][0]['revision'] = 'f' * 40
        self.assertEqual(self.evaluate(request)['exitCode'], 1)
        request['gates'][0]['receipts'] = []
        report = self.evaluate(request)
        self.assertEqual(report['exitCode'], 3)
        self.assertEqual(self.result(report, 'PRS-EVIDENCE-01')['status'], 'unknown')
        self.assertEqual(report['overall'], 'unknown')

    def test_silent_scope_loss_fails_and_explanation_does_not_authenticate_scope_admission(self):
        request = deepcopy(self.request)
        request['record']['items'] = []
        request['record']['milestones'] = []
        request['record']['groups'] = []
        report = self.evaluate(request)
        self.assertEqual(report['exitCode'], 1)
        self.assertEqual(self.result(report, 'PRS-HISTORY-01')['status'], 'fail')
        request['changes'] = [dict(kind='removed', id='SYNTHETIC-LEAF-01', reason='Synthetic approved removal', source='synthetic:decision'),
                              dict(kind='group-scope', id='G', reason='Synthetic removal', source='synthetic:decision'),
                              dict(kind='milestone-scope', id='M', reason='Synthetic removal', source='synthetic:decision')]
        report = self.evaluate(request)
        self.assertEqual(self.result(report, 'PRS-HISTORY-01')['status'], 'pass')
        self.assertEqual(self.result(report, 'PRS-SCOPE-01')['status'], 'unknown')
        self.assertEqual(report['exitCode'], 3)

    def test_private_public_input_and_nonempty_output_are_rejected_before_writes(self):
        request = deepcopy(self.request)
        request['record']['inputVisibility'].append('private')
        request['record']['items'][0]['note'] = 'PRIVATE_PAYLOAD_SENTINEL'
        report = self.evaluate(request)
        self.assertEqual(report['exitCode'], 1)
        self.assertEqual(self.result(report, 'PRS-PRIVACY-01')['status'], 'fail')
        self.assertNotIn('PRIVATE_PAYLOAD_SENTINEL', json.dumps(report))
        output = self.folder / 'new-output'
        output.mkdir()
        (output / 'private.txt').write_text('keep')
        report = self.evaluate()
        self.assertEqual(self.result(report, 'PRS-OWNED-01')['status'], 'fail')
        self.assertEqual((output / 'private.txt').read_text(), 'keep')

    def test_direct_file_cli_and_thin_wrapper_return_equivalent_diagnostics_and_exit_codes(self):
        import contextlib
        import io
        import os
        import subprocess
        import sys
        from project_record.__main__ import main
        from project_record.policy import evaluate_file
        for mode, expected in [('pass', 0), ('fail', 1), ('unknown', 3)]:
            request = deepcopy(self.request)
            if mode == 'fail':
                request['gates'][0]['revision'] = 'e' * 40
            elif mode == 'unknown':
                request['gates'] = []
            path = self.folder / 'request.json'
            path.write_text(json.dumps(request))
            direct = self.evaluate(request)
            self.assertEqual(evaluate_file(path), direct)
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = main(['policy-check', '--request', str(path)])
            self.assertEqual(code, expected)
            self.assertEqual(json.loads(stream.getvalue()), direct)
            env = {**os.environ, 'PYTHONPATH': str(ROOT / 'src')}
            for command in [[sys.executable, '-m', 'project_record', 'policy-check'],
                            [sys.executable, str(ROOT / 'tools/check_policy.py')]]:
                result = subprocess.run([*command, '--request', str(path)], cwd=ROOT,
                                        env=env, capture_output=True, text=True)
                with self.subTest(mode=mode, command=command):
                    self.assertEqual(result.returncode, expected, result.stderr)
                    self.assertEqual(json.loads(result.stdout), direct)
                    self.assertEqual(result.stderr, '')
            self.assertFalse((self.folder / 'new-output').exists())

    def test_unknown_catalogue_rule_cannot_be_downgraded_to_success_by_omission(self):
        request = deepcopy(self.request)
        request['requiredRules'].append('PRS-HOST-01')
        report = self.evaluate(request)
        self.assertEqual(report['exitCode'], 3)
        self.assertTrue(self.result(report, 'PRS-HOST-01')['required'])
        self.assertEqual(self.result(report, 'PRS-HOST-01')['status'], 'unknown')

    def test_empty_policy_and_unpinned_gate_do_not_certify_success(self):
        for change in [dict(policy={}), dict(policy=None), dict(revision=None), dict(receipts=None)]:
            request = deepcopy(self.request)
            request['gates'][0].update(change)
            with self.subTest(change=change):
                self.assertEqual(self.evaluate(request)['exitCode'], 3)
        request['gates'][0]['revision'] = 'main'
        self.assertEqual(self.evaluate(request)['exitCode'], 1)

    def test_missing_changed_and_uppercase_source_hashes_keep_identity_semantics(self):
        request = deepcopy(self.request)
        request['source']['expectedSha256'] = request['source']['expectedSha256'].upper()
        self.assertEqual(self.evaluate(request)['exitCode'], 0)
        self.source.write_text('changed')
        report = self.evaluate()
        self.assertEqual(self.result(report, 'PRS-SOURCE-01')['status'], 'fail')
        self.source.unlink()
        report = self.evaluate()
        self.assertEqual(self.result(report, 'PRS-SOURCE-01')['status'], 'unknown')
        self.assertEqual(report['exitCode'], 3)

    def test_new_done_requires_its_gate_and_new_source_acceptance_remains_unauthenticated(self):
        request = deepcopy(self.request)
        request['before']['items'][0].update(state='active', sourceState='active')
        request['gates'] = []
        request['requiredRules'] = ['PRS-ACCOUNT-01']
        report = self.evaluate(request)
        self.assertTrue(self.result(report, 'PRS-EVIDENCE-01')['required'])
        self.assertEqual(report['exitCode'], 3)
        request['gates'] = deepcopy(self.request['gates'])
        request['record']['milestones'][0]['sourceAccepted'] = True
        report = self.evaluate(request)
        self.assertEqual(self.result(report, 'PRS-ACCEPT-01')['status'], 'unknown')
        self.assertEqual(report['exitCode'], 3)

    def test_existing_automated_acceptance_rule_does_not_invent_an_owner_gate(self):
        request = deepcopy(self.request)
        for record in [request['record'], request['before']]:
            record['milestones'][0]['acceptanceRule'] = 'all-gate-items'
        request['before']['items'][0].update(state='active', sourceState='active')
        report = self.evaluate(request)
        self.assertEqual(self.result(report, 'PRS-ACCEPT-01')['status'], 'pass')
        self.assertEqual(report['exitCode'], 0)
        self.assertFalse(report['operationAuthorized'])

    def test_criterion_dependency_and_visibility_changes_need_explicit_history_and_authority(self):
        for field, value in [('criterion', 'Weakened criterion'), ('dependsOn', ['SYNTHETIC-LEAF-01'])]:
            request = deepcopy(self.request)
            request['record']['items'][0][field] = value
            with self.subTest(field=field):
                self.assertEqual(self.evaluate(request)['exitCode'], 1)
        request = deepcopy(self.request)
        request['before']['project']['visibility'] = 'private'
        report = self.evaluate(request)
        self.assertEqual(self.result(report, 'PRS-HISTORY-01')['status'], 'fail')
        request['changes'] = [dict(kind='visibility', id='synthetic-handoff', reason='Reviewed projection proposed', source='synthetic:proposal')]
        report = self.evaluate(request)
        self.assertEqual(self.result(report, 'PRS-SCOPE-01')['status'], 'unknown')
        self.assertEqual(report['exitCode'], 3)

    def test_malformed_input_has_structured_exit_two_but_invalid_record_is_a_failed_check(self):
        import contextlib
        import io
        from project_record.__main__ import main
        for change in [dict(policyVersion=True), dict(requiredRules=[]), dict(requiredRules=['NOT-A-RULE']),
                       dict(extraField=True), dict(output=dict(path='bad\x00path'))]:
            request = deepcopy(self.request)
            request.update(change)
            with self.subTest(change=change):
                self.assertEqual(self.evaluate(request)['exitCode'], 2)
        path = self.folder / 'broken.json'
        path.write_text('{')
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = main(['policy-check', '--request', str(path)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stream.getvalue())['overall'], 'invalid-input')
        request = deepcopy(self.request)
        request['record'] = None
        self.assertEqual(self.evaluate(request)['exitCode'], 1)
        request = deepcopy(self.request)
        request['gates'][0]['receipts'][0]['result'] = []
        self.assertEqual(self.evaluate(request)['exitCode'], 1)

    def test_unrelated_prior_project_and_output_symlink_are_not_success(self):
        request = deepcopy(self.request)
        request['before']['project']['id'] = 'other'
        report = self.evaluate(request)
        self.assertEqual(report['exitCode'], 1)
        self.assertEqual(self.result(report, 'PRS-HISTORY-01')['status'], 'fail')
        real = self.folder / 'real-output'
        real.mkdir()
        link = self.folder / 'output-link'
        link.symlink_to(real, target_is_directory=True)
        request = deepcopy(self.request)
        request['output']['path'] = str(link)
        report = self.evaluate(request)
        self.assertEqual(self.result(report, 'PRS-OWNED-01')['status'], 'fail')
        self.assertEqual(list(real.iterdir()), [])

    def test_new_done_cannot_use_consistently_old_gate_and_receipts_against_declared_new_artifact(self):
        request = deepcopy(self.request)
        request['before']['items'][0].update(state='active', sourceState='active')
        request['gates'][0]['revision'] = 'a' * 40
        for receipt in request['gates'][0]['receipts']:
            receipt['revision'] = 'a' * 40
        report = self.evaluate(request)
        self.assertEqual(report['exitCode'], 1)
        self.assertEqual(self.result(report, 'PRS-EVIDENCE-01')['status'], 'fail')

    def test_existing_01_record_contract_remains_readable(self):
        request = deepcopy(self.request)
        request['record']['contractVersion'] = '0.1.0'
        request['before']['contractVersion'] = '0.1.0'
        self.assertEqual(self.evaluate(request)['exitCode'], 0)

    def test_history_guard_rejects_reverse_observation_order_with_or_without_new_source_identity(self):
        for changed_identity in [False, True]:
            request = deepcopy(self.request)
            request['record']['source']['observedOn'] = '2026-10-29'
            if changed_identity:
                request['record']['source']['sha256'] = 'e' * 64
            with self.subTest(changed_identity=changed_identity):
                report = self.evaluate(request)
                self.assertEqual(self.result(report, 'PRS-HISTORY-01')['status'], 'fail')
                self.assertEqual(report['exitCode'], 1)

    def test_restoring_cancelled_work_requires_explanation_and_admission_assessment(self):
        request = deepcopy(self.request)
        request['before']['items'][0].update(state='cancelled', sourceState='cancelled', note='Synthetic prior cancellation')
        request['record']['items'][0].update(state='backlog', sourceState='backlog')
        report = self.evaluate(request)
        self.assertEqual(report['exitCode'], 1)
        self.assertEqual(self.result(report, 'PRS-SCOPE-01')['status'], 'fail')
        request['changes'] = [dict(kind='restored', id=request['record']['items'][0]['id'],
                                  reason='Restore scoped work', source='synthetic:decision')]
        report = self.evaluate(request)
        self.assertEqual(self.result(report, 'PRS-HISTORY-01')['status'], 'pass')
        self.assertEqual(self.result(report, 'PRS-SCOPE-01')['status'], 'unknown')
        self.assertEqual(report['exitCode'], 3)

    def test_malformed_visibility_returns_structured_failed_check_through_all_interfaces(self):
        import os
        import subprocess
        import sys
        from project_record.policy import evaluate_file
        for malformed in [None, 'public', {}, ['not-classified'], [None]]:
            with self.subTest(visibility=malformed):
                request = deepcopy(self.request)
                request['record']['inputVisibility'] = malformed
                request['before']['inputVisibility'] = malformed
                report = self.evaluate(request)
                self.assertEqual(report['exitCode'], 1)
                self.assertEqual(self.result(report, 'PRS-PRIVACY-01')['status'], 'fail')
                path = self.folder / 'malformed.json'
                path.write_text(json.dumps(request))
                self.assertEqual(evaluate_file(path), report)
                for command in [[sys.executable, '-m', 'project_record', 'policy-check'],
                                [sys.executable, str(ROOT / 'tools/check_policy.py')]]:
                    result = subprocess.run(command + ['--request', str(path)], cwd=ROOT,
                                            env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')),
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(json.loads(result.stdout), report)
                    self.assertEqual(result.stderr, '')

    def test_additional_public_fragment_does_not_invent_visibility_scope_change(self):
        request = deepcopy(self.request)
        request['record']['inputVisibility'].append('public')
        report = self.evaluate(request)
        self.assertEqual(self.result(report, 'PRS-SCOPE-01')['status'], 'pass')
        self.assertEqual(self.result(report, 'PRS-HISTORY-01')['status'], 'pass')
        self.assertEqual(report['exitCode'], 0)
