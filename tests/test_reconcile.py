from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for p in (ROOT / 'tests/fixtures/reconcile').iterdir():
            shutil.copyfile(p, self.root / p.name)
        self.config = self.root / 'projects.json'
        self.source = self.root / 'ledger.json'
        self.profile = dict(reconcileVersion=1, projectId='synthetic-reconcile',
                            manifest=str(self.config), journal=str(self.root / 'journal'),
                            output=str(self.root / 'generated'), audience='public',
                            authority=dict(source='synthetic:adopted-host-grant', routineRecording=True),
                            workPolicies={'WORK-1': dict(allOf=['implementation', 'test'])},
                            scopeAdmission={})
        self.event = dict(eventVersion=1, eventId='session-1:result-1', projectId='synthetic-reconcile',
                          workItemId='WORK-1', sourceSha256=self.digest(self.source),
                          manifestSha256=self.digest(self.config), artifactRevision='a' * 40,
                          result='completed', producer='synthetic-worker', source='synthetic:session',
                          observedOn='2026-10-30', summary='Implemented and checked the synthetic criterion.',
                          receipts=[dict(kind=k, subject='WORK-1', revision='a' * 40,
                                         result='passed', source='synthetic:' + k) for k in ['implementation', 'test']],
                          discoveries=[])

    def digest(self, path):
        return sha256(path.read_bytes()).hexdigest()

    def run_event(self, event=None, apply=True):
        from project_record.reconcile import reconcile
        return reconcile(self.event if event is None else event, self.profile, apply=apply)

    def test_preview_then_apply_updates_one_leaf_and_views_with_no_owner_acceptance(self):
        before = self.source.read_bytes()
        preview = self.run_event(apply=False)
        self.assertEqual(preview['status'], 'preview')
        self.assertEqual(self.source.read_bytes(), before)
        self.assertFalse((self.root / 'journal').exists())
        result = self.run_event()
        self.assertEqual(result['status'], 'applied', result)
        self.assertEqual(result['metrics']['after']['work']['done'], 1)
        self.assertEqual(result['metrics']['after']['milestones']['done'], 0)
        self.assertTrue((Path(result['output']) / 'synthetic-reconcile/record.json').is_file())
        config = json.loads(self.config.read_text())['projects'][0]
        self.assertEqual((self.root / config['previousSourceFile']).read_bytes(), before)

    def test_replay_is_idempotent_and_same_id_with_other_payload_conflicts(self):
        first = self.run_event()
        self.assertEqual(first['status'], 'applied', first)
        snapshot = self.source.read_bytes(), self.config.read_bytes()
        self.assertEqual(self.run_event()['status'], 'duplicate')
        self.assertEqual((self.source.read_bytes(), self.config.read_bytes()), snapshot)
        changed = deepcopy(self.event)
        changed['summary'] = 'Another event with a reused ID'
        self.assertEqual(self.run_event(changed)['status'], 'conflict')
        self.assertEqual((self.source.read_bytes(), self.config.read_bytes()), snapshot)

    def test_wrong_revision_missing_proof_and_stale_source_never_complete(self):
        for change, expected in [('wrong', 'rejected'), ('missing', 'held'), ('stale', 'conflict')]:
            event = deepcopy(self.event)
            if change == 'wrong':
                event['receipts'][1]['revision'] = 'b' * 40
            elif change == 'missing':
                event['receipts'] = []
            else:
                event['sourceSha256'] = 'f' * 64
            before = self.source.read_bytes()
            with self.subTest(change=change):
                result = self.run_event(event)
                self.assertEqual(result['status'], expected, result)
                self.assertEqual(self.source.read_bytes(), before)

    def test_failed_cancelled_and_blocked_results_cannot_award_done(self):
        for result in ['failed', 'cancelled', 'blocked']:
            event = deepcopy(self.event)
            event['result'] = result
            with self.subTest(result=result):
                report = self.run_event(event, apply=False)
                self.assertEqual(report['status'], 'preview', report)
                self.assertEqual(report['metrics']['after']['work']['done'], 0)

    def test_unknown_authority_cannot_write_or_be_granted_by_event(self):
        self.profile['authority']['routineRecording'] = None
        self.assertEqual(self.run_event()['status'], 'held')
        self.event['authority'] = True
        self.assertEqual(self.run_event()['exitCode'], 2)

    def test_admitted_scope_has_origin_and_count_effect_while_other_scope_stays_proposed(self):
        item = dict(id='NEW-1', title='Investigate the encountered constraint', groupId='G',
                    milestoneId='M', required=True, dependsOn=[], criterion='Produce a sourced finding', kind='research')
        self.event['discoveries'] = [dict(item=item, origin='WORK-1', reason='Actual synthetic constraint', source='synthetic:failure')]
        preview = self.run_event(apply=False)
        self.assertEqual(preview['discoveries'][0]['disposition'], 'proposed')
        self.assertEqual(preview['metrics']['after']['work']['total'], 1)
        self.profile['scopeAdmission']['NEW-1'] = dict(required=True, groupId='G', milestoneId='M', source='synthetic:bounded-admission')
        report = self.run_event()
        self.assertEqual(report['status'], 'applied', report)
        self.assertEqual(report['metrics']['after']['work']['total'], 2)
        self.assertEqual(report['metrics']['after']['work']['done'], 1)
        new = json.loads(self.source.read_text())['items'][1]
        self.assertEqual(new['state'], 'backlog')
        self.assertEqual(new['discovery']['origin'], 'WORK-1')
        self.assertEqual(new['discovery']['admissionSource'], 'synthetic:bounded-admission')

    def test_scope_grant_cannot_be_reused_for_other_membership_or_duplicate_id(self):
        self.event['discoveries'] = [dict(item=dict(id='WORK-1'), origin='WORK-1', reason='Duplicate', source='synthetic:gap')]
        self.assertEqual(self.run_event()['status'], 'conflict')
        self.event['discoveries'][0]['item'] = dict(id='NEW-1', required=False, groupId='G', milestoneId='M')
        self.profile['scopeAdmission']['NEW-1'] = dict(required=True, groupId='G', milestoneId='M', source='synthetic:grant')
        self.assertEqual(self.run_event()['status'], 'conflict')
        self.assertEqual(json.loads(self.source.read_text())['items'][0]['state'], 'active')

    def test_each_interrupted_phase_resumes_without_duplicate_credit(self):
        from unittest.mock import patch
        for stage in ['prepared', 'snapshot', 'source', 'manifest', 'views', 'readme', 'committed']:
            with self.subTest(stage=stage):
                with tempfile.TemporaryDirectory() as folder:
                    case = ReconciliationTests('test_preview_then_apply_updates_one_leaf_and_views_with_no_owner_acceptance')
                    case.setUp()
                    try:
                        def interrupt(current):
                            if current == stage:
                                raise OSError('Injected interruption at ' + stage)
                        with patch('project_record.reconcile._checkpoint', side_effect=interrupt):
                            first = case.run_event()
                        self.assertEqual(first['status'], 'recoverable', first)
                        result = case.run_event()
                        self.assertIn(result['status'], ['applied', 'duplicate'], result)
                        self.assertEqual(result['metrics']['after']['work']['done'], 1)
                        self.assertEqual(case.run_event()['status'], 'duplicate')
                        self.assertEqual(len(json.loads(case.source.read_text())['items']), 1)
                    finally:
                        case.doCleanups()

    def test_interrupted_transaction_blocks_other_events_and_preserves_newer_source_edits(self):
        from unittest.mock import patch
        def interrupt(stage):
            if stage == 'source':
                raise OSError('After first authored write')
        with patch('project_record.reconcile._checkpoint', side_effect=interrupt):
            self.assertEqual(self.run_event()['status'], 'recoverable')
        other = deepcopy(self.event)
        other['eventId'] = 'another-session'
        self.assertEqual(self.run_event(other)['status'], 'held')
        newer = self.source.read_bytes() + b'\n'
        self.source.write_bytes(newer)
        self.assertEqual(self.run_event()['status'], 'conflict')
        self.assertEqual(self.source.read_bytes(), newer)

    def test_manifest_and_theme_changes_are_not_overwritten_on_recovery(self):
        from unittest.mock import patch
        def interrupt(stage):
            if stage == 'prepared':
                raise OSError('Prepared only')
        with patch('project_record.reconcile._checkpoint', side_effect=interrupt):
            self.assertEqual(self.run_event()['status'], 'recoverable')
        original = self.source.read_bytes()
        self.config.write_bytes(self.config.read_bytes() + b'\n')
        self.assertEqual(self.run_event()['status'], 'conflict')
        self.assertEqual(self.source.read_bytes(), original)

    def test_symlink_and_mixed_output_targets_fail_without_source_writes(self):
        self.profile['output'] = str(self.root / 'output-link')
        (self.root / 'output-link').symlink_to(self.root, target_is_directory=True)
        self.assertEqual(self.run_event()['exitCode'], 2)
        self.assertEqual(json.loads(self.source.read_text())['items'][0]['state'], 'active')

    def test_marked_readme_preserves_authored_prose_and_crlf(self):
        path = self.root / 'README.md'
        original = b'Authored intro\r\n<!-- project-record:start -->\r\nold\r\n<!-- project-record:end -->\r\nAuthored tail\r\n'
        path.write_bytes(original)
        self.profile['readme'] = str(path)
        report = self.run_event()
        self.assertEqual(report['status'], 'applied', report)
        self.assertTrue(path.read_bytes().startswith(b'Authored intro\r\n'))
        self.assertTrue(path.read_bytes().endswith(b'\r\nAuthored tail\r\n'))
        self.assertIn(b'1/1', path.read_bytes())

    def test_cli_preview_and_apply_use_same_engine_and_invalid_input_is_structured(self):
        import os
        import subprocess
        import sys
        event, profile = self.root / 'event.json', self.root / 'profile.json'
        event.write_text(json.dumps(self.event))
        profile.write_text(json.dumps(self.profile))
        command = [sys.executable, '-m', 'project_record', 'reconcile', '--event', str(event), '--profile', str(profile)]
        preview = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')), capture_output=True, text=True)
        self.assertEqual(json.loads(preview.stdout), self.run_event(apply=False))
        result = subprocess.run(command + ['--apply'], cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)['status'], 'applied')
        event.write_text('{broken')
        result = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')), capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'invalid-input')

    def test_actual_process_death_releases_lock_and_resumes_source_and_committed_boundaries(self):
        import os
        import subprocess
        import sys
        for stage in ['source', 'committed']:
            with self.subTest(stage=stage):
                case = ReconciliationTests('test_preview_then_apply_updates_one_leaf_and_views_with_no_owner_acceptance')
                case.setUp()
                try:
                    event, profile = case.root / 'event.json', case.root / 'profile.json'
                    event.write_text(json.dumps(case.event)); profile.write_text(json.dumps(case.profile))
                    script = "import os,json; from pathlib import Path; import project_record.reconcile as r; r._checkpoint=lambda s: os._exit(73) if s == " + repr(stage) + " else None; r.reconcile(json.loads(Path(" + repr(str(event)) + ").read_text()),json.loads(Path(" + repr(str(profile)) + ").read_text()),apply=True)"
                    result = subprocess.run([sys.executable, '-c', script], env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')), capture_output=True, text=True)
                    self.assertEqual(result.returncode, 73, result.stderr)
                    resumed = case.run_event()
                    self.assertIn(resumed['status'], ['applied', 'duplicate'], resumed)
                    self.assertEqual(resumed['metrics']['after']['work']['done'], 1)
                finally:
                    case.doCleanups()

    def test_actual_second_process_cannot_write_while_cooperating_lock_is_held(self):
        import os
        import subprocess
        import sys
        from project_record.reconcile import _lock
        event, profile = self.root / 'event.json', self.root / 'profile.json'
        event.write_text(json.dumps(self.event)); profile.write_text(json.dumps(self.profile))
        with _lock(self.config):
            result = subprocess.run([sys.executable, '-m', 'project_record', 'reconcile', '--event', str(event), '--profile', str(profile), '--apply'],
                                    env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')), capture_output=True, text=True)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'held')
        self.assertEqual(json.loads(self.source.read_text())['items'][0]['state'], 'active')

    def test_missing_journal_after_marker_creation_can_resume_without_manual_reconstruction(self):
        from unittest.mock import patch
        import project_record.reconcile as module
        original = module._atomic
        def fail_journal(path, data):
            if path.parent == self.root / 'journal':
                raise OSError('Crash before prepared journal')
            original(path, data)
        with patch('project_record.reconcile._atomic', side_effect=fail_journal):
            report = self.run_event()
        self.assertEqual(report['status'], 'recoverable')
        self.assertIsNone(report['written'])
        self.assertEqual(json.loads(self.source.read_text())['items'][0]['state'], 'active')
        self.assertEqual(self.run_event()['status'], 'applied')

    def test_corrupted_journal_is_retained_and_cannot_rewrite_source(self):
        from unittest.mock import patch
        def interrupt(stage):
            if stage == 'prepared':
                raise OSError('Stop before source')
        with patch('project_record.reconcile._checkpoint', side_effect=interrupt):
            self.run_event()
        journal = next((self.root / 'journal').glob('*.json'))
        content = json.loads(journal.read_text())
        content['plan']['files'][1]['after'] = '{}'
        journal.write_text(json.dumps(content))
        old = self.source.read_bytes()
        self.assertEqual(self.run_event()['status'], 'conflict')
        self.assertEqual(self.source.read_bytes(), old)
        self.assertEqual(json.loads(journal.read_text())['plan']['files'][1]['after'], '{}')

    def test_edit_between_planning_and_commit_is_detected_without_overwrite(self):
        from unittest.mock import patch
        newer = self.source.read_bytes() + b'\n'
        def edit(stage):
            if stage == 'prepared':
                self.source.write_bytes(newer)
        with patch('project_record.reconcile._checkpoint', side_effect=edit):
            report = self.run_event()
        self.assertEqual(report['status'], 'conflict')
        self.assertTrue(report['recoveryPending'])
        self.assertEqual(self.source.read_bytes(), newer)

    def test_negative_events_are_recorded_without_cancelling_scope_or_accepting_outcomes(self):
        for outcome in ['failed', 'cancelled', 'blocked']:
            with self.subTest(outcome=outcome):
                case = ReconciliationTests('test_preview_then_apply_updates_one_leaf_and_views_with_no_owner_acceptance')
                case.setUp()
                try:
                    case.event['result'] = outcome
                    report = case.run_event()
                    self.assertEqual(report['status'], 'applied', report)
                    leaf = json.loads(case.source.read_text())['items'][0]
                    self.assertEqual(leaf['state'], 'active')
                    self.assertEqual(leaf['blocked'], outcome == 'blocked')
                    self.assertEqual(leaf['evidence'][-1]['outcome'], outcome)
                    self.assertEqual(report['metrics']['after']['work']['done'], 0)
                    self.assertEqual(report['metrics']['after']['work']['total'], 1)
                    self.assertEqual(report['metrics']['after']['milestones']['done'], 0)
                finally:
                    case.doCleanups()

    def test_later_work_is_preserved_when_an_old_committed_event_is_replayed(self):
        raw = json.loads(self.source.read_text())
        second = deepcopy(raw['items'][0]); second['id'] = 'WORK-2'
        raw['items'].append(second)
        self.source.write_text(json.dumps(raw))
        self.event['sourceSha256'] = self.digest(self.source)
        self.profile['workPolicies']['WORK-2'] = deepcopy(self.profile['workPolicies']['WORK-1'])
        first = self.run_event()
        self.assertEqual(first['status'], 'applied', first)
        second_event = deepcopy(self.event)
        second_event.update(eventId='second-work', workItemId='WORK-2', sourceSha256=self.digest(self.source), manifestSha256=self.digest(self.config))
        for receipt in second_event['receipts']:
            receipt['subject'] = 'WORK-2'
        report = self.run_event(second_event)
        self.assertEqual(report['status'], 'applied', report)
        self.assertEqual(report['metrics']['after']['work']['done'], 2)
        newer = self.source.read_bytes(), self.config.read_bytes()
        replay = self.run_event()
        self.assertEqual(replay['status'], 'duplicate')
        self.assertIn('historical', replay['reason'])
        self.assertEqual((self.source.read_bytes(), self.config.read_bytes()), newer)

    def test_private_source_cannot_be_written_as_public_projection(self):
        config = json.loads(self.config.read_text())
        config['projects'][0]['project']['visibility'] = 'private'
        self.config.write_text(json.dumps(config))
        self.event['manifestSha256'] = self.digest(self.config)
        old = self.source.read_bytes()
        report = self.run_event()
        self.assertEqual(report['status'], 'rejected', report)
        self.assertEqual(self.source.read_bytes(), old)
        self.assertFalse((self.root / 'journal').exists())

    def test_invalid_versions_unknown_event_fields_and_nonboolean_apply_never_write(self):
        from project_record.reconcile import reconcile
        for field, value in [('eventVersion', True), ('acceptMilestone', True), ('artifactRevision', 'main')]:
            event = deepcopy(self.event); event[field] = value
            self.assertEqual(self.run_event(event)['status'], 'invalid-input')
        self.assertEqual(reconcile(self.event, self.profile, apply='yes')['exitCode'], 2)
        self.assertEqual(json.loads(self.source.read_text())['items'][0]['state'], 'active')
