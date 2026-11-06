"""Renders bounded owner-local views with links to exact selected source fields."""

from hashlib import sha256
from html import escape
import json
from pathlib import Path
import sysconfig

from .core import RecordError, summarize
from .delivery import delivery_summary

ROLES = {'project-record': 'work', 'project-manifest': 'provenance',
         'history': 'history', 'delivery': 'delivery', 'build-manifest': 'provenance',
         'skill-suite': 'operations', 'installation-receipt': 'operations',
         'discovery': 'discovery', 'readiness-assessment': 'readiness',
         'evidence-record': 'evidence', 'collection-observation': 'operations'}
MISSING = object()


class _Html:
    """Refuses expansion incrementally, before collecting an unbounded page."""

    def __init__(self, text='', limit=32*1024*1024):
        self.parts, self.size, self.limit = [], 0, limit
        self += text

    def __iadd__(self, text):
        size = len(text.encode('utf-8'))
        if self.size + size > self.limit:
            raise RecordError('Inspector HTML expansion exceeds its budget; narrow the selection')
        self.parts.append(text); self.size += size
        return self

    def __str__(self):
        return ''.join(self.parts)


def _join(parts):
    result = _Html(limit=4*1024*1024)
    for part in parts:
        result += part
    return str(result)


def _asset(name):
    local = Path(__file__).resolve().parents[2] / name
    installed = Path(sysconfig.get_path('data')) / 'share/project-record-standard' / name
    return (local if local.is_file() else installed).read_text(encoding='utf-8')


def within_render_budget(value):
    """Bounds source node count and depth before recursive HTML formatting."""
    pending, count, cost = [(value, 0, 0)], 0, 0
    while pending:
        value, depth, pointer_size = pending.pop(); count += 1
        cost += pointer_size + (len(value) if isinstance(value, str) else 32)
        if count > 5000 or depth > 64 or cost > 512 * 1024 or (isinstance(value, str) and len(value) > 32768):
            return False
        if isinstance(value, (dict, list)):
            if count + len(pending) + len(value) > 5000:
                return False
            children = value.items() if isinstance(value, dict) else enumerate(value)
            for k, v in children:
                if len(str(k)) > 2048:
                    return False
                pending.append((v, depth + 1, pointer_size + len(str(k)) * 2 + 1))
    return True


def assessment_shape(kind, value):
    """Recognizes explicit assessment entry points, without certifying their claims."""
    if not isinstance(value, dict):
        return False
    fields = {'discovery': {'projectId': str, 'sources': list, 'cleanupQueue': list, 'unresolvedDecisions': list},
              'readiness-assessment': {'recordKind': str, 'readinessLevel': str, 'dimensions': dict, 'autonomy': dict},
              'evidence-record': {'receipts': list},
              'collection-observation': {'projectId': str, 'status': str, 'attemptedAt': str, 'source': str, 'coverage': dict}}
    if kind not in fields or not all(isinstance(value.get(k), t) for k, t in fields[kind].items()):
        return False
    return kind != 'readiness-assessment' or value['recordKind'] == 'repository-readiness-assessment'


