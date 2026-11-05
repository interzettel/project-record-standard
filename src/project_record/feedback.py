"""Routes encountered gaps without publishing private context or duplicate retries."""

from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import re
import time

from .core import RecordError
from .reconcile import _atomic, _identity, _json, _lock, _path

DESTINATION = 'interzettel/project-record-standard'
_URL = re.compile(r'https://github\.com/interzettel/project-record-standard/(?:issues|pull)/[1-9][0-9]*\Z')


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and '\x00' not in value


def _validate(encounter, profile, search):
    fields = {'feedbackVersion', 'encounterId', 'rootCause', 'classification', 'task', 'impact',
              'affectedIds', 'identity', 'rule', 'reproduction', 'workaround', 'proposedChange'}
    if not isinstance(encounter, dict) or set(encounter) - {'privateContext', 'effort'} != fields or type(encounter.get('feedbackVersion')) is not int or encounter['feedbackVersion'] != 1:
        raise RecordError('Use the exact feedbackVersion1 encounter fields')
    for key in ['encounterId', 'rootCause', 'task', 'workaround', 'proposedChange']:
        if not _text(encounter[key]):
            raise RecordError('Encounter needs ' + key)
    if not isinstance(encounter['impact'], str) or encounter['classification'] not in {'shared-standard', 'host-only', 'preference', 'uncertain'}:
        raise RecordError('Declare impact and the host judgment of defect ownership')
    if not isinstance(encounter['affectedIds'], list) or not encounter['affectedIds'] or any(not _text(v) for v in encounter['affectedIds']):
        raise RecordError('Name affected stable IDs')
    identity = encounter['identity']
    if not isinstance(identity, dict) or set(identity) != {'toolkitCommit', 'suiteVersion', 'contractVersion', 'adapterRuntime'} or any(v is not None and not _text(v) for v in identity.values()):
        raise RecordError('Known identity strings or explicit nulls are required')
    for key, required in [('rule', {'source', 'expected', 'observed'}),
                          ('reproduction', {'steps', 'actual', 'synthetic', 'limits'})]:
        obj = encounter[key]
        if not isinstance(obj, dict) or set(obj) != required or any(not _text(obj[k]) for k in required - {'synthetic'}):
            raise RecordError('Incomplete ' + key)
    if type(encounter['reproduction']['synthetic']) is not bool:
        raise RecordError('Label synthetic reproductions explicitly')
    effort = encounter.get('effort', {})
    if not isinstance(effort, dict) or set(effort) - {'trackingSeconds', 'correctionSeconds', 'ownerInterventions'} or any(type(v) not in {int, float} or not 0 <= v < 1e9 for v in effort.values()):
        raise RecordError('Effort must be explicit nonnegative observations')
    if not isinstance(profile, dict) or set(profile) != {'feedbackPolicyVersion', 'destination', 'grant', 'review', 'redactions', 'maxAttempts'} or type(profile['feedbackPolicyVersion']) is not int or profile['feedbackPolicyVersion'] != 1 or profile['destination'] != DESTINATION:
        raise RecordError('Use a host-adopted policy for the canonical destination')
    grant = profile['grant']
    if not isinstance(grant, dict) or set(grant) != {'source', 'actions'} or not _text(grant['source']) or not isinstance(grant['actions'], list) or any(v != 'create-issue' for v in grant['actions']):
        raise RecordError('Grant must name its source and supported actions')
    if not isinstance(profile['redactions'], list) or any(not _text(v) for v in profile['redactions']):
        raise RecordError('Redactions must be explicit nonempty literal strings')
    review = profile['review']
    if review is not None and (not isinstance(review, dict) or set(review) != {'reportSha256', 'source'} or not _text(review['source']) or not isinstance(review['reportSha256'], str) or not re.fullmatch('[a-f0-9]{64}', review['reportSha256'])):
        raise RecordError('Public review must bind exact sanitized report bytes')
    if type(profile['maxAttempts']) is not int or not 1 <= profile['maxAttempts'] <= 3:
        raise RecordError('Adopt a bounded attempt budget between one and three')
    keys = {'searchVersion', 'destination', 'rootCause', 'observedOn', 'source', 'coverage', 'resources', 'states', 'nextCursor', 'matches'}
    if not isinstance(search, dict) or set(search) != keys or type(search['searchVersion']) is not int or search['searchVersion'] != 1 or search['destination'] != DESTINATION or search['rootCause'] != encounter['rootCause']:
        raise RecordError('Search receipt must bind this root cause and destination')
    date.fromisoformat(search['observedOn'])
    if not _text(search['source']) or search['coverage'] not in {'complete', 'partial', 'not-inspected'} or not isinstance(search['resources'], list) or any(not isinstance(v, str) or v not in {'issues', 'pull-requests'} for v in search['resources']) or not isinstance(search['states'], list) or any(not isinstance(v, str) or v not in {'open', 'closed'} for v in search['states']) or not (search['nextCursor'] is None or _text(search['nextCursor'])) or not isinstance(search['matches'], list):
        raise RecordError('Search must preserve actual coverage and retrieval source')
    for match in search['matches']:
        if not isinstance(match, dict) or set(match) != {'rootCause', 'url'} or not _text(match['rootCause']) or not isinstance(match['url'], str) or not _URL.fullmatch(match['url']):
            raise RecordError('Existing report must name a canonical issue or PR URL')
    # Reject non-JSON values before any durable or external side effect.
    _json(encounter)
    _json(profile)
    _json(search)


