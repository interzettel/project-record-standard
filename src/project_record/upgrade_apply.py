"""Applies digest-reviewed local upgrade plans with conservative recovery."""

import base64
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile

from .agents import RECEIPT, install_skills
from .core import RecordError
from .pins import _COMMIT, _DIGEST, _file, _match, _relative, verify_installation
from .reconcile import _atomic, _lock, _sync
from .upgrades import _read, _release, assess_upgrade


def _json(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def _facts(data: bytes):
    """Rejects ambiguous JSON before a source-preserving transformation."""
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise RecordError('Duplicate source JSON key requires explicit reconciliation')
            result[key] = value
        return result
    def constant(value):
        raise RecordError('Nonfinite source number is unsupported')
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    except RecursionError as error:
        raise RecordError('Source JSON nesting exceeds supported depth') from error


def _digest(value: bytes | None):
    return None if value is None else sha256(value).hexdigest()


def _encode(value: bytes | None):
    return None if value is None else base64.b64encode(value).decode()


def _decode(value):
    if value is None:
        return None
    try:
        return base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as error:
        raise RecordError('Invalid journal/plan byte encoding') from error


def _current(root: Path, relative: str):
    path = _file(root, relative)
    return _read(path) if path.exists() else None


def _destination(root: Path, relative: str) -> Path:
    _relative(relative)
    if relative.split('/')[0] == '.git':
        raise RecordError('Upgrade refuses Git metadata writes')
    return _file(root, relative)


def _plan_hash(plan: dict) -> str:
    return sha256(_json({k: v for k, v in plan.items() if k != 'planSha256'})).hexdigest()


def _root(value) -> Path:
    """Requires an unambiguous real root before lock/containment decisions."""
    path = Path(value).absolute()
    if '..' in path.parts or any(p.is_symlink() for p in [path, *path.parents]):
        raise RecordError('Host/journal roots must be canonical and have no symlink ancestors')
    return path.resolve()


def preview_upgrade(request: dict, transformations: list, guards: list[str], producer_revision: str) -> dict:
    """Builds an explicit plan without writing the host or awarding permission.

    The existing installer runs only against a disposable staging host. JSON
    formatting preserves all parsed values; arbitrary semantic migrations need
    a separately reviewed adapter and are not interpreted by this helper.
    """
    request = deepcopy(request)
    request['host'] = str(_root(request['host']))
    assessment = assess_upgrade(request)
    if assessment['overall'] not in {'assessment-ready', 'simulation-only'}:
        raise RecordError('Resolve assessment conflicts/unknowns before previewing application')
    if not _match(_COMMIT, producer_revision):
        raise RecordError('Name the immutable producer implementation revision')
    if not isinstance(transformations, list) or not isinstance(guards, list) or len(set(guards)) != len(guards):
        raise RecordError('Explicit unique source guards and transformations required')
    host = Path(request['host']).absolute()
    old, target = request['installedPin'], request['releases'][-1]['pin']
    prefix = old['toolkit']['prefix']
    if target['toolkit']['prefix'] != prefix:
        raise RecordError('Toolkit relocation needs a reviewed host adapter')
    if set(old['toolkit']['files']) - set(target['toolkit']['files']):
        raise RecordError('Retiring pinned toolkit files needs an explicit host adapter')
    guard_data = {}
    for path in guards:
        _destination(host, path)
        data = _current(host, path)
        if data is None:
            raise RecordError('Guarded source is unavailable')
        _facts(data)
        guard_data[path] = data
    managed = {'/'.join(p for p in [prefix, path] if p): digest for path, digest in target['toolkit']['files'].items()}
    if set(managed) & set(target['suite']['files']):
        raise RecordError('Toolkit and installed suite destination ownership overlap')
    managed.update(target['suite']['files'])
    if set(managed) & {RECEIPT, 'AGENTS.md'}:
        raise RecordError('Toolkit selection collides with installer-owned outputs')
    desired = {}
    release = request['releases'][-1]
    with tempfile.TemporaryDirectory(prefix='prs-upgrade-preview-') as folder:
        stage = Path(folder); kit = stage / 'kit'; staged_host = stage / 'host'
        kit.mkdir(); staged_host.mkdir()
        with ZipFile(BytesIO(_read(Path(release['archive']), 64 * 1024 * 1024))) as archive:
            selected = set(target['toolkit']['files']) | {'skills/manifest.json'}
            selected |= {p.removeprefix('.agents/') for p in target['suite']['files']}
            for path in sorted(selected):
                data = archive.read('/'.join(p for p in [release['archivePrefix'], path] if p))
                out = _destination(kit, path); out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(data)
            for path in target['toolkit']['files']:
                relative = '/'.join(p for p in [prefix, path] if p)
                desired[relative] = _read(_file(kit, path))
                if path not in old['toolkit']['files']:
                    existing = _current(host, relative)
                    if existing is not None and existing != desired[relative]:
                        raise RecordError('Unowned toolkit path collision: ' + relative)
        old_names = set(old['suite']['manifest']['skills'])
        for name in set(target['suite']['manifest']['skills']) - old_names:
            if _file(host, '.agents/skills/' + name).exists():
                raise RecordError('New skill namespace collides with unowned host content: ' + name)
        for path in sorted(set(old['suite']['files']) | set(target['suite']['files']) | {RECEIPT, 'AGENTS.md'}):
            data = _current(host, path)
            if data is not None:
                out = _destination(staged_host, path); out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(data)
        install_skills(kit, staged_host, apply=True, upgrade=True, rules_sha256=target['suite']['rulesSha256'])
        for path in sorted(set(target['suite']['files']) | {RECEIPT, 'AGENTS.md'}):
            desired[path] = _read(_file(staged_host, path))
    seen = set()
    for transform in transformations:
        if not isinstance(transform, dict) or transform.get('kind') not in {'format-json', 'replace-text'}:
            raise RecordError('Choose an explicit supported source-preserving transformation')
        kind = transform['kind']
        keys = {'kind', 'path', 'beforeSha256'} | ({'text'} if kind == 'replace-text' else set())
        if set(transform) != keys:
            raise RecordError('Use exact transformation fields')
        path = transform['path']; _destination(host, path)
        if path in seen or path in desired:
            raise RecordError('Duplicate/managed path is an ambiguous transformation')
        seen.add(path)
        data = _current(host, path)
        if _digest(data) != transform['beforeSha256']:
            raise RecordError('Transformation preimage does not match current bytes')
        if kind == 'format-json':
            if data is None:
                raise RecordError('Cannot format a missing source')
            result = _json(_facts(data))
        else:
            if not isinstance(transform['text'], str):
                raise RecordError('Replacement must be explicit text')
            result = transform['text'].encode()
        if len(result) > 16 * 1024 * 1024:
            raise RecordError('Transformation output exceeds its byte limit')
        if path in guard_data and _json(_facts(result)) != _json(_facts(guard_data[path])):
            raise RecordError('Guarded source facts must remain identical')
        desired[path] = result
    for path, data in guard_data.items():
        if path in desired and _json(_facts(desired[path])) != _json(_facts(data)):
            raise RecordError('Managed replacement conflicts with guarded source')
    entries = []
    for path, after in sorted(desired.items()):
        _destination(host, path)
        before = _current(host, path)
        if before != after:
            entries.append({'path': path, 'beforeSha256': _digest(before), 'afterSha256': _digest(after), 'after': _encode(after)})
    paths = sorted(desired)
    if any(b.startswith(a + '/') for a, b in zip(paths, paths[1:])):
        raise RecordError('File/directory destination collision')
    input_paths = set(desired)
    input_paths |= {'/'.join(p for p in [prefix, path] if p) for path in old['toolkit']['files']}
    if old['policy'] is not None:
        input_paths.add(old['policy']['path'])
    for decision in request['decisions'].values():
        input_paths |= {ref['path'] for ref in decision['evidence']}
    input_guards = {p: _digest(_current(host, p)) for p in sorted(input_paths)}
    plan = {'upgradePlanVersion': 1, 'host': str(host), 'request': deepcopy(request),
            'requestSha256': assessment['requestSha256'], 'producerRevision': producer_revision,
            'synthetic': any(r['kind'] == 'synthetic' for r in request['releases']),
            'transformations': deepcopy(transformations), 'sourceGuards': {p: _digest(d) for p, d in sorted(guard_data.items())},
            'entries': entries, 'inputGuards': input_guards, 'written': False, 'applicationAuthorized': False,
            'checks': ['selected target installation bytes', 'all guarded JSON facts', 'exact modified-path pre/postimages'],
            'remainingGate': 'Host functional checks and owner outcome acceptance remain separate; no release/deployment'}
    plan['planSha256'] = _plan_hash(plan)
    _validate_plan(plan)
    return plan


def _validate_plan(plan: dict) -> None:
    fields = {'upgradePlanVersion', 'host', 'request', 'requestSha256', 'producerRevision', 'synthetic', 'transformations', 'sourceGuards', 'inputGuards', 'entries', 'written', 'applicationAuthorized', 'checks', 'remainingGate', 'planSha256'}
    if (not isinstance(plan, dict) or set(plan) != fields or type(plan['upgradePlanVersion']) is not int
            or plan['upgradePlanVersion'] != 1 or plan['planSha256'] != _plan_hash(plan)
            or not _match(_COMMIT, plan['producerRevision']) or type(plan['synthetic']) is not bool
            or plan['written'] is not False or plan['applicationAuthorized'] is not False):
        raise RecordError('Plan fields or reviewed digest are invalid')
    if len(_json(plan)) > 64 * 1024 * 1024 or not isinstance(plan['entries'], list):
        raise RecordError('Plan exceeds supported bounds')
    paths = []
    host = _root(plan['host'])
    for entry in plan['entries']:
        if not isinstance(entry, dict) or set(entry) != {'path', 'beforeSha256', 'afterSha256', 'after'}:
            raise RecordError('Invalid plan file entry')
        path = entry['path']; _destination(host, path); paths.append(path)
        after = _decode(entry['after'])
        if (after is None or len(after) > 16 * 1024 * 1024 or _digest(after) != entry['afterSha256']
                or (entry['beforeSha256'] is not None and not _match(_DIGEST, entry['beforeSha256']))):
            raise RecordError('Plan bytes/preimages are inconsistent')
    if len(paths) != len(set(paths)) or any(b.startswith(a + '/') for a, b in zip(sorted(paths), sorted(paths)[1:])):
        raise RecordError('Ambiguous plan file destinations')
    for path, digest in {**plan['sourceGuards'], **plan['inputGuards']}.items():
        _destination(host, path)
        if digest is not None and not _match(_DIGEST, digest):
            raise RecordError('Invalid source guard')


def _grant(plan: dict, grant: dict, mode: str) -> None:
    if (not isinstance(grant, dict) or set(grant) != {'planSha256', 'source', 'apply', 'rollback', 'allowSynthetic'}
            or grant['planSha256'] != plan['planSha256'] or not isinstance(grant['source'], str) or not grant['source'].strip()
            or any(type(grant[k]) is not bool for k in ['apply', 'rollback', 'allowSynthetic'])
            or not grant[mode] or (plan['synthetic'] and not grant['allowSynthetic'])):
        raise RecordError('Separate explicit plan-bound grant is required')


def _verification(plan: dict, mode: str) -> dict:
    pin = plan['request']['releases'][-1]['pin'] if mode == 'apply' else plan['request']['installedPin']
    origin = {k: pin['toolkit'][k] for k in ['sourceCommit', 'archiveSha256']}
    result = verify_installation(pin, Path(plan['host']), origin, plan['request']['runtime'])
    if result['bytes'] != 'selected-bytes-match':
        raise RecordError('Post-operation selected installation verification failed')
    return result


def apply_upgrade(plan: dict, grant: dict, journal: Path, *, mode: str = 'apply', _checkpoint=None) -> dict:
    """Applies or rolls back a reviewed plan; never overwrites unknown bytes.

    A private journal records recoverable per-file state, not a multi-file
    transaction. The supplied grant attributes existing authority; it cannot
    authenticate a user or expand runtime permission. All diagnostics are local.
    """
    if mode not in {'apply', 'rollback'}:
        raise RecordError('Choose apply or rollback explicitly')
    _validate_plan(plan); _grant(plan, grant, mode)
    host = _root(plan['host']); journal = _root(journal)
    if not host.is_dir() or any(p.is_symlink() for p in [host, *host.parents, journal, *journal.parents]):
        raise RecordError('Use real host/journal paths without symlink ancestors')
    if journal == host or host in journal.parents or journal in host.parents:
        raise RecordError('Journal must be outside the host tree')
    for release in plan['request']['releases']:
        if _release(release):
            raise RecordError('Pinned release evidence changed or became unavailable')
    locks = Path(tempfile.gettempdir()) / 'prs-upgrade-locks'
    if locks.is_symlink():
        raise RecordError('Unsafe lock directory')
    locks.mkdir(mode=0o700, exist_ok=True)
    key = locks / sha256(str(host).encode()).hexdigest()
    lock_path = Path(str(key) + '.prs-lock')
    if lock_path.exists() and (lock_path.is_symlink() or not lock_path.is_file()):
        raise RecordError('Unsafe host lock path')
    checkpoint = _checkpoint or (lambda stage: None)
    with _lock(key):
        state_path = journal / 'state.json'
        if journal.exists():
            if not journal.is_dir() or set(p.name for p in journal.iterdir()) != {'state.json'}:
                raise RecordError('Journal has unknown/incomplete contents; preserve it for recovery inspection')
            state = json.loads(_read(state_path, 128 * 1024 * 1024))
            if (set(state) != {'journalVersion', 'plan', 'grant', 'grantHistory', 'before', 'status', 'verification'}
                    or state['journalVersion'] != 1 or state['plan'] != plan
                    or state['status'] not in {'prepared', 'applying', 'applied', 'rolling-back', 'rolled-back'}):
                raise RecordError('Journal identity or phase conflict')
        else:
            if mode == 'rollback':
                raise RecordError('Rollback needs the original preserved journal')
            rebuilt = preview_upgrade(plan['request'], plan['transformations'], list(plan['sourceGuards']), plan['producerRevision'])
            if rebuilt != plan:
                raise RecordError('Reviewed plan no longer matches its inputs')
            before = {e['path']: _encode(_current(host, e['path'])) for e in plan['entries']}
            journal.mkdir(mode=0o700, parents=True)
            state = {'journalVersion': 1, 'plan': plan, 'grant': grant, 'before': before,
                     'status': 'prepared', 'verification': None, 'grantHistory': [{'mode': 'apply', 'grant': deepcopy(grant)}]}
            _atomic(state_path, _json(state))
        if not isinstance(state['grantHistory'], list) or not state['grantHistory']:
            raise RecordError('Journal approval history is missing')
        if state['grantHistory'][0] != {'mode': 'apply', 'grant': state['grant']}:
            raise RecordError('Journal original approval identity conflict')
        for observed in state['grantHistory']:
            if not isinstance(observed, dict) or set(observed) != {'mode', 'grant'} or observed['mode'] not in {'apply', 'rollback'}:
                raise RecordError('Invalid journal approval history')
            _grant(plan, observed['grant'], observed['mode'])
        if os.name != 'nt' and (journal.stat().st_mode & 0o077 or state_path.stat().st_mode & 0o077):
            raise RecordError('Journal/preimages require owner-only permissions')
        if set(state['before']) != {e['path'] for e in plan['entries']}:
            raise RecordError('Journal backup path mismatch')
        for entry in plan['entries']:
            if _digest(_decode(state['before'][entry['path']])) != entry['beforeSha256']:
                raise RecordError('Journal backup digest conflict')
        # Inspect all destinations before any mutation, including recovery/repeat.
        entries = {e['path']: e for e in plan['entries']}
        for entry in plan['entries']:
            actual = _digest(_current(host, entry['path']))
            if actual not in {entry['beforeSha256'], entry['afterSha256']}:
                raise RecordError('Authored/unknown post-snapshot edit: ' + entry['path'])
        for path, digest in {**plan['sourceGuards'], **plan['inputGuards']}.items():
            allowed = {digest}
            if path in entries:
                allowed.add(entries[path]['afterSha256'])
            if _digest(_current(host, path)) not in allowed:
                raise RecordError('Guarded source changed after snapshot: ' + path)
        terminal = 'applied' if mode == 'apply' else 'rolled-back'
        if state['status'] == 'rolled-back' or state['status'] == terminal:
            expected_mode = 'rollback' if state['status'] == 'rolled-back' else 'apply'
            expected_images = {e['path']: e['beforeSha256'] if expected_mode == 'rollback' else e['afterSha256'] for e in plan['entries']}
            if any(_digest(_current(host, path)) != digest for path, digest in expected_images.items()):
                raise RecordError('Completed journal no longer matches actual bytes')
            return _receipt(plan, state, False)
        if mode == 'apply' and state['status'] == 'rolling-back':
            raise RecordError('Finish interrupted rollback before starting a new plan')
        operation_grant = {'mode': mode, 'grant': deepcopy(grant)}
        if state['grantHistory'][-1] != operation_grant:
            state['grantHistory'].append(operation_grant)
        state['status'] = 'applying' if mode == 'apply' else 'rolling-back'
        _atomic(state_path, _json(state)); checkpoint('journal-prepared')
        written = False
        for entry in plan['entries']:
            path = _destination(host, entry['path'])
            data = _decode(entry['after'] if mode == 'apply' else state['before'][entry['path']])
            if _current(host, entry['path']) == data:
                continue
            checkpoint('before-host-write')
            if data is None:
                path.unlink(); _sync(path.parent)
            else:
                _atomic(path, data)
            written = True; checkpoint('after-host-write')
        checkpoint('before-verification')
        state['verification'] = _verification(plan, mode)
        state['status'] = terminal
        _atomic(state_path, _json(state)); checkpoint('journal-complete')
        return _receipt(plan, state, written)


def _receipt(plan: dict, state: dict, written: bool) -> dict:
    return {'upgradeReceiptVersion': 1, 'planSha256': plan['planSha256'], 'requestSha256': plan['requestSha256'],
            'producerRevision': plan['producerRevision'], 'status': state['status'], 'written': written,
            'from': plan['request']['installedPin']['toolkit'], 'to': plan['request']['releases'][-1]['pin']['toolkit'],
            'paths': [e['path'] for e in plan['entries']], 'sourceGuards': plan['sourceGuards'],
            'approvalSource': state['grantHistory'][-1]['grant']['source'],
            'approvalHistory': [{'mode': g['mode'], 'source': g['grant']['source'], 'planSha256': g['grant']['planSha256']} for g in state['grantHistory']],
            'synthetic': plan['synthetic'],
            'verification': state['verification'], 'externalWrites': False,
            'scopeDelta': 0, 'completionCredit': 0, 'remainingGate': plan['remainingGate']}
