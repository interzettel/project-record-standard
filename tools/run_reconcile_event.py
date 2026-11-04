"""Runs the shared reconciler on a sealed host-prepared request."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from project_record.reconcile import _identity, reconcile


def main() -> int:
    """Checks the request identity again immediately before shared-core invocation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--expected', required=True)
    args = parser.parse_args()
    request = json.loads(args.request.read_text())
    if _identity(request) != args.expected:
        result = dict(status='conflict', exitCode=1, reason='Prepared request changed')
    else:
        result = reconcile(request['event'], request['profile'], apply=True)
    print(json.dumps(result))
    return result['exitCode']


if __name__ == '__main__':
    raise SystemExit(main())
