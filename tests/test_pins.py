"""Verifies read-only expected pins against real disposable installations."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from project_record.agents import RECEIPT, install_skills
from project_record.core import RecordError
from project_record.pins import assess_update, capture_pin, validate_pin, verify_installation


class PinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / 'host'
        self.kit = self.target / 'tools/prs'
        (self.kit / 'skills/example').mkdir(parents=True)
        (self.kit / 'skills/example/SKILL.md').write_text('---\nname: example\ndescription: Synthetic pin fixture\n---\n# Example\n')
        manifest = {'schemaVersion':1, 'suiteVersion':'0.4.1', 'contractVersion':'0.2.0', 'skills':['example']}
        (self.kit / 'skills/manifest.json').write_text(json.dumps(manifest))
        (self.kit / 'pyproject.toml').write_text('[project]\nname = "synthetic"\nversion = "0.4.1"\nrequires-python = ">=3.10"\n')
        (self.kit / 'policy.md').write_text('Synthetic policy; not an actual approval\n')
        install_skills(self.kit, self.target, apply=True)
        self.pin = capture_pin(self.kit, ['policy.md'], 'a' * 40, 'tools/prs', 'b' * 64, 'policy.md',
                               runtime={'python':{'versions':['3.15.2'], 'evidence':'synthetic test profile'}})

    def verify(self, **kwargs):
        return verify_installation(self.pin, self.target, **kwargs)

    def test_clean_bytes_do_not_authenticate_origin_or_grant_upgrades(self):
        before = {str(p.relative_to(self.target)):p.read_bytes() for p in self.target.rglob('*') if p.is_file()}
        value = self.verify()
        self.assertEqual(value['bytes'], 'selected-bytes-match')
        self.assertEqual(value['provenance'], 'not-supplied')
        self.assertFalse(value['publisherAuthenticated'])
        self.assertFalse(value['upgradeApplied'])
        self.assertEqual(value['runtime']['python'], 'unknown')
        self.assertEqual(before, {str(p.relative_to(self.target)):p.read_bytes() for p in self.target.rglob('*') if p.is_file()})

    def test_declared_provenance_matches_separately_and_can_conflict(self):
        origin = {'sourceCommit':'a' * 40, 'archiveSha256':'b' * 64, 'source':'synthetic receipt'}
        value = self.verify(provenance=origin)
        self.assertEqual(value['provenance'], 'matches-declared-evidence')
        self.assertFalse(value['publisherAuthenticated'])
        origin['archiveSha256'] = 'c' * 64
        self.assertEqual(self.verify(provenance=origin)['provenance'], 'conflicted')
        self.assertEqual(self.verify(provenance=origin)['bytes'], 'selected-bytes-match')

    def test_mutable_refs_and_inconsistent_expected_hashes_are_rejected(self):
        for value in ['main', 'latest', 'v0.4.1', 'a' * 39]:
            broken = deepcopy(self.pin)
            broken['toolkit']['sourceCommit'] = value
            with self.assertRaises(RecordError):
                verify_installation(broken, self.target)
        broken = deepcopy(self.pin)
        broken['suite']['files']['.agents/skills/example/SKILL.md'] = '0' * 64
        with self.assertRaises(RecordError):
            validate_pin(broken)

    def test_locally_edited_toolkit_policy_and_skill_are_conflicted(self):
        for path in ['tools/prs/policy.md', '.agents/skills/example/SKILL.md']:
            with self.subTest(path=path):
                file = self.target / path
                original = file.read_bytes()
                file.write_text('local edit')
                value = self.verify()
                self.assertEqual(value['bytes'], 'conflicted')
                self.assertIn(path, value['conflicts'])
                file.write_bytes(original)

    def test_missing_receipt_or_file_remains_partial(self):
        receipt = self.target / RECEIPT
        original = receipt.read_bytes()
        receipt.unlink()
        self.assertEqual(self.verify()['bytes'], 'partial')
        receipt.write_bytes(original)
        (self.target / '.agents/skills/example/SKILL.md').unlink()
        self.assertEqual(self.verify()['bytes'], 'partial')

    def test_forged_receipt_cannot_bless_edited_bytes(self):
        file = self.target / '.agents/skills/example/SKILL.md'
        file.write_text('altered')
        path = self.target / RECEIPT
        value = json.loads(path.read_text())
        value['files']['.agents/skills/example/SKILL.md'] = sha256(file.read_bytes()).hexdigest()
        path.write_text(json.dumps(value))
        result = self.verify()
        self.assertEqual(result['bytes'], 'conflicted')
        self.assertIn('installation-receipt', result['conflicts'])

    def test_mixed_suite_and_unexpected_owned_file_conflict(self):
        receipt = self.target / RECEIPT
        data = json.loads(receipt.read_text())
        original = receipt.read_bytes()
        data['suiteVersion'] = '0.5.0'
        receipt.write_text(json.dumps(data))
        self.assertEqual(self.verify()['bytes'], 'conflicted')
        receipt.write_bytes(original)
        (self.target / '.agents/skills/example/untracked.md').write_text('unexpected owned-folder file')
        self.assertEqual(self.verify()['bytes'], 'conflicted')

    def test_project_instructions_outside_owned_region_are_preserved(self):
        file = self.target / 'AGENTS.md'
        file.write_bytes(b'# Project-owned instructions\n' + file.read_bytes())
        self.assertEqual(self.verify()['bytes'], 'selected-bytes-match')
        file.write_bytes(file.read_bytes().replace(b'Project tracking agent rules', b'Edited tracking rules'))
        self.assertEqual(self.verify()['bytes'], 'conflicted')

    def test_unrelated_user_skill_is_not_claimed_or_scanned(self):
        folder = self.target / '.agents/skills/unrelated'
        folder.mkdir()
        (folder / 'private.md').write_text('unrelated content')
        self.assertEqual(self.verify()['bytes'], 'selected-bytes-match')

    def test_path_escape_and_symlink_are_refused(self):
        broken = deepcopy(self.pin)
        broken['toolkit']['files']['../outside'] = 'a' * 64
        with self.assertRaises(RecordError):
            verify_installation(broken, self.target)
        file = self.target / '.agents/skills/example/SKILL.md'
        file.unlink()
        file.symlink_to(self.kit / 'policy.md')
        self.assertEqual(self.verify()['bytes'], 'conflicted')

    def test_expected_manifest_symlink_is_refused(self):
        file = self.kit / 'skills/manifest.json'
        external = Path(self.temp.name) / 'external.json'
        external.write_bytes(file.read_bytes())
        file.unlink()
        file.symlink_to(external)
        with self.assertRaises(RecordError):
            capture_pin(self.kit, [], 'a' * 40)

    def test_native_version_drift_is_explicit(self):
        file = self.kit / 'pyproject.toml'
        file.write_text(file.read_text().replace('version = "0.4.1"', 'version = "0.5.0"'))
        self.assertIn('native-version', self.verify()['conflicts'])

    def test_runtime_support_and_old_contracts_are_separate_from_bytes(self):
        self.assertEqual(self.verify(observed_runtime={'python':'3.15.2'})['runtime']['python'], 'matches-declared-support')
        result = self.verify(observed_runtime={'python':'3.10.22'})
        self.assertEqual(result['runtime']['python'], 'unsupported')
        self.assertEqual(result['bytes'], 'selected-bytes-match')
        self.pin['recordContractVersion'] = '0.1.0'
        self.assertEqual(self.verify()['recordContract'], 'readable')
        self.pin['recordContractVersion'] = '0.3.0'
        self.assertEqual(self.verify()['recordContract'], 'unsupported')
        self.assertIn('>=3.10', (self.kit / 'pyproject.toml').read_text())

    def test_adapter_support_requires_its_exact_declared_identity(self):
        adapter = {'id':'synthetic', 'version':'1.0.0', 'sourceCommit':'c' * 40,
                   'runtime':{'name':'synthetic-host','version':'2.1.0'}, 'evidence':'synthetic run'}
        self.pin['adapters'] = [adapter]
        self.assertEqual(self.verify()['adapters']['synthetic'], 'unknown')
        self.assertEqual(self.verify(observed_adapters=[adapter])['adapters']['synthetic'], 'matches-declared-support')
        self.assertEqual(self.verify(observed_adapters=[{**adapter,'version':'1.1.0'}])['adapters']['synthetic'], 'conflicted')

    def test_missing_policy_is_not_inferred_as_verified(self):
        self.pin['policy'] = None
        self.assertEqual(self.verify()['policy'], 'not-pinned')

    def test_major_minor_patch_and_security_have_distinct_assessments(self):
        for version, kind in [('1.0.0','major'), ('0.5.0','minor'), ('0.4.2','patch')]:
            result = assess_update('0.4.1', version)
            self.assertEqual(result['change'], kind)
            self.assertFalse(result['applicationAuthorized'])
        defer = {'from':'0.4.1', 'to':'0.4.2', 'reason':'No affected capability; reassess on relevant change'}
        self.assertEqual(assess_update('0.4.1', '0.4.2', deferral=defer)['disposition'], 'deferred-with-reason')
        self.assertEqual(assess_update('0.4.1', '0.4.2', security=True, deferral=defer)['disposition'], 'prioritized-assessment-required')
        self.assertEqual(assess_update('0.4.1', '0.4.3', deferral=defer)['disposition'], 'patch-triage-required')

    def test_prerelease_stabilization_build_metadata_and_downgrade(self):
        self.assertEqual(assess_update('0.4.1', '0.5.0-alpha.1')['disposition'], 'opt-in-only')
        self.assertEqual(assess_update('0.5.0-alpha.2', '0.5.0-alpha.10')['change'], 'prerelease')
        self.assertEqual(assess_update('0.5.0-alpha.1', '0.5.0')['change'], 'stabilization')
        self.assertEqual(assess_update('1.0.0+one', '1.0.0+two')['change'], 'unchanged')
        self.assertEqual(assess_update('1.0.0', '0.5.0')['change'], 'downgrade')
        self.assertEqual(assess_update('0.4.1', '0.4.1', security=True)['disposition'], 'prioritized-assessment-required')
        for invalid in ['latest', '01.2.3', '1.2.3-alpha.01']:
            with self.assertRaises(RecordError):
                assess_update('0.4.1', invalid)

    def test_pin_capture_and_verification_do_not_rewrite_legacy_receipt(self):
        receipt = self.target / RECEIPT
        before = receipt.read_bytes()
        pin_before = deepcopy(self.pin)
        self.verify()
        self.assertEqual(self.pin, pin_before)
        self.assertEqual(before, receipt.read_bytes())
        self.assertEqual(set(json.loads(before)), {'schemaVersion','suiteVersion','contractVersion','suiteDigest','files','rulesSha256'})

    def test_existing_record_readers_and_illustrative_legacy_pin_are_not_migrated(self):
        from project_record.adapters import load_config
        from project_record.core import validate
        root = Path(__file__).resolve().parents[1]
        record = load_config(root / 'examples/projects.json', {'standard'})[0]
        for version in ['0.1.0', '0.2.0']:
            record['contractVersion'] = version
            before = deepcopy(record)
            validate(record)
            self.assertEqual(record, before)
        legacy = {'status':'illustrative-dependency-record-not-a-validated-runtime-format',
                  'toolkit':{'version':'0.4.1'}}
        before = deepcopy(legacy)
        with self.assertRaises(RecordError):
            verify_installation(legacy, self.target)
        self.assertEqual(legacy, before)

    def test_optional_archive_and_explicit_policy_shapes(self):
        self.pin['toolkit'].pop('archiveSha256')
        self.assertEqual(self.verify()['bytes'], 'selected-bytes-match')
        self.pin.pop('policy')
        with self.assertRaises(RecordError):
            self.verify()

    def test_existing_null_or_invalid_schema_receipt_is_conflicted(self):
        path = self.target / RECEIPT
        original = path.read_bytes()
        for value in [None, [], True]:
            path.write_text(json.dumps(value))
            self.assertEqual(self.verify()['bytes'], 'conflicted')
        for version in [True, 1.0]:
            value = json.loads(original)
            value['schemaVersion'] = version
            path.write_text(json.dumps(value))
            self.assertEqual(self.verify()['bytes'], 'conflicted')

    def test_existing_receipt_directory_is_conflicted(self):
        path = self.target / RECEIPT
        path.unlink()
        path.mkdir()
        self.assertEqual(self.verify()['bytes'], 'conflicted')

    def test_selected_skill_directory_replaced_by_file_is_conflicted(self):
        import shutil
        path = self.target / '.agents/skills/example'
        shutil.rmtree(path)
        path.write_text('replacement')
        self.assertEqual(self.verify()['bytes'], 'conflicted')

    def test_equal_prerelease_precedence_reports_no_change(self):
        for available in ['1.0.0-alpha.1', '1.0.0-alpha.1+build-two']:
            result = assess_update('1.0.0-alpha.1+build-one', available)
            self.assertEqual(result['change'], 'unchanged')
            self.assertEqual(result['disposition'], 'no-change')
