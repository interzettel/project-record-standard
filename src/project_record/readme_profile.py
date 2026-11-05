"""Synchronizes a README and graphic without a website, runtime or version rewrite."""

from hashlib import sha256
import json
from pathlib import Path

from .adapters import load_config
from .build import render_readme
from .core import RecordError, export_record
from .readme import END, START, update_readme
from .reconcile import _atomic, _check_inputs, _inputs, _lock, _path, _relative


def sync_readme(config: Path, project_id: str, readme: Path, image: Path, *, write: bool = False) -> dict:
    """Previews/checks owned output; explicit writes preserve outside-region bytes.

    A failure between the two atomic replacements can leave stale output. The
    read-only parity gate detects that state and a rerun recovers it. This does
    not claim a multi-file transaction or install a website/CI workflow.
    """
    if type(write) is not bool:
        raise RecordError('Write must be an explicit boolean')
    config, readme, image = [_path(str(p)).resolve() for p in [config, readme, image]]
    manifest = json.loads(config.read_text())
    entries = [e for e in manifest['projects'] if e['project']['id'] == project_id]
    if len(entries) != 1 or entries[0]['presentation'].get('renderer') != 'readme':
        raise RecordError('Select exactly one explicit README-only project')
    inputs = _inputs(entries[0], config)
    declared = {config}
    for entry in manifest['projects']:
        names = [entry['sourceFile'], entry['presentation']['theme']]
        names += [point['sourceFile'] for point in entry.get('snapshots', [])]
        names += [point['path'] for point in entry.get('supplements', []) + entry.get('changeFiles', [])]
        if entry.get('previousSourceFile'):
            names.append(entry['previousSourceFile'])
        declared.update(_relative(config.parent, name).resolve() for name in names)
    if readme == image or readme in declared or image in declared:
        raise RecordError('README/image outputs cannot replace a selected source or theme')
    if not image.is_relative_to(readme.parent):
        raise RecordError('The graphic must stay in the README repository subtree')
    expected_image = './' + image.relative_to(readme.parent).as_posix()
    if entries[0]['presentation'].get('readmeImageUrl') != expected_image:
        raise RecordError('readmeImageUrl must match the selected local graphic path')
    record = export_record(load_config(config, {project_id})[0], 'public')
    theme = json.loads((config.parent / entries[0]['presentation']['theme']).read_text())
    svg, module = render_readme(record, theme)
    original = readme.read_bytes()
    preview = update_readme(readme, module)
    text = original.decode('utf-8')
    replacement = module[module.index(START):module.index(END) + len(END)]
    expected = (text[:text.index(START)] + replacement + text[text.index(END) + len(END):]).encode('utf-8')
    graphic = svg.encode('utf-8')
    image_before = image.read_bytes() if image.exists() else None
    image_changed = image_before != graphic
    changed = preview['changed'] or image_changed
    _check_inputs(inputs)
    if write and changed:
        with _lock(readme):
            if readme.read_bytes() != original or (image.read_bytes() if image.exists() else None) != image_before:
                raise RecordError('Owned output changed during preview; review and retry')
            _check_inputs(inputs)
            if image_changed:
                _atomic(image, graphic)
            if preview['changed']:
                _atomic(readme, expected)
    return dict(changed=changed, written=write and changed, readmeChanged=preview['changed'], imageChanged=image_changed,
                source=record['source'], metrics=record['metrics'], readmeSha256=sha256(expected).hexdigest(),
                imageSha256=sha256(graphic).hexdigest(), diff=preview['diff'])
