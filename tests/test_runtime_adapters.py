from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from project_record.core import RecordError
from project_record.runtime_adapters import (
    capture_core, configure_hooks, deliver_ticket, hook_command, inspect_runtime,
    prepare_ticket, rollback_hooks, ticket_status,
)

ROOT = Path(__file__).resolve().parents[1]


class RuntimeAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in (ROOT / 'tests/fixtures/reconcile').iterdir():
            shutil.copyfile(path, self.root / path.name)
        self.source = self.root / 'ledger.json'
        manifest = self.root / 'projects.json'
        event = dict(eventVersion=1, eventId='session-1:result-1', projectId='synthetic-reconcile',
                     workItemId='WORK-1', sourceSha256=sha256(self.source.read_bytes()).hexdigest(),
                     manifestSha256=sha256(manifest.read_bytes()).hexdigest(), artifactRevision='a' * 40,
                     result='completed', producer='synthetic-worker', source='synthetic:session',
                     observedOn='2026-11-04', summary='Synthetic implementation and checks.',
                     receipts=[dict(kind=k, subject='WORK-1', revision='a' * 40, result='passed',
                                    source='synthetic:' + k) for k in ['implementation', 'test']], discoveries=[])
        profile = dict(reconcileVersion=1, projectId='synthetic-reconcile', manifest=str(manifest),
                       journal=str(self.root / 'journal'), output=str(self.root / 'generated'),
                       audience='public', authority=dict(source='synthetic:host', routineRecording=True),
                       workPolicies={'WORK-1': dict(allOf=['implementation', 'test'])}, scopeAdmission={})
        self.request = dict(adapterVersion=1, runtime='codex', runtimeVersion='1.2.3',
                            runtimeExecutable=None, sessionId='session-1', turnId='turn-1',
                            workspace=str(self.root), toolkit=str(ROOT), coreFiles=capture_core(ROOT),
                            python=sys.executable, timeout=10, event=event, profile=profile)
        self.payload = dict(session_id='session-1', turn_id='turn-1', cwd=str(self.root), hook_event_name='Stop')

    def prepare(self):
        return Path(prepare_ticket(self.request, self.root / 'outbox')['ticket'])

    def native(self, ticket, payload=None):
        with patch('project_record.runtime_adapters.inspect_runtime', return_value={'version': '1.2.3', 'nativeTriggerVerified': False}):
            return deliver_ticket(ticket, self.payload if payload is None else payload)

    def test_missing_trigger_is_durably_pending_without_source_edits(self):
        before = self.source.read_bytes()
        ticket = self.prepare()
        self.assertEqual(ticket_status(ticket)['reason'], 'awaiting-trigger')
        self.assertEqual(prepare_ticket(self.request, self.root / 'outbox')['state'], 'pending')
        self.assertEqual(self.source.read_bytes(), before)
        altered = deepcopy(self.request)
        altered['event']['summary'] = 'different event bytes'
        with self.assertRaises(RecordError):
            prepare_ticket(altered, self.root / 'outbox')

    def test_both_synthetic_runtime_envelopes_call_real_shared_worker(self):
        for runtime in ['codex', 'claude-code']:
            with self.subTest(runtime=runtime):
                self.request['runtime'] = runtime
                self.request['turnId'] = 'turn-1' if runtime == 'codex' else None
                ticket = self.prepare()
                first = self.native(ticket)
                self.assertEqual(first['state'], 'delivered', first)
                self.assertEqual(first['coreStatus'], 'applied')
                source = self.source.read_bytes()
                self.assertTrue(self.native(ticket)['duplicateDelivery'])
                self.assertEqual(self.source.read_bytes(), source)
                self.assertEqual(json.loads((ticket / 'last-core-result.json').read_text())['metrics']['after']['work']['done'], 1)
                if runtime == 'codex':
                    self.temp.cleanup()
                    self.setUp()

    def test_core_crash_after_commit_before_transport_receipt_is_safe_to_retry(self):
        ticket = self.prepare()
        import project_record.runtime_adapters as module
        atomic = module._atomic
        def fail_delivered(path, data):
            if path.name == 'state.json' and json.loads(data).get('state') == 'delivered':
                raise OSError('synthetic disk failure after shared core commit')
            return atomic(path, data)
        with patch.object(module, '_atomic', side_effect=fail_delivered):
            result = self.native(ticket)
        self.assertEqual(result['state'], 'pending')
        source = self.source.read_bytes()
        result = self.native(ticket)
        self.assertEqual(result['coreStatus'], 'duplicate', result)
        self.assertEqual(self.source.read_bytes(), source)

    def test_bad_native_envelopes_do_not_launch_core(self):
        cases = [(dict(session_id='other'), 'missing-or-mismatched-session'),
                 (dict(turn_id='other'), 'mismatched-turn'),
                 (dict(cwd='/'), 'mismatched-workspace'),
                 (dict(cwd=str(self.root / '..' / 'unrelated-workspace')), 'mismatched-workspace'),
                 (dict(hook_event_name='InventedEvent'), 'unsupported-trigger'),
                 (dict(stop_hook_active=True), 'continued-stop-held'),
                 (dict(hook_event_name='SessionEnd'), 'terminal-trigger-does-not-support-prepared-result')]
        ticket = self.prepare()
        for changes, reason in cases:
            with self.subTest(reason=reason), patch('project_record.runtime_adapters.subprocess.run') as run:
                result = deliver_ticket(ticket, dict(self.payload, **changes))
                self.assertEqual(result['reason'], reason)
                run.assert_not_called()
                self.assertEqual(ticket_status(ticket)['state'], 'pending')

    def test_version_drift_is_held_and_manual_retry_is_labeled(self):
        ticket = self.prepare()
        with patch('project_record.runtime_adapters.inspect_runtime', return_value={'version': '9.0.0'}):
            self.assertEqual(deliver_ticket(ticket, self.payload)['reason'], 'runtime-version-unavailable-or-different')
        result = deliver_ticket(ticket, None, manual=True)
        self.assertEqual(result['state'], 'delivered', result)
        self.assertEqual(result['deliveryMode'], 'manual-retry')

    def test_pin_drift_unavailable_python_timeout_and_invalid_output_retain_request(self):
        ticket = self.prepare()
        original = (ticket / 'request.json').read_bytes()
        with patch('project_record.runtime_adapters.capture_core', return_value={'different': 'bytes'}):
            self.assertEqual(deliver_ticket(ticket, None, manual=True)['reason'], 'core-pin-conflict')
        failures = [(OSError('missing worker'), 'core-unavailable-or-invalid-response'),
                    (subprocess.TimeoutExpired('worker', 0.01), 'core-timeout-retry-same-ticket')]
        for error, reason in failures:
            with patch('project_record.runtime_adapters.subprocess.run', side_effect=error):
                self.assertEqual(deliver_ticket(ticket, None, manual=True)['reason'], reason)
        for stdout in ['garbage', '[]', '{"exitCode":1,"status":"held"}']:
            with patch('project_record.runtime_adapters.subprocess.run', return_value=subprocess.CompletedProcess([], 1, stdout, '')):
                self.assertEqual(deliver_ticket(ticket, None, manual=True)['state'], 'pending')
        self.assertEqual((ticket / 'request.json').read_bytes(), original)
        self.assertEqual(deliver_ticket(ticket, None, manual=True)['state'], 'delivered')

    def test_real_worker_deadline_retains_pending_without_source_changes(self):
        self.request['timeout'] = 0.00001
        before = self.source.read_bytes()
        ticket = self.prepare()
        result = deliver_ticket(ticket, None, manual=True)
        self.assertEqual(result['reason'], 'core-timeout-retry-same-ticket', result)
        self.assertEqual(ticket_status(ticket)['state'], 'pending')
        self.assertEqual(self.source.read_bytes(), before)
        self.assertTrue((ticket / 'request.json').is_file())

    def test_shared_policy_holds_insufficient_evidence(self):
        self.request['event']['receipts'] = []
        result = self.native(self.prepare())
        self.assertEqual(result['state'], 'pending')
        self.assertEqual(result['reason'], 'shared-writer-pending')

    def test_failure_and_cancellation_use_same_core_without_done_credit(self):
        for runtime, trigger, outcome in [('codex', 'Interrupt', 'cancelled'), ('claude-code', 'StopFailure', 'failed')]:
            with self.subTest(runtime=runtime):
                self.request['runtime'] = runtime
                self.request['turnId'] = 'turn-1' if runtime == 'codex' else None
                self.request['event']['result'] = outcome
                self.request['event']['eventId'] = runtime
                result = self.native(self.prepare(), dict(self.payload, hook_event_name=trigger))
                self.assertEqual(result['state'], 'delivered', result)
                record = json.loads(self.source.read_text())
                self.assertNotEqual(record['items'][0]['state'], 'done')
                if runtime == 'codex':
                    self.temp.cleanup()
                    self.setUp()

    def test_symlink_request_and_state_are_refused(self):
        ticket = self.prepare()
        before = self.source.read_bytes()
        for filename in ['request.json', 'state.json']:
            target = self.root / filename
            path = ticket / filename
            path.rename(target)
            path.symlink_to(target)
            result = deliver_ticket(ticket, None, manual=True)
            self.assertEqual(result['state'], 'pending')
            self.assertIn('symlink', result['reason'])
            path.unlink()
            target.rename(path)
        self.assertEqual(self.source.read_bytes(), before)

    def test_hook_cli_invalid_stdin_exits_quietly_and_retains_pending(self):
        ticket = self.prepare()
        result = subprocess.run([sys.executable, '-I', str(ROOT / 'tools/run_runtime_adapter.py'),
                                 'hook', '--ticket', str(ticket)], input='malformed', text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {})
        self.assertIn('pending', result.stderr)
        self.assertEqual(ticket_status(ticket)['reason'], 'missing-or-mismatched-session')

    def test_install_preview_apply_exact_rollback_and_later_edit_guard(self):
        for runtime in ['codex', 'claude-code']:
            config = self.root / runtime / 'settings.json'
            config.parent.mkdir()
            before = '{ "custom": true, "hooks": {"Stop":[{"hooks":[{"type":"command","command":"existing"}]}]}}\n'
            before = before.replace('\n', '\r\n')
            config.write_bytes(before.encode())
            receipt = self.root / (runtime + '-receipt.json')
            preview = configure_hooks(config, runtime, 'reviewed command', receipt)
            self.assertEqual(config.read_bytes(), before.encode())
            self.assertFalse(receipt.exists())
            self.assertIn('existing', preview['after'])
            configure_hooks(config, runtime, 'reviewed command', receipt, apply=True)
            after = config.read_text()
            config.write_text(after + '\n')
            with self.assertRaises(RecordError):
                rollback_hooks(receipt)
            self.assertEqual(config.read_text(), after + '\n')
            config.write_text(after)
            self.assertEqual(rollback_hooks(receipt)['status'], 'restored')
            self.assertEqual(config.read_bytes(), before.encode())
            self.assertEqual(rollback_hooks(receipt)['status'], 'already-restored')

    def test_new_config_rollback_and_existing_receipt_refusal(self):
        config, receipt = self.root / 'new.json', self.root / 'receipt.json'
        configure_hooks(config, 'codex', 'reviewed', receipt, apply=True)
        with self.assertRaises(RecordError):
            configure_hooks(config, 'codex', 'reviewed', receipt, apply=True)
        rollback_hooks(receipt)
        self.assertFalse(config.exists())

    def test_probe_is_not_native_certification_and_command_quotes_paths(self):
        with patch('project_record.runtime_adapters.shutil.which', return_value=None):
            result = inspect_runtime('codex')
        self.assertEqual(result['status'], 'not-installed')
        self.assertFalse(result['nativeTriggerVerified'])
        with patch('project_record.runtime_adapters.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'codex-cli 1.2.3', '')):
            self.assertFalse(inspect_runtime('codex')['nativeTriggerVerified'])
        import shlex
        self.assertEqual(shlex.split(hook_command(Path('/tmp/a b'), ROOT, Path(sys.executable)))[-1], '/tmp/a b')
