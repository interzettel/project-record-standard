"""Manages exactly two generated inspector files; parity checks never write."""

from hashlib import sha256
import json
import os
from pathlib import Path
import re
import tempfile

from .core import RecordError
from .inspector import _decode, _load_selection, inspector_model, MAX_SELECTION_BYTES
from .inspector_privacy import public_model
from .inspector_views import render_inspector, within_render_budget
from .reconcile import _path, _relative

NAMES = {'index.html','inspector-output.json'}


def _load(path):
    path = _path(str(path))
    if not path.is_file():
        raise RecordError('Profile/review input must be a regular file')
    with path.open('rb') as stream:
        data = stream.read(MAX_SELECTION_BYTES+1)
    if len(data) > MAX_SELECTION_BYTES:
        raise RecordError('Profile/review input exceeds 128KiB')
    try:
        value = _decode(data)
    except (ValueError,UnicodeError,RecursionError) as error:
        raise RecordError('Profile/review must be bounded strict UTF-8 JSON') from error
    if not isinstance(value,dict) or not within_render_budget(value):
        raise RecordError('Profile/review needs an object within the explicit depth/node/text budget')
    return value


def _brand(value):
    if value is None:
        return None
    if not isinstance(value,dict) or set(value) != {'brandVersion','name','font','light','dark'} or type(value['brandVersion']) is not int or value['brandVersion'] != 1:
        raise RecordError('Use explicit brandVersion1 tokens')
    if not isinstance(value['name'],str) or not value['name'].strip() or len(value['name'])>160 or value['font'] not in {'system','serif','mono'}:
        raise RecordError('Brand needs a short name and supported local font stack')
    value['name'].encode('utf-8')
    for mode in ['light','dark']:
        if not isinstance(value[mode],dict) or set(value[mode]) != {'background','text','link'} or any(not isinstance(c,str) or not re.fullmatch(r'#[a-fA-F0-9]{6}',c) for c in value[mode].values()):
            raise RecordError('Brand colours must be explicit six-digit hex tokens')
    return value


def _write(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.prs-inspector-', delete=False) as stream:
            temporary = Path(stream.name);stream.write(data)
        os.replace(temporary,path)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)


def _matches(path, data):
    if not path.is_file():return False
    with path.open('rb') as stream:
        return stream.read(len(data)+1)==data


def sync_profile(root, selection_file, output, *, observed_at, audience='owner', profile='private-offline', review=None, brand=None, write=False, check=False):
    """Previews, regenerates or compares a dedicated owned inspector directory."""
    if type(write) is not bool or type(check) is not bool or write and check:
        raise RecordError('Choose preview, write or read-only check')
    if (profile,audience) not in {('private-offline','owner'),('host-branded','public')}:
        raise RecordError('Private-offline needs owner audience; host-branded needs reviewed public input')
    root,selection_file,output = [_path(str(p)).resolve() for p in [root,selection_file,output]]
    selection = _load_selection(selection_file)
    inputs = {selection_file} | {_relative(root,row['path']).resolve() for row in selection['records']}
    inputs.update(_path(str(p)).resolve() for p in [review,brand] if p is not None)
    if any(output/name in inputs for name in NAMES):
        raise RecordError('Inspector outputs cannot replace any selected source/config/review/brand input')
    if output.exists():
        if not output.is_dir() or set(p.name for p in output.iterdir()) - NAMES:
            raise RecordError('Owned output refuses unrelated files or non-directory destinations')
        for name in NAMES:
            _path(str(output/name))
        if not (output/'inspector-output.json').is_file():
            raise RecordError('Existing output requires a valid generator ownership receipt')
        prior = _load(output/'inspector-output.json')
        if not isinstance(prior,dict) or type(prior.get('inspectorOutputVersion')) is not int or prior['inspectorOutputVersion'] != 1 or prior.get('generator') != 'prs-inspector' or prior.get('profile') != profile or prior.get('audience') != audience or not isinstance(prior.get('files'),dict) or set(prior['files']) != {'index.html'} or not isinstance(prior['files']['index.html'],str) or not re.fullmatch('[a-f0-9]{64}',prior['files']['index.html']):
            raise RecordError('Existing output ownership/profile does not match')
    tokens = _brand(_load(brand)) if brand is not None else None
    if audience == 'public':
        model = public_model(root,selection,_load(review) if review is not None else None,observed_at=observed_at)
    else:
        if review is not None or brand is not None:
            raise RecordError('Private-offline does not consume public review or host brand')
        model = inspector_model(root,selection,observed_at=observed_at)
    page = render_inspector(model,brand=tokens).encode('utf-8')
    receipt = dict(inspectorOutputVersion=1,generator='prs-inspector',profile=profile,audience=audience,
                   inspectedAt=observed_at,publishable=audience=='public',files={'index.html':sha256(page).hexdigest()})
    expected = {'index.html':page,'inspector-output.json':(json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode()}
    mode_changed = os.name=='posix' and output.exists() and ((output.stat().st_mode & 0o777)!=0o700 or any((output/name).is_file() and (output/name).stat().st_mode & 0o777 != 0o600 for name in NAMES))
    changed = not output.exists() or mode_changed or any(not _matches(output/name,data) for name,data in expected.items())
    if write and changed:
        new = not output.exists()
        if new:output.mkdir(mode=0o700,parents=True)
        try:
            if os.name=='posix':output.chmod(0o700)
            for name,data in expected.items():_write(output/name,data)
        except OSError:
            if new:
                for name in expected:(output/name).unlink(missing_ok=True)
                output.rmdir()
            raise
    return dict(changed=changed,written=write and changed,exitCode=1 if check and changed else model['exitCode'],
                publishable=model['publishable'],profile=profile,audience=audience,files=receipt['files'],coverage=model['coverage'])
