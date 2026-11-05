from copy import deepcopy
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch

from project_record.core import RecordError
from project_record.feedback import DESTINATION, dispatch_feedback, prepare_feedback, public_report
from project_record.reconcile import _identity, _lock

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://github.com/interzettel/project-record-standard/issues/36'


class FeedbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.encounter = json.loads((ROOT / 'tests/fixtures/feedback/runtime-path-gap.json').read_text())
        self.profile = dict(feedbackPolicyVersion=1, destination=DESTINATION,
                            grant=dict(source='synthetic:adopted-feedback-grant', actions=['create-issue']),
                            review=None, redactions=['sensitive-private-text'], maxAttempts=2)
        self.search = dict(searchVersion=1, destination=DESTINATION, rootCause=self.encounter['rootCause'],
                           observedOn='2026-11-04', source='synthetic:all-pages-inspected', coverage='complete',
                           resources=['issues', 'pull-requests'], states=['open', 'closed'], nextCursor=None, matches=[])

    def prepare(self):
        result = prepare_feedback(self.encounter, self.profile, self.search, self.root / 'outbox', apply=True)
        self.profile['review'] = dict(reportSha256=result['reportSha256'], source='synthetic:public-content-review')
        return Path(result['ticket'])

    def read(self, ticket):
        return json.loads((ticket / 'feedback.json').read_text())

    def test_preview_and_suppression_write_nothing(self):
        result = prepare_feedback(self.encounter, self.profile, self.search, self.root / 'outbox')
        self.assertEqual(result['status'], 'proposal')
        self.assertFalse((self.root / 'outbox').exists())
        for ownership in ['host-only', 'preference']:
            self.encounter['classification'] = ownership
            self.assertEqual(prepare_feedback(self.encounter, self.profile, self.search, self.root / 'outbox', apply=True)['status'], 'suppressed')
        self.encounter['classification'] = 'shared-standard'
        self.encounter['impact'] = ''
        self.assertEqual(prepare_feedback(self.encounter, self.profile, self.search, self.root / 'outbox', apply=True)['status'], 'suppressed')
        self.assertFalse((self.root / 'outbox').exists())

    def test_unknown_pins_are_preserved_without_inventing_versions(self):
        self.encounter['identity'] = {k: None for k in self.encounter['identity']}
        self.assertTrue(all(v is None for v in self.read(self.prepare())['report']['identity'].values()))

    def test_private_context_is_omitted_and_literals_redacted_before_review(self):
        self.encounter['privateContext'] = {'memory': 'NEVER EXPORT THIS', 'credentials': 'a-secret'}
        self.encounter['reproduction']['steps'] += ' sensitive-private-text'
        ticket = self.prepare()
        published = []
        result = dispatch_feedback(ticket, self.profile, self.search, transport=lambda req: published.append(req) or dict(status='submitted', url=URL))
        self.assertEqual(result['status'], 'submitted')
        payload = json.dumps(published)
        self.assertNotIn('NEVER EXPORT THIS', payload)
        self.assertNotIn('sensitive-private-text', payload)
        self.assertNotIn('a-secret', payload)
        self.assertIn('[redacted]', payload)
        self.assertNotIn('effort', published[0]['report'])
        self.assertEqual(set(published[0]), {'destination', 'action', 'marker', 'title', 'report', 'reportSha256'})

    def test_missing_permission_retains_one_proposal_without_prompt_or_transport(self):
        ticket = self.prepare()
        self.profile['grant']['actions'] = []
        with patch('builtins.input', side_effect=AssertionError('must not prompt')):
            for _ in range(2):
                result = dispatch_feedback(ticket, self.profile, self.search, transport=lambda _: self.fail('no grant'))
                self.assertEqual(result['status'], 'proposal')
        self.assertEqual(self.read(ticket)['attempts'], 0)
        self.assertTrue(prepare_feedback(self.encounter, self.profile, self.search, self.root / 'outbox', apply=True)['reused'])

    def test_complete_coverage_is_required_before_new_issue(self):
        ticket = self.prepare()
        cases = [dict(coverage='partial'), dict(coverage='not-inspected'), dict(nextCursor='next-page'),
                 dict(resources=['issues']), dict(states=['open'])]
        for change in cases:
            with self.subTest(change=change):
                result = dispatch_feedback(ticket, self.profile, dict(self.search, **change), transport=lambda _: self.fail('incomplete search'))
                self.assertEqual(result['status'], 'proposal')
                self.assertEqual(self.read(ticket)['attempts'], 0)
                self.assertEqual(self.read(ticket)['search'], dict(self.search, **change))

    def test_actual_encounter_links_existing_pr_even_with_partial_search(self):
        ticket = self.prepare()
        self.search.update(coverage='partial', matches=[dict(rootCause=self.encounter['rootCause'], url='https://github.com/interzettel/project-record-standard/pull/63')])
        result = dispatch_feedback(ticket, self.profile, self.search, transport=lambda _: self.fail('existing report'))
        self.assertEqual(result['status'], 'linked')
        self.assertEqual(self.read(ticket)['attempts'], 0)
        self.assertTrue(dispatch_feedback(ticket, self.profile, self.search)['reused'])

    def test_root_cause_reuse_retains_first_reviewed_bytes_and_unique_effort(self):
        ticket = self.prepare()
        before = self.read(ticket)['reportSha256']
        self.encounter['encounterId'] = 'another-real-encounter'
        self.encounter['impact'] = 'Additional known impact'
        self.encounter['effort'] = dict(trackingSeconds=3, correctionSeconds=2)
        for _ in range(2):
            result = prepare_feedback(self.encounter, self.profile, self.search, self.root / 'outbox', apply=True)
            self.assertEqual(result['ticket'], str(ticket))
        record = self.read(ticket)
        self.assertEqual(len(record['encounters']), 2)
        self.assertEqual(record['telemetry']['reusedRootCauses'], 1)
        self.assertEqual(record['reportSha256'], before)
        self.assertEqual(record['encounters']['another-real-encounter']['effort']['trackingSeconds'], 3)
        self.assertEqual(record['encounters']['another-real-encounter']['proposedAmendment']['impact'], 'Additional known impact')
        self.encounter['impact'] = 'changed observation under same ID'
        with self.assertRaises(RecordError):
            prepare_feedback(self.encounter, self.profile, self.search, self.root / 'outbox', apply=True)

    def test_review_digest_and_permission_are_independent(self):
        ticket = self.prepare()
        for review in [None, dict(reportSha256='0' * 64, source='synthetic:wrong-text')]:
            self.profile['review'] = review
            result = dispatch_feedback(ticket, self.profile, self.search, transport=lambda _: self.fail('unreviewed bytes'))
            self.assertEqual(result['status'], 'proposal')
        self.assertEqual(self.read(ticket)['attempts'], 0)

    def test_success_is_deduplicated_and_does_not_award_acceptance(self):
        ticket = self.prepare()
        calls = []
        transport = lambda req: calls.append(req) or dict(status='submitted', url=URL)
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=transport)['status'], 'submitted')
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=transport)['status'], 'submitted')
        self.assertEqual(len(calls), 1)
        record = self.read(ticket)
        self.assertEqual(len(record['telemetry']['transportSeconds']), 1)
        self.assertNotIn('sourceAccepted', json.dumps(record))
        self.assertNotIn('completion', json.dumps(calls))

    def test_denied_transport_is_bounded_and_does_not_lose_proposal(self):
        ticket = self.prepare()
        calls = []
        for _ in range(3):
            self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=lambda req: calls.append(req) or dict(status='denied'))['status'], 'proposal')
        self.assertEqual(len(calls), 2)
        self.assertTrue((ticket / 'feedback.json').exists())
        self.assertEqual(self.read(ticket)['attempts'], 2)

    def test_unknown_transport_or_exception_never_blindly_retries(self):
        ticket = self.prepare()
        calls = []
        def fail(req):
            calls.append(req)
            raise TimeoutError('Authorization: sensitive-private-text')
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=fail)['status'], 'uncertain')
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=fail)['status'], 'uncertain')
        self.assertEqual(len(calls), 1)
        self.assertNotIn('sensitive-private-text', (ticket / 'feedback.json').read_text())
        self.search['matches'] = [dict(rootCause=self.encounter['rootCause'], url=URL)]
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=fail)['status'], 'linked')
        self.assertEqual(len(calls), 1)

    def test_partial_or_wrong_destination_receipt_stays_uncertain(self):
        ticket = self.prepare()
        result = dispatch_feedback(ticket, self.profile, self.search, transport=lambda _: dict(status='submitted', url='https://github.com/other/private/issues/1'))
        self.assertEqual(result['status'], 'uncertain')
        self.assertNotIn('other/private', (ticket / 'feedback.json').read_text())
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search)['status'], 'uncertain')

    def test_crash_after_remote_write_keeps_submitting_marker(self):
        ticket = self.prepare()
        class ProcessDeath(BaseException):
            pass
        def die(_):
            raise ProcessDeath()
        with self.assertRaises(ProcessDeath):
            dispatch_feedback(ticket, self.profile, self.search, transport=die)
        self.assertEqual(self.read(ticket)['status'], 'submitting')
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=lambda _: self.fail('unsafe duplicate'))['status'], 'uncertain')

    def test_uncertain_ownership_missing_transport_and_budget_do_not_publish(self):
        self.encounter['classification'] = 'uncertain'
        ticket = self.prepare()
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=lambda _: self.fail('unclassified'))['status'], 'proposal')
        self.assertEqual(self.read(ticket)['attempts'], 0)

    def test_path_symlinks_payload_edits_and_lock_contention_are_refused(self):
        ticket = self.prepare()
        with _lock(ticket):
            with self.assertRaises(RecordError):
                dispatch_feedback(ticket, self.profile, self.search)
            with self.assertRaises(RecordError):
                prepare_feedback(self.encounter, self.profile, self.search, self.root / 'outbox', apply=True)
        path = ticket / 'feedback.json'
        original = path.read_bytes()
        record = json.loads(original)
        record['report']['task'] = 'unreviewed replacement'
        path.write_text(json.dumps(record))
        with self.assertRaises(RecordError):
            dispatch_feedback(ticket, self.profile, self.search)
        path.write_bytes(original)
        target = self.root / 'saved.json'
        path.rename(target)
        path.symlink_to(target)
        with self.assertRaises(RecordError):
            dispatch_feedback(ticket, self.profile, self.search)

    def test_interrupted_initial_save_can_recover_same_ticket(self):
        import project_record.feedback as module
        with patch.object(module, '_atomic', side_effect=OSError('synthetic initial save failure')):
            with self.assertRaises(OSError):
                self.prepare()
        ticket = self.prepare()
        self.assertEqual(self.read(ticket)['status'], 'proposal')
        self.assertEqual(self.read(ticket)['attempts'], 0)

    def test_redacted_root_cause_keeps_private_search_identity(self):
        self.encounter['rootCause'] += '-sensitive-private-text'
        self.search['rootCause'] = self.encounter['rootCause']
        ticket = self.prepare()
        calls = []
        result = dispatch_feedback(ticket, self.profile, self.search, transport=lambda req: calls.append(req) or dict(status='submitted', url=URL))
        self.assertEqual(result['status'], 'submitted')
        self.assertNotIn('sensitive-private-text', json.dumps(calls))
        self.assertEqual(self.read(ticket)['rootCause'], self.encounter['rootCause'])

    def test_cli_preview_and_local_apply_never_submit(self):
        encounter, profile, search = [self.root / name for name in ['encounter.json', 'profile.json', 'search.json']]
        for path, value in [(encounter, self.encounter), (profile, self.profile), (search, self.search)]:
            path.write_text(json.dumps(value))
        outbox = self.root / 'cli-outbox'
        cmd = [sys.executable, '-m', 'project_record', 'feedback', '--encounter', str(encounter), '--profile', str(profile),
               '--search', str(search), '--directory', str(outbox)]
        preview = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertFalse(outbox.exists())
        applied = subprocess.run(cmd + ['--apply'], capture_output=True, text=True)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        ticket = Path(json.loads(applied.stdout)['ticket'])
        self.assertEqual(self.read(ticket)['attempts'], 0)

    def test_actual_process_death_releases_lock_but_blocks_create_retry(self):
        ticket = self.prepare()
        profile, search = self.root / 'host-policy.json', self.root / 'search.json'
        profile.write_text(json.dumps(self.profile))
        search.write_text(json.dumps(self.search))
        script = "import json,os; from pathlib import Path; from project_record.feedback import dispatch_feedback; dispatch_feedback(Path(" + repr(str(ticket)) + "),json.loads(Path(" + repr(str(profile)) + ").read_text()),json.loads(Path(" + repr(str(search)) + ").read_text()),transport=lambda request: os._exit(73))"
        result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 73, result.stderr)
        self.assertEqual(self.read(ticket)['status'], 'submitting')
        self.assertEqual(dispatch_feedback(ticket, self.profile, self.search, transport=lambda _: self.fail('duplicate create'))['status'], 'uncertain')

    def test_missing_host_transport_retains_reviewed_proposal(self):
        ticket = self.prepare()
        result = dispatch_feedback(ticket, self.profile, self.search)
        self.assertEqual(result['status'], 'proposal')
        self.assertIn('No host transport', result['reason'])
        self.assertEqual(self.read(ticket)['attempts'], 0)

    def test_malformed_delivery_state_cannot_restart_uncertain_submission(self):
        ticket = self.prepare()
        path = ticket / 'feedback.json'
        record = self.read(ticket)
        for changes in [dict(status='unrecognized'), dict(attempts=-1), dict(attempts=True), dict(rootCause='changed-key')]:
            path.write_text(json.dumps(dict(record, **changes)))
            with self.subTest(changes=changes), self.assertRaises(RecordError):
                dispatch_feedback(ticket, self.profile, self.search, transport=lambda _: self.fail('corrupt state'))
        path.write_text(json.dumps(record))

    def test_invalid_shapes_cannot_expand_export_or_destination(self):
        for change in [dict(extra='private text'), dict(feedbackVersion=True), dict(affectedIds=[]), dict(classification='invented')]:
            with self.subTest(change=change), self.assertRaises((RecordError, ValueError)):
                prepare_feedback(dict(self.encounter, **change), self.profile, self.search, self.root / 'outbox', apply=True)
        self.profile['destination'] = 'another/repository'
        with self.assertRaises(RecordError):
            self.prepare()