def make_model(report, values):
    """Keeps each observation separate and derives work metrics using shared code."""
    artifacts = []
    for declared in report['records']:
        row = dict(declared, views=[]); artifacts.append(row)
        if row['id'] not in values:
            continue
        value = values[row['id']]; row['value'] = value
        role = ROLES.get(row['kind'], 'uninterpreted')
        if row['status'] not in {'validated', 'recognized-shape'}:
            role = 'uninterpreted'
        if role == 'work':
            try:
                record = summarize(value)
                delivery = delivery_summary(record)
            except (RecordError, ValueError, TypeError, KeyError, RecursionError):
                row['views'] = [dict(role='uninterpreted', pointer='')]
                row['status'] = 'semantic-unavailable'
                continue
            row['views'] = [dict(role='work', pointer='/items', metrics=record['metrics'],
                                 items=record['items'], milestones=record['milestones']),
                            dict(role='provenance', pointer='/source'),
                            dict(role='evidence', pointer='/items'),
                            dict(role='delivery', pointer='', summary=delivery)]
            for field, name in [('history', 'history'), ('governance', 'readiness'), ('discovery', 'discovery'), ('operations', 'operations')]:
                if field in value:
                    from .inspector import _shape
                    recognized = (field == 'governance' or
                                  field == 'history' and _shape('history', value[field]) or
                                  field == 'discovery' and assessment_shape('discovery', value[field]) or
                                  field == 'operations' and assessment_shape('collection-observation', value[field]))
                    row['views'].append(dict(role=name if recognized else 'uninterpreted', pointer='/' + field,
                                             validation='existing-governance-checks' if field == 'governance' else 'entry-point-shape-only' if recognized else 'unvalidated-extra'))
        else:
            row['views'] = [dict(role=role, pointer='')]
    catalogue = json.loads(_asset('standards/inspector-inventory.json'))
    coverage = [dict(familyId=r['id'], kind=r['kind'], view=ROLES.get(r['selectorKind'], 'uninterpreted'),
                     limitation=r['schemaStatus']) for r in catalogue['records']]
    for mapping in coverage:
        if mapping['familyId'] == 'I-COLLECTION':
            mapping['view'] = 'operations with explicit collection-observation; otherwise uninterpreted'
        if mapping['familyId'] == 'I-DISCOVERY':
            mapping['view'] = 'discovery/readiness/evidence with explicit builder kind; otherwise uninterpreted'
    problems = sum(r['status'] not in {'validated', 'recognized-shape'} for r in artifacts)
    return dict(inspectorViewVersion=1, audience='owner-local', publishable=False,
                inspectedAt=report['inspectedAt'], artifacts=artifacts, coverageTable=coverage,
                coverage=dict(report['coverage'], problems=problems), exitCode=3 if problems or not artifacts else 0)


def _id(artifact, pointer=''):
    return 'source-' + sha256((artifact + '\0' + pointer).encode()).hexdigest()


def _work_id(row, identity):
    return 'work-' + sha256((row['id'] + '\0' + str(identity)).encode()).hexdigest()


def _text(value):
    if value is None:
        return 'Unknown / not supplied'
    return json.dumps(value, ensure_ascii=False, allow_nan=False) if not isinstance(value, str) else value


def _pointer(parent, key):
    return parent + '/' + str(key).replace('~', '~0').replace('/', '~1')


def _lookup(value, pointer):
    for key in pointer.split('/')[1:]:
        key = key.replace('~1', '/').replace('~0', '~')
        try:
            value = value[int(key)] if isinstance(value, list) else value[key]
        except (KeyError, ValueError, TypeError, IndexError):
            return MISSING
    return value


def _link(row, pointer, label='Source field'):
    return '<a href="#' + _id(row['id'], pointer) + '">' + escape(label) + '</a>'


def _claim(row, pointer, label, value=None, *, derived=False):
    present = _lookup(row['value'], pointer)
    # Missing fields link to the present source root; no fabricated pointer target.
    target = pointer if present is not MISSING else ''
    shown = value if derived else present
    text = 'Unknown / not supplied' if shown is MISSING else 'null (supplied)' if shown is None and not derived else _text(shown)
    return '<dt>' + escape(label) + '</dt><dd>' + escape(text) + ' · ' + _link(row, target, 'Basis ' + (pointer or '/')) + '</dd>'


def _source_tree(row, value, pointer=''):
    label = pointer or '/'
    if isinstance(value, (dict, list)):
        children = value.items() if isinstance(value, dict) else enumerate(value)
        body = _join(_source_tree(row, v, _pointer(pointer, k)) for k, v in children)
        return '<div class="source-node" id="' + _id(row['id'], pointer) + '"><h5><code>' + escape(label) + '</code> · ' + str(len(value)) + ' ' + ('members' if isinstance(value, dict) else 'entries') + '</h5>' + body + '</div>'
    return '<p class="source-field" id="' + _id(row['id'], pointer) + '"><code>' + escape(label) + '</code> <span>' + escape(json.dumps(value, allow_nan=False)) + '</span></p>'


