"""Assesses explicit release deltas against selected host bytes without writes."""

from hashlib import sha256
import json
import re
from pathlib import Path
import stat
from zipfile import BadZipFile, ZipFile

from .core import RecordError
from .pins import (_DIGEST, _COMMIT, _file, _match, _relative, _version,
                   assess_update, validate_pin, verify_installation)

_PROFILES = {'readme-only', 'host-branded', 'private-offline'}
_KINDS = {'mandatory', 'optional', 'deprecated', 'removed', 'security'}
_DIMENSIONS = {'toolkit', 'suite', 'contract', 'runtime', 'layout', 'records',
               'guidance', 'renderer', 'ci', 'authority'}
_DECISIONS = {'already-satisfied', 'applicable-needs-change', 'not-applicable',
              'optional-deferred', 'conflict-requires-owner', 'blocked-unknown'}
_LIMIT = 16 * 1024 * 1024


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip()) and '\x00' not in value


def _read(path: Path, limit: int = _LIMIT) -> bytes:
    """Reads a bounded regular file, refusing symlinks including ancestors."""
    path = path.absolute()
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise RecordError('Comparison refuses symlinks')
    if not stat.S_ISREG(path.stat().st_mode) or path.stat().st_size > limit:
        raise RecordError('Comparison requires a bounded regular file')
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise RecordError('Comparison input exceeds its byte limit')
    return data


def _references(value: object) -> list:
    if not isinstance(value, list) or not value:
        raise RecordError('Reviewed evidence needs explicit file/digest references')
    for ref in value:
        if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
            raise RecordError('Evidence reference needs path and SHA-256 only')
        _relative(ref['path'])
        if not _match(_DIGEST, ref['sha256']):
            raise RecordError('Evidence requires an exact lowercase SHA-256')
    if len({r['path'] for r in value}) != len(value):
        raise RecordError('Duplicate evidence path')
    return value


