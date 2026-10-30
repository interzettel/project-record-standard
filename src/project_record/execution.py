"""Assesses declared work selection and observed alignment without writing facts."""

from copy import deepcopy
from datetime import date
from pathlib import Path
import re

from .core import RecordError, policy_satisfied, summarize
from .readme import update_readme


def _profile(record: dict, profile: dict) -> None:
    """Rejects ambiguous queue/condition mappings in the optional local profile."""
    allowed = {'executionVersion', 'projectId', 'sourceSha256', 'order', 'conditions',
               'dependencyKinds', 'nativeMilestones', 'obsoleteArtifactUrls', 'milestonePolicies'}
    if (not isinstance(profile, dict) or set(profile) - allowed
            or type(profile.get('executionVersion')) is not int or profile['executionVersion'] != 1
            or profile.get('projectId') != record['project']['id']):
        raise RecordError('Execution profile needs version1 and this project identity')
    if not isinstance(profile.get('sourceSha256'), str) or not re.fullmatch(r'[a-f0-9]{64}', profile['sourceSha256']):
        raise RecordError('Execution profile needs an exact source SHA-256')
    ids = {i['id'] for i in record['items']}
    order = profile.get('order')
    if (not isinstance(order, list) or any(not isinstance(i, str) for i in order)
            or len(order) != len(set(order)) or set(order) != ids):
        raise RecordError('Execution order must name every selected-record leaf exactly once')
    conditions = profile.get('conditions', {})
    if not isinstance(conditions, dict) or set(conditions) - ids:
        raise RecordError('Execution conditions reference undeclared work')
    for row in conditions.values():
        if (not isinstance(row, dict) or set(row) - {'authorized', 'hold', 'capacity'}
                or any(v is not None and type(v) is not bool for v in row.values())):
            raise RecordError('Execution conditions must be explicit booleans or unknown')
    kinds = profile.get('dependencyKinds', {})
    if not isinstance(kinds, dict) or set(kinds) - ids:
        raise RecordError('Dependency meanings reference undeclared work')
    items = {i['id']: i for i in record['items']}
    for identity, mapping in kinds.items():
        if (not isinstance(mapping, dict) or set(mapping) - set(items[identity]['dependsOn'])
                or any(not isinstance(k, str) or k not in {'execution', 'completion', 'acceptance', 'unknown'} for k in mapping.values())):
            raise RecordError('Dependency meanings must map existing edges explicitly')
    milestones = {m['id'] for m in record['milestones']}
    native = profile.get('nativeMilestones', {})
    if (not isinstance(native, dict) or set(native) - milestones
            or any(v is not None and (type(v) is not int or v < 1) for v in native.values())):
        raise RecordError('Native milestone mapping must be declared, not inferred')
    obsolete = profile.get('obsoleteArtifactUrls', [])
    if not isinstance(obsolete, list) or any(not isinstance(v, str) or not v for v in obsolete):
        raise RecordError('Obsolete artifact URLs must be explicitly supplied')
    policies = profile.get('milestonePolicies', {})
    if not isinstance(policies, dict) or set(policies) - milestones:
        raise RecordError('Milestone evidence policy references unknown outcomes')
    for rule in policies.values():
        if not isinstance(rule, dict) or set(rule) != {'policy', 'revision'}:
            raise RecordError('Milestone evidence check needs policy and exact revision')
        if not isinstance(rule['revision'], str) or not re.fullmatch(r'(?:[a-f0-9]{40}|[a-f0-9]{64})', rule['revision']):
            raise RecordError('Milestone evidence check needs immutable revision')
        policy = rule['policy']
        if not isinstance(policy, dict) or set(policy) - {'allOf', 'anyOf'}:
            raise RecordError('Milestone evidence policy needs allOf/anyOf kinds')
        if any(not isinstance(v, list) or any(not isinstance(k, str) or not k for k in v) for v in policy.values()):
            raise RecordError('Milestone evidence kinds must be string arrays')


def _age(observed: str, as_of: str, days: int) -> bool:
    """Returns true for stale observations; rejects contradictory dates."""
    try:
        age = (date.fromisoformat(as_of) - date.fromisoformat(observed)).days
    except (TypeError, ValueError) as error:
        raise RecordError('Execution observations need ISO reporting/observation dates') from error
    if type(days) is not int or days < 0 or age < 0:
        raise RecordError('Execution observation cannot follow its reporting date')
    return age > days


