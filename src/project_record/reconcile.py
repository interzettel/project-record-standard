"""Reconciles bounded work events through a host-adopted local writer policy."""

from contextlib import contextmanager
from copy import deepcopy
from datetime import date
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile

from .adapters import load_config
from .build import build, check_output_destination
from .core import RecordError, export_record, summarize
from .policy import evaluate
from .readme import update_readme
from .timeline import comparison


class Conflict(RecordError):
    """A current file or reused event identity conflicts with the transaction."""


class Held(RecordError):
    """Required authority, evidence or recovery is unresolved."""


def _json(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + '\n'


def _hash(data: bytes) -> str:
    return sha256(data).hexdigest()


def _identity(value) -> str:
    return _hash(_json(value).encode())


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip()) and '\x00' not in value


def _path(value) -> Path:
    if not _text(value):
        raise RecordError('Host paths must be nonempty local strings')
    path = Path(value).absolute()
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise Conflict('Writer paths refuse symlinks, including ancestors')
    return path


def _relative(root: Path, value: str) -> Path:
    if not _text(value) or Path(value).is_absolute() or '..' in Path(value).parts:
        raise RecordError('Manifest inputs must be contained relative paths')
    return _path(str(root / value))


def _validate(event: dict, profile: dict) -> None:
    event_keys = {'eventVersion', 'eventId', 'projectId', 'workItemId', 'sourceSha256',
                  'manifestSha256', 'artifactRevision', 'result', 'producer', 'source',
                  'observedOn', 'summary', 'receipts', 'discoveries'}
    profile_keys = {'reconcileVersion', 'projectId', 'manifest', 'journal', 'output',
                    'audience', 'authority', 'workPolicies', 'scopeAdmission', 'readme'}
    if not isinstance(event, dict) or set(event) != event_keys or type(event.get('eventVersion')) is not int or event['eventVersion'] != 1:
        raise RecordError('Use the exact eventVersion1 work-result fields')
    if not isinstance(profile, dict) or set(profile) - profile_keys or not (profile_keys - {'readme'}) <= set(profile) or type(profile.get('reconcileVersion')) is not int or profile['reconcileVersion'] != 1:
        raise RecordError('Use a reconcileVersion1 host profile with explicit writer fields')
    for key in ['eventId', 'projectId', 'workItemId', 'producer', 'source', 'summary']:
        if not _text(event[key]):
            raise RecordError('Event needs a nonempty ' + key)
    if event['projectId'] != profile['projectId']:
        raise Conflict('Event and adopted writer profile must name the same project')
    for key in ['sourceSha256', 'manifestSha256']:
        if not isinstance(event[key], str) or not re.fullmatch('[a-f0-9]{64}', event[key]):
            raise RecordError('Event source and manifest preconditions need lowercase SHA-256')
    if not isinstance(event['artifactRevision'], str) or not re.fullmatch(r'(?:[a-fA-F0-9]{40}|(?:sha256:)?[a-fA-F0-9]{64})', event['artifactRevision']):
        raise RecordError('Event needs an immutable artifact revision')
    if not isinstance(event['result'], str) or event['result'] not in {'completed', 'failed', 'cancelled', 'blocked'}:
        raise RecordError('Unsupported work-result event')
    date.fromisoformat(event['observedOn'])
    if not isinstance(event['receipts'], list) or any(not isinstance(r, dict) or
            any(not _text(r.get(k)) for k in ['kind', 'subject', 'revision', 'source']) or
            not isinstance(r.get('result'), str) or r['result'] not in {'passed', 'failed', 'partial', 'unknown'}
            for r in event['receipts']):
        raise RecordError('Receipts need explicit kind/subject/revision/result/source fields')
    if not isinstance(event['discoveries'], list) or any(not isinstance(d, dict) or
            set(d) != {'item', 'origin', 'reason', 'source'} or not isinstance(d['item'], dict) or
            any(not _text(d[k]) for k in ['origin', 'reason', 'source']) for d in event['discoveries']):
        raise RecordError('Discoveries need item, origin, reason and source')
    if profile['audience'] not in {'owner', 'public'}:
        raise RecordError('Host audience must be owner or public')
    authority = profile['authority']
    if not isinstance(authority, dict) or set(authority) != {'source', 'routineRecording'} or not _text(authority['source']) or not (authority['routineRecording'] is None or type(authority['routineRecording']) is bool):
        raise RecordError('Host authority needs its adopted source and explicit routineRecording observation')
    if not isinstance(profile['workPolicies'], dict) or not isinstance(profile['scopeAdmission'], dict):
        raise RecordError('Host work policies and scope admissions must be explicit maps')
    for value in [profile['manifest'], profile['journal'], profile['output'], *([profile['readme']] if 'readme' in profile else [])]:
        _path(value)
    json.loads(_json(event))
    json.loads(_json(profile))


