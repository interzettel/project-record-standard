from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from project_record.agents import install_skills
from project_record.core import RecordError


class AgentInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'kit'
        self.target = self.root / 'project'
        self.target.mkdir()
        (self.source / 'skills/example/agents').mkdir(parents=True)
        (self.source / 'skills/example/SKILL.md').write_text('---\nname: example\ndescription: Use when tracking work.\n---\n\n# Example\n')
        (self.source / 'skills/example/agents/openai.yaml').write_text('interface:\n  display_name: "Example"\n')
        (self.source / 'skills/manifest.json').write_text(json.dumps({'schemaVersion': 1, 'suiteVersion': '0.3.0', 'contractVersion': '0.2.0', 'skills': ['example']}))

    def test_preview_writes_nothing_and_apply_is_idempotent_preserving_instructions(self):
        original = b'# Loomglass\r\n\r\nPreserve burgundy and serif type.\r\n'
        instructions = self.target / 'AGENTS.md'
        instructions.write_bytes(original)
        preview = install_skills(self.source, self.target)
        self.assertFalse(preview['written'])
        self.assertEqual(instructions.read_bytes(), original)
        self.assertFalse((self.target / '.agents').exists())
        applied = install_skills(self.source, self.target, apply=True)
        self.assertTrue(applied['written'])
        self.assertTrue(instructions.read_bytes().startswith(original))
        self.assertIn(b'.agents/skills/example/SKILL.md', instructions.read_bytes())
        installed = instructions.read_bytes()
        repeated = install_skills(self.source, self.target, apply=True)
        self.assertEqual(repeated['changes'], [])
        self.assertEqual(instructions.read_bytes(), installed)
        receipt = json.loads((self.target / '.project-record/agent-installation.json').read_text())
        self.assertEqual(receipt['files']['.agents/skills/example/SKILL.md'], sha256((self.source / 'skills/example/SKILL.md').read_bytes()).hexdigest())

    def test_foreign_file_collision_fails_before_any_other_write(self):
        existing = self.target / '.agents/skills/example/SKILL.md'
        existing.parent.mkdir(parents=True)
        existing.write_text('Human instructions')
        with self.assertRaises(RecordError):
            install_skills(self.source, self.target, apply=True)
        self.assertEqual(existing.read_text(), 'Human instructions')
        self.assertFalse((self.target / 'AGENTS.md').exists())
        self.assertFalse((existing.parent / 'agents').exists())

    def test_upgrade_requires_opt_in_and_unmodified_owned_files(self):
        install_skills(self.source, self.target, apply=True)
        source = self.source / 'skills/example/SKILL.md'
        source.write_text(source.read_text() + '\nUpdated reference.\n')
        with self.assertRaises(RecordError):
            install_skills(self.source, self.target, apply=True)
        install_skills(self.source, self.target, apply=True, upgrade=True)
        target = self.target / '.agents/skills/example/SKILL.md'
        self.assertEqual(target.read_bytes(), source.read_bytes())
        target.write_text('Local human edit')
        with self.assertRaises(RecordError):
            install_skills(self.source, self.target, apply=True, upgrade=True)
        self.assertEqual(target.read_text(), 'Local human edit')

    def test_symlink_escape_and_unrecognized_instruction_markers_fail(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.target / '.agents').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(RecordError):
            install_skills(self.source, self.target, apply=True)
        self.assertEqual(list(outside.iterdir()), [])
        (self.target / '.agents').unlink()
        (self.target / 'AGENTS.md').write_text('<!-- project-record:agents:start -->\nA local section without receipt.\n<!-- project-record:agents:end -->\n')
        with self.assertRaises(RecordError):
            install_skills(self.source, self.target, apply=True)

    def test_local_instruction_edits_and_unknown_files_survive_upgrade(self):
        install_skills(self.source, self.target, apply=True)
        instructions = self.target / 'AGENTS.md'
        instructions.write_bytes(b'# Local rules\n\n' + instructions.read_bytes() + b'\nKeep this after the section.\n')
        extra = self.target / '.agents/skills/example/local.txt'
        extra.write_text('Local reference')
        install_skills(self.source, self.target, apply=True, upgrade=True)
        self.assertTrue(instructions.read_bytes().startswith(b'# Local rules\n\n'))
        self.assertTrue(instructions.read_bytes().endswith(b'\nKeep this after the section.\n'))
        self.assertEqual(extra.read_text(), 'Local reference')

    def test_source_manifest_path_escape_is_rejected(self):
        manifest = self.source / 'skills/manifest.json'
        value = json.loads(manifest.read_text())
        value['skills'] = ['../outside']
        manifest.write_text(json.dumps(value))
        with self.assertRaises(RecordError):
            install_skills(self.source, self.target, apply=True)

    def test_temporary_collision_is_checked_before_writing_any_skill(self):
        temporary = self.target / '.agents/skills/example/agents/openai.yaml.project-record-tmp'
        temporary.parent.mkdir(parents=True)
        temporary.write_text('Human file')
        with self.assertRaises(RecordError):
            install_skills(self.source, self.target, apply=True)
        self.assertFalse((self.target / '.agents/skills/example/SKILL.md').exists())
        self.assertEqual(temporary.read_text(), 'Human file')

    def test_interrupted_matching_install_resumes_without_receipt_or_duplicate_rules(self):
        install_skills(self.source, self.target, apply=True)
        rules = (self.target / 'AGENTS.md').read_bytes()
        (self.target / '.project-record/agent-installation.json').unlink()
        (self.target / '.agents/skills/example/agents/openai.yaml').unlink()
        install_skills(self.source, self.target, apply=True)
        self.assertEqual((self.target / 'AGENTS.md').read_bytes(), rules)
        self.assertEqual(install_skills(self.source, self.target, apply=True)['changes'], [])


    def test_changed_owned_rules_need_upgrade_even_when_skill_suite_bytes_match(self):
        from unittest.mock import patch
        from project_record.agents import START, END
        legacy = START + b'\nHistorical owned rules\n' + END
        with patch('project_record.agents._rules', return_value=legacy):
            install_skills(self.source, self.target, apply=True)
        old_receipt = (self.target / '.project-record/agent-installation.json').read_bytes()
        old_instructions = (self.target / 'AGENTS.md').read_bytes()
        with self.assertRaisesRegex(RecordError, 'upgrade'):
            install_skills(self.source, self.target)
        self.assertEqual((self.target / 'AGENTS.md').read_bytes(), old_instructions)
        self.assertEqual((self.target / '.project-record/agent-installation.json').read_bytes(), old_receipt)
        install_skills(self.source, self.target, apply=True, upgrade=True)
        self.assertEqual(install_skills(self.source, self.target)['changes'], [])



