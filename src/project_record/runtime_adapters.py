"""Delivers prepared work events without deriving completion from runtime prose."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess

from .core import RecordError
from .reconcile import _atomic, _identity, _json, _lock, _path, _sync, _validate

EVENTS = {'codex': ['Stop', 'Interrupt', 'SessionEnd'],
          'claude-code': ['Stop', 'StopFailure', 'SessionEnd']}


def inspect_runtime(runtime: str, executable: str | None = None) -> dict:
    """Observes a CLI version; neither version presence nor docs prove a hook ran."""
    if runtime not in EVENTS:
        raise RecordError('Unknown runtime')
    selected = executable or shutil.which('codex' if runtime == 'codex' else 'claude')
    result = dict(runtime=runtime, executable=selected, version=None,
                  nativeTriggerVerified=False, documentedEvents=EVENTS[runtime])
    if not selected:
        return dict(result, status='not-installed')
    try:
        run = subprocess.run([selected, '--version'], capture_output=True, text=True, timeout=3)
        version = re.search(r'\b\d+\.\d+\.\d+(?:[-+][\w.-]+)?', run.stdout)
        if run.returncode or not version:
            return dict(result, status='version-unavailable')
        return dict(result, version=version[0], status='version-observed')
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return dict(result, status='version-unavailable')


def capture_core(toolkit: Path) -> dict:
    """Captures reviewed source bytes for explicit host adoption, not provenance."""
    toolkit = _path(str(toolkit))
    paths = sorted((toolkit / 'src/project_record').rglob('*.py'))
    paths += [toolkit / 'tools/run_reconcile_event.py', toolkit / 'tools/run_runtime_adapter.py', toolkit / 'pyproject.toml']
    if not paths or not (toolkit / 'src/project_record/reconcile.py').is_file():
        raise RecordError('Toolkit core is unavailable')
    return {p.relative_to(toolkit).as_posix(): sha256(_path(str(p)).read_bytes()).hexdigest()
            for p in paths}


def _validate_request(request: dict) -> None:
    keys = {'adapterVersion', 'runtime', 'runtimeVersion', 'runtimeExecutable', 'sessionId',
            'turnId', 'workspace', 'toolkit', 'coreFiles', 'python', 'timeout', 'event', 'profile'}
    if not isinstance(request, dict) or set(request) != keys or type(request['adapterVersion']) is not int or request['adapterVersion'] != 1:
        raise RecordError('Use the exact adapterVersion1 request')
    if request['runtime'] not in EVENTS:
        raise RecordError('Unknown runtime')
    if not isinstance(request['runtimeVersion'], str) or not re.fullmatch(r'\d+\.\d+\.\d+(?:[-+][\w.-]+)?', request['runtimeVersion']):
        raise RecordError('Pin an exact expected runtime version')
    if not isinstance(request['sessionId'], str) or not request['sessionId'].strip():
        raise RecordError('Bind the prepared event to a session')
    if request['runtime'] == 'codex' and (not isinstance(request['turnId'], str) or not request['turnId'].strip()):
        raise RecordError('Codex tickets require an exact turn ID')
    if request['runtime'] == 'claude-code' and request['turnId'] is not None:
        raise RecordError('This Claude adapter has no verified turn-ID contract')
    for key in ['workspace', 'toolkit', 'python']:
        if not isinstance(request[key], str) or not Path(request[key]).is_absolute():
            raise RecordError('Host paths must be absolute')
    for key in ['workspace', 'toolkit']:
        _path(request[key])
    if request['runtimeExecutable'] is not None and (not isinstance(request['runtimeExecutable'], str) or not Path(request['runtimeExecutable']).is_absolute()):
        raise RecordError('Runtime executable must be an explicit absolute path or null')
    if type(request['timeout']) not in {float, int} or not 0 < request['timeout'] <= 60:
        raise RecordError('Use a bounded core timeout of at most 60 seconds')
    if not isinstance(request['coreFiles'], dict) or not request['coreFiles']:
        raise RecordError('Host-adopted complete core file hashes are required')
    _validate(request['event'], request['profile'])


def prepare_ticket(request: dict, outbox: Path) -> dict:
    """Persists one immutable request before a hook can be missed or interrupted."""
    _validate_request(request)
    outbox = _path(str(outbox))
    outbox.mkdir(parents=True, exist_ok=True, mode=0o700)
    ticket = _path(str(outbox / _identity(request['event']['eventId'])))
    with _lock(outbox / 'queue'):
        ticket.mkdir(exist_ok=True, mode=0o700)
        path = _path(str(ticket / 'request.json'))
        if path.exists() and path.read_text() != _json(request):
            raise RecordError('This event ID already has a different prepared request')
        if not path.exists():
            _atomic(path, _json(request).encode())
        state = _path(str(ticket / 'state.json'))
        if state.exists():
            if json.loads(state.read_text()).get('requestSha256') != _identity(request):
                raise RecordError('Ticket state does not match its request')
        else:
            _atomic(state, _json(dict(requestSha256=_identity(request), state='pending',
                    attempts=0, reason='awaiting-trigger', deliveryMode=None)).encode())
    return dict(ticket=str(ticket), state=json.loads(state.read_text())['state'], written=True)


def ticket_status(ticket: Path) -> dict:
    """Reads pending/delivered transport state without claiming work completion."""
    ticket = _path(str(ticket))
    return json.loads(_path(str(ticket / 'state.json')).read_text())


def deliver_ticket(ticket: Path, payload: dict | None, *, manual: bool = False) -> dict:
    """Retries the shared writer; failures retain the request and pending state.

    The host selects ticket and manual mode outside runtime stdin. The payload
    supplies only trigger observations; it cannot replace paths, evidence or policy.
    """
    ticket = _path(str(ticket))
    if type(manual) is not bool:
        raise RecordError('Manual retry must be an explicit boolean')
    try:
        with _lock(ticket / 'delivery'):
            request = json.loads(_path(str(ticket / 'request.json')).read_text())
            _validate_request(request)
            state = ticket_status(ticket)
            if state.get('requestSha256') != _identity(request):
                raise RecordError('Prepared request changed; preserve ticket for repair')
            if state['state'] == 'delivered':
                return dict(state, duplicateDelivery=True, exitCode=0)

            def retain(reason, **details):
                state.update(state='pending', reason=reason, **details)
                _atomic(ticket / 'state.json', _json(state).encode())
                return dict(state, exitCode=3)

            state['attempts'] += 1
            state['deliveryMode'] = 'manual-retry' if manual else 'native-hook'
            _atomic(ticket / 'state.json', _json(state).encode())
            if not manual:
                if not isinstance(payload, dict) or payload.get('session_id') != request['sessionId']:
                    return retain('missing-or-mismatched-session')
                if request['turnId'] is not None and payload.get('turn_id') != request['turnId']:
                    return retain('mismatched-turn')
                cwd = payload.get('cwd')
                if not isinstance(cwd, str) or not Path(cwd).is_absolute() or '..' in Path(cwd).parts or not _path(cwd).is_relative_to(_path(request['workspace'])):
                    return retain('mismatched-workspace')
                trigger = payload.get('hook_event_name')
                if trigger not in EVENTS[request['runtime']]:
                    return retain('unsupported-trigger')
                state['trigger'] = trigger
                if payload.get('stop_hook_active') is True:
                    return retain('continued-stop-held')
                outcome = request['event']['result']
                allowed = {'Stop': {'completed', 'failed', 'blocked', 'cancelled'},
                           'StopFailure': {'failed', 'blocked'}, 'Interrupt': {'cancelled', 'blocked'},
                           'SessionEnd': {'failed', 'cancelled', 'blocked'}}
                if outcome not in allowed[trigger]:
                    return retain('terminal-trigger-does-not-support-prepared-result')
                probe = inspect_runtime(request['runtime'], request['runtimeExecutable'])
                state['runtimeObservation'] = probe
                if probe['version'] != request['runtimeVersion']:
                    return retain('runtime-version-unavailable-or-different')
            try:
                if capture_core(Path(request['toolkit'])) != request['coreFiles']:
                    return retain('core-pin-conflict')
                # The isolated worker imports only this host-selected pinned core.
                run = subprocess.run([request['python'], '-I', str(Path(request['toolkit']) / 'tools/run_reconcile_event.py'),
                        '--request', str(ticket / 'request.json'), '--expected', _identity(request)],
                        cwd=request['workspace'], capture_output=True, text=True, timeout=request['timeout'])
                result = json.loads(run.stdout)
                if not isinstance(result, dict):
                    return retain('core-unavailable-or-invalid-response')
                _atomic(ticket / 'last-core-result.json', _json(result).encode())
                if run.returncode != 0 or result.get('exitCode') != 0 or result.get('status') not in {'applied', 'duplicate'}:
                    return retain('shared-writer-pending', coreStatus=result.get('status'))
                state.update(state='delivered', reason='shared-writer-recorded', coreStatus=result['status'])
                _atomic(ticket / 'state.json', _json(state).encode())
                return dict(state, exitCode=0)
            except subprocess.TimeoutExpired:
                return retain('core-timeout-retry-same-ticket')
            except (OSError, ValueError, UnicodeError, RecordError):
                return retain('core-unavailable-or-invalid-response')
    except (OSError, ValueError, TypeError, KeyError, RecordError) as error:
        return dict(state='pending', exitCode=3, reason=str(error),
                    recovery='Preserve ticket bytes; resolve lock, disk or integrity problem before retry')


def hook_command(ticket: Path, toolkit: Path, python: Path) -> str:
    """Builds a POSIX hook command without interpolating runtime payload fields."""
    return shlex.join([str(python), '-I', str(toolkit / 'tools/run_runtime_adapter.py'),
                       'hook', '--ticket', str(ticket)])


def configure_hooks(config: Path, runtime: str, command: str, receipt: Path, *, apply: bool = False) -> dict:
    """Previews additive JSON hook groups; an apply receipt preserves exact bytes."""
    if runtime not in EVENTS or not isinstance(command, str) or not command.strip():
        raise RecordError('Runtime and a reviewed hook command are required')
    config, receipt = _path(str(config)), _path(str(receipt))
    if config == receipt or receipt.exists():
        raise RecordError('Use a separate new receipt; recover an existing attempt first')
    before = config.read_bytes().decode('utf-8') if config.exists() else None
    value = json.loads(before) if before is not None else {}
    if not isinstance(value, dict) or not isinstance(value.get('hooks', {}), dict):
        raise RecordError('Preserve unsupported host configuration for manual integration')
    value = deepcopy(value)
    hooks = value.setdefault('hooks', {})
    for event in EVENTS[runtime]:
        groups = hooks.setdefault(event, [])
        if not isinstance(groups, list) or any(not isinstance(g, dict) or not isinstance(g.get('hooks'), list) for g in groups):
            raise RecordError('Unsupported hook group; no host config replaced')
        handler = dict(type='command', command=command, timeout=3)
        if not any(not g.get('matcher') and handler in g['hooks'] for g in groups):
            groups.append(dict(hooks=[handler]))
    after = _json(value)
    result = dict(config=str(config), runtime=runtime, before=before, after=after,
                  nativeTriggerVerified=False, trustReviewRequired=runtime == 'codex', written=False)
    if apply:
        config.parent.mkdir(parents=True, exist_ok=True)
        receipt.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with _lock(config):
            if (config.read_bytes().decode('utf-8') if config.exists() else None) != before:
                raise RecordError('Host config changed during preview/apply')
            _atomic(receipt, _json(result).encode())
            _atomic(config, after.encode())
        result['written'] = True
    return result


def rollback_hooks(receipt: Path) -> dict:
    """Restores exact prior config only if no later host edits would be lost."""
    receipt = _path(str(receipt))
    saved = json.loads(receipt.read_text())
    config = _path(saved['config'])
    with _lock(config):
        current = config.read_bytes().decode('utf-8') if config.exists() else None
        if current == saved['before']:
            return dict(status='already-restored', written=False)
        if current != saved['after']:
            raise RecordError('Later host config edits preserved; reconcile rollback manually')
        if saved['before'] is None:
            config.unlink()
            _sync(config.parent)
        else:
            _atomic(config, saved['before'].encode())
    return dict(status='restored', written=True)