def public_report(encounter: dict, redactions: list[str]) -> dict:
    """Projects only report fields, then applies host-declared literal redactions.

    This is minimization, not a classifier or a guarantee that arbitrary prose is
    safe. Publication additionally requires host review of this exact projection.
    """
    keys = ['rootCause', 'task', 'impact', 'affectedIds', 'identity', 'rule', 'reproduction', 'workaround', 'proposedChange']
    value = deepcopy({k: encounter[k] for k in keys})
    def redact(item):
        if isinstance(item, str):
            for literal in sorted(redactions, key=len, reverse=True):
                item = item.replace(literal, '[redacted]')
            return item
        if isinstance(item, dict):
            return {k: redact(v) for k, v in item.items()}
        if isinstance(item, list):
            return [redact(v) for v in item]
        return item
    return redact(value)


def _complete(search):
    return search['coverage'] == 'complete' and set(search['resources']) == {'issues', 'pull-requests'} and set(search['states']) == {'open', 'closed'} and search['nextCursor'] is None


def _existing(search):
    return next((m['url'] for m in search['matches'] if m['rootCause'] == search['rootCause']), None)


def _load(ticket):
    ticket = _path(str(ticket))
    record = json.loads(_path(str(ticket / 'feedback.json')).read_text())
    if not isinstance(record, dict) or record.get('feedbackVersion') != 1 or record.get('destination') != DESTINATION or not _text(record.get('rootCause')) or record.get('status') not in {'proposal', 'submitting', 'uncertain', 'submitted', 'linked'} or type(record.get('attempts')) is not int or not 0 <= record['attempts'] <= 3:
        raise RecordError('Malformed delivery state; preserve record for recovery')
    if ticket.name != _identity(dict(destination=DESTINATION, rootCause=record['rootCause'])):
        raise RecordError('Ticket path does not match retained root-cause identity')
    if record['reportSha256'] != _identity(record['report']):
        raise RecordError('Public report changed; preserve record and review before repair')
    return ticket, record


def prepare_feedback(encounter: dict, profile: dict, search: dict, directory: Path, *, apply: bool = False) -> dict:
    """Previews or retains one local proposal per declared root cause; never sends."""
    started = time.monotonic()
    _validate(encounter, profile, search)
    if type(apply) is not bool:
        raise RecordError('Apply must be an explicit boolean')
    if encounter['classification'] in {'host-only', 'preference'} or not encounter['impact'].strip():
        return dict(status='suppressed', reason='No impacted shared-standard gap', written=False)
    report = public_report(encounter, profile['redactions'])
    key = _identity(dict(destination=DESTINATION, rootCause=encounter['rootCause']))
    directory = _path(str(directory))
    ticket = _path(str(directory / key))
    result = dict(ticket=str(ticket), report=report, reportSha256=_identity(report), written=False,
                  status='proposal', search=search, reason='Public review and publication grant are separate host decisions')
    if not apply:
        return result
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with _lock(ticket):
        path = _path(str(ticket / 'feedback.json'))
        if path.exists():
            _, record = _load(ticket)
            identity = _identity(encounter)
            encounters = record['encounters']
            previous = encounters.get(encounter['encounterId'])
            if previous is not None and previous['sha256'] != identity:
                raise RecordError('An encounter ID cannot be reused for changed observations')
            if previous is None:
                encounters[encounter['encounterId']] = dict(sha256=identity, effort=encounter.get('effort', {}))
                if _identity(report) != record['reportSha256']:
                    encounters[encounter['encounterId']]['proposedAmendment'] = report
                record['telemetry']['reusedRootCauses'] += 1
                _atomic(path, _json(record).encode())
            return dict(ticket=str(ticket), status=record['status'], reused=True, written=previous is None,
                        report=record['report'], reportSha256=record['reportSha256'],
                        reason='Reuse the retained proposal; newer text does not replace reviewed or uncertain bytes')
        ticket.mkdir(mode=0o700, exist_ok=True)
        record = dict(feedbackVersion=1, destination=DESTINATION, rootCause=encounter['rootCause'], report=report, reportSha256=_identity(report),
                      classification=encounter['classification'], search=search, status='proposal', attempts=0,
                      encounters={encounter['encounterId']: dict(sha256=_identity(encounter), effort=encounter.get('effort', {}))},
                      telemetry=dict(preparationSeconds=time.monotonic() - started, reusedRootCauses=0, transportSeconds=[]),
                      submittedUrl=None, reason=result['reason'])
        _atomic(path, _json(record).encode())
    return dict(result, written=True)