class ExecutionAssessmentTests(unittest.TestCase):
    def setUp(self):
        from project_record.adapters import load_config
        from project_record.execution import select_work, check_alignment
        from copy import deepcopy
        self.copy = deepcopy
        self.select = select_work
        self.align = check_alignment
        self.fixture = Path(__file__).resolve().parent / 'fixtures/execution'
        self.record = load_config(self.fixture / 'projects.json')[0]
        self.profile = json.loads((self.fixture / 'profile.json').read_text())
        self.issues = json.loads((self.fixture / 'issues.json').read_text())

    def selection(self, profile=None, **kwargs):
        return self.select(self.record, profile or self.profile,
                           current_source_sha256=self.record['source']['sha256'],
                           as_of='2026-10-30', **kwargs)

    def alignment(self, issues=None, **kwargs):
        return self.align(self.record, self.profile, self.issues if issues is None else issues,
                          as_of='2026-10-30', **kwargs)

    def test_selects_existing_eligible_leaf_and_names_canonical_start_contract(self):
        before = self.copy(self.record)
        result = self.selection()
        selected = result['selected']
        self.assertEqual(selected['leafId'], 'EX-NEXT')
        self.assertEqual(selected['issueUrl'], 'https://github.com/interzettel/project-record-standard/issues/31')
        self.assertEqual(selected['milestoneId'], 'M5')
        self.assertEqual(selected['criterion'], self.record['items'][2]['criterion'])
        self.assertEqual(selected['dependencyStatus'], [])
        rows = {x['leafId']: x for x in result['candidates']}
        self.assertEqual(rows['EX-BLOCK']['status'], 'blocked')
        self.assertEqual(rows['EX-WAIT']['status'], 'unknown')
        self.assertEqual(rows['EX-GAP']['status'], 'unknown')
        self.assertEqual(rows['EX-DONE']['status'], 'ineligible')
        self.assertEqual(rows['EX-LATER']['status'], 'ineligible')
        self.assertEqual(result['metrics']['work']['done'], 1)
        self.assertEqual(result['metrics']['work']['total'], 5)
        self.assertEqual(self.record, before)
        self.assertFalse(result['written'])
        self.assertFalse(result['applicationAuthorized'])

    def test_conditions_are_required_and_holds_capacity_authority_prevent_selection(self):
        for change in [dict(authorized=False), dict(hold=True), dict(capacity=False), dict(authorized=None)]:
            profile = self.copy(self.profile)
            profile['conditions']['EX-NEXT'].update(change)
            with self.subTest(change=change):
                self.assertIsNone(self.selection(profile)['selected'])
        profile = self.copy(self.profile)
        profile['conditions'].pop('EX-NEXT')
        self.assertIsNone(self.selection(profile)['selected'])

    def test_changed_missing_or_stale_source_cannot_supply_current_eligibility(self):
        for current, date in [(None, '2026-10-30'), ('f' * 64, '2026-10-30'),
                              (self.record['source']['sha256'], '2026-11-15')]:
            with self.subTest(current=current, date=date):
                result = self.select(self.record, self.profile, current_source_sha256=current, as_of=date)
                self.assertIsNone(result['selected'])
                self.assertEqual(result['source'], self.record['source'])
        profile = self.copy(self.profile)
        profile['sourceSha256'] = 'e' * 64
        self.assertIsNone(self.selection(profile)['selected'])

    def test_completion_edge_does_not_become_a_start_prerequisite_or_done_credit(self):
        profile = self.copy(self.profile)
        profile['dependencyKinds']['EX-WAIT']['EX-GAP'] = 'completion'
        result = self.selection(profile)
        self.assertEqual(result['selected']['leafId'], 'EX-WAIT')
        self.assertEqual(result['selected']['dependencyStatus'][0]['meaning'], 'completion')
        self.assertEqual(result['metrics']['work']['done'], 1)
        self.assertEqual(self.record['items'][1]['dependsOn'], ['EX-GAP'])
        profile['dependencyKinds']['EX-WAIT'].pop('EX-GAP')
        self.assertEqual(self.selection(profile)['selected']['leafId'], 'EX-NEXT')

    def test_offroad_duplicate_and_incomplete_orders_are_rejected(self):
        for order in [self.profile['order'] + ['OFFROAD'], self.profile['order'][:-1],
                      self.profile['order'] + ['EX-NEXT']]:
            profile = self.copy(self.profile)
            profile['order'] = order
            with self.subTest(order=order), self.assertRaises(RecordError):
                self.selection(profile)
        profile = self.copy(self.profile)
        profile['conditions']['OFFROAD'] = dict(authorized=True)
        with self.assertRaises(RecordError):
            self.selection(profile)

    def test_stale_issue_milestone_and_artifact_links_are_reported_without_native_inference(self):
        result = self.alignment()
        findings = {(x['code'], x['subject']) for x in result['findings']}
        self.assertIn(('issue-leaf-link-missing-or-stale', 'EX-WAIT'), findings)
        self.assertIn(('issue-milestone-link-missing-or-stale', 'EX-NEXT'), findings)
        self.assertIn(('configured-obsolete-artifact-reference', 'EX-NEXT'), findings)
        self.assertIn(('unmapped-observed-issue', 'https://github.com/interzettel/project-record-standard/issues/9'), findings)
        self.assertFalse(any('native-milestone' in x['code'] for x in result['findings']))
        self.assertEqual(result['issueObservation'], self.issues)
        self.assertEqual(result['metrics']['work']['total'], 5)
        self.assertFalse(result['written'])

    def test_missing_remote_is_unknown_unless_fresh_complete_coverage_declares_absence(self):
        absent = self.align(self.record, self.profile, None, as_of='2026-10-30')
        self.assertIn('issue-observation-unavailable', [x['code'] for x in absent['findings']])
        partial = self.copy(self.issues)
        partial.update(complete=False, issues=[])
        report = self.alignment(partial)
        self.assertTrue(all(x['status'] == 'unknown' for x in report['findings']))
        partial['complete'] = True
        self.assertIn('issue-missing-from-complete-snapshot', [x['code'] for x in self.alignment(partial)['findings']])
        old = self.align(self.record, self.profile, partial, as_of='2026-11-15')
        self.assertNotIn('issue-missing-from-complete-snapshot', [x['code'] for x in old['findings']])
        self.assertEqual(old['source']['observedOn'], '2026-10-30')

    def test_explicit_native_mapping_does_not_mask_conflicting_canonical_body_mapping(self):
        profile = self.copy(self.profile)
        profile['nativeMilestones']['M5'] = 1
        issues = self.copy(self.issues)
        for row in issues['issues']:
            row['nativeMilestone'] = 1
        result = self.align(self.record, profile, issues, as_of='2026-10-30')
        self.assertIn(('issue-milestone-link-missing-or-stale', 'EX-NEXT'),
                      {(x['code'], x['subject']) for x in result['findings']})
        issues['issues'][2]['milestoneId'] = None
        result = self.align(self.record, profile, issues, as_of='2026-10-30')
        self.assertNotIn(('issue-milestone-link-missing-or-stale', 'EX-NEXT'),
                         {(x['code'], x['subject']) for x in result['findings']})

    def test_accepted_without_applicable_evidence_is_reported_without_rewriting_history(self):
        record = self.copy(self.record)
        record['milestones'][0]['sourceAccepted'] = True
        result = self.align(record, self.profile, self.issues, as_of='2026-10-30')
        self.assertIn('accepted-outcome-evidence-unassessed', [x['code'] for x in result['findings']])
        profile = self.copy(self.profile)
        profile['milestonePolicies'] = {'M5': dict(policy=dict(allOf=['owner-review']), revision='a' * 40)}
        result = self.align(record, profile, self.issues, as_of='2026-10-30')
        self.assertIn('accepted-outcome-policy-unsatisfied', [x['code'] for x in result['findings']])
        self.assertIs(record['milestones'][0]['sourceAccepted'], True)
        self.assertEqual(result['metrics']['milestones']['done'], 1)

    def test_actual_marked_readme_drift_is_read_only_and_unmarked_prose_is_preserved(self):
        from project_record.build import render_readme
        from project_record.core import summarize
        root = Path(__file__).resolve().parents[1]
        theme = json.loads((root / 'examples/themes/standard.json').read_text())
        _, module = render_readme(summarize(self.record), theme)
        with tempfile.TemporaryDirectory() as folder:
            readme = Path(folder) / 'README.md'
            original = '# Keep local branding\n\n' + module.replace('1/5', '0/5')
            readme.write_text(original)
            result = self.alignment(readme=readme, expected_module=module)
            self.assertIn('readme-generated-region-drift', [x['code'] for x in result['findings']])
            self.assertEqual(readme.read_text(), original)
            readme.write_text('# Keep local branding\n\n' + module)
            result = self.alignment(readme=readme, expected_module=module)
            self.assertNotIn('readme-generated-region-drift', [x['code'] for x in result['findings']])
            readme.unlink()
            result = self.alignment(readme=readme, expected_module=module)
            self.assertIn('readme-unavailable', [x['code'] for x in result['findings']])

    def test_duplicate_snapshots_bad_profile_values_and_future_dates_are_rejected(self):
        issues = self.copy(self.issues)
        issues['issues'].append(self.copy(issues['issues'][0]))
        with self.assertRaises(RecordError):
            self.alignment(issues)
        profile = self.copy(self.profile)
        profile['conditions']['EX-NEXT']['authorized'] = 1
        with self.assertRaises(RecordError):
            self.selection(profile)
        with self.assertRaises(RecordError):
            self.select(self.record, self.profile, current_source_sha256=None, as_of='2026-10-29')


if __name__ == '__main__':
    unittest.main()