def _atomic(path: Path, data: bytes) -> None:
    """Flushes one replacement file before renaming it in the same directory."""
    _path(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, name = tempfile.mkstemp(prefix='.prs-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.chmod(name, mode)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        _sync(path.parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _sync(directory: Path) -> None:
    if os.name != 'nt':
        fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


@contextmanager
def _lock(manifest: Path):
    """Serializes cooperating writers; the OS releases the lock after process exit."""
    path = _path(str(manifest) + '.prs-lock')
    with path.open('a+b') as stream:
        try:
            if os.name == 'nt':
                import msvcrt
                stream.seek(0)
                if not stream.read(1):
                    stream.write(b'0')
                    stream.flush()
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise Held('Another cooperating writer holds this manifest; retry after it finishes') from error
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def _checkpoint(stage: str) -> None:
    """Marks transaction boundaries for fault-injection tests."""


def _inputs(entry: dict, manifest: Path) -> dict:
    paths = [manifest, _relative(manifest.parent, entry['sourceFile'])]
    paths += [_relative(manifest.parent, s['sourceFile']) for s in entry.get('snapshots', [])]
    if entry.get('previousSourceFile'):
        paths.append(_relative(manifest.parent, entry['previousSourceFile']))
    paths += [_relative(manifest.parent, s['path']) for s in entry.get('supplements', []) + entry.get('changeFiles', [])]
    paths.append(_relative(manifest.parent, entry['presentation']['theme']))
    return {str(p): _hash(p.read_bytes()) for p in paths}


def _check_inputs(inputs: dict) -> None:
    for name, expected in inputs.items():
        path = _path(name)
        if not path.is_file() or _hash(path.read_bytes()) != expected:
            raise Conflict('Input changed; retain the pending transaction and reconcile: ' + name)


def _discover(raw: dict, event: dict, profile: dict) -> tuple[list, list]:
    outcomes, changes = [], []
    known = {i['id'] for i in raw['items']}
    seen = set()
    for proposal in event['discoveries']:
        item = proposal['item']
        allowed = {'id', 'title', 'groupId', 'milestoneId', 'required', 'dependsOn',
                   'criterion', 'kind', 'deferReason', 'note'}
        if set(item) - allowed or not _text(item.get('id')) or item['id'] in seen:
            raise RecordError('Discovery needs one distinct new item and supported scope fields')
        seen.add(item['id'])
        if item['id'] in known:
            raise Conflict('Discovery ID already exists; relate to it instead of adding duplicate credit')
        grant = profile['scopeAdmission'].get(item['id'])
        if grant is None:
            outcomes.append(dict(id=item['id'], disposition='proposed', origin=proposal['origin'],
                                 reason=proposal['reason'], source=proposal['source']))
            continue
        if not isinstance(grant, dict) or set(grant) != {'required', 'groupId', 'milestoneId', 'source'} or not _text(grant['source']) or type(grant['required']) is not bool:
            raise RecordError('Each admission grant needs exact required/group/milestone fields and attributed source')
        if any(item.get(k) != grant[k] for k in ['required', 'groupId', 'milestoneId']):
            raise Conflict('Discovered scope does not match its bounded host admission')
        new = dict(item, state='backlog', sourceState='admitted-discovery', blocked=False,
                   unmappedDependencies=[], evidence=[], completionBasis='Not complete',
                   owner=event['producer'], issueUrl=None, priority=None,
                   discovery=dict(origin=proposal['origin'], reason=proposal['reason'], source=proposal['source'],
                                  eventId=event['eventId'], admissionSource=grant['source']))
        raw['items'].append(new)
        known.add(new['id'])
        changes.append(dict(kind='added', id=new['id'], reason=proposal['reason'], source=grant['source']))
        outcomes.append(dict(id=new['id'], disposition='admitted', **new['discovery']))
    return outcomes, changes


def _prepare(event: dict, profile: dict) -> dict:
    manifest = _path(profile['manifest'])
    config_bytes = manifest.read_bytes()
    if _hash(config_bytes) != event['manifestSha256']:
        raise Conflict('Manifest precondition is stale; refresh the event against current authored inputs')
    config = json.loads(config_bytes)
    entries = [e for e in config['projects'] if e['project']['id'] == profile['projectId']]
    if len(entries) != 1 or entries[0]['adapter'] != 'normalized-v1':
        raise RecordError('This writer supports exactly one selected normalized-v1 source; other adapters need their own writer')
    entry = entries[0]
    source = _relative(manifest.parent, entry['sourceFile'])
    if source == manifest:
        raise Conflict('Manifest and source cannot share a writer path')
    inputs = _inputs(entry, manifest)
    before_bytes = source.read_bytes()
    if _hash(before_bytes) != event['sourceSha256']:
        raise Conflict('Source precondition is stale; no newer authored work will be overwritten')
    before = summarize(load_config(manifest, {profile['projectId']})[0])
    _check_inputs(inputs)
    if event['observedOn'] < before['source']['observedOn']:
        raise Conflict('Event observation predates the current authored observation')
    if profile['authority']['routineRecording'] is not True:
        raise Held('Routine recording authority is unresolved; adopt the host policy before applying')
    policy = profile['workPolicies'].get(event['workItemId'])
    if policy is None:
        raise Held('Host has not authorized routine recording for this stable work item')
    raw = json.loads(before_bytes)
    leaf = next((i for i in raw['items'] if i['id'] == event['workItemId']), None)
    if leaf is None:
        raise Conflict('Work item is absent from the canonical source')
    if leaf['state'] == 'cancelled' or not leaf['required']:
        raise Held('Cancelled/deferred work needs explicit scope handling before routine recording')
    if leaf['state'] == 'done':
        raise Held('Existing Done work is preserved; use a reviewed correction rather than overwriting its artifact')
    if event['result'] == 'completed':
        leaf.update(state='done', blocked=False, sourceState='after-work-completed',
                    implementationRevision=event['artifactRevision'], completionBasis=event['summary'])
    elif event['result'] == 'blocked':
        leaf.update(blocked=True, sourceState='after-work-blocked')
    receipts = deepcopy(event['receipts'])
    if any(r['subject'] != leaf['id'] or r['revision'] != event['artifactRevision'] for r in receipts):
        raise RecordError('Work receipts must match this exact work item and artifact revision')
    receipt = dict(kind='work-result', subject=leaf['id'], revision=event['artifactRevision'],
                   result={'completed': 'passed', 'failed': 'failed', 'cancelled': 'unknown', 'blocked': 'unknown'}[event['result']],
                   source=event['source'], producer=event['producer'], observedOn=event['observedOn'],
                   eventId=event['eventId'], outcome=event['result'], summary=event['summary'])
    for observation in receipts + [receipt]:
        if observation not in leaf['evidence']:
            leaf['evidence'].append(observation)
    discoveries, changes = _discover(raw, event, profile)
    after_bytes = _json(raw).encode()
    snapshot = source.parent / 'reconciliation-history' / (event['sourceSha256'] + '.json')
    snapshot = _path(str(snapshot))
    if snapshot.exists() and snapshot.read_bytes() != before_bytes:
        raise Conflict('Historical snapshot path contains other bytes')
    if entry.get('previousSourceFile'):
        entry.setdefault('snapshots', []).append(dict(sourceFile=entry['previousSourceFile'], source=entry['previousSource']))
    entry['previousSourceFile'] = snapshot.relative_to(manifest.parent).as_posix()
    entry['previousSource'] = deepcopy(entry['source'])
    entry['source'] = dict(entry['source'], kind='file-snapshot', commit=None,
                           observedOn=event['observedOn'], updatedOn=event['observedOn'])
    after = deepcopy(before)
    after.update(raw)
    after['source'] = dict(entry['source'], sha256=_hash(after_bytes))
    after = summarize(after)
    after['history']['snapshots'].append(dict(observedOn=event['observedOn'], source=after['source'], metrics=after['metrics']))
    after['history']['comparisons'].append(comparison(before, after))
    gates = [dict(subject=leaf['id'], revision=event['artifactRevision'], policy=policy, receipts=receipts)] if event['result'] == 'completed' else None
    request = dict(policyVersion=1, record=after, before=before, requiredRules=['PRS-ACCOUNT-01', 'PRS-HISTORY-01'],
                   audience=profile['audience'], source=dict(path=str(source), expectedSha256=event['sourceSha256']), changes=changes)
    if gates is not None:
        request['gates'] = gates
    checks = evaluate(request)
    required = [c for c in checks['checks'] if c['required']]
    failures = [c for c in required if c['status'] == 'fail']
    if failures:
        raise RecordError('Required policy failed: ' + ', '.join(c['ruleId'] for c in failures))
    unknown = [c for c in required if c['status'] == 'unknown' and not (c['ruleId'] == 'PRS-SCOPE-01' and changes)]
    if unknown:
        raise Held('Required policy remains unknown: ' + ', '.join(c['ruleId'] for c in unknown))
    export_record(after, profile['audience'])
    key = _hash(event['eventId'].encode())
    output = _path(profile['output']) / key
    check_output_destination(output)
    files = [dict(path=str(snapshot), before=snapshot.read_bytes().decode('utf-8') if snapshot.exists() else None, after=before_bytes.decode()),
             dict(path=str(source), before=before_bytes.decode(), after=after_bytes.decode()),
             dict(path=str(manifest), before=config_bytes.decode(), after=_json(config))]
    toolkit = Path(__file__).resolve().parents[2]
    if not (toolkit / 'web/components.mjs').is_file():
        import sys
        toolkit = Path(sys.prefix) / 'share/project-record-standard'
    with tempfile.TemporaryDirectory(prefix='prs-reconcile-preview-') as folder:
        generated = Path(folder) / 'views'
        build([after], manifest, generated, profile['audience'], toolkit)
        view_files = {p.relative_to(generated).as_posix(): p.read_text() for p in sorted(generated.rglob('*')) if p.is_file()}
        if 'readme' in profile:
            readme = _path(profile['readme'])
            if readme in {source, manifest, snapshot}:
                raise Conflict('README cannot overlap an authored source writer')
            old = readme.read_bytes().decode('utf-8')
            copy = Path(folder) / 'README.md'
            copy.write_bytes(old.encode('utf-8'))
            update_readme(copy, view_files[profile['projectId'] + '/README-module.md'], True)
            files.append(dict(path=str(readme), before=old, after=copy.read_bytes().decode('utf-8')))
    for directory in [_path(profile['journal']), _path(profile['output'])]:
        for file in [Path(f['path']) for f in files] + [Path(p) for p in inputs]:
            if directory == file or directory in file.parents or file in directory.parents:
                raise Conflict('Transport/output paths cannot overlap selected authored inputs or targets')
    if _path(profile['journal']) == _path(profile['output']) or _path(profile['journal']) in _path(profile['output']).parents or _path(profile['output']) in _path(profile['journal']).parents:
        raise Conflict('Journal and output roots must be separate')
    _check_inputs(inputs)
    return dict(files=files, inputs=inputs, views=view_files, output=str(output),
                beforeNormalized=before, policy=checks, discoveries=discoveries,
                metrics=dict(before=before['metrics'], after=after['metrics']),
                event=event, profile=profile)


def _current(path: Path):
    return path.read_bytes().decode('utf-8') if path.exists() else None


def _check_targets(plan: dict) -> None:
    for f in plan['files']:
        path = _path(f['path'])
        if _current(path) not in [f['before'], f['after']]:
            raise Conflict('Pending target differs from both preserved states; reconcile without overwriting: ' + str(path))
    targets = {f['path'] for f in plan['files']}
    _check_inputs({p: h for p, h in plan['inputs'].items() if p not in targets})


def _views(plan: dict) -> None:
    output = _path(plan['output'])
    if output.exists() and any(output.iterdir()):
        paths = list(output.rglob('*'))
        if any(p.is_symlink() for p in paths):
            raise Conflict('Projection contains an unowned symlink; preserve it for recovery')
        actual = {p.relative_to(output).as_posix(): p.read_text() for p in paths if p.is_file()}
        if actual != plan['views']:
            raise Conflict('Existing projection differs; preserve it and repair in a new owned destination')
        return
    check_output_destination(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.prs-stage-', dir=output.parent) as folder:
        stage = Path(folder) / 'views'
        stage.mkdir()
        for name, content in plan['views'].items():
            path = stage / name
            _atomic(path, content.encode())
        if output.exists():
            output.rmdir()
        os.replace(stage, output)
        _sync(output.parent)


def _report(status: str, code: int, reason: str, **details) -> dict:
    return dict(reconciliationResultVersion=1, status=status, exitCode=code, reason=reason,
                written=None if details.get('recoveryPending') else False, **details)


def reconcile(event: dict, profile: dict, *, apply: bool = False) -> dict:
    """Previews or resumes one event under an independently adopted host policy.

    Args:
        event: Untrusted eventVersion1 work-result data; it grants no permissions.
        profile: Trusted host-selected paths, work policies and bounded admissions.
        apply: True enables the local cooperating writer; preview is the default.

    Returns:
        Structured status, exact identities, before/after counts and recovery action.
        Exit0 means preview/applied/duplicate,1 rejected/conflict,2 invalid input,
        and3 held/recoverable. OS credentials and protected host policy remain
        the authority boundary; this function does not authenticate either.
    """
    prepared = False
    try:
        if type(apply) is not bool:
            raise RecordError('apply must be an explicit boolean')
        _validate(event, profile)
    except (RecordError, ValueError, TypeError, KeyError) as error:
        return _report('invalid-input', 2, str(error))
    try:
        if not apply:
            plan = _prepare(event, profile)
            return _report('preview', 0, 'No host targets or journal changed; adopt/apply through the host writer',
                           metrics=plan['metrics'], discoveries=plan['discoveries'], policy=plan['policy'])
        manifest = _path(profile['manifest'])
        key = _hash(event['eventId'].encode())
        journal = _path(str(_path(profile['journal']) / (key + '.json')))
        pending = _path(str(manifest) + '.prs-pending.json')
        with _lock(manifest):
            prepared = pending.exists()
            if pending.exists() and json.loads(pending.read_text()) != dict(key=key, profileSha256=_identity(profile)):
                raise Held('Another interrupted transaction owns this manifest; resume its original event/profile first')
            if journal.exists():
                transaction = json.loads(journal.read_text())
                plan = transaction['plan']
                if transaction.get('journalVersion') != 1 or transaction['planSha256'] != _identity(plan):
                    raise Conflict('Journal integrity mismatch; preserve it for recovery')
                if plan['event'] != event or plan['profile'] != profile:
                    raise Conflict('Event ID was reused with another payload or host policy')
                if transaction['status'] == 'applied':
                    if pending.exists():
                        pending.unlink()
                    return dict(transaction['result'], status='duplicate', written=False,
                                reason='This exact event was committed once; historical result is not a fresh source observation')
                prepared = True
                if not pending.exists():
                    raise Held('Prepared journal has no manifest recovery marker; inspect before resuming')
            else:
                plan = _prepare(event, profile)
                transaction = dict(journalVersion=1, status='prepared', plan=plan, planSha256=_identity(plan))
                _atomic(pending, _json(dict(key=key, profileSha256=_identity(profile))).encode())
                prepared = True
                _atomic(journal, _json(transaction).encode())
            _checkpoint('prepared')
            _check_targets(plan)
            for index, f in enumerate(plan['files'][:3]):
                _check_targets(plan)
                path = _path(f['path'])
                if _current(path) != f['after']:
                    _atomic(path, f['after'].encode())
                _checkpoint(['snapshot', 'source', 'manifest'][index])
            _check_targets(plan)
            _views(plan)
            _checkpoint('views')
            for f in plan['files'][3:]:
                _check_targets(plan)
                if _current(_path(f['path'])) != f['after']:
                    _atomic(_path(f['path']), f['after'].encode())
            _checkpoint('readme')
            _check_targets(plan)
            result = _report('applied', 0, 'Canonical source and projections committed under the adopted host policy',
                             metrics=plan['metrics'], discoveries=plan['discoveries'], output=plan['output'],
                             sourceSha256=_hash(plan['files'][1]['after'].encode()), eventSha256=_identity(event),
                             profileSha256=_identity(profile), policy=plan['policy'])
            result['written'] = True
            transaction.update(status='applied', result=result)
            _atomic(journal, _json(transaction).encode())
            _checkpoint('committed')
            pending.unlink()
            _sync(pending.parent)
            return result
    except Conflict as error:
        return _report('conflict', 1, str(error), recoveryPending=prepared)
    except Held as error:
        return _report('held', 3, str(error), recoveryPending=prepared)
    except (RecordError, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        return _report('recoverable' if prepared else 'rejected', 3 if prepared else 1,
                       str(error), recoveryPending=prepared,
                       nextAction='Resume the exact event/profile after resolving the error; never reset newer authored files' if prepared else 'Correct the explicit inputs; no source write was authorized')


def reconcile_files(event_path: Path, profile_path: Path, *, apply: bool = False) -> dict:
    """Reads explicit event/profile files; relative host paths use the process cwd."""
    try:
        event = json.loads(event_path.read_text())
        profile = json.loads(profile_path.read_text())
    except (OSError, ValueError, UnicodeError) as error:
        return _report('invalid-input', 2, str(error))
    return reconcile(event, profile, apply=apply)
