"""Inspects only declared JSON inputs; diagnostics are not a public projection."""

from datetime import date, datetime
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re

from .core import RecordError, validate
from .reconcile import _path, _relative

MAX_FILES = 128
MAX_BYTES = 2 * 1024 * 1024
MAX_SELECTION_BYTES = 128 * 1024
KINDS = frozenset({'project-record', 'project-manifest', 'history', 'delivery',
                   'build-manifest', 'skill-suite', 'installation-receipt'})


def _timestamp(value):
    if not isinstance(value, str):
        raise RecordError('Observation/render time must be an explicit zoned timestamp')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise RecordError('Observation/render time must include its timezone')


def _json_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate JSON member')
        value[key] = item
    return value


def _decode(data):
    value = json.loads(data.decode('utf-8'), object_pairs_hook=_json_object)
    # Strict JSON excludes nonfinite numbers accepted by Python's default reader.
    json.dumps(value, allow_nan=False)
    return value


def _validate_selection(selection):
    if not isinstance(selection, dict) or set(selection) != {'selectionVersion', 'records'} or type(selection['selectionVersion']) is not int or selection['selectionVersion'] != 1:
        raise RecordError('Use selectionVersion1 with an explicit records list')
    rows = selection['records']
    if not isinstance(rows, list) or len(rows) > MAX_FILES:
        raise RecordError('Selection is limited to 128 declared records')
    ids, paths = set(), set()
    required = {'id', 'path', 'kind', 'visibility'}
    optional = {'sourceObservedOn', 'sourceUpdatedOn', 'renderedAt', 'producerRevision', 'expectedSha256', 'synthetic'}
    for row in rows:
        if not isinstance(row, dict) or not required <= set(row) or set(row) - required - optional:
            raise RecordError('Use only declared selection fields')
        if not isinstance(row['id'], str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}', row['id']) or row['id'] in ids:
            raise RecordError('Selection needs unique stable artifact IDs')
        name = row['path']
        if not isinstance(name, str) or not name or '\\' in name or any(ord(c) < 32 for c in name) or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or PurePosixPath(name).as_posix() != name or any(c in name for c in '*?[]') or not name.endswith('.json') or name in paths:
            raise RecordError('Use unique literal contained JSON paths, without aliases or globs')
        if not isinstance(row['kind'], str) or not row['kind'].strip() or not isinstance(row['visibility'], str) or row['visibility'] not in {'public', 'private'}:
            raise RecordError('Declare kind and audience; an unknown kind remains unsupported')
        for key in ['sourceObservedOn', 'sourceUpdatedOn']:
            if row.get(key) is not None:
                date.fromisoformat(row[key])
        if row.get('renderedAt') is not None:
            _timestamp(row['renderedAt'])
        if row.get('producerRevision') is not None and (not isinstance(row['producerRevision'], str) or not re.fullmatch('[a-fA-F0-9]{40}|[a-fA-F0-9]{64}', row['producerRevision'])):
            raise RecordError('Known producer revisions must be immutable hex identities')
        if row.get('expectedSha256') is not None and (not isinstance(row['expectedSha256'], str) or not re.fullmatch('[a-f0-9]{64}', row['expectedSha256'])):
            raise RecordError('Expected file identity must be a lowercase SHA-256 or null')
        if row.get('synthetic') is not None and type(row['synthetic']) is not bool:
            raise RecordError('Synthetic status must be true, false or unknown')
        ids.add(row['id']); paths.add(name)


def _shape(kind, value):
    if kind == 'build-manifest':
        return isinstance(value, list) and all(isinstance(v, dict) and isinstance(v.get('project'), str) and isinstance(v.get('files'), list) and isinstance(v.get('sha256'), dict) for v in value)
    if not isinstance(value, dict):
        return False
    fields = {'history': {'coverage': str, 'snapshots': list, 'comparisons': list},
              'delivery': {'coverage': str, 'unreleased': list, 'plans': list, 'releases': list, 'deployments': list},
              'project-manifest': {'projects': list},
              'skill-suite': {'suiteVersion': str, 'contractVersion': str, 'skills': list},
              'installation-receipt': {'suiteVersion': str, 'contractVersion': str, 'suiteDigest': str, 'files': dict, 'rulesSha256': str}}
    return all(isinstance(value.get(k), t) for k, t in fields[kind].items())


