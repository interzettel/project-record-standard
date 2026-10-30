"""Offline consumer reference: assess proposals, never write canonical facts.

This fixture is not a supported adapter or a transaction/idempotency service.
It only demonstrates the pinned boundary cases exercised by test_handoff.py.
"""

from copy import deepcopy
import json

from project_record.core import policy_satisfied, summarize
from project_record.status import project_status


def assess(record, handoff, events, current_source, *, issue=None,
           collection=None, as_of='2026-10-30'):
    """Returns local diagnostics for synthetic events against a pinned snapshot.

    Canonical metrics always come from record, never event status or receipt count.
    Conflicts and unknown observations withhold proposals; nothing is applied.

    Args:
        record: The loaded synthetic source, or None when never observed.
        handoff: The pinned test envelope and identity mapping.
        events: The well-shaped synthetic consumer events to assess.
        current_source: The observed current source identity, or None if unknown.
        issue: The optional supplied issue state; not a fetched observation.
        collection: The optional sourced collection receipt for project_status.
        as_of: The explicit reporting date. Default: 2026-10-30.

    Returns:
        The local pass/conflict/unknown diagnostic and compatible proposals.

    Raises:
        RecordError: If the loaded record or collection metadata is invalid.
    """
    result = dict(status='unknown', reasons=[], proposals=[], source=None,
                  metrics=None, collection=None, applicationAuthorized=False,
                  written=False)
    if record is None:
        result['reasons'].append('no-source-observation')
        return result
    value = summarize(record)
    result.update(source=deepcopy(value['source']), metrics=deepcopy(value['metrics']))
    mapping, pin = handoff['mapping'], handoff['pin']
    reasons = result['reasons']
    if value['contractVersion'] != pin['contractVersion'] or value['source']['sha256'] != pin['sourceSha256']:
        reasons.append('snapshot-pin-conflict')
    if value['project']['id'] != mapping['projectId']:
        reasons.append('project-mapping-conflict')
    if current_source is None:
        reasons.append('current-source-unknown')
    elif any(current_source.get(k) != value['source'].get(k) for k in ['sha256', 'observedOn']):
        reasons.append('current-source-conflict')
    status = project_status(value, as_of, observation=collection)
    result['collection'] = status['collection']
    result['freshness'] = status['freshness']
    if status['freshness']['ageStatus'] == 'stale':
        reasons.append('source-freshness-unknown')
    if collection is not None and not status['collection']['complete']:
        reasons.append('collection-unknown')
    leaf = next((i for i in value['items'] if i['id'] == mapping['prsLeafId']), None)
    if leaf is None:
        reasons.append('leaf-mapping-conflict')
    elif issue is not None and issue.get('state') == 'open' and leaf['state'] == 'done':
        reasons.append('issue-reopen-conflict')
    seen_events, proposed = {}, {}
    for event in events:
        event_id = event.get('id')
        payload = json.dumps(event, sort_keys=True)
        if not isinstance(event_id, str) or not event_id:
            reasons.append('event-identity-conflict')
            continue
        if event_id in seen_events and seen_events[event_id] != payload:
            reasons.append('event-replay-conflict')
        seen_events[event_id] = payload
        expected = dict(projectId=mapping['projectId'], prsLeafId=mapping['prsLeafId'],
                        consumerTaskId=mapping['consumerTaskId'], sourceSha256=pin['sourceSha256'])
        if any(event.get(k) != v for k, v in expected.items()):
            reasons.append('event-correlation-conflict')
            continue
        if leaf is None or event.get('implementationRevision') != leaf.get('implementationRevision'):
            reasons.append('implementation-revision-conflict')
            continue
        receipts = event.get('receipts', [])
        if not policy_satisfied(handoff['workPolicy'], receipts, leaf['id'], leaf['implementationRevision']):
            reasons.append('work-evidence-conflict')
            continue
        for receipt in receipts:
            kind = receipt.get('kind')
            if kind in handoff['workPolicy']['allOf'] and policy_satisfied(
                    {'allOf': [kind]}, [receipt], leaf['id'], leaf['implementationRevision']):
                proposed[json.dumps(receipt, sort_keys=True)] = deepcopy(receipt)
    if reasons:
        result['status'] = 'conflict' if any(r.endswith('conflict') for r in reasons) else 'unknown'
    else:
        result['status'] = 'pass'
        result['proposals'] = [proposed[k] for k in sorted(proposed)]
    result['reasons'] = sorted(set(reasons))
    return result