def select_work(record: dict, profile: dict, *, current_source_sha256: str | None,
                as_of: str, freshness_days: int = 7) -> dict:
    """Selects the first eligible leaf under supplied order and conditions.

    Args:
        record: The loaded authoritative source observation.
        profile: The optional version1 queue and explicitly supplied conditions.
        current_source_sha256: The observed current source hash, or None if unknown.
        as_of: The explicit reporting date.
        freshness_days: The observation age threshold in days. Default: 7.

    Returns:
        The selected start handoff, exclusions and unchanged canonical metrics.
        Eligibility is conditional on supplied facts, not an authorization token.

    Raises:
        RecordError: If the record, profile, hash or dates are invalid.
    """
    value = summarize(record)
    _profile(value, profile)
    if current_source_sha256 is not None and (not isinstance(current_source_sha256, str)
            or not re.fullmatch(r'[a-f0-9]{64}', current_source_sha256)):
        raise RecordError('Current source needs exact SHA-256 or explicit unknown')
    stale = _age(value['source']['observedOn'], as_of, freshness_days)
    source_reasons = []
    if value['source']['sha256'] != profile['sourceSha256']:
        source_reasons.append('source-pin-conflict')
    if current_source_sha256 is None:
        source_reasons.append('current-source-unknown')
    elif current_source_sha256 != value['source']['sha256']:
        source_reasons.append('current-source-conflict')
    if stale:
        source_reasons.append('source-observation-stale')
    items = {i['id']: i for i in value['items']}
    rows, selected = [], None
    for identity in profile['order']:
        item = items[identity]
        reasons, dependencies = [], []
        status = 'eligible'
        if item['state'] in {'done', 'cancelled'} or not item['required']:
            status, reasons = 'ineligible', ['done-or-cancelled' if item['required'] else 'outside-required-scope']
        else:
            unknown, blocked = list(source_reasons), []
            if item['state'] == 'unknown':
                unknown.append('work-state-unknown')
            if item['blocked']:
                blocked.append('blocked-flag')
            conditions = profile.get('conditions', {}).get(identity, {})
            for key, expected in [('authorized', True), ('hold', False), ('capacity', True)]:
                actual = conditions.get(key)
                if actual is None:
                    unknown.append(key + '-unknown')
                elif actual != expected:
                    blocked.append(key + '-prevents-selection')
            for dependency in item['dependsOn']:
                kind = profile.get('dependencyKinds', {}).get(identity, {}).get(dependency, 'unknown')
                state = items[dependency]['state']
                dependencies.append(dict(id=dependency, meaning=kind, state=state))
                if kind == 'unknown':
                    unknown.append('dependency-meaning-unknown:' + dependency)
                elif kind == 'execution' and state != 'done':
                    (unknown if state == 'unknown' else blocked).append('execution-prerequisite:' + dependency)
            if item.get('unmappedDependencies'):
                unknown.append('unmapped-prerequisites')
            if not item.get('issueUrl') or not item.get('milestoneId') or not item.get('criterion'):
                unknown.append('canonical-mapping-or-criterion-missing')
            reasons = blocked + unknown
            status = 'blocked' if blocked else ('unknown' if unknown else 'eligible')
        row = dict(leafId=identity, status=status, reasons=reasons,
                   issueUrl=item.get('issueUrl'), milestoneId=item.get('milestoneId'),
                   criterion=item.get('criterion'), dependencyStatus=dependencies)
        rows.append(row)
        if selected is None and status == 'eligible':
            selected = deepcopy(row)
    return dict(selected=selected, candidates=rows, source=deepcopy(value['source']),
                metrics=deepcopy(value['metrics']), written=False, applicationAuthorized=False,
                limits=['Supplied conditions and current-source observation are not authenticated.',
                        'No work, acceptance, scope, credentials or remote service was changed.',
                        'Completion/acceptance edges do not grant start permission; conditions and holds still apply.'])


