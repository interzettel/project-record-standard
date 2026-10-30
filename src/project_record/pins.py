"""Compares expected pins with local bytes without applying upgrades."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re

from .agents import END, RECEIPT, START, _rules, _safe_path, suite_identity
from .core import RecordError

_DIGEST = re.compile(r'[0-9a-f]{64}')
_COMMIT = re.compile(r'[0-9a-f]{40}')
_VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?')


def _match(pattern: re.Pattern, value: object) -> bool:
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _version(value: str) -> tuple:
    if not _match(_VERSION, value):
        raise RecordError('An exact SemVer identity is required')
    match = _VERSION.fullmatch(value)
    pre = match[4].split('.') if match[4] else []
    if any(x.isdigit() and len(x) > 1 and x[0] == '0' for x in pre):
        raise RecordError('Numeric prerelease identifiers cannot have leading zeroes')
    return tuple(int(match[i]) for i in [1, 2, 3]), pre


def _relative(value: object) -> str:
    if (not isinstance(value, str) or not value or any(c in value for c in ['\\', ':', '\x00'])
            or PurePosixPath(value).is_absolute() or '..' in PurePosixPath(value).parts
            or value != PurePosixPath(value).as_posix() or value == '.'):
        raise RecordError('Pin paths must be canonical relative paths')
    return value


def _file(root: Path, relative: str) -> Path:
    return _safe_path(root, _relative(relative))


def _native_version(root: Path) -> str:
    text = _file(root, 'pyproject.toml').read_text()
    section = re.search(r'^\[project\]\s*\n(.*?)(?=^\[|\Z)', text, re.M | re.S)
    values = re.findall(r'^version\s*=\s*[\"\']([^\"\']+)[\"\']\s*$', section[1], re.M) if section else []
    if len(values) != 1:
        raise RecordError('Native project version is unavailable or dynamic')
    _version(values[0])
    return values[0]


def capture_pin(toolkit: Path, files: list[str], source_commit: str,
                toolkit_prefix: str = '', archive_sha256: str | None = None,
                policy_path: str | None = None, runtime: dict | None = None,
                adapters: list | None = None) -> dict:
    """Builds expected metadata from a reviewed kit; never observes an install.

    Source identities are supplied claims, not authenticated provenance. File
    coverage is explicit; the complete installed suite uses the existing
    installer hash algorithm. No expected-pin file or receipt is written.
    """
    if not _match(_COMMIT, source_commit) or (archive_sha256 is not None and not _match(_DIGEST, archive_sha256)):
        raise RecordError('Immutable source commit and optional archive digest required')
    if toolkit_prefix:
        _relative(toolkit_prefix)
    if not isinstance(files, list) or any(not isinstance(p, str) for p in files):
        raise RecordError('Select toolkit files explicitly')
    toolkit = toolkit.absolute()
    identity = suite_identity(toolkit)
    selected = sorted(set(['pyproject.toml', *files]))
    pin = {'pinVersion': 1, 'toolkit': {'version': _native_version(toolkit),
           'sourceCommit': source_commit, 'archiveSha256': archive_sha256,
           'prefix': toolkit_prefix, 'files': {p: sha256(_file(toolkit, p).read_bytes()).hexdigest() for p in selected}},
           'suite': {**identity, 'rulesSha256': sha256(_rules(identity['manifest']['skills'], identity['suiteDigest'])).hexdigest()},
           'recordContractVersion': identity['manifest']['contractVersion'],
           'policy': None if policy_path is None else {'path': '/'.join(p for p in [toolkit_prefix, policy_path] if p),
                       'sourceCommit': source_commit, 'sha256': sha256(_file(toolkit, policy_path).read_bytes()).hexdigest()},
           'runtime': deepcopy({} if runtime is None else runtime), 'adapters': deepcopy([] if adapters is None else adapters)}
    validate_pin(pin)
    return pin


def validate_pin(pin: dict) -> None:
    """Rejects mutable identities, malformed hashes and ambiguous expectations."""
    if not isinstance(pin, dict) or type(pin.get('pinVersion')) is not int or pin['pinVersion'] != 1:
        raise RecordError('Unsupported pinVersion')
    toolkit, suite = pin.get('toolkit'), pin.get('suite')
    if not isinstance(toolkit, dict) or not isinstance(suite, dict):
        raise RecordError('Toolkit and suite expectations are required')
    _version(toolkit.get('version'))
    _version(pin.get('recordContractVersion'))
    if not _match(_COMMIT, toolkit.get('sourceCommit')):
        raise RecordError('Mutable source names cannot certify an installation')
    if toolkit.get('archiveSha256') is not None and not _match(_DIGEST, toolkit['archiveSha256']):
        raise RecordError('Invalid archive digest')
    prefix = toolkit.get('prefix')
    if not isinstance(prefix, str):
        raise RecordError('Toolkit prefix must be explicit')
    if prefix:
        _relative(prefix)
    manifest, digests = suite.get('manifest'), suite.get('files')
    if not isinstance(manifest, dict) or type(manifest.get('schemaVersion')) is not int or manifest.get('schemaVersion') != 1:
        raise RecordError('Expected installer manifest is required')
    _version(manifest.get('suiteVersion'))
    _version(manifest.get('contractVersion'))
    names = manifest.get('skills')
    if not isinstance(names, list) or not names or any(not isinstance(n, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', n) or len(n) > 63 for n in names) or len(set(names)) != len(names):
        raise RecordError('Expected skill names must be unique and safe')
    for table in [toolkit.get('files'), digests]:
        if not isinstance(table, dict) or not table:
            raise RecordError('Expected file hashes must be nonempty')
        for path, digest in table.items():
            _relative(path)
            if not _match(_DIGEST, digest):
                raise RecordError('Expected file digest is invalid')
    if 'pyproject.toml' not in toolkit['files']:
        raise RecordError('Pin the native toolkit version source')
    if any(not any(path.startswith('.agents/skills/' + n + '/') for n in names) for path in digests):
        raise RecordError('Suite files must stay in expected skill namespaces')
    if any('.agents/skills/' + n + '/SKILL.md' not in digests for n in names):
        raise RecordError('Each expected skill needs instructions')
    expected = sha256(json.dumps({'manifest': manifest, 'files': digests}, sort_keys=True).encode()).hexdigest()
    if expected != suite.get('suiteDigest') or sha256(_rules(names, expected)).hexdigest() != suite.get('rulesSha256'):
        raise RecordError('Expected suite identity is internally inconsistent')
    if 'policy' not in pin:
        raise RecordError('Policy must be explicitly pinned or null')
    policy = pin.get('policy')
    if policy is not None:
        if not isinstance(policy, dict) or not _match(_COMMIT, policy.get('sourceCommit')) or not _match(_DIGEST, policy.get('sha256')):
            raise RecordError('Policy needs an immutable identity')
        _relative(policy.get('path'))
    runtime = pin.get('runtime')
    if not isinstance(runtime, dict):
        raise RecordError('Runtime expectations must be explicit')
    for name, requirement in runtime.items():
        if not isinstance(name, str) or not isinstance(requirement, dict) or not isinstance(requirement.get('versions'), list) or not requirement['versions'] or not isinstance(requirement.get('evidence'), str) or not requirement['evidence'].strip():
            raise RecordError('Runtime support needs exact versions and evidence')
        for version in requirement['versions']:
            _version(version)
    adapters = pin.get('adapters')
    if not isinstance(adapters, list) or any(not isinstance(a, dict) for a in adapters):
        raise RecordError('Adapter pins must be an explicit list')
    ids = []
    for adapter in adapters:
        if not isinstance(adapter.get('id'), str) or not adapter['id'] or not _match(_COMMIT, adapter.get('sourceCommit')) or not isinstance(adapter.get('evidence'), str) or not adapter['evidence'].strip():
            raise RecordError('Adapter identity and support evidence required')
        _version(adapter.get('version'))
        host = adapter.get('runtime')
        if not isinstance(host, dict) or not isinstance(host.get('name'), str) or not host['name']:
            raise RecordError('Adapter needs its tested host runtime')
        _version(host.get('version'))
        ids.append(adapter['id'])
    if len(ids) != len(set(ids)):
        raise RecordError('Duplicate adapter identity')


def verify_installation(pin: dict, target: Path, provenance: dict | None = None,
                        observed_runtime: dict | None = None, observed_adapters: list | None = None) -> dict:
    """Reads selected files and the existing receipt; performs no upgrades/writes.

    Provenance evidence and runtime observations are caller-supplied. Identity
    matching never authenticates their publisher, origin or actual execution.
    Reports are local diagnostics, not approved public exports.
    """
    validate_pin(pin)
    target = target.absolute()
    if target.is_symlink() or not target.is_dir():
        raise RecordError('Installation target must be an existing directory')
    issues = []
    missing = []
    def check(relative: str, digest: str) -> None:
        try:
            path = _file(target, relative)
            if not path.exists():
                missing.append(relative)
            elif not path.is_file():
                issues.append(relative)
            elif sha256(path.read_bytes()).hexdigest() != digest:
                issues.append(relative)
        except (OSError, RecordError):
            issues.append(relative)
    prefix = pin['toolkit']['prefix']
    for path, digest in pin['toolkit']['files'].items():
        check('/'.join(p for p in [prefix, path] if p), digest)
    try:
        kit = target if not prefix else _file(target, prefix)
        if _native_version(kit) != pin['toolkit']['version']:
            issues.append('native-version')
    except (OSError, RecordError, UnicodeError):
        missing.append('native-version')
    suite = pin['suite']
    for path, digest in suite['files'].items():
        check(path, digest)
    try:
        receipt_path = _file(target, RECEIPT)
        receipt = json.loads(receipt_path.read_text()) if receipt_path.is_file() else None
        if receipt is None:
            missing.append(RECEIPT)
        elif (not isinstance(receipt, dict) or receipt.get('schemaVersion') != 1
              or receipt.get('files') != suite['files'] or receipt.get('suiteDigest') != suite['suiteDigest']
              or receipt.get('suiteVersion') != suite['manifest']['suiteVersion']
              or receipt.get('contractVersion') != suite['manifest']['contractVersion']
              or receipt.get('rulesSha256') != suite['rulesSha256']):
            issues.append('installation-receipt')
        instruction_path = _file(target, 'AGENTS.md')
        if not instruction_path.exists():
            missing.append('AGENTS.md')
        elif not instruction_path.is_file():
            issues.append('tracking-instructions')
        else:
            instructions = instruction_path.read_bytes()
            if instructions.count(START) != 1 or instructions.count(END) != 1 or instructions.index(START) > instructions.index(END):
                issues.append('tracking-instructions')
            else:
                section = instructions[instructions.index(START):instructions.index(END) + len(END)]
                if sha256(section).hexdigest() != suite['rulesSha256']:
                    issues.append('tracking-instructions')
        for name in suite['manifest']['skills']:
            folder = _file(target, '.agents/skills/' + name)
            for path in folder.rglob('*'):
                relative = path.relative_to(target).as_posix()
                _file(target, relative)
                if path.is_file() and path.suffix != '.pyc' and '__pycache__' not in path.parts and relative not in suite['files']:
                    issues.append(relative)
    except (OSError, RecordError, ValueError, UnicodeError):
        issues.append('receipt-or-owned-path-unreadable')
    if pin['policy'] is not None:
        check(pin['policy']['path'], pin['policy']['sha256'])
    runtime = {} if observed_runtime is None else observed_runtime
    if not isinstance(runtime, dict):
        raise RecordError('Observed runtimes must be a mapping')
    for value in runtime.values():
        _version(value)
    runtime_checks = {name: 'unknown' if name not in runtime else 'matches-declared-support' if runtime[name] in req['versions'] else 'unsupported'
                      for name, req in pin['runtime'].items()}
    actual = [] if observed_adapters is None else observed_adapters
    if not isinstance(actual, list) or any(not isinstance(a, dict) or not isinstance(a.get('id'), str) for a in actual):
        raise RecordError('Observed adapter identities must be explicit')
    if len({a['id'] for a in actual}) != len(actual):
        raise RecordError('Duplicate observed adapter identity')
    adapter_checks = {a['id']: 'matches-declared-support' if a in actual else
                      'conflicted' if any(v['id'] == a['id'] for v in actual) else 'unknown' for a in pin['adapters']}
    expected_origin = {k: pin['toolkit'].get(k) for k in ['sourceCommit', 'archiveSha256']}
    origin = 'not-supplied' if provenance is None else 'matches-declared-evidence' if isinstance(provenance, dict) and all(provenance.get(k) == v for k, v in expected_origin.items()) else 'conflicted'
    return {'bytes': 'conflicted' if issues else 'partial' if missing else 'selected-bytes-match',
            'conflicts': sorted(set(issues)), 'missing': sorted(set(missing)),
            'provenance': origin, 'publisherAuthenticated': False,
            'runtime': runtime_checks, 'adapters': adapter_checks,
            'recordContract': 'readable' if pin['recordContractVersion'] in {'0.1.0', '0.2.0'} else 'unsupported',
            'policy': 'not-pinned' if pin['policy'] is None else 'included-in-byte-check',
            'coverage': 'Only explicitly pinned toolkit files and the complete selected suite; no unselected toolkit file claim',
            'receiptWriter': RECEIPT, 'written': False, 'upgradeApplied': False}


def _compare_versions(left: str, right: str) -> int:
    a, ap = _version(left)
    b, bp = _version(right)
    if a != b:
        return 1 if a > b else -1
    if not ap or not bp:
        return 0 if ap == bp else 1 if not ap else -1
    for x, y in zip(ap, bp):
        if x != y:
            if x.isdigit() and y.isdigit():
                return 1 if int(x) > int(y) else -1
            if x.isdigit() != y.isdigit():
                return -1 if x.isdigit() else 1
            return 1 if x > y else -1
    return (len(ap) > len(bp)) - (len(ap) < len(bp))


def assess_update(installed: str, available: str, security: bool = False,
                  deferral: dict | None = None) -> dict:
    """Classifies supplied release identities; grants no upgrade permission."""
    old, _ = _version(installed)
    new, pre = _version(available)
    if type(security) is not bool:
        raise RecordError('Security relevance must be explicit')
    order = _compare_versions(installed, available)
    kind = ('downgrade' if order > 0 else 'prerelease' if pre else 'unchanged' if order == 0 else
            'major' if new[0] != old[0] else 'minor' if new[1] != old[1] else 'patch' if new[2] != old[2] else 'stabilization')
    if security:
        disposition = 'prioritized-assessment-required'
    elif kind in {'major', 'minor', 'stabilization'}:
        disposition = 'compatibility-assessment-required'
    elif kind == 'prerelease':
        disposition = 'opt-in-only'
    elif kind == 'patch':
        valid = (isinstance(deferral, dict) and deferral.get('from') == installed and deferral.get('to') == available
                 and isinstance(deferral.get('reason'), str) and bool(deferral['reason'].strip()))
        disposition = 'deferred-with-reason' if valid else 'patch-triage-required'
    else:
        disposition = 'no-change' if kind == 'unchanged' else 'review-downgrade'
    return {'from': installed, 'to': available, 'change': kind, 'securityRelevant': security,
            'disposition': disposition, 'securityAssessment': 'not-performed-by-helper', 'upgradeApplied': False, 'applicationAuthorized': False}
