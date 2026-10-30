"""Runs the shared read-only policy command with the caller's explicit request.

Use python3 tools/check_policy.py --request request.json. The implementation
and exit semantics are the same as python3 -m project_record policy-check.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from project_record.__main__ import main


if __name__ == '__main__':
    raise SystemExit(main(['policy-check', *sys.argv[1:]]))
