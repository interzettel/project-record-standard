"""Checks candidate JSON through a separately selected trusted policy core."""

from copy import deepcopy
from fnmatch import fnmatch
from hashlib import sha256
import json
from pathlib import Path

from .adapters import load_config
from .core import RecordError, summarize
from .policy import _digest


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _inside(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute() or '..' in Path(name).parts or '\x00' in name:
        raise RecordError('CI inputs must use contained relative paths')
    path = root / name
    if not path.resolve().is_relative_to(root.resolve()) or any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise RecordError('CI inputs refuse symlinks and paths outside the selected checkout')
    return path


def _load(root: Path, profile: dict) -> tuple[dict, dict]:
    config_path = _inside(root, profile['config'])
    config = json.loads(config_path.read_bytes())
    rows = [e for e in config['projects'] if e['project']['id'] == profile['projectId']]
    if len(rows) != 1:
        raise RecordError('CI profile must select exactly one declared project')
    entry = rows[0]
    files = [entry['sourceFile']]
    files += [s['sourceFile'] for s in entry.get('snapshots', [])]
    if entry.get('previousSourceFile'):
        files.append(entry['previousSourceFile'])
    files += [s['path'] for s in entry.get('supplements', []) + entry.get('changeFiles', [])]
    for name in files:
        _inside(config_path.parent, name)
    record = summarize(load_config(config_path, {profile['projectId']})[0])
    return record, entry


def _protected(base: Path, candidate: Path, patterns: list[str]) -> list[str]:
    names = set()
    for root in [base, candidate]:
        for path in root.rglob('*'):
            relative = path.relative_to(root).as_posix()
            if '.git' in path.relative_to(root).parts:
                continue
            if any(fnmatch(relative, pattern) for pattern in patterns) and (path.is_file() or path.is_symlink()):
                names.add(relative)
    changed = []
    for name in sorted(names):
        left, right = _inside(base, name), _inside(candidate, name)
        if not left.exists() or not right.exists() or _hash(left) != _hash(right):
            changed.append(name)
    return changed


def _cli(request: dict) -> dict:
    import contextlib
    import io
    import tempfile
    from .__main__ import main
    with tempfile.TemporaryDirectory(prefix='prs-policy-ci-') as folder:
        path = Path(folder) / 'request.json'
        path.write_text(json.dumps(request))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main(['policy-check', '--request', str(path)])
        return json.loads(output.getvalue())


def check_checkouts(base: Path, candidate: Path, profile: dict) -> dict:
    """Evaluates selected JSON data without executing candidate code or Git hooks.

    Args:
        base: The trusted GitHub base/before checkout, selected by the host.
        candidate: The untrusted head checkout; only declared JSON is interpreted.
        profile: The trusted host policy, never read from the candidate checkout.

    Returns:
        Scoped shared policy results, protected-file review notices and exit0/1/3/2.
        This read-only check does not activate or certify host protection settings.
    """
    report = dict(policyCIResultVersion=1, exitCode=2, overall='invalid-input',
                  hostEnforcement='not-assessed', written=False, protectedChanges=[])
    try:
        allowed = {'ciProfileVersion', 'config', 'projectId', 'audience', 'completionPolicy', 'protectedPaths', 'approvedChanges'}
        if not isinstance(profile, dict) or set(profile) != allowed or type(profile.get('ciProfileVersion')) is not int or profile['ciProfileVersion'] != 1:
            raise RecordError('Use the exact ciProfileVersion1 trusted host profile')
        if profile['audience'] not in {'owner', 'public'} or not isinstance(profile['projectId'], str):
            raise RecordError('Host profile needs a project ID and audience')
        if not isinstance(profile['protectedPaths'], list) or any(not isinstance(s, str) or not s for s in profile['protectedPaths']):
            raise RecordError('Protected-path notices need explicit glob patterns')
        if not isinstance(profile['approvedChanges'], list):
            raise RecordError('Adopted exact-input decisions must be a list')
        for decision in profile['approvedChanges']:
            if not isinstance(decision, dict) or set(decision) != {'beforeCanonicalSha256', 'afterCanonicalSha256', 'rules', 'source'} or not isinstance(decision['source'], str) or not decision['source'].strip():
                raise RecordError('Adopted decisions need exact input hashes, rules and attributed source')
            if any(not isinstance(decision[k], str) or len(decision[k]) != 64 or any(c not in '0123456789abcdef' for c in decision[k]) for k in ['beforeCanonicalSha256', 'afterCanonicalSha256']):
                raise RecordError('Adopted decisions require lowercase SHA-256 input identities')
            if not isinstance(decision['rules'], list) or not decision['rules'] or any(r not in ['PRS-SCOPE-01', 'PRS-ACCEPT-01'] for r in decision['rules']):
                raise RecordError('Only scope/acceptance identity decisions can be supplied by the trusted profile')
        base, candidate = base.absolute(), candidate.absolute()
        report['protectedChanges'] = _protected(base, candidate, profile['protectedPaths'])
        report['protectedChangeMeaning'] = 'Review notices, not authorization or a tamper-proof future-workflow guarantee'
        before, old_entry = _load(base, profile)
        after, new_entry = _load(candidate, profile)
        for key in ['adapter', 'sourceFile', 'project']:
            if old_entry[key] != new_entry[key]:
                report.update(overall='unknown', exitCode=3, reason='Source ownership/project changes need an explicitly reviewed CI profile migration')
                return report
        for key in ['path', 'authority']:
            if old_entry['source'].get(key) != new_entry['source'].get(key):
                report.update(overall='unknown', exitCode=3, reason='Source locator/authority changes need an explicitly reviewed migration')
                return report
        old_points = before['history']['snapshots']
        new_points = after['history']['snapshots']
        if [p['source'] for p in new_points[:len(old_points)]] != [p['source'] for p in old_points]:
            report.update(overall='fail', exitCode=1, reason='Candidate must retain the exact ordered prior source observations and raw snapshot bytes')
            return report
        old_states = {i['id']: i['state'] for i in before['items']}
        gates = [dict(subject=i['id'], revision=i.get('implementationRevision'),
                      policy=deepcopy(profile['completionPolicy']), receipts=i['evidence'])
                 for i in after['items'] if i['state'] == 'done' and old_states.get(i['id']) != 'done']
        request = dict(policyVersion=1, record=after, before=before,
                       requiredRules=['PRS-ACCOUNT-01', 'PRS-HISTORY-01'], audience=profile['audience'],
                       source=dict(path=str(_inside(base / Path(profile['config']).parent, old_entry['sourceFile'])),
                                   expectedSha256=before['source']['sha256']), changes=[])
        decisions = [d for d in profile['approvedChanges'] if d['beforeCanonicalSha256'] == _digest(before) and d['afterCanonicalSha256'] == _digest(after)]
        if decisions:
            from .policy import _scope_changes
            from .timeline import comparison
            scope_decisions = [d for d in decisions if 'PRS-SCOPE-01' in d['rules']]
            if scope_decisions:
                request['changes'] = [dict(kind=k, id=i, reason='Exact-input host scope decision', source=scope_decisions[0]['source'])
                                      for k, i in sorted(_scope_changes(before, after, comparison(before, after)))]
        if gates:
            request['gates'] = gates
        policy = _cli(request)
        if policy['exitCode'] == 2:
            report.update(overall='invalid-input', exitCode=2, policy=policy, reason='Shared CLI rejected the constructed host policy request')
            return report
        allowed_unknown = {r for d in decisions for r in d['rules']}
        required = [c for c in policy['checks'] if c['required']]
        failing = any(c['status'] == 'fail' for c in required)
        unknown = [c['ruleId'] for c in required if c['status'] == 'unknown' and c['ruleId'] not in allowed_unknown]
        overall = 'fail' if failing else 'unknown' if unknown else 'pass'
        report.update(overall=overall, exitCode={'pass': 0, 'fail': 1, 'unknown': 3}[overall], policy=policy,
                      inputs=dict(beforeSourceSha256=before['source']['sha256'], afterSourceSha256=after['source']['sha256'],
                                  beforeCanonicalSha256=_digest(before), afterCanonicalSha256=_digest(after)),
                      hostDecisions=decisions,
                      reason='Verdict covers selected data predicates and separately adopted exact-input authority decisions only')
        return report
    except (RecordError, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        report.update(overall='fail', exitCode=1, reason=str(error))
        return report