def _fields(row, pointer, title):
    value = _lookup(row['value'], pointer)
    if value is MISSING:
        return '<p>' + escape(title) + ': Unknown / not supplied. ' + _link(row, '', 'Inspect selected source') + '</p>'
    if not isinstance(value, (dict, list)):
        return '<dl>' + _claim(row, pointer, title) + '</dl>'
    children = value.items() if isinstance(value, dict) else enumerate(value)
    fields = []
    for key, child in children:
        child_pointer = _pointer(pointer, key)
        if isinstance(child, (dict, list)):
            fields.append('<div class="semantic-group"><h5>' + escape(str(key)) + ' · ' + _link(row, child_pointer) + '</h5>' + _fields(row, child_pointer, str(key)) + '</div>')
        else:
            fields.append('<dl>' + _claim(row, child_pointer, str(key)) + '</dl>')
    return _join(fields) if fields else '<p>No entries supplied for ' + escape(title) + '. ' + _link(row, pointer) + '</p>'


def _gate_inputs(row, pointers):
    return '<p>' + _join(_link(row, pointer, 'Gate input ' + pointer) + ' ' for pointer in pointers if _lookup(row['value'], pointer) is not MISSING) + '</p>'


def _view(row, view):
    role, pointer = view['role'], view['pointer']
    body = _Html('<h3>' + escape(role.capitalize()) + '</h3>', limit=4*1024*1024)
    if view.get('validation'):
        body += '<p>View validation: ' + escape(view['validation']) + '. Embedded context does not inherit checks outside its documented shape.</p>'
    if role == 'uninterpreted':
        body += '<p>Uninterpreted declared JSON. No semantic mapping, schema certification or work credit. ' + _link(row, pointer, 'Selected source fields') + '</p>'
        return str(body)
    if role == 'work':
        body += '<p>One selected project observation; never summed with other files. Metrics are recalculated by the shared PRS core.</p><dl>'
        for name, basis in [('work', '/items'), ('ledger', '/items'), ('milestones', '/milestones')]:
            metric = view['metrics'][name]
            label = {'work': 'Required leaves', 'ledger': 'Retained leaves', 'milestones': 'Accepted milestones'}[name]
            pct = str(metric['percent']) + '%' if metric['percent'] is not None else 'Not measured'
            body += _claim(row, basis, label, f"{metric['done']}/{metric['total']} · {pct} · {metric['method']}", derived=True)
        body += '</dl><h4>Work and prerequisites</h4>'
        for n, item in enumerate(view['items']):
            p = '/items/' + str(n)
            body += '<article class="work-item" id="' + _work_id(row, item['id']) + '"><h5>' + escape(_text(item['id'])) + ' · ' + _link(row, p+'/title', _text(item['title'])) + '</h5><dl>'
            for key in ['id', 'groupId', 'milestoneId', 'state', 'sourceState', 'required', 'blocked', 'owner', 'criterion', 'dependsOn', 'unmappedDependencies', 'completionBasis', 'implementationRevision', 'evidence', 'issueUrl']:
                body += _claim(row, p + '/' + key, key)
            body += '</dl>'
            for dependency in item['dependsOn']:
                body += '<p><a href="#' + _work_id(row, dependency) + '">' + escape('Prerequisite ' + dependency) + '</a> · ' + _link(row, p+'/dependsOn', 'Declared prerequisite basis') + '</p>'
            body += '</article>'
        body += '<h4>Milestones and acceptance</h4>'
        for n, milestone in enumerate(view['milestones']):
            p = '/milestones/' + str(n)
            body += '<article><h5>' + escape(_text(milestone['id'])) + ' · ' + escape(_text(milestone['title'])) + '</h5><dl>'
            for key in ['goal', 'horizon', 'gateItemIds', 'acceptanceRule', 'sourceAccepted', 'nextAction']:
                body += _claim(row, p + '/' + key, key)
            body += _claim(row, p, 'Calculated acceptance under declared rule', milestone['accepted'], derived=True) + '</dl>'
            inputs = [p+'/acceptanceRule']
            if milestone['acceptanceRule'] == 'source-state':
                inputs.append(p+'/sourceAccepted')
            elif milestone['acceptanceRule'] == 'all-gate-items':
                index = {item['id']: n for n, item in enumerate(view['items'])}
                for j, identity in enumerate(milestone['gateItemIds']):
                    inputs += [p+'/gateItemIds/'+str(j), '/items/'+str(index[identity])+'/state']
            body += _gate_inputs(row, inputs) + '</article>'
    elif role == 'evidence' and row['kind'] == 'project-record':
        body += '<p>Receipt kind, subject, revision and result remain separate. Failed CI, merge and recommendations confer no verified, released or accepted claim.</p>'
        for n, item in enumerate(row['value']['items']):
            body += '<h4>' + escape(_text(item['id'])) + '</h4>' + _fields(row, '/items/' + str(n) + '/evidence', 'Evidence')
    elif role == 'delivery' and row['kind'] == 'project-record':
        body += '<p>Candidate readiness uses the shared delivery calculation. Publication and deployment are separate supplied observations; readiness never publishes.</p>'
        for field in ['changes', 'releasePlans', 'releases', 'deployments', 'deliveryCoverage']:
            body += '<h4>' + field + '</h4>' + _fields(row, '/' + field, field)
        body += '<h4>Calculated candidate gates</h4><dl>'
        index = {item['id']: n for n, item in enumerate(row['value']['items'])}
        for n, plan in enumerate(view['summary']['plans']):
            p = '/releasePlans/'+str(n)
            body += _claim(row, p, str(plan['id']), f"{plan['status']} · {plan['passed']}/{plan['total']} gates · candidate only", derived=True)
            original = row['value']['releasePlans'][n]
            for j, identity in enumerate(original.get('workItemIds', [])):
                body += '</dl>' + _gate_inputs(row, [p+'/workItemIds/'+str(j), '/items/'+str(index[identity])+'/state']) + '<dl>'
            for j, gate in enumerate(original.get('gates', [])):
                g = p+'/gates/'+str(j)
                body += '</dl>' + _gate_inputs(row, [p+'/revision', g+'/id', g+'/policy', g+'/receipts']) + '<dl>'
        body += '</dl>'
    else:
        notes = {'provenance': 'Source authority and locators are supplied claims; referenced files are not followed.',
                 'history': 'Listed observations only; intervening events remain unknown. Source time and render time differ.',
                 'delivery': 'Authored projection only; shape recognition does not recalculate or authenticate these receipts.',
                 'readiness': 'Readiness and risk are supplied assessments, separate from completion, acceptance and permission.',
                 'discovery': 'Collection coverage, findings, actions and decisions remain distinct; empty findings do not prove completeness.',
                 'evidence': 'Supplied receipts only; failed, missing and wrong-revision evidence is not promoted to verified work or acceptance.',
                 'operations': 'A collection attempt or installation receipt does not prove live runtime health or fresh source observations.'}
        body += '<p>' + notes[role] + '</p>' + _fields(row, pointer, role)
    return str(body)


