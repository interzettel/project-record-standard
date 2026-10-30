"""Validates optional record homes without reading or moving host files."""

from copy import deepcopy

from .core import RecordError

CLASSES = frozenset({
    'personal-memory', 'session-context', 'instructions', 'knowledge', 'plan',
    'work', 'decisions', 'evidence', 'runbooks', 'generated',
})
_PRIVATE = {'personal-memory', 'session-context'}


def _text(value: object) -> bool:
    """Returns whether a required textual identity is present."""
    return isinstance(value, str) and bool(value.strip())


def _path(value: object) -> bool:
    """Accepts literal repository-relative paths, optionally with an anchor."""
    if not _text(value) or any(c in value for c in ['\\', ':', '\x00', '\n', '\r', '?', '%']):
        return False
    path, _, anchor = value.partition('#')
    return bool(path) and not path.startswith('/') and all(
        part not in {'', '.', '..'} for part in path.split('/')
    ) and '#' not in anchor


def validate_layout(profile: dict) -> None:
    """Checks one declared home/writer per class and explicit privacy policies.

    Args:
        profile: An optional layoutVersion 1 mapping; no file content is read.

    Raises:
        RecordError: If mapping, authority, references or publication is ambiguous.
    """
    if not isinstance(profile, dict) or type(profile.get('layoutVersion')) is not int or profile.get('layoutVersion') != 1:
        raise RecordError('Unsupported layoutVersion')
    stores = profile.get('stores')
    if not isinstance(stores, list) or any(not isinstance(s, dict) for s in stores):
        raise RecordError('Stores must be objects')
    classes = [s.get('class') for s in stores]
    if any(not isinstance(c, str) for c in classes) or set(classes) != CLASSES or len(classes) != len(CLASSES):
        raise RecordError('Map every class exactly once, including unused classes')
    owned = set()
    for store in stores:
        home = store.get('home')
        if not _text(store.get('writer')) or not _text(store.get('retention')):
            raise RecordError('A store needs writer and retention')
        if store.get('visibility') not in ('public', 'private') or any(type(store.get(k)) is not bool for k in ['git', 'publicIndex']):
            raise RecordError('Declare visibility, git and publicIndex explicitly')
        if not isinstance(home, dict) or home.get('kind') not in ('repo', 'external', 'unused'):
            raise RecordError('A home must be repo, external or unused')
        if home['kind'] == 'repo' and (not _path(home.get('path')) or home.get('scope') not in ('file', 'directory')):
            raise RecordError('Repository home must be a literal relative path')
        if home['kind'] == 'external' and not _text(home.get('reference')):
            raise RecordError('External home needs a private host reference')
        if home['kind'] != 'repo' and (store['git'] or store['publicIndex']):
            raise RecordError('External/unused homes are never selected for Git/public indexes')
        if store['visibility'] == 'private' and store['publicIndex']:
            raise RecordError('Private metadata must not enter a public index')
        if store['class'] in _PRIVATE or store.get('transient') is True:
            if store['visibility'] != 'private' or store['publicIndex']:
                raise RecordError('Personal/session/transient stores remain private')
            if store['git']:
                approval = store.get('gitApproval', {})
                if not isinstance(approval, dict) or not all(_text(approval.get(k)) for k in ['by', 'source', 'reason']):
                    raise RecordError('Private/transient Git inclusion needs an explicit attributed decision')
        fields = store.get('owns', [])
        if not isinstance(fields, list) or any(not _text(f) for f in fields):
            raise RecordError('Owned fields must be textual identities')
        if store['class'] == 'generated' and fields:
            raise RecordError('Generated views cannot own authoritative fields')
        if home['kind'] == 'repo' and home['scope'] == 'directory' and '#' in home['path']:
            raise RecordError('Directory homes cannot have a file anchor')
        for field in fields:
            if field in owned or (field.startswith('work.') and store['class'] != 'work'):
                raise RecordError('One work-field writer; plans/views cannot become a second ledger')
            owned.add(field)
    index = {}
    records = profile.get('records', [])
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise RecordError('Records must be objects')
    homes = {s['class']: s for s in stores}
    for record in records:
        kind = record.get('class')
        if not isinstance(kind, str) or kind not in CLASSES or not _text(record.get('id')) or not _text(record.get('revision')):
            raise RecordError('Record needs a known class, stable ID and revision')
        key = (kind, record['id'])
        if key in index:
            raise RecordError('Duplicate class-scoped record ID')
        store = homes[kind]
        if store['home']['kind'] != 'repo' or not _path(record.get('path')):
            raise RecordError('Indexed records need a repository home/path')
        home, path = store['home']['path'], record['path']
        if path != home and not (store['home']['scope'] == 'directory' and path.startswith(home + '/')):
            raise RecordError('Record path does not belong to its declared home')
        aliases = record.get('previousPaths', [])
        if not isinstance(aliases, list) or any(not _path(p) for p in aliases):
            raise RecordError('Previous paths must be literal repository paths')
        index[key] = record
    for key, record in index.items():
        target = record.get('supersededBy')
        if target is not None and (not _text(target) or (record['class'], target) not in index):
            raise RecordError('Unknown superseding record in the same class')
        seen = set()
        while target is not None:
            if not _text(target):
                raise RecordError('Superseding identity must be textual')
            if target in seen or target == record['id']:
                raise RecordError('Supersession cycle')
            seen.add(target)
            target = index[(record['class'], target)].get('supersededBy')


