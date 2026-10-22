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


if __name__ == '__main__':
    unittest.main()
