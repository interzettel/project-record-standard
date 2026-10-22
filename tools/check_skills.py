"""Checks the distributable skill manifest and its local instruction metadata.

Run PYTHONPATH=src python3 tools/check_skills.py from the toolkit root.
This checks packaging and discovery metadata, not agent behavior.
"""

import json
from pathlib import Path
import re

from project_record.core import RecordError

ROOT = Path(__file__).resolve().parents[1]


def check_suite(root: Path) -> dict:
    """Checks declared skills and references without modifying the source kit.

    Args:
        root: The toolkit root containing the distribution manifest.

    Returns:
        The skill count, versions and scope of metadata validation.

    Raises:
        RecordError: If declared folders, metadata or references conflict.
    """
    manifest = json.loads((root / 'skills/manifest.json').read_text())
    names = manifest['skills']
    if not names or len(names) != len(set(names)):
        raise RecordError('Skill manifest must declare unique skills')
    found = {p.name for p in (root / 'skills').iterdir() if p.is_dir()}
    if found != set(names):
        raise RecordError('Skill manifest and distribution folders disagree')
    for name in names:
        if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 63:
            raise RecordError('Unsafe skill name')
        path = root / 'skills' / name
        content = (path / 'SKILL.md').read_text()
        match = re.match(r'---\nname: ([^\n]+)\ndescription: ([^\n]+)\n---\n', content)
        if not match or match[1] != name or not match[2].startswith('Use when ') or len(match[0]) > 1024:
            raise RecordError('Unsupported skill discovery metadata: ' + name)
        if '[TODO' in content or len(content.splitlines()) > 500:
            raise RecordError('Skill contains a placeholder or exceeds the line budget: ' + name)
        interface = (path / 'agents/openai.yaml').read_text()
        if '$' + name not in interface:
            raise RecordError('Skill prompt must name its invocation: ' + name)
        for other in re.findall(r'\*\*([a-z0-9]+(?:-[a-z0-9]+)+)\*\*', content):
            if other not in names:
                raise RecordError('Missing referenced workflow: ' + other)
    return {'skills': len(names), 'suiteVersion': manifest['suiteVersion'],
            'contractVersion': manifest['contractVersion'], 'metadata': 'valid',
            'behavior': 'See audit/skills and the application evidence; metadata is not behavioral verification.'}


if __name__ == '__main__':
    print(json.dumps(check_suite(ROOT), indent=2))