def layout_index(profile: dict, audience: str = 'public') -> list[dict]:
    """Returns approved repository locators; omits private values and counts.

    Args:
        profile: The host's mapping, kept private when it has private metadata.
        audience: public for a safe index, or owner for authorized local use.

    Returns:
        Explicit safe fields only; never external references or record contents.
    """
    validate_layout(profile)
    if audience not in {'public', 'owner'}:
        raise RecordError('Audience must be public or owner')
    stores = {s['class']: s for s in profile['stores']}
    return [dict(className=r['class'], id=r['id'], path=r['path'], revision=r['revision'])
            for r in profile.get('records', [])
            if audience == 'owner' or (stores[r['class']]['visibility'] == 'public' and stores[r['class']]['publicIndex'])]


def resolve_record(profile: dict, kind: str, identity: str, recalled_revision: str | None = None) -> dict:
    """Resolves an authorized local lookup without making recall authoritative.

    Returns:
        Current locator, stale-recall status and any explicit successor ID.
        A missing record remains unknown. This API is not a public endpoint.
    """
    validate_layout(profile)
    exact = [r for r in profile.get('records', []) if r['class'] == kind and r['id'] == identity]
    matches = exact or [r for r in profile.get('records', []) if r['class'] == kind and
                        identity in [r['path'], *r.get('previousPaths', [])]]
    if len(matches) != 1:
        return {'status': 'ambiguous' if matches else 'unknown'}
    record = matches[0]
    return {'status': 'superseded' if record.get('supersededBy') else 'current',
            'id': record['id'], 'path': record['path'], 'revision': record['revision'],
            'staleRecall': recalled_revision is not None and recalled_revision != record['revision'],
            'supersededBy': record.get('supersededBy')}


def migration_preview(before: dict, after: dict) -> list[dict]:
    """Lists mapped moves for common identities; performs no filesystem writes."""
    validate_layout(before)
    validate_layout(after)
    old = {(r['class'], r['id']): r for r in before.get('records', [])}
    result = []
    prior = {s['class']: s for s in before['stores']}
    for store in after['stores']:
        changed = [key for key in ['home', 'writer', 'visibility', 'git', 'publicIndex', 'owns', 'retention']
                   if prior[store['class']].get(key) != store.get(key)]
        if changed:
            result.append({'class': store['class'], 'action': 'policy-change-hold',
                           'fields': changed, 'applied': False})
    for record in after.get('records', []):
        previous = old.get((record['class'], record['id']))
        if previous and previous['path'] != record['path']:
            if previous['path'] not in record.get('previousPaths', []):
                raise RecordError('Moved record must retain its previous locator')
            result.append({'class': record['class'], 'id': record['id'], 'from': previous['path'],
                           'to': record['path'], 'applied': False})
    new_keys = {(r['class'], r['id']) for r in after.get('records', [])}
    for key, record in old.items():
        if key not in new_keys:
            result.append({'class': key[0], 'id': key[1], 'from': record['path'],
                           'action': 'unmapped-hold', 'applied': False})
    for record in after.get('records', []):
        if (record['class'], record['id']) not in old:
            result.append({'class': record['class'], 'id': record['id'], 'to': record['path'],
                           'action': 'new-reference', 'applied': False})
    return deepcopy(result)


def git_paths(profile: dict) -> list[str]:
    """Lists explicitly selected record paths for local review; never stages files."""
    validate_layout(profile)
    stores = {s['class']: s for s in profile['stores']}
    return sorted({r['path'].split('#')[0] for r in profile.get('records', [])
                   if stores[r['class']]['git']})
