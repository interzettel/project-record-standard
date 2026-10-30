from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PolicyCITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base, self.candidate = self.root / 'base', self.root / 'candidate'
        for path in [self.base, self.candidate]:
            path.mkdir()
            for p in (ROOT / 'tests/fixtures/reconcile').iterdir():
                shutil.copyfile(p, path / p.name)
        self.profile = dict(ciProfileVersion=1, config='projects.json', projectId='synthetic-reconcile',
                            audience='public', completionPolicy=dict(allOf=['implementation', 'test']),
                            protectedPaths=['tools/*', '.github/*', 'src/*'], approvedChanges=[])

    def check(self):
        from project_record.policy_ci import check_checkouts
        return check_checkouts(self.base, self.candidate, self.profile)

    def write_source(self, edit):
        source = self.candidate / 'ledger.json'
        raw = json.loads(source.read_text()); edit(raw)
        old = (self.base / 'ledger.json').read_bytes()
        source.write_text(json.dumps(raw, indent=2) + '\n')
        (self.candidate / 'before.json').write_bytes(old)
        path = self.candidate / 'projects.json'
        config = json.loads(path.read_text()); entry = config['projects'][0]
        entry.update(previousSourceFile='before.json', previousSource=deepcopy(entry['source']))
        path.write_text(json.dumps(config))

    def test_unchanged_data_passes_without_host_enforcement_claim(self):
        report = self.check()
        self.assertEqual(report['exitCode'], 0, report)
        self.assertEqual(report['hostEnforcement'], 'not-assessed')
        self.assertFalse(report['written'])

    def test_duplicate_credit_is_rejected_and_corrected_data_passes_with_same_checker(self):
        source = self.candidate / 'ledger.json'; original = source.read_bytes()
        raw = json.loads(original); raw['items'].append(deepcopy(raw['items'][0]))
        source.write_text(json.dumps(raw))
        self.assertEqual(self.check()['exitCode'], 1)
        source.write_bytes(original)
        self.assertEqual(self.check()['exitCode'], 0)

    def test_done_needs_pinned_matching_evidence_and_preserved_raw_observation(self):
        def edit(raw):
            leaf = raw['items'][0]
            leaf.update(state='done', implementationRevision='a' * 40)
            leaf['evidence'] = [dict(kind=k, subject=leaf['id'], revision='a' * 40, result='passed', source='synthetic:' + k) for k in ['implementation', 'test']]
        self.write_source(edit)
        self.assertEqual(self.check()['exitCode'], 0, self.check())
        config = json.loads((self.candidate / 'projects.json').read_text())
        config['projects'][0].pop('previousSourceFile')
        config['projects'][0].pop('previousSource')
        (self.candidate / 'projects.json').write_text(json.dumps(config))
        self.assertEqual(self.check()['exitCode'], 1)

    def test_missing_evidence_is_unknown_and_wrong_revision_fails(self):
        self.write_source(lambda raw: raw['items'][0].update(state='done', implementationRevision='a' * 40))
        self.assertEqual(self.check()['exitCode'], 3)
        path = self.candidate / 'ledger.json'; raw = json.loads(path.read_text())
        raw['items'][0]['evidence'] = [dict(kind='test', subject='WORK-1', revision='b' * 40, result='passed', source='synthetic:wrong')]
        path.write_text(json.dumps(raw))
        self.assertEqual(self.check()['exitCode'], 1)

    def test_scope_loss_and_new_owner_acceptance_cannot_silently_pass(self):
        self.write_source(lambda raw: raw['items'][0].update(required=False, deferReason='Synthetic proposal'))
        self.assertEqual(self.check()['exitCode'], 1)
        inputs = self.check()['inputs']
        before, after = inputs['beforeCanonicalSha256'], inputs['afterCanonicalSha256']
        self.profile['approvedChanges'] = [dict(beforeCanonicalSha256=before, afterCanonicalSha256=after, rules=['PRS-SCOPE-01'], source='synthetic:adopted-host-decision')]
        report = self.check()
        self.assertEqual(report['exitCode'], 0, report)
        scope = next(c for c in report['policy']['checks'] if c['ruleId'] == 'PRS-SCOPE-01')
        self.assertEqual(scope['status'], 'unknown')
        self.assertEqual(len(report['hostDecisions']), 1)

    def test_exact_input_decision_cannot_exempt_evidence_or_another_candidate(self):
        self.profile['approvedChanges'] = [dict(beforeCanonicalSha256='a' * 64, afterCanonicalSha256='b' * 64, rules=['PRS-EVIDENCE-01'], source='synthetic:invalid')]
        self.assertNotEqual(self.check()['exitCode'], 0)
        self.profile['approvedChanges'][0]['rules'] = ['PRS-SCOPE-01']
        self.write_source(lambda raw: raw['items'][0].update(required=False, deferReason='Unadopted'))
        self.assertEqual(self.check()['exitCode'], 1)

    def test_candidate_code_hooks_and_profile_are_not_executed_or_adopted(self):
        for name in ['tools/run_policy_ci.py', '.git/hooks/pre-commit', 'src/project_record/__init__.py']:
            path = self.candidate / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("raise RuntimeError('candidate code must never execute')")
        path = self.candidate / '.github/prs-policy.json'; path.parent.mkdir(exist_ok=True)
        path.write_text('{"approvedChanges":["candidate cannot grant authority"]}')
        report = self.check()
        self.assertEqual(report['exitCode'], 0, report)
        self.assertIn('tools/run_policy_ci.py', report['protectedChanges'])
        self.assertIn('.github/prs-policy.json', report['protectedChanges'])
        self.assertEqual(report['hostDecisions'], [])

    def test_escape_and_symlink_inputs_are_rejected(self):
        source = self.candidate / 'ledger.json'; source.unlink()
        source.symlink_to(self.base / 'ledger.json')
        self.assertEqual(self.check()['exitCode'], 1)
        source.unlink(); source.write_bytes((self.base / 'ledger.json').read_bytes())
        path = self.candidate / 'projects.json'; config = json.loads(path.read_text()); config['projects'][0]['sourceFile'] = '../base/ledger.json'; path.write_text(json.dumps(config))
        self.assertEqual(self.check()['exitCode'], 1)

    def test_public_input_cannot_hide_a_private_supplement(self):
        config = json.loads((self.candidate / 'projects.json').read_text())
        config['projects'][0]['supplements'] = [dict(path='private.json', visibility='private', authority='Synthetic', observedOn='2026-10-30')]
        (self.candidate / 'private.json').write_text('{"decisions":[]}')
        (self.candidate / 'projects.json').write_text(json.dumps(config))
        self.assertEqual(self.check()['exitCode'], 1)

    def test_cli_uses_same_engine_and_propagates_failure_unknown_and_pass(self):
        import os
        import subprocess
        import sys
        profile = self.root / 'profile.json'; profile.write_text(json.dumps(self.profile))
        command = [sys.executable, str(ROOT / 'tools/run_policy_ci.py'), '--base', str(self.base), '--candidate', str(self.candidate), '--profile', str(profile)]
        for expected in [0, 3, 1]:
            if expected == 3:
                self.write_source(lambda raw: raw['items'][0].update(state='done', implementationRevision='a' * 40))
            if expected == 1:
                source = self.candidate / 'ledger.json'; raw = json.loads(source.read_text()); raw['items'].append(deepcopy(raw['items'][0])); source.write_text(json.dumps(raw))
            result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')), capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout), self.check())

    def test_workflow_uses_trusted_base_for_target_event_and_least_privilege(self):
        text = (ROOT / '.github/workflows/policy.yml').read_text()
        self.assertIn('pull_request_target:', text)
        self.assertIn('github.event.pull_request.base.sha || github.sha', text)
        self.assertIn('python3 trusted/tools/run_policy_ci.py', text)
        self.assertIn('--profile trusted/.github/prs-policy.json', text)
        self.assertIn('contents: read', text)
        for forbidden in ['paths:', 'paths-ignore:', 'continue-on-error', 'secrets.', 'candidate/tools', 'candidate/src', 'cache:', 'write-all']:
            self.assertNotIn(forbidden, text)
        self.assertEqual(text.count('persist-credentials: false'), 3)
        self.assertIn('head.repo.full_name != github.repository', text)
        self.assertNotIn('allow-unsafe-pr-checkout', text)
        self.assertNotIn('paths:', (ROOT / 'templates/.github/workflows/project-record.example.yml').read_text())

    def test_adopted_decision_is_bound_to_supplement_bytes_as_well_as_raw_source(self):
        self.write_source(lambda raw: raw['items'][0].update(required=False, deferReason='Proposal'))
        inputs = self.check()['inputs']
        self.profile['approvedChanges'] = [dict(beforeCanonicalSha256=inputs['beforeCanonicalSha256'], afterCanonicalSha256=inputs['afterCanonicalSha256'], rules=['PRS-SCOPE-01'], source='synthetic:adopted')]
        self.assertEqual(self.check()['exitCode'], 0)
        path = self.candidate / 'projects.json'; config = json.loads(path.read_text())
        config['projects'][0]['supplements'] = [dict(path='additional.json', visibility='public', authority='Synthetic', observedOn='2026-10-30')]
        (self.candidate / 'additional.json').write_text('{"decisions":[]}')
        path.write_text(json.dumps(config))
        self.assertEqual(self.check()['exitCode'], 1)
        self.assertEqual(self.check()['hostDecisions'], [])

    def test_new_source_acceptance_needs_separate_exact_input_host_decision(self):
        def edit(raw):
            leaf = raw['items'][0]
            leaf.update(state='done', implementationRevision='a' * 40)
            leaf['evidence'] = [dict(kind=k, subject=leaf['id'], revision='a' * 40, result='passed', source='synthetic:' + k) for k in ['implementation', 'test']]
            raw['milestones'][0]['sourceAccepted'] = True
        self.write_source(edit)
        report = self.check()
        self.assertEqual(report['exitCode'], 3, report)
        self.profile['approvedChanges'] = [dict(beforeCanonicalSha256=report['inputs']['beforeCanonicalSha256'], afterCanonicalSha256=report['inputs']['afterCanonicalSha256'], rules=['PRS-ACCEPT-01'], source='synthetic:actual-host-decision')]
        report = self.check()
        self.assertEqual(report['exitCode'], 0, report)
        self.assertEqual(next(c for c in report['policy']['checks'] if c['ruleId'] == 'PRS-ACCEPT-01')['status'], 'unknown')