def check_alignment(record: dict, profile: dict, issue_snapshot: dict | None, *,
                    as_of: str, freshness_days: int = 7,
                    readme: Path | None = None, expected_module: str | None = None) -> dict:
    """Reports source-to-snapshot and marked README gaps without changing files.

    Args:
        record: The loaded authoritative source observation.
        profile: The optional version1 explicit mappings and evidence policies.
        issue_snapshot: The interpreted issue observation, or None if unavailable.
        as_of: The explicit reporting date.
        freshness_days: The observation age threshold in days. Default: 7.
        readme: The optional local README path to inspect.
        expected_module: The current generator's module paired with readme.

    Returns:
        The local findings, actual observation coverage and unchanged metrics.
        This diagnostic can contain private URLs; it is not a public projection.

    Raises:
        RecordError: If record/profile/snapshot metadata or README pairing is invalid.
    """
    value = summarize(record)
    _profile(value, profile)
    source_stale = _age(value['source']['observedOn'], as_of, freshness_days)
    findings, observed = [], {}

    def add(code, subject, status='mismatch'):
        findings.append(dict(code=code, subject=subject, status=status))

    if value['source']['sha256'] != profile['sourceSha256']:
        add('source-pin-conflict', value['project']['id'])
    if source_stale:
        add('source-observation-stale', value['project']['id'], 'unknown')
    complete, stale = False, False
    if issue_snapshot is not None:
        if (not isinstance(issue_snapshot, dict) or issue_snapshot.get('projectId') != value['project']['id']
                or not isinstance(issue_snapshot.get('source'), str) or not issue_snapshot['source']
                or type(issue_snapshot.get('complete')) is not bool or not isinstance(issue_snapshot.get('issues'), list)):
            raise RecordError('Issue snapshot needs project/source/coverage and issue rows')
        stale = _age(issue_snapshot.get('observedOn'), as_of, freshness_days)
        complete = issue_snapshot['complete'] and not stale
        for issue in issue_snapshot['issues']:
            if (not isinstance(issue, dict) or not isinstance(issue.get('url'), str) or not issue['url']
                    or issue['url'] in observed or not isinstance(issue.get('artifactUrls', []), list)
                    or any(not isinstance(u, str) for u in issue.get('artifactUrls', []))):
                raise RecordError('Issue snapshot needs distinct URLs and string artifact refs')
            leaf_ids = issue.get('leafIds')
            if 'leafIds' in issue and (not isinstance(leaf_ids, list)
                    or any(not isinstance(i, str) or not i for i in leaf_ids)
                    or len(leaf_ids) != len(set(leaf_ids))
                    or ('leafId' in issue and issue['leafId'] not in leaf_ids)):
                raise RecordError('Issue leafIds must be distinct and agree with scalar linkage')
            native = issue.get('nativeMilestone')
            if native is not None and (type(native) is not int or native < 1):
                raise RecordError('Observed native milestone must be a positive number or unknown')
            observed[issue['url']] = issue
        if stale:
            add('issue-observation-stale', value['project']['id'], 'unknown')
        if not issue_snapshot['complete']:
            add('issue-coverage-incomplete', value['project']['id'], 'unknown')
    else:
        add('issue-observation-unavailable', value['project']['id'], 'unknown')
    linked = set()
    for item in value['items']:
        identity, url = item['id'], item.get('issueUrl')
        if not url:
            add('canonical-issue-link-missing', identity)
        if url:
            linked.add(url)
        milestone = item.get('milestoneId')
        if not milestone:
            add('canonical-milestone-link-missing', identity)
        issue = observed.get(url)
        if issue is None:
            add('issue-not-observed' if not complete else 'issue-missing-from-complete-snapshot', identity,
                'unknown' if not complete else 'mismatch')
            continue
        if identity not in issue.get('leafIds', [issue.get('leafId')]):
            add('issue-leaf-link-missing-or-stale', identity)
        native_expected = profile.get('nativeMilestones', {}).get(milestone)
        declared_milestone = issue.get('milestoneId')
        if ((declared_milestone is not None and declared_milestone != milestone)
                or (declared_milestone is None and not (native_expected is not None
                    and issue.get('nativeMilestone') == native_expected))):
            add('issue-milestone-link-missing-or-stale', identity)
        if native_expected is not None and issue.get('nativeMilestone') != native_expected:
            add('native-milestone-mapping-mismatch', identity)
        if set(issue.get('artifactUrls', [])) & set(profile.get('obsoleteArtifactUrls', [])):
            add('configured-obsolete-artifact-reference', identity)
    for url, issue in observed.items():
        if url not in linked:
            add('unmapped-observed-issue', url, 'unknown')
    for milestone in value['milestones']:
        if milestone['accepted'] is True:
            rule = profile.get('milestonePolicies', {}).get(milestone['id'])
            if not rule:
                add('accepted-outcome-evidence-unassessed', milestone['id'], 'unknown')
            elif not policy_satisfied(rule['policy'], milestone.get('evidence', []), milestone['id'], rule['revision']):
                add('accepted-outcome-policy-unsatisfied', milestone['id'])
    if (readme is None) != (expected_module is None):
        raise RecordError('README check needs actual path and current generated module together')
    if readme is None:
        add('readme-not-observed', value['project']['id'], 'unknown')
    else:
        try:
            if update_readme(readme, expected_module)['changed']:
                add('readme-generated-region-drift', value['project']['id'])
        except (OSError, UnicodeError):
            add('readme-unavailable', value['project']['id'], 'unknown')
        except RecordError:
            add('readme-marker-conflict', value['project']['id'])
    return dict(findings=findings, source=deepcopy(value['source']),
                issueObservation=deepcopy(issue_snapshot), metrics=deepcopy(value['metrics']),
                written=False, applicationAuthorized=False,
                limits=['Issue mappings/coverage/policies are supplied local observations, not fetched or authenticated.',
                        'Findings never change canonical completion, native milestones or owner acceptance.',
                        'README check compares only the marked region with the supplied generator module; SVG/layout are separate checks.'])
