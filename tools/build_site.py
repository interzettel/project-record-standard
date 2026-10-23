"""Builds the canonical public example site from verified record output.

Run with --records .record-build --output .site after the public pipeline.
Requires the pinned documentation dependency in requirements-site.txt.
Only manifest-listed, hash-matching public files enter the site.
"""

import argparse
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

import markdown

from project_record.core import RecordError, export_record

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/interzettel/project-record-standard'
DOCUMENTS = [
    ('START-HERE', 'Start here'),
    ('STANDARD', 'Terminology and percentages'),
    ('GITHUB', 'Issues and GitHub Projects'),
    ('AUTOMATION', 'Automation'),
    ('ADAPTATION-PROFILES', 'New and existing projects'),
    ('AGENT-WORKFLOWS', 'Agent skills and planning'),
    ('READINESS', 'L0–L5 agent readiness'),
    ('PMI-ALIGNMENT', 'PMI alignment'),
    ('PRESENTATION', 'Brand and interaction'),
    ('ACCESSIBILITY', 'Accessibility evidence'),
    ('UPGRADING', 'Upgrades and recovery'),
    ('DELIVERY', 'Repository and delivery evidence'),
]

SITE_CSS = """
.site-nav{max-width:1160px;margin:auto;padding:14px 34px;display:flex;gap:6px 22px;flex-wrap:wrap;border-bottom:1px solid var(--border,#ccc);font:14px/1.5 system-ui,sans-serif}
.site-nav a{display:inline-flex;align-items:center;min-height:44px;color:inherit;text-underline-offset:4px}
.guide{background:#f6f7f9;color:#172638;font:17px/1.65 system-ui,sans-serif;margin:0;overflow-wrap:anywhere}
.guide *{box-sizing:border-box}.guide a{color:#244f9b;text-underline-offset:4px}.guide a:focus-visible,.guide summary:focus-visible{outline:3px solid #244f9b;outline-offset:4px}
.guide .layout{max-width:1160px;margin:auto;display:grid;grid-template-columns:220px minmax(0,1fr);gap:48px;padding:40px 34px 80px}
.guide aside nav{display:grid;gap:5px}.guide aside a{display:block;padding:8px 0;min-height:44px;font-size:14px}.guide [aria-current=page]{font-weight:750;color:#172638}
.guide article{min-width:0;max-width:78ch}.guide h1{font-size:clamp(34px,4vw,52px);line-height:1.1;letter-spacing:-.04em;margin:0 0 28px}.guide h2{font-size:26px;line-height:1.25;letter-spacing:-.025em;margin-top:42px}.guide h3{font-size:20px;margin-top:28px}
.guide pre{padding:20px;background:#e7ecf2;border:1px solid #c4ceda;overflow:auto;border-radius:8px;font-size:14px;line-height:1.6}.guide code{font-family:ui-monospace,Consolas,monospace}.guide :not(pre)>code{font-size:.88em;background:#e7ecf2;padding:2px 4px;border-radius:3px}
.guide table{display:block;overflow:auto;border-collapse:collapse;width:100%;font-size:14px}.guide td,.guide th{padding:12px;text-align:left;border:1px solid #c4ceda;vertical-align:top}.guide th{background:#e7ecf2}.guide blockquote{border-left:3px solid #244f9b;padding-left:20px;margin-left:0;color:#48596c}
.guide .doc-source{margin-top:50px;border-top:1px solid #c4ceda;padding-top:20px;font-size:13px}.guide .skip-link{position:absolute;top:-100px;background:#fff;padding:12px}.guide .skip-link:focus{top:0;z-index:10}
@media(max-width:750px){.guide .layout{grid-template-columns:minmax(0,1fr);gap:28px;padding:28px 18px 60px}.guide aside nav{grid-template-columns:repeat(2,minmax(0,1fr));gap:2px 20px}.site-nav{padding-inline:18px;gap:4px 16px}.guide article{max-width:100%}}
@media(prefers-color-scheme:dark){.guide{background:#101923;color:#edf2f7}.guide a{color:#a8c8ff}.guide [aria-current=page]{color:#edf2f7}.guide pre,.guide :not(pre)>code,.guide th{background:#202e3e}.guide td,.guide th,.guide pre,.guide .doc-source{border-color:#506176}.guide blockquote{color:#b0bfd0}.guide .skip-link{background:#101923}.guide a:focus-visible,.guide summary:focus-visible{outline-color:#a8c8ff}}
"""


def navigation(prefix: str) -> str:
    """Returns navigation relative to the current page's public directory."""
    return (f'<nav class="site-nav" aria-label="Standard website">'
            f'<a href="{prefix}index.html">Example tracker</a>'
            f'<a href="{prefix}guide/START-HERE.html">Use the standard</a>'
            f'<a href="{prefix}prehnite/progress.html">Prehnite example</a>'
            f'<a href="{REPOSITORY}">GitHub source</a></nav>')


