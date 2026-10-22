"""Reports project progress and collection health without refreshing inputs."""

from copy import deepcopy
from datetime import date, datetime

from .core import RecordError, summarize
from .delivery import delivery_summary


def project_status(record: dict, as_of: str, freshness_days: int = 7,
                   observation: dict | None = None) -> dict:
    """Reports named metrics, blockers and the age of the recorded observation.

    Args:
        record: The normalized last successful project observation.
        as_of: The explicit reporting date, independent of build time.
        freshness_days: The maximum observation age before a stale result.
        observation: The optional sourced collection attempt and page coverage.

    Returns:
        The source identity, metrics, evidence limits and collection state.

    Raises:
        RecordError: If dates, project identity or collection coverage conflict.
    """
    value = summarize(record)
    try:
        report_date = date.fromisoformat(as_of)
        observed = date.fromisoformat(value['source']['observedOn'])
    except (ValueError, TypeError) as error:
        raise RecordError('Status needs explicit ISO reporting and observation dates') from error
    if type(freshness_days) is not int or freshness_days < 0 or report_date < observed:
        raise RecordError('Reporting date and freshness threshold cannot precede the observation')
    age = (report_date - observed).days
    freshness = 'stale' if age > freshness_days else 'within-threshold'
    collection = {'status': 'not-reconciled', 'complete': None,
                  'note': 'No external collection receipt supplied; file age does not establish service health.'}
    if observation is not None:
        if not isinstance(observation, dict) or observation.get('projectId') != value['project']['id']:
            raise RecordError('Collection receipt must identify this project')
        if observation.get('status') not in {'success', 'partial', 'failed', 'unknown'} or not observation.get('source'):
            raise RecordError('Collection receipt needs a sourced outcome')
        try:
            attempted = datetime.fromisoformat(observation['attemptedAt'].replace('Z', '+00:00'))
        except (KeyError, ValueError, TypeError, AttributeError) as error:
            raise RecordError('Collection attempt needs a zoned timestamp') from error
        if attempted.tzinfo is None or not observed <= attempted.date() <= report_date:
            raise RecordError('Collection attempt must fall between observation and report dates')
        coverage = observation.get('coverage', {})
        if not isinstance(coverage, dict):
            raise RecordError('Collection coverage must be an object')
        read, expected = coverage.get('pagesRead'), coverage.get('pagesExpected')
        if type(read) is not int or read < 0 or (expected is not None and (type(expected) is not int or expected < 1 or read > expected)):
            raise RecordError('Collection coverage needs valid page counts or unknown expected pages')
        complete = observation['status'] == 'success' and expected is not None and read == expected
        collection = {**deepcopy(observation), 'complete': complete}
        if not complete:
            freshness = 'degraded'
    return {'project': deepcopy(value['project']), 'source': deepcopy(value['source']),
            'asOf': as_of, 'metrics': value['metrics'],
            'freshness': {'status': freshness, 'ageDays': age, 'thresholdDays': freshness_days,
                          'ageStatus': 'stale' if age > freshness_days else 'within-threshold'},
            'collection': collection,
            'blockers': [{'id': i['id'], 'title': i['title'], 'reason': i.get('note'),
                          'dependsOn': i['dependsOn'], 'owner': i.get('owner')} for i in value['items'] if i['blocked']],
            'nextActions': [{'milestoneId': m['id'], 'action': m.get('nextAction')} for m in value['milestones'] if m.get('nextAction')],
            'history': deepcopy(value.get('history', {})), 'delivery': delivery_summary(value),
            'warnings': deepcopy(value.get('warnings', [])),
            'limits': ['Completed-leaf ratios do not measure effort, cost or business value.',
                       'Collection receipts are supplied observations; this command performs no network reconciliation.',
                       'Rebuilding this report does not refresh source dates or certify acceptance.']}