def render_inspector(model, *, brand=None):
    """Returns a portable page; selected data never becomes executable markup or URLs."""
    css, script = _asset('web/inspector.css'), _asset('web/inspector.mjs')
    if brand is not None:
        from .inspector_profile import _brand
        brand = _brand(brand)
        for mode in ['light','dark']:
            colors=brand[mode]
            rule=':root{--paper:'+colors['background']+';--ink:'+colors['text']+';--muted:'+colors['text']+';--link:'+colors['link']+'}'
            css += rule if mode=='light' else '@media(prefers-color-scheme:dark){'+rule+'}'
            css += ':root[data-appearance="'+mode+'"]'+rule[len(':root'):]
        font={'system':'system-ui,sans-serif','serif':'Georgia,serif','mono':'ui-monospace,monospace'}[brand['font']]
        css += 'body{font-family:'+font+'}'
    head = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; img-src \'none\'; connect-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>PRS · Offline record inspector</title><style>' + css + '</style><body><a class="skip" href="#main">Skip to records</a>'
    body = _Html(head + '<header><p class="eyebrow">Project Record Standard · owner-local</p><h1>Offline record inspector</h1><p>Trace a claim to the selected source.</p><p class="notice">Contains selected raw contents, including private context. Not a public export. No permission or acceptance is granted.</p><p>Inspection time: ' + escape(model['inspectedAt']) + '. Source timestamps below are separate supplied observations.</p></header>')
    if model.get('audience') == 'public':
        # Header literals are trusted renderer text; no input content is replaced.
        header=str(body).replace('Project Record Standard · owner-local','Project Record Standard · reviewed public projection').replace('Contains selected raw contents, including private context. Not a public export. No permission or acceptance is granted.','Only explicitly reviewed normalized work/source/evidence fields are included. Other channels and extensions are omitted. Review attribution is host-supplied; no work acceptance or runtime permission is granted.')
        body=_Html(header)
    if brand is not None:
        body += '<p class="host-brand">Host: '+escape(brand['name'])+'</p>'
    body += '<nav aria-label="Inspector sections"><a href="#index">Declared files</a> <a href="#coverage">Coverage and limits</a></nav><main id="main" tabindex="-1"><section id="index"><h2>Declared files</h2><label for="find">Find a declared file</label><input id="find" type="search"><p id="results" role="status" aria-live="polite"></p><ul id="artifact-index">'
    for row in model['artifacts']:
        body += '<li><a href="#artifact-' + escape(row['id'], quote=True) + '">' + escape(row['id'] + ' · ' + row['path'] + ' · ' + row['status']) + '</a></li>'
    body += '</ul><p>Filters affect this index only. All records and source anchors remain readable. Unselected files: Not inspected. Repository coverage: Not assessed. Each artifact is an observation, not an additional credited work item.</p></section>'
    if not model['artifacts']:
        body += '<p>No files declared. Not measured.</p>'
    for row in model['artifacts']:
        body += '<section class="artifact" id="artifact-' + escape(row['id'], quote=True) + '"><h2>' + escape(row['id']) + ' · ' + escape(row['path']) + '</h2><dl>'
        for field in ['kind', 'visibility', 'status', 'validation', 'sha256', 'sourceObservedOn', 'sourceUpdatedOn', 'renderedAt', 'producerRevision', 'synthetic']:
            body += '<dt>' + field + '</dt><dd>' + escape(_text(row.get(field))) + '</dd>'
        body += '</dl><p>Metadata above combines explicit host declaration and this bounded inspection; it is not authenticated provenance.</p>'
        if 'value' in row:
            for view in row['views']:
                body += '<div class="semantic-view">' + _view(row, view) + '</div>'
            # Source stays open so fragment targets work with no client script.
            body += '<h3>Exact selected source fields</h3><p>JSON pointers into the bytes identified by the SHA-256 above; parsed JSON notation is shown, with strings escaped and null distinct from missing. Numeric literals follow Python JSON parsing and can round or underflow; the digest identifies the exact input bytes. No source URL is activated.</p>' + _source_tree(row, row['value'])
        else:
            body += '<p>No source body available for this status; no semantic claim is made. Other declared records remain available.</p>'
        body += '<p><a href="#index">Back to declared files</a></p></section>'
    body += '<section id="coverage"><h2>Coverage and limits</h2><p>All 29 reviewed producer/input families are mapped below. A view mapping is conditional on an explicit declaration and successful bounded read; it does not claim that the file was selected, fully validated or published. Other explicit assessment kinds are shape-only. Raw adapter ledgers remain uninterpreted.</p><div class="table-wrap"><table><caption>Producer-family view coverage</caption><thead><tr><th scope="col">Family</th><th scope="col">View</th><th scope="col">Validation limit</th></tr></thead><tbody>'
    for row in model['coverageTable']:
        body += '<tr><th scope="row">' + escape(row['familyId'] + ' · ' + row['kind']) + '</th><td>' + escape(row['view']) + '</td><td>' + escape(row['limitation']) + '</td></tr>'
    body += '</tbody></table></div><p>Limits: 128 literal declarations; 2MiB per file, 16MiB total read budget; 5000 source nodes and depth64 per file. Missing, malformed, digest-conflict, unsafe and unsupported states remain explicit. No network, directory scan, automatic refresh, external source navigation or browser write. Owner-local output requires a separately reviewed public projection before sharing. Public profile coverage and host deployment authority remain separate. Native screen-reader and zoom evidence is host-specific.</p></section></main><footer>PRS · inspect, then return to your work.</footer><script>' + script + '</script></body></html>'
    return str(body)
