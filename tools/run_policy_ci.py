"""Checks candidate JSON using the separately selected trusted toolkit."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from project_record.policy_ci import check_checkouts


def main() -> int:
    """Parses host-selected checkouts/profile and returns the shared policy verdict."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text())
        result = check_checkouts(args.base, args.candidate, profile)
    except (OSError, ValueError, TypeError) as error:
        result = dict(policyCIResultVersion=1, overall='invalid-input', exitCode=2, reason=str(error), written=False)
    print(json.dumps(result, indent=2))
    return result['exitCode']


if __name__ == '__main__':
    raise SystemExit(main())
