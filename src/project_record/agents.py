"""Installs versioned agent skills without replacing project instructions."""

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re

from .core import RecordError

START = b'<!-- project-record:agents:start -->'
END = b'<!-- project-record:agents:end -->'
RECEIPT = '.project-record/agent-installation.json'


def _digest(content: bytes) -> str:
    return sha256(content).hexdigest()


def _safe_path(root: Path, relative: str) -> Path:
    """Rejects path traversal and symlinks before checking file ownership."""
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in relative or not path.parts:
        raise RecordError('Installation path must stay inside the target')
    candidate = root
    for part in path.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise RecordError('Installation refuses symlinks: ' + relative)
    return candidate


def _rules(names: list[str], digest: str) -> bytes:
    rows = [START.decode(), '## Project tracking agent rules', '',
            'Read the matching skill before tracking work. Discover project purpose, scope, existing authority and local instructions first. Use the project’s terminology aliases and brand.', '',
            '| Workflow skill | Instructions |', '| --- | --- |']
    rows += [f'| {name} | `.agents/skills/{name}/SKILL.md` |' for name in names]
    rows += ['', 'Treat authored sources as authority and README/Pages as derived views. Scout docs, issues, PRs, branches, releases and existing trackers before planning a setup or scope expansion. Record inaccessible sources and observation dates.',
             'Keep stable IDs and one accounting owner per leaf. Use named fractions and the toolkit calculators. Preserve snapshots when scope grows. A rebuild does not refresh source observation or award acceptance.',
             'Run record checks and relevant project checks before reporting completion. Preserve evidence subject and revision. Keep unavailable acceptance tests pending. Review public output and protect project-owned files.',
             'Tracking work alone does not authorize deployment, credentials, GitHub changes or changes to another repository. Follow authorization already provided for the task.', '',
             f'Skill suite identity: `{digest}`. Installation ownership: `.project-record/agent-installation.json`.', END.decode()]
    return '\n'.join(rows).encode()


def install_skills(toolkit: Path, target: Path, apply: bool = False,
                   upgrade: bool = False) -> dict:
    """Previews or applies an additive, resumable agent-skill installation.

    Args:
        toolkit: The source toolkit containing a skill manifest and folders.
        target: The project directory whose instructions remain authoritative.
        apply: If true, writes the preflighted plan; if false, previews it.
        upgrade: If true, replaces unchanged owned files from an older suite.
            If false, requires an explicit upgrade for differing owned files.

    Returns:
        The changed paths, suite identity and whether writes were applied.

    Raises:
        RecordError: If an owned file was edited or a path conflicts.
    """
    toolkit, target = toolkit.absolute(), target.absolute()
    if target.is_symlink() or not target.is_dir():
        raise RecordError('Target must be an existing project directory')
    manifest = json.loads((toolkit / 'skills/manifest.json').read_text())
    names = manifest.get('skills')
    if (manifest.get('schemaVersion') != 1 or not isinstance(names, list) or not names
            or any(not isinstance(n, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', n) or len(n) > 63 for n in names)
            or len(names) != len(set(names))):
        raise RecordError('Skill manifest needs unique safe skill names')
    files = {}
    for name in names:
        folder = _safe_path(toolkit, 'skills/' + name)
        if not (folder / 'SKILL.md').is_file():
            raise RecordError('Missing skill instructions: ' + name)
        for path in sorted(folder.rglob('*')):
            relative = path.relative_to(toolkit).as_posix()
            _safe_path(toolkit, relative)
            if path.is_file():
                if path.suffix == '.pyc' or '__pycache__' in path.parts:
                    continue
                files['.agents/' + relative] = path.read_bytes()
    digests = {name: _digest(content) for name, content in files.items()}
    suite_digest = _digest(json.dumps({'manifest': manifest, 'files': digests}, sort_keys=True).encode())
    section = _rules(names, suite_digest)
    receipt_path = _safe_path(target, RECEIPT)
    previous = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    if previous is not None and (not isinstance(previous, dict) or previous.get('schemaVersion') != 1 or not isinstance(previous.get('files'), dict)):
        raise RecordError('Installation receipt has an unsupported shape')
    old_files = previous['files'] if previous else {}
    if set(old_files) - set(files):
        raise RecordError('Removed skills require a reviewed retirement before upgrade')
    if previous and previous.get('suiteDigest') != suite_digest and not upgrade:
        raise RecordError('Different suite identity; preview and use --upgrade deliberately')
    changes = {}
    for relative, content in files.items():
        path = _safe_path(target, relative)
        if path.exists():
            actual = path.read_bytes()
            if relative in old_files and _digest(actual) != old_files[relative]:
                raise RecordError('Locally edited owned file: ' + relative)
            if actual != content:
                if relative not in old_files:
                    raise RecordError('Unowned file collision: ' + relative)
                changes[relative] = content
        else:
            changes[relative] = content
    instructions = _safe_path(target, 'AGENTS.md')
    original = instructions.read_bytes() if instructions.exists() else b''
    if START in original or END in original:
        if original.count(START) != 1 or original.count(END) != 1 or original.index(START) > original.index(END):
            raise RecordError('AGENTS.md needs one ordered tracking marker pair')
        start, end = original.index(START), original.index(END) + len(END)
        existing = original[start:end]
        owned = previous and _digest(existing) == previous.get('rulesSha256')
        if not owned and existing != section:
            raise RecordError('Unowned or edited tracking instructions in AGENTS.md')
        updated = original[:start] + section + original[end:]
    else:
        if previous:
            raise RecordError('Owned tracking instructions are missing; review their removal')
        updated = original + (b'\n\n' if original else b'') + section + b'\n'
    if updated != original:
        changes['AGENTS.md'] = updated
    receipt = {'schemaVersion': 1, 'suiteVersion': manifest['suiteVersion'],
               'contractVersion': manifest['contractVersion'], 'suiteDigest': suite_digest,
               'files': digests, 'rulesSha256': _digest(section)}
    content = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
    if not receipt_path.exists() or receipt_path.read_bytes() != content:
        changes[RECEIPT] = content
    for relative in changes:
        path = _safe_path(target, relative)
        temporary = path.with_name(path.name + '.project-record-tmp')
        if temporary.exists() or temporary.is_symlink():
            raise RecordError('Temporary installation path already exists: ' + str(temporary))
        parent = path.parent
        while parent != target:
            if parent.exists() and not parent.is_dir():
                raise RecordError('Installation parent is not a directory: ' + str(parent))
            parent = parent.parent
    if apply:
        for relative, content in changes.items():
            path = _safe_path(target, relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + '.project-record-tmp')
            temporary.write_bytes(content)
            temporary.replace(path)
    return {'suiteVersion': manifest['suiteVersion'], 'suiteDigest': suite_digest,
            'changes': list(changes), 'written': apply and bool(changes),
            'externalWrites': False}