def _release(release: dict) -> list[str]:
    """Checks selected archive members and supplied catalogue source references."""
    required = {'kind', 'pin', 'archive', 'archivePrefix', 'source', 'fromCommit', 'changes', 'review'}
    if not isinstance(release, dict) or set(release) != required:
        raise RecordError('Use explicit release descriptor fields')
    validate_pin(release['pin'])
    if release['kind'] not in {'published', 'synthetic'} or not _text(release['source']):
        raise RecordError('Release kind and attributed origin are required')
    prefix = release['archivePrefix']
    if prefix != '':
        _relative(prefix)
    if release['fromCommit'] is not None and not _match(_COMMIT, release['fromCommit']):
        raise RecordError('Predecessor must be an immutable commit or null')
    if not isinstance(release['changes'], list):
        raise RecordError('Delta catalogue must be explicit, including empty')
    for change in release['changes']:
        if (not isinstance(change, dict) or set(change) != {'id', 'kind', 'dimension', 'summary', 'profiles', 'sources'}
                or not _text(change['id']) or not _text(change['summary'])
                or change['kind'] not in _KINDS or change['dimension'] not in _DIMENSIONS
                or not isinstance(change['profiles'], list) or not change['profiles']
                or any(not isinstance(p, str) or p not in _PROFILES for p in change['profiles'])
                or len(set(change['profiles'])) != len(change['profiles'])):
            raise RecordError('Invalid reviewed change catalogue row')
        _references(change['sources'])
    review = release['review']
    gaps = []
    if not isinstance(review, dict) or set(review) != {'reviewer', 'source'} or not all(_text(v) for v in review.values()):
        gaps.append('catalogue-review-missing')
    if release['archive'] is None or release['pin']['toolkit']['archiveSha256'] is None:
        return gaps + ['archive-evidence-missing']
    if not _text(release['archive']):
        raise RecordError('Archive path must be explicit or null')
    try:
        data = _read(Path(release['archive']), 64 * 1024 * 1024)
        if sha256(data).hexdigest() != release['pin']['toolkit']['archiveSha256']:
            return gaps + ['archive-digest-conflict']
        # Never extract a release or import/execute code from it.
        from io import BytesIO
        with ZipFile(BytesIO(data)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                return gaps + ['archive-duplicate-members']
            def member(path):
                name = '/'.join(p for p in [prefix, path] if p)
                info = archive.getinfo(name)
                for ancestor in Path(name).parents:
                    for candidate in [ancestor.as_posix(), ancestor.as_posix() + '/']:
                        if candidate in names and stat.S_ISLNK(archive.getinfo(candidate).external_attr >> 16):
                            raise RecordError('Archive selected member has symlink ancestor')
                if info.file_size > _LIMIT or stat.S_IFMT(info.external_attr >> 16) not in {0, stat.S_IFREG}:
                    raise RecordError('Archive selected member must be bounded regular bytes')
                with archive.open(info) as stream:
                    value = stream.read(_LIMIT + 1)
                if len(value) > _LIMIT:
                    raise RecordError('Archive member exceeds its byte limit')
                return value
            pin = release['pin']
            # Keep overlapping expectations independent: neither table can hide the other.
            files = list(pin['toolkit']['files'].items())
            files += [(p.removeprefix('.agents/'), h) for p, h in pin['suite']['files'].items()]
            selected_suite = set()
            for name in names:
                relative = name.removeprefix(prefix + '/') if prefix else name
                if any(relative == 'skills/' + skill or relative.startswith('skills/' + skill + '/')
                       for skill in pin['suite']['manifest']['skills']):
                    _relative(relative.rstrip('/'))
                    info = archive.getinfo(name)
                    if stat.S_ISLNK(info.external_attr >> 16):
                        gaps.append('archive-suite-symlink-conflict')
                    if not name.endswith('/') and not relative.endswith('.pyc') and '__pycache__' not in Path(relative).parts:
                        selected_suite.add('.agents/' + relative)
            if selected_suite != set(pin['suite']['files']):
                gaps.append('archive-suite-inventory-conflict')
            for path, digest in files:
                if sha256(member(path)).hexdigest() != digest:
                    gaps.append('archive-selected-file-conflict:' + path)
            native_text = member('pyproject.toml').decode('utf-8')
            section = re.search(r'^\[project\]\s*\n(.*?)(?=^\[|\Z)', native_text, re.M | re.S)
            versions = re.findall(r'^version\s*=\s*["\']([^"\']+)["\']\s*$', section[1], re.M) if section else []
            if versions != [pin['toolkit']['version']]:
                gaps.append('archive-native-version-conflict')
            if pin['recordContractVersion'] != pin['suite']['manifest']['contractVersion']:
                gaps.append('archive-contract-identity-conflict')
            if json.loads(member('skills/manifest.json')) != pin['suite']['manifest']:
                gaps.append('archive-suite-manifest-conflict')
            for change in release['changes']:
                for ref in change['sources']:
                    if sha256(member(ref['path'])).hexdigest() != ref['sha256']:
                        gaps.append('delta-source-conflict:' + change['id'])
    except FileNotFoundError:
        gaps.append('archive-unavailable')
    except (OSError, RecordError, BadZipFile, KeyError, ValueError, RuntimeError):
        gaps.append('archive-unreadable-or-conflicted')
    return sorted(set(gaps))


def assess_upgrade(request: dict) -> dict:
    """Returns an owner-local, source-backed applicability matrix.

    The caller supplies reviewed release coverage and semantic host judgments;
    this helper checks their byte preconditions, not their natural-language
    truth or actor identity. It has no network, apply or acceptance operation.
    """
    fields = {'upgradeVersion', 'installedPin', 'host', 'hostVersion', 'recordContractVersion',
              'profile', 'runtime', 'provenance', 'releases', 'coverage', 'decisions'}
    if not isinstance(request, dict) or set(request) != fields or type(request['upgradeVersion']) is not int or request['upgradeVersion'] != 1:
        raise RecordError('Use exact upgradeVersion1 assessment fields')
    validate_pin(request['installedPin'])
    _version(request['hostVersion'])
    _version(request['recordContractVersion'])
    if request['profile'] not in _PROFILES or not _text(request['host']):
        raise RecordError('Select one host and its existing profile')
    if not isinstance(request['runtime'], dict) or any(not _text(k) for k in request['runtime']):
        raise RecordError('Observed runtime identities must be a mapping')
    for value in request['runtime'].values():
        _version(value)
    releases, decisions, coverage = request['releases'], request['decisions'], request['coverage']
    if not isinstance(releases, list) or not releases or not isinstance(decisions, dict):
        raise RecordError('Select ordered releases and explicit host decisions')
    if not isinstance(coverage, dict) or set(coverage) != {'complete', 'source'} or type(coverage['complete']) is not bool or not _text(coverage['source']):
        raise RecordError('Release enumeration coverage must be attributed explicitly')
    release_results = []
    conflicts, unknown = [], []
    ids = set()
    for release in releases:
        gaps = _release(release)
        pin = release['pin']
        identity = {k: pin['toolkit'][k] for k in ['version', 'sourceCommit', 'archiveSha256']}
        release_results.append({'identity': identity, 'kind': release['kind'], 'gaps': gaps,
                                'source': release['source'], 'review': release['review']})
        for gap in gaps:
            (conflicts if 'conflict' in gap or 'duplicate' in gap else unknown).append(gap)
        for c in release['changes']:
            if c['id'] in ids:
                raise RecordError('Change IDs must be unique across the selected chain')
            ids.add(c['id'])
    if set(decisions) - ids:
        raise RecordError('Host decision does not belong to this release delta')
    # The anchor is an identity, never a new delta to apply to itself.
    if releases[0]['changes']:
        raise RecordError('The installed anchor must have an empty delta catalogue')
    expected = request['installedPin']
    if releases[0]['pin'] != expected:
        conflicts.append('installed-anchor-pin-conflict')
    if not coverage['complete']:
        unknown.append('intervening-release-coverage-incomplete')
    host = Path(request['host']).absolute()
    if not host.is_dir() or any(p.is_symlink() for p in [host, *host.parents]):
        raise RecordError('Host must be an existing real directory without symlink ancestors')
    # Bound every read path used by the shared verifier, not just its native version.
    selected = {'/'.join(p for p in [expected['toolkit']['prefix'], path] if p)
                for path in expected['toolkit']['files']}
    selected |= set(expected['suite']['files']) | {'AGENTS.md', '.project-record/agent-installation.json'}
    if expected['policy'] is not None:
        selected.add(expected['policy']['path'])
    try:
        for relative in sorted(selected):
            path = _file(host, relative)
            if path.exists():
                _read(path)
        installation = verify_installation(expected, host, request['provenance'], request['runtime'])
    except FileNotFoundError:
        installation = {'bytes': 'partial', 'provenance': 'not-assessed', 'runtime': {}, 'adapters': {}}
    except (OSError, RecordError):
        installation = {'bytes': 'conflicted', 'provenance': 'not-assessed', 'runtime': {}, 'adapters': {}}
    if installation['bytes'] == 'conflicted' or installation['provenance'] == 'conflicted':
        conflicts.append('installed-bytes-or-origin-conflict')
    elif installation['bytes'] != 'selected-bytes-match' or installation['provenance'] != 'matches-declared-evidence':
        unknown.append('installed-identity-incomplete')
    for key in ['runtime', 'adapters']:
        for result in installation[key].values():
            if result in {'unsupported', 'conflicted'}:
                conflicts.append('installed-' + key + '-conflict')
            elif result == 'unknown':
                unknown.append('installed-' + key + '-unknown')
    if installation.get('recordContract') == 'unsupported':
        unknown.append('installed-contract-unsupported')
    if request['recordContractVersion'] not in {'0.1.0', '0.2.0'}:
        unknown.append('host-contract-unsupported')
    transitions, matrix = [], []
    for previous, release in zip(releases, releases[1:]):
        old, new = previous['pin']['toolkit'], release['pin']['toolkit']
        if release['fromCommit'] != old['sourceCommit']:
            unknown.append('intervening-predecessor-missing')
        transition = assess_update(old['version'], new['version'], security=any(c['kind'] == 'security' for c in release['changes']))
        if transition['change'] in {'downgrade', 'unchanged'}:
            conflicts.append('non-increasing-release-chain')
        if release['pin']['adapters']:
            unknown.append('target-adapter-native-support-unverified')
        target_runtime = {}
        for name, requirement in release['pin']['runtime'].items():
            actual = request['runtime'].get(name)
            target_runtime[name] = ('unknown' if actual is None else
                                    'matches-declared-support' if actual in requirement['versions'] else 'unsupported')
            if actual is None:
                unknown.append('target-runtime-unknown:' + name)
            elif actual not in requirement['versions']:
                conflicts.append('target-runtime-conflict:' + name)
        transition['targetRuntime'] = target_runtime
        transitions.append(transition)
        if release['pin']['recordContractVersion'] not in {'0.1.0', '0.2.0'}:
            unknown.append('target-contract-unsupported')
        for change in release['changes']:
            decision = decisions.get(change['id'])
            status, evidence = 'blocked-unknown', []
            reason = 'No byte-bound host semantic review supplied'
            if decision is not None:
                if (not isinstance(decision, dict) or set(decision) != {'decision', 'reason', 'evidence'}
                        or decision['decision'] not in _DECISIONS or not _text(decision['reason'])):
                    raise RecordError('Host judgment needs decision, reason and evidence')
                evidence = _references(decision['evidence'])
                if decision['decision'] == 'optional-deferred' and change['kind'] != 'optional':
                    raise RecordError('Required/security/removed changes cannot be deferred as optional')
                status, reason = decision['decision'], decision['reason']
                try:
                    if any(sha256(_read(_file(host, ref['path']))).hexdigest() != ref['sha256'] for ref in evidence):
                        status, reason = 'conflict-requires-owner', 'Host judgment is stale against selected bytes'
                except (OSError, RecordError):
                    status, reason = 'conflict-requires-owner', 'Host evidence unavailable or unsafe'
            if request['profile'] not in change['profiles'] and status != 'conflict-requires-owner':
                status, reason = 'not-applicable', 'Outside reviewed catalogue profiles; existing host choice retained'
            if status == 'conflict-requires-owner':
                conflicts.append('host-decision-conflict:' + change['id'])
            elif status == 'blocked-unknown':
                unknown.append('host-review-missing:' + change['id'])
            matrix.append({**change, 'release': new['sourceCommit'], 'disposition': status,
                           'reason': reason, 'hostEvidence': evidence})
    overall = ('conflicted' if conflicts else 'blocked-unknown' if unknown else
               'simulation-only' if any(r['kind'] == 'synthetic' for r in releases) else 'assessment-ready')
    return {'upgradeAssessmentVersion': 1, 'overall': overall,
            'exitCode': 1 if conflicts else 3 if unknown else 0,
            'requestSha256': sha256(json.dumps(request, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest(),
            'dimensions': {'hostVersion': request['hostVersion'], 'hostRecordContract': request['recordContractVersion'],
                           'profile': request['profile'], 'fromSuite': expected['suite']['manifest']['suiteVersion'],
                           'toSuite': releases[-1]['pin']['suite']['manifest']['suiteVersion'],
                           'fromContract': expected['recordContractVersion'], 'toContract': releases[-1]['pin']['recordContractVersion']},
            'installation': installation, 'releases': release_results, 'coverage': coverage,
            'transitions': transitions, 'matrix': matrix, 'conflicts': sorted(set(conflicts)), 'unknown': sorted(set(unknown)),
            'publisherAuthenticated': False, 'semanticJudgmentsAuthenticated': False,
            'coverageLimit': 'Selected toolkit files, complete selected suite and cited delta members only; supplied enumeration and semantic judgments are not independently authenticated',
            'written': False, 'upgradeApplied': False, 'applicationAuthorized': False,
            'scopeDelta': 0, 'completionCredit': 0}


def assess_file(path: Path) -> dict:
    """Reads an explicit bounded local request; paths use the process cwd."""
    try:
        return assess_upgrade(json.loads(_read(path, 1024 * 1024)))
    except RecursionError as error:
        raise RecordError('Upgrade request nesting exceeds supported decoding depth') from error