def rewrite_links(html: str) -> str:
    """Maps authored relative documentation links to their public routes."""
    def replace(match: re.Match) -> str:
        target = match.group(1)
        parts = urlsplit(target)
        if parts.scheme or parts.netloc or not parts.path:
            return match.group(0)
        if parts.path.endswith('.md'):
            stem = Path(parts.path).stem
            if stem in {name for name, _ in DOCUMENTS}:
                target = stem + '.html'
                if parts.fragment:
                    target += '#' + parts.fragment
            else:
                relative = parts.path if parts.path.startswith('standards/') else 'standards/' + parts.path
                target = REPOSITORY + '/blob/main/' + relative
        elif not parts.path.endswith('.html'):
            target = REPOSITORY + '/blob/main/' + parts.path.removeprefix('../')
        return 'href="' + escape(target, quote=True) + '"'
    return re.sub(r'href="([^"]+)"', replace, html)


def build_site(records: Path, output: Path) -> dict:
    """Writes a public site after validating every selected record and digest.

    Args:
        records: The dedicated public pipeline output directory.
        output: A new or empty website destination.

    Returns:
        The public project IDs and number of published documentation pages.

    Raises:
        RecordError: If input is private, modified, unsafe or incomplete.
    """
    if output.exists() and any(output.iterdir()):
        raise RecordError('The website output must be new or empty')
    entries = json.loads((records / 'build-manifest.json').read_text())
    selected = {}
    projects = []
    for entry in entries:
        if entry['audience'] != 'public':
            raise RecordError('Only public pipeline output can become a website')
        project = entry['project']
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', project):
            raise RecordError('Unsafe website project ID')
        record_path = records / project / 'record.json'
        if not record_path.resolve().is_relative_to(records.resolve()):
            raise RecordError('Record input must stay inside the public build')
        record = json.loads(record_path.read_text())
        export_record(record, 'public')
        projects.append(project)
        for relative in entry['files']:
            path = Path(relative)
            if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != project:
                raise RecordError('Unsafe website path')
            source = records / path
            if source.is_symlink() or not source.resolve().is_relative_to(records.resolve()):
                raise RecordError('Website inputs must stay inside the public build')
            content = source.read_bytes()
            if sha256(content).hexdigest() != entry['sha256'][relative]:
                raise RecordError('A website input changed after the public build')
            selected[relative] = content
    if not {'standard', 'prehnite'}.issubset(projects):
        raise RecordError('The canonical website requires both public references')
    for relative, content in selected.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.endswith('/progress.html'):
            html = content.decode().replace('</head>', '<style>' + SITE_CSS + '</style></head>')
            html = html.replace('<main class="wrap"', navigation('../') + '<main class="wrap"', 1)
            content = html.encode()
        target.write_bytes(content)
    homepage = (output / 'standard/progress.html').read_text()
    homepage = homepage.replace(navigation('../'), navigation(''), 1)
    (output / 'index.html').write_text(homepage)
    (output / '.nojekyll').touch()
    (output / 'record-build-manifest.json').write_bytes((records / 'build-manifest.json').read_bytes())
    guide = output / 'guide'
    guide.mkdir()
    for name, title in DOCUMENTS:
        body = rewrite_links(markdown.markdown((ROOT / 'standards' / (name + '.md')).read_text(), extensions=['fenced_code', 'tables', 'toc', 'sane_lists']))
        menu = ''.join(f'<a href="{other}.html"' + (' aria-current="page"' if other == name else '') + f'>{escape(label)}</a>' for other, label in DOCUMENTS)
        html = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} · Project record standard</title><style>{SITE_CSS}</style></head><body class="guide"><a class="skip-link" href="#content">Skip to guide</a>{navigation("../")}<div class="layout"><aside><nav aria-label="Standard guide">{menu}</nav></aside><main id="content" tabindex="-1"><article>{body}<p class="doc-source"><a href="{REPOSITORY}/blob/main/standards/{name}.md">View this document on GitHub</a></p></article></main></div></body></html>'
        (guide / (name + '.html')).write_text(html)
    review = output / 'qa'
    review.mkdir()
    (review / 'accessibility.html').write_bytes((ROOT / 'tools/accessibility_review.html').read_bytes())
    identity = {
        'projects': projects,
        'sourceCommit': os.environ.get('GITHUB_SHA'),
        'recordInputs': entries,
        'presentation': 'Website navigation is added to the hash-verified reference pages.',
        'sha256': {path.relative_to(output).as_posix(): sha256(path.read_bytes()).hexdigest()
                   for path in sorted(output.rglob('*')) if path.is_file()},
    }
    (output / 'website-build.json').write_text(json.dumps(identity, indent=2) + '\n')
    return {'projects':projects, 'documents':len(DOCUMENTS), 'audience':'public'}


def main() -> None:
    """Builds the canonical example website at the explicit output path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_site(args.records, args.output)))


if __name__ == '__main__':
    main()
