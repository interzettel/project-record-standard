"""Returns scoped offline policy diagnostics using the existing record core."""

from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re

from .build import check_output_destination
from .core import RecordError, export_record, policy_satisfied, summarize
from .timeline import comparison, make_timeline

RULES = (
    'PRS-ACCOUNT-01', 'PRS-EVIDENCE-01', 'PRS-ACCEPT-01', 'PRS-SOURCE-01',
    'PRS-SCOPE-01', 'PRS-PRIVACY-01', 'PRS-OWNED-01', 'PRS-HISTORY-01',
    'PRS-PINS-01', 'PRS-ELIGIBLE-01', 'PRS-DELIVERY-01', 'PRS-HOST-01',
    'PRS-EVENT-01', 'PRS-FRESH-01', 'PRS-TRANSPORT-01', 'PRS-FEEDBACK-01',
    'PRS-OVERHEAD-01',
)


def _digest(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def invalid_report(reason: str) -> dict:
    """Returns an input error without certifying a rule or exposing input payloads."""
    return dict(policyResultVersion=1, catalogueRevision=1, overall='invalid-input',
                exitCode=2, errors=[reason], checks=[], inputDigests={},
                operationAuthorized=False, written=False)


def _request(value: dict) -> None:
    """Rejects unknown request fields and ambiguous required-rule declarations."""
    allowed = {'policyVersion', 'record', 'before', 'requiredRules', 'gates',
               'source', 'audience', 'output', 'changes'}
    if (not isinstance(value, dict) or set(value) - allowed or 'record' not in value
            or type(value.get('policyVersion')) is not int or value['policyVersion'] != 1):
        raise RecordError('Use a policyVersion1 request with record and supported context fields')
    required = value.get('requiredRules')
    if (not isinstance(required, list) or not required
            or any(not isinstance(r, str) or r not in RULES for r in required)
            or len(required) != len(set(required))):
        raise RecordError('requiredRules must name distinct known rules and cannot be empty')
    if value.get('audience') not in {None, 'owner', 'public'}:
        raise RecordError('Policy audience must be owner, public or omitted')
    for key in ['source', 'output']:
        context = value.get(key)
        if context is not None and (not isinstance(context, dict)
                or set(context) - ({'path', 'expectedSha256'} if key == 'source' else {'path'})):
            raise RecordError('Policy file contexts need supported path/hash fields')
        if context is not None and context.get('path') is not None and (not isinstance(context['path'], str) or not context['path'] or '\x00' in context['path']):
            raise RecordError('Policy file paths must be nonempty strings')
    gates = value.get('gates')
    if gates is not None and (not isinstance(gates, list) or any(not isinstance(g, dict)
            or set(g) - {'subject', 'revision', 'policy', 'receipts'} for g in gates)):
        raise RecordError('Policy gates must be objects with subject, revision, policy and receipts')
    changes = value.get('changes', [])
    if not isinstance(changes, list) or any(not isinstance(c, dict) or set(c) != {'kind', 'id', 'reason', 'source'}
            or any(not isinstance(c[k], str) or not c[k].strip() for k in c) for c in changes):
        raise RecordError('Change explanations need kind, id, reason and source strings')


def _scope_changes(before: dict, record: dict, delta: dict) -> set[tuple[str, str]]:
    """Names changed scope fields beyond the existing count/history comparison."""
    changes = {('added', i) for i in delta['added']} | {('removed', i) for i in delta['removed']}
    changes |= {('membership', c['id']) for c in delta['scopeChanges']}
    changes |= {('cancelled', c['id']) for c in delta['stateChanges'] if c['to'] == 'cancelled'}
    changes |= {('restored', c['id']) for c in delta['stateChanges'] if c['from'] == 'cancelled' and c['to'] != 'cancelled'}
    old = {i['id']: i for i in before['items']}
    new = {i['id']: i for i in record['items']}
    for identity in old.keys() & new.keys():
        for key, kind in [('criterion', 'criterion'), ('dependsOn', 'dependencies'),
                          ('groupId', 'placement'), ('milestoneId', 'placement')]:
            if old[identity].get(key) != new[identity].get(key):
                changes.add((kind, identity))
    for category, kind, keys in [('groups', 'group-scope', []),
            ('milestones', 'milestone-scope', ['goal', 'groupIds', 'gateItemIds', 'acceptanceRule'])]:
        left = {i['id']: i for i in before[category]}
        right = {i['id']: i for i in record[category]}
        changes |= {(kind, i) for i in left.keys() ^ right.keys()}
        for identity in left.keys() & right.keys():
            if any(left[identity].get(k) != right[identity].get(k) for k in keys):
                changes.add((kind, identity))
    def classifications(value):
        if isinstance(value, list) and all(isinstance(v, str) for v in value):
            return set(value)
        return value

    if (before['project']['visibility'] != record['project']['visibility']
            or classifications(before.get('inputVisibility')) != classifications(record.get('inputVisibility'))):
        changes.add(('visibility', record['project']['id']))
    if before.get('governance') != record.get('governance'):
        changes.add(('governance', record['project']['id']))
    return changes


def _gate(gate: dict) -> dict:
    """Classifies one supplied exact-revision evidence policy without running tests."""
    subject, revision = gate.get('subject'), gate.get('revision')
    result = dict(subject=subject if isinstance(subject, str) else None,
                  revision=revision if isinstance(revision, str) else None)

    def finish(status, reason):
        return dict(result, status=status, reason=reason)

    if not isinstance(subject, str) or not subject.strip() or revision is None:
        return finish('unknown', 'Supply the exact gate subject and immutable artifact revision')
    if not isinstance(revision, str) or not re.fullmatch(r'(?:[a-fA-F0-9]{40}|(?:sha256:)?[a-fA-F0-9]{64})', revision):
        return finish('fail', 'Mutable or malformed artifact revision cannot certify evidence')
    policy = gate.get('policy')
    if policy is None:
        return finish('unknown', 'Supply the declared applicable evidence policy')
    if (not isinstance(policy, dict) or set(policy) - {'allOf', 'anyOf'}
            or any(not isinstance(v, list) or any(not isinstance(k, str) or not k for k in v) for v in policy.values())):
        return finish('fail', 'Use explicit allOf/anyOf evidence-kind arrays')
    if not policy.get('allOf') and not policy.get('anyOf'):
        return finish('unknown', 'An empty evidence policy cannot certify a required gate')
    receipts = gate.get('receipts')
    if receipts is None or receipts == []:
        return finish('unknown', 'Applicable evidence is unavailable; obtain a sourced receipt')
    if (not isinstance(receipts, list) or any(not isinstance(r, dict)
            or any(not isinstance(r.get(k), str) or not r[k] for k in ['kind', 'subject', 'revision', 'source'])
            or not isinstance(r.get('result'), str)
            or r['result'] not in {'passed', 'failed', 'partial', 'unknown'} for r in receipts)):
        return finish('fail', 'Receipts need attributed kind/subject/revision/result/source fields')
    if policy_satisfied(policy, receipts, subject, revision):
        return finish('pass', 'Supplied metadata satisfies this exact subject/revision policy only')
    kinds = set(policy.get('allOf', [])) | set(policy.get('anyOf', []))
    relevant = [r for r in receipts if r['kind'] in kinds]
    if any(r['result'] == 'failed' or r.get('supersededBy') or
           (r['result'] == 'passed' and (r['subject'] != subject or r['revision'] != revision)) for r in relevant):
        return finish('fail', 'Failed, superseded or mismatched proof cannot certify this required policy')
    return finish('unknown', 'Required kinds or passing applicable observations are missing')


def evaluate(request: dict) -> dict:
    """Evaluates explicit local inputs with no writes or model/server dependency.

    Args:
        request: The policyVersion1 JSON request and reviewed required-rule subset.
            Relative file paths resolve from the caller's working directory.

    Returns:
        The rule-ID results and canonical input digests. Exit codes are 0 for
        required predicates passing, 1 for failure, 3 for unknown and 2 for
        invalid input. No verdict authorizes the proposed operation.
    """
    try:
        _request(request)
        identities = dict(requestCanonicalSha256=_digest(request),
                          recordCanonicalSha256=_digest(request['record']))
        if request.get('before') is not None:
            identities['beforeCanonicalSha256'] = _digest(request['before'])
    except (RecordError, TypeError, ValueError) as error:
        return invalid_report(str(error))
    record, before = request['record'], request.get('before')
    required = set(request['requiredRules']) | {'PRS-ACCOUNT-01'}
    if request.get('audience') == 'public':
        required.add('PRS-PRIVACY-01')
    for key, rule in [('output', 'PRS-OWNED-01'), ('source', 'PRS-SOURCE-01'), ('gates', 'PRS-EVIDENCE-01')]:
        if request.get(key) is not None:
            required.add(rule)
    if before is not None:
        required.add('PRS-HISTORY-01')
    pending = {
        'PRS-ACCEPT-01': 'Obtain the designated acceptance observation; this interface cannot authenticate an owner',
        'PRS-SOURCE-01': 'Supply actual source path and expected SHA-256 for a read-only precondition observation',
        'PRS-PRIVACY-01': 'Declare the intended audience before assessing public input visibility',
        'PRS-OWNED-01': 'Supply an explicit output path for the shared dedicated-directory guard',
        'PRS-PINS-01': 'Use pins.verify_installation with expected/observed installation inputs; this request does not evaluate installation pins',
        'PRS-ELIGIBLE-01': 'Use execution.select_work with an explicit source/queue/conditions profile; this request does not select work',
        'PRS-DELIVERY-01': 'Use declared delivery/channel/environment observations; this request does not certify publication or deployment',
        'PRS-HOST-01': 'Verify actual required-check settings and permitted bypass through #33; no host enforcement is tested here',
        'PRS-EVENT-01': 'Retain and test event replay/recovery through #32/#34; no journal or lifecycle adapter is evaluated here',
        'PRS-FRESH-01': 'Use status.project_status with a dated collection receipt; this request performs no collection/freshness assessment',
        'PRS-TRANSPORT-01': 'Test the actual optional client/protocol transport in #40; no MCP transport is evaluated here',
        'PRS-FEEDBACK-01': 'Assess the encountered gap, privacy and duplicates through #36; no feedback relevance judgment is performed here',
        'PRS-OVERHEAD-01': 'Measure actual sessions, interventions and model/runtime coverage in #35/#37; synthetic validity cannot certify overhead reduction',
    }
    checks = {rule: dict(ruleId=rule, required=False, status='unknown',
                         scope='Predicate or context not evaluated by this request',
                         reasons=[pending.get(rule, 'Supply the required predicate context')]) for rule in RULES}

    def put(rule, status, scope, reason, **details):
        checks[rule].update(status=status, scope=scope, reasons=[reason], **details)

    normalized, previous = None, None
    try:
        normalized = summarize(record)
        previous = summarize(before) if before is not None else None
        put('PRS-ACCOUNT-01', 'pass', 'Existing record validator/accounting/reference structure',
            'Current and any supplied prior record satisfy existing structural checks')
    except (RecordError, KeyError, TypeError, ValueError, AttributeError) as error:
        put('PRS-ACCOUNT-01', 'fail', 'Existing record validator/accounting/reference structure', str(error))
    if normalized is not None:
        source = normalized['source']
        identities['declaredSource'] = {k: source.get(k) for k in ['commit', 'sha256', 'observedOn']}
    new_done, new_acceptance = set(), False
    observed_changes, missing_changes = set(), set()
    comparable = (normalized is not None and previous is not None
                  and normalized['project']['id'] == previous['project']['id'])
    if normalized is not None and previous is not None and not comparable:
        put('PRS-HISTORY-01', 'fail', 'Supplied before/after project identity',
            'Before and candidate must describe the same canonical project')
    if comparable:
        history_error = None
        try:
            left_identity = (previous['source'].get('commit'), previous['source']['sha256'])
            right_identity = (normalized['source'].get('commit'), normalized['source']['sha256'])
            if left_identity != right_identity:
                make_timeline([previous, normalized])
            elif date.fromisoformat(previous['source']['observedOn']) > date.fromisoformat(normalized['source']['observedOn']):
                raise RecordError('Prior observation cannot follow the candidate observation')
        except RecordError as error:
            history_error = str(error)
        delta = comparison(previous, normalized)
        observed_changes = _scope_changes(previous, normalized, delta)
        declared = {(c['kind'], c['id']) for c in request.get('changes', [])}
        missing_changes = observed_changes - declared
        put('PRS-HISTORY-01', 'fail' if missing_changes or history_error else 'pass',
            'Supplied before/after comparison and declared scope explanations',
            history_error or ('Explain every changed scope field and retain its source' if missing_changes else
            'Supplied prior observation/order and explicit scope explanations cover this comparison'),
            changes=[dict(kind=k, id=i) for k, i in sorted(observed_changes)],
            missingExplanations=[dict(kind=k, id=i) for k, i in sorted(missing_changes)])
        if observed_changes:
            required.add('PRS-SCOPE-01')
            put('PRS-SCOPE-01', 'fail' if missing_changes else 'unknown',
                'Scope-field change detection; authority is not authenticated',
                'Unexplained scope changes cannot pass' if missing_changes else
                'Explanations are supplied, but admission/authority must be established outside this metadata checker')
        else:
            put('PRS-SCOPE-01', 'pass', 'No scope/criteria/dependency/governance change in supplied comparison',
                'No new scope admission is claimed; routine unchanged-scope updates need no new approval here')
        old_states = {i['id']: i['state'] for i in previous['items']}
        new_done = {i['id'] for i in normalized['items'] if i['state'] == 'done' and old_states.get(i['id']) != 'done'}
        old_acceptance = {m['id']: m['accepted'] for m in previous['milestones']}
        accepted = [m for m in normalized['milestones'] if m['accepted'] is True and old_acceptance.get(m['id']) is not True]
        new_acceptance = bool(accepted)
        if new_acceptance:
            required.add('PRS-ACCEPT-01')
            old_milestones = {m['id']: m for m in previous['milestones']}
            if all(m['acceptanceRule'] == 'all-gate-items'
                   and m['id'] in old_milestones
                   and all(m.get(k) == old_milestones[m['id']].get(k) for k in ['acceptanceRule','gateItemIds','groupIds','goal'])
                   for m in accepted):
                put('PRS-ACCEPT-01', 'pass', 'Unchanged declared all-gate-items derivation only',
                    'Core derives this outcome from its existing gate rule; no owner decision is inferred')
        else:
            put('PRS-ACCEPT-01', 'not-applicable', 'No new acceptance decision in supplied comparison',
                'Historical acceptance remains unchanged and is not recertified')
    elif normalized is not None and previous is None:
        put('PRS-HISTORY-01', 'unknown', 'Prior authored observation needed',
            'Supply the prior record before assessing scope/history preservation')
        put('PRS-SCOPE-01', 'unknown', 'Prior authored observation needed',
            'Initial scope/admission cannot be authenticated from a structurally valid record')
    gates = request.get('gates')
    if new_done:
        required.add('PRS-EVIDENCE-01')
    if gates is not None or 'PRS-EVIDENCE-01' in required:
        gate_results = [_gate(g) for g in gates or []]
        subjects = {g.get('subject') for g in gates or [] if isinstance(g.get('subject'), str)}
        for identity in sorted(new_done - subjects):
            gate_results.append(dict(subject=identity, revision=None, status='unknown', reason='New Done claim needs its declared applicable evidence gate'))
        artifacts = {i['id']: i.get('implementationRevision') for i in normalized['items']} if normalized is not None else {}
        for identity in sorted(new_done & subjects):
            expected_artifact = artifacts.get(identity)
            declared = [g for g in gates or [] if g.get('subject') == identity]
            if expected_artifact is not None and not any(g.get('revision') == expected_artifact for g in declared):
                gate_results.append(dict(subject=identity, revision=expected_artifact if isinstance(expected_artifact, str) else None,
                                         status='fail', reason='New Done gate does not target the leaf declared implementation revision'))
        states = [g['status'] for g in gate_results]
        state = 'fail' if 'fail' in states else ('unknown' if not states or 'unknown' in states else 'pass')
        put('PRS-EVIDENCE-01', state, 'Supplied exact-subject/revision metadata policies, not test execution or criterion interpretation',
            'Resolve each required gate; missing data never certifies success', gates=gate_results)
    probe = request.get('source')
    if probe is not None:
        expected = probe.get('expectedSha256')
        reference = previous if previous is not None else normalized
        if expected is None or not probe.get('path') or reference is None:
            put('PRS-SOURCE-01', 'unknown', 'Read-only source precondition observation', 'Supply comparable record, actual source path and expected SHA-256')
        elif not isinstance(expected, str) or not re.fullmatch(r'[a-fA-F0-9]{64}', expected):
            put('PRS-SOURCE-01', 'fail', 'Read-only source precondition observation', 'Expected source identity must be an immutable SHA-256')
        else:
            try:
                actual = sha256(Path(probe['path']).read_bytes()).hexdigest()
                identities['observedSourceSha256'] = actual
                matched = actual == expected.lower() == reference['source']['sha256'].lower()
                put('PRS-SOURCE-01', 'pass' if matched else 'fail', 'Actual source bytes against before/current expected identity',
                    'Source bytes match the declared precondition; no lock/CAS/write is performed' if matched else 'Source identity drift: refresh/reconcile before proposing a write')
            except OSError:
                put('PRS-SOURCE-01', 'unknown', 'Read-only source precondition observation', 'Source bytes are unavailable; preserve the last observation')
    audience = request.get('audience')
    if audience == 'owner':
        put('PRS-PRIVACY-01', 'not-applicable', 'No public export requested', 'Owner-local assessment requests no public projection')
    elif audience == 'public' and normalized is not None:
        try:
            visibility = record.get('inputVisibility', [])
            if (not isinstance(visibility, list)
                    or any(not isinstance(v, str) or v not in {'public', 'private'} for v in visibility)):
                raise RecordError('Input visibility must be a list of public/private declarations')
            export_record(record, 'public')
            put('PRS-PRIVACY-01', 'pass', 'Existing declared visibility/input selection guard', 'Public export guard accepts declared input visibility; no content classification or publication performed')
        except RecordError as error:
            put('PRS-PRIVACY-01', 'fail', 'Existing declared visibility/input selection guard', str(error))
    output = request.get('output')
    if output is not None and output.get('path'):
        try:
            check_output_destination(Path(output['path']))
            put('PRS-OWNED-01', 'pass', 'Shared new/empty nonsymlink destination guard', 'Selected path is currently new/empty; no output or reservation was written')
        except RecordError as error:
            put('PRS-OWNED-01', 'fail', 'Shared new/empty nonsymlink destination guard', str(error))
        except OSError:
            put('PRS-OWNED-01', 'unknown', 'Shared destination guard', 'Output path cannot be inspected')
    for rule in required:
        checks[rule]['required'] = True
    states = [checks[r]['status'] for r in required]
    overall = 'fail' if 'fail' in states else ('unknown' if 'unknown' in states else 'pass')
    return dict(policyResultVersion=1, catalogueRevision=1, overall=overall,
                exitCode={'pass': 0, 'fail': 1, 'unknown': 3}[overall], inputDigests=identities,
                checks=[checks[r] for r in RULES], operationAuthorized=False, written=False,
                limits=['Pass concerns only required predicates and their reported scope, not all catalogue rules.',
                        'Requests, evidence, policy and authority metadata must come from reviewed host inputs; this interface authenticates none of them.',
                        'No repair, source lock/CAS, test execution, public content review, publication, host enforcement or permission grant occurs.',
                        'Reports are local diagnostics and can contain private identifiers; they are not approved public projections.'])


def evaluate_file(path: Path) -> dict:
    """Reads one explicit local request and returns the same evaluation as the API."""
    try:
        return evaluate(json.loads(path.read_text()))
    except (OSError, UnicodeError, ValueError) as error:
        return invalid_report(str(error))
