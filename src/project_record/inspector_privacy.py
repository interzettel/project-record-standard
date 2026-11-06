"""Projects only structurally allowed, digest-reviewed public record fields."""

from copy import deepcopy
from hashlib import sha256
import json

from .core import RecordError, export_record, validate
from .inspector import _inspect, _validate_selection
from .inspector_views import make_model

FIELDS = {
    'project': {'id','name','visibility','repository'},
    'source': {'kind','path','commit','observedOn','updatedOn','authority','sha256'},
    'items': {'id','title','groupId','milestoneId','state','sourceState','required','blocked','dependsOn','unmappedDependencies','evidence','completionBasis','kind','criterion','owner','priority','issueUrl','note','deferReason','implementationRevision'},
    'groups': {'id','title','panel'},
    'milestones': {'id','title','goal','horizon','groupIds','gateItemIds','acceptanceRule','sourceAccepted','nextAction','unscopedWork'},
}
RECEIPT_FIELDS = {'kind','source','subject','revision','result','producer','observedOn','observedAt','supersededBy'}
ARRAY_FIELDS = {'dependsOn','unmappedDependencies','groupIds','gateItemIds','unscopedWork'}


def _scalar(value):
    return value is None or type(value) in {str, bool, int, float}


def _object(value, allowed):
    result = {}
    for key in sorted(allowed & value.keys()):
        item = value[key]
        if key == 'evidence':
            result[key] = [_object(r, RECEIPT_FIELDS) for r in item]
        elif key in ARRAY_FIELDS:
            if not isinstance(item,list) or any(not isinstance(v,str) for v in item):
                raise RecordError('Public projection requires explicit string-reference arrays')
            result[key] = list(item)
        elif _scalar(item):
            result[key] = item
        else:
            raise RecordError('Public projection does not support nested values in scalar fields')
    return result


def public_record(value):
    """Removes extensions before rendering; visibility refusal is never a scrubber."""
    export_record(value, 'public')
    result = {'contractVersion': value['contractVersion']}
    for name in ['project','source']:
        result[name] = _object(value[name], FIELDS[name])
    for name in ['items','groups','milestones']:
        result[name] = [_object(row, FIELDS[name]) for row in value[name]]
    validate(result)
    return result


def public_field_pointers(value, pointer=''):
    """Names each published primitive or empty container, never whole subtrees."""
    if isinstance(value,(dict,list)) and value:
        rows = value.items() if isinstance(value,dict) else enumerate(value)
        return [p for key,v in rows for p in public_field_pointers(v, pointer+'/'+str(key).replace('~','~0').replace('/','~1'))]
    return [pointer]


def public_model(root, selection, review, *, observed_at):
    """Requires a host-supplied review of exact bytes and every published field."""
    _validate_selection(selection)
    if not selection['records'] or any(r['visibility'] != 'public' or r['kind'] != 'project-record' for r in selection['records']):
        raise RecordError('Public inspector supports explicit public normalized records only; private and unmapped inputs are refused')
    if not isinstance(review,dict) or set(review) != {'publicReviewVersion','reviewer','decisionSource','records'} or type(review['publicReviewVersion']) is not int or review['publicReviewVersion'] != 1:
        raise RecordError('A separate host-adopted publicReviewVersion1 review is required')
    if any(not isinstance(review.get(k),str) or not review[k].strip() for k in ['reviewer','decisionSource']):
        raise RecordError('Public review needs an attributed reviewer and decision source')
    if not isinstance(review['records'],list) or len(review['records']) != len(selection['records']):
        raise RecordError('Review must cover exactly the selected public records')
    reviews = {}
    for row in review['records']:
        if not isinstance(row,dict) or set(row) != {'id','sha256','pointers'} or not isinstance(row['id'],str) or row['id'] in reviews or not isinstance(row['sha256'],str) or not isinstance(row['pointers'],list) or any(not isinstance(p,str) for p in row['pointers']) or len(row['pointers']) != len(set(row['pointers'])):
            raise RecordError('Review entries require unique identity, digest and explicit field pointers')
        reviews[row['id']] = row
    if set(reviews) != {r['id'] for r in selection['records']}:
        raise RecordError('Review identities must match the selected inputs')
    report, values = _inspect(root,selection,observed_at=observed_at,capture=True)
    clean, rows = {}, []
    for row in report['records']:
        approval = reviews[row['id']]
        if row['status'] != 'validated' or approval['sha256'] != row['sha256']:
            raise RecordError('Public input is unavailable, invalid or not the exact reviewed bytes')
        value = public_record(values[row['id']])
        if set(public_field_pointers(value)) != set(approval['pointers']):
            raise RecordError('Review must enumerate every allowed published leaf; no wildcard, unknown or missing field')
        clean[row['id']] = value
        # Local paths and free selection metadata are never part of public output.
        rows.append(dict(id=row['id'],path=row['id']+'.json',kind='project-record',visibility='public',
                         contentRead=True,sha256=row['sha256'],status='validated',validation='existing-core-contract; reviewed-public-field-projection',
                         sourceObservedOn=value['source']['observedOn']))
    result = make_model(dict(report,records=rows),clean)
    for artifact in result['artifacts']:
        artifact['views'] = [v for v in artifact['views'] if v['role'] in {'work','provenance','evidence'}]
    for family in result['coverageTable']:
        family['view'] = 'reviewed work/provenance/evidence fields' if family['familyId']=='R-RECORD' else 'not included in public profile; owner-local mapping remains separate'
    result.update(audience='public',publishable=True,projection='reviewed-normalized-fields-v1')
    return result