def inspect_inventory(root: Path, selection: dict, *, observed_at: str) -> dict:
    """Reports selected file identity/problems without discovery or transitive reads.

    Source/render timestamps and producer identities are host declarations. The
    inspection clock neither refreshes them nor authenticates their claims.
    Only project-record delegates full contract checks to the existing core;
    other known families receive explicitly limited entry-point shape checks.
    """
    _timestamp(observed_at)
    _validate_selection(selection)
    root = _path(str(root))
    if not root.is_dir():
        raise RecordError('The selected root must be an existing directory')
    result = []
    for declaration in selection['records']:
        row = dict(declaration, contentRead=False, sha256=None, validation='none')
        result.append(row)
        if row['kind'] not in KINDS:
            row['status'] = 'unsupported-kind'
            continue
        try:
            path = _relative(root, row['path'])
            if not path.is_file():
                row['status'] = 'missing' if not path.exists() else 'not-a-regular-file'
                continue
            with path.open('rb') as stream:
                data = stream.read(MAX_BYTES + 1)
            row['contentRead'] = True
            if len(data) > MAX_BYTES:
                row['status'] = 'oversized'
                continue
            row['sha256'] = sha256(data).hexdigest()
            if row.get('expectedSha256') is not None and row['expectedSha256'] != row['sha256']:
                row['status'] = 'digest-conflict'
                continue
            try:
                value = _decode(data)
            except (ValueError, UnicodeError, RecursionError):
                row['status'] = 'malformed-json'
                continue
            if row['kind'] == 'project-record':
                if not isinstance(value, dict) or not isinstance(value.get('contractVersion'), str) or value['contractVersion'] not in {'0.1.0', '0.2.0'}:
                    row['status'] = 'unsupported-version'
                    continue
                try:
                    validate(value)
                except RecursionError:
                    row['status'] = 'validation-unavailable'
                    continue
                except (RecordError, ValueError, TypeError, KeyError):
                    row['status'] = 'invalid-record'
                    continue
                row.update(status='validated', validation='existing-core-contract')
            elif row['kind'] in {'skill-suite', 'installation-receipt'} and (not isinstance(value, dict) or type(value.get('schemaVersion')) is not int or value['schemaVersion'] != 1):
                row['status'] = 'unsupported-version'
            elif _shape(row['kind'], value):
                row.update(status='recognized-shape', validation='entry-point-shape-only')
            else:
                row['status'] = 'invalid-shape'
        except RecordError:
            row['status'] = 'unsafe-path'
        except OSError:
            row['status'] = 'unavailable'
    problems = sum(r['status'] not in {'validated', 'recognized-shape'} for r in result)
    return dict(inspectorInventoryVersion=1, audience='owner-local-diagnostic', publishable=False,
                inspectedAt=observed_at, records=result,
                coverage=dict(declared=len(result), contentRead=sum(r['contentRead'] for r in result), problems=problems,
                              unselected='not-inspected', repositoryCoverage='not-assessed'),
                exitCode=3 if problems or not result else 0,
                limits=['Only literal declared files; no recursive, glob, linked-file or network traversal.',
                        'Declared timestamps, visibility and producer identities are not authenticated or refreshed.',
                        'Shape recognition is not full schema validation, publication approval or inspector UI support.',
                        'Local diagnostics can contain private locators; no public export is implemented here.'])


def inspect_files(root: Path, selection_file: Path, *, observed_at: str) -> dict:
    """Loads a bounded explicit selection; does not infer declarations from files."""
    path = _path(str(selection_file))
    if not path.is_file():
        raise RecordError('Selection must be a regular file')
    with path.open('rb') as stream:
        data = stream.read(MAX_SELECTION_BYTES + 1)
    if len(data) > MAX_SELECTION_BYTES:
        raise RecordError('Selection file exceeds 128KiB')
    try:
        selection = _decode(data)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise RecordError('Selection must be bounded strict UTF-8 JSON') from error
    return inspect_inventory(root, selection, observed_at=observed_at)
