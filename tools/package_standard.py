"""Builds a deterministic reusable archive without owner-review material.

Run python3 tools/package_standard.py --output /absolute/path/standard.zip.
The archive uses an explicit file selection, public example configuration,
generic adoption notes and content checksums. It performs no publication.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]


def package(destination: Path) -> dict:
    """Writes a public-input-only source kit with reproducible ZIP metadata."""
    files = {}
    for folder in ['src', 'web', 'schemas', 'templates', 'skills', 'progress', '.github/workflows', '.github/ISSUE_TEMPLATE', 'assets']:
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and not any(p.endswith('.egg-info') for p in path.parts) and path.suffix != '.pyc':
                files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    for relative in ['.python-version', '.node-version', 'LICENSE', 'CHANGELOG.md', 'INSTALL.md', 'pyproject.toml', 'action.yml', 'MANIFEST.in', 'VERIFICATION-public.md', 'tools/run_action.py', 'tools/build_schemas.py', 'tools/check_palette.py', 'tools/check_policy.py', 'tools/package_standard.py', 'tests/test_delivery.py', 'tests/test_packaging.py', 'tests/test_site.py', 'tests/test_agents.py', 'tests/fixtures/execution/projects.json', 'tests/fixtures/execution/ledger.json', 'tests/fixtures/execution/profile.json', 'tests/fixtures/execution/issues.json', 'tests/test_status.py', 'tests/test_reconcile.py', 'tests/fixtures/reconcile/projects.json', 'tests/fixtures/reconcile/ledger.json', 'tests/fixtures/reconcile/theme.json', 'tests/test_policy.py', 'tests/test_record_layout.py', 'tests/test_pins.py', 'tests/test_handoff.py', 'tests/test_evidence_stages.py', 'tests/fixtures/evidence_stages/cases.json', 'tests/fixtures/handoff/projects.json', 'tests/fixtures/handoff/ledger.json', 'tests/fixtures/handoff/handoff.json', 'tests/fixtures/handoff/consumer_stub.py', 'tests/fixtures/record_layout/readme-research.json', 'tests/fixtures/record_layout/private-agent.json', 'tests/fixtures/record_layout/shared-repository.json', 'tests/fixtures/policy/cases.json', 'tests/metrics.test.mjs', 'tools/build_site.py', 'tools/check_readme.py', 'requirements-site.txt', 'package.json', 'package-lock.json', 'tests/accessibility.test.mjs', 'tools/accessibility_review.html']:
        files[relative] = (ROOT / relative).read_bytes()
    files['tools/check_skills.py'] = (ROOT / 'tools/check_skills.py').read_bytes()
    files['tests/test_percentages.py'] = (ROOT / 'tests/test_percentages.py').read_bytes()
    for name in ['STANDARD', 'PRESENTATION', 'GITHUB', 'PMI-ALIGNMENT', 'ADAPTATION-PROFILES', 'AUTOMATION', 'UPGRADING', 'ACCESSIBILITY', 'START-HERE', 'DELIVERY', 'AGENT-WORKFLOWS', 'READINESS', 'WORK-MODEL', 'ARCHITECTURE', 'POLICY', 'COMPATIBILITY', 'HANDOFF', 'RECORDS', 'FEEDBACK']:
        text = (ROOT / 'standards' / (name + '.md')).read_text()
        if name == 'STANDARD' and 'The last formula matches' in text:
            start = text.index('The last formula matches')
            end = text.index('\n\n', start)
            text = text[:start] + 'An equal-milestone mean, retained-ledger progress and required-scope progress are different named measures. Each project selects the measures its readers need, with exact counts and exclusions visible.' + text[end:]
        text = text.replace('The supplied public export refuses the private portfolio fixture.', 'Public export refuses private inputs.')
        files['standards/' + name + '.md'] = text.encode()
    files['standards/ADAPTATION.md'] = files['standards/ADAPTATION-PROFILES.md']
    files['README.md'] = (ROOT / 'PUBLIC-README.md').read_bytes()
    files['PUBLIC-README.md'] = files['README.md']
    config = json.loads((ROOT / 'examples/projects.json').read_text())
    config['projects'] = [e for e in config['projects'] if e['project']['visibility'] == 'public']
    files['examples/projects.json'] = (json.dumps(config, indent=2) + '\n').encode()
    for entry in config['projects']:
        selected = [entry['sourceFile'], entry['presentation']['theme']]
        selected += [s['path'] for s in entry.get('supplements', [])]
        selected += [s['path'] for s in entry.get('changeFiles', [])]
        selected += [p['sourceFile'] for p in entry.get('snapshots', [])]
        if entry.get('previousSourceFile'):
            selected.append(entry['previousSourceFile'])
        for relative in selected:
            path = ROOT / 'examples' / relative
            files['examples/' + relative] = path.read_bytes()
    files['AGENTS.md'] = (ROOT / 'AGENTS.md').read_bytes()
    checksums = ''.join(sha256(content).hexdigest() + '  ' + name + '\n' for name, content in sorted(files.items()))
    files['checksums.sha256'] = checksums.encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, 'w', compression=ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            info = ZipInfo('project-record-standard/' + name, (1980,1,1,0,0,0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, content)
    return {'path':str(destination), 'files':len(files), 'sha256':sha256(destination.read_bytes()).hexdigest(), 'audience':'public-input-only source distribution', 'published':False}


def main() -> None:
    """Parses the explicit archive path and prints its content identity."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(package(args.output),indent=2))


if __name__ == '__main__':
    main()