def dispatch_feedback(ticket: Path, profile: dict, search: dict, *, transport=None) -> dict:
    """Invokes at most one host transport call after coverage, grant and byte review.

    A persisted submitting marker prevents a crash or unknown response from
    creating a duplicate on retry. The host supplies transport and credentials;
    the standard itself has no network client, token discovery or prompt loop.
    """
    ticket = _path(str(ticket))
    with _lock(ticket):
        _, record = _load(ticket)
        # Revalidate the host decisions and fresh retrieval against retained text.
        encounter = dict(record['report'], feedbackVersion=1, encounterId='validation-only', classification=record['classification'], rootCause=record['rootCause'])
        _validate(encounter, profile, search)
        def save(status, reason, **extra):
            record.update(status=status, reason=reason, **extra)
            _atomic(ticket / 'feedback.json', _json(record).encode())
            return {**dict(status=status, reason=reason, submittedUrl=record['submittedUrl'], attempts=record['attempts']), **extra}
        if record['status'] in {'submitted', 'linked'}:
            return dict(status=record['status'], submittedUrl=record['submittedUrl'], reused=True)
        existing = _existing(search)
        if existing:
            return save('linked', 'Reuse verified existing root-cause report; no comment or new issue', submittedUrl=existing, search=search)
        if record['status'] in {'submitting', 'uncertain'}:
            return save('uncertain', 'Possible remote write: inspect destination and link its receipt before any retry', search=search)
        if record['classification'] != 'shared-standard':
            return save('proposal', 'Ownership remains uncertain; keep local and continue host task', search=search)
        if not _complete(search):
            return save('proposal', 'Incomplete search cannot establish absence', search=search)
        if 'create-issue' not in profile['grant']['actions']:
            return save('proposal', 'No publication grant; retain once without prompting', search=search)
        review = profile['review']
        if review is None or review['reportSha256'] != record['reportSha256']:
            return save('proposal', 'Review the exact redacted public report before publication', search=search)
        if transport is None:
            return save('proposal', 'No host transport installed', search=search)
        if record['attempts'] >= profile['maxAttempts']:
            return save('proposal', 'Attempt budget exhausted; keep local proposal', search=search)
        request = dict(destination=DESTINATION, action='create-issue', marker='prs-feedback:' + ticket.name,
                       title='[feedback] ' + record['report']['rootCause'][:90], report=record['report'],
                       reportSha256=record['reportSha256'])
        record['attempts'] += 1
        save('submitting', 'Remote outcome not yet observed', search=search,
             grantSource=profile['grant']['source'], reviewSource=review['source'])
        started = time.monotonic()
        try:
            receipt = transport(deepcopy(request))
        except Exception:
            # Exception text can contain private transport headers or credentials.
            receipt = dict(status='unknown')
        record['telemetry']['transportSeconds'].append(time.monotonic() - started)
        if isinstance(receipt, dict) and receipt.get('status') == 'submitted' and isinstance(receipt.get('url'), str) and _URL.fullmatch(receipt['url']):
            return save('submitted', 'Host transport reported a canonical remote URL', submittedUrl=receipt['url'])
        if isinstance(receipt, dict) and receipt.get('status') == 'denied':
            return save('proposal', 'Host transport explicitly confirmed no write; retain proposal')
        return save('uncertain', 'Unknown or partial transport outcome; never blindly create again')
