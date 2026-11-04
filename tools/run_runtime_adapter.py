"""Prepares, delivers and recovers opt-in local runtime adapter tickets."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from project_record.runtime_adapters import capture_core, configure_hooks, deliver_ticket, inspect_runtime, prepare_ticket, rollback_hooks, ticket_status


def main() -> int:
    """Keeps native hook output quiet; explicit commands report transport results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['probe', 'pin', 'prepare', 'hook', 'retry', 'status', 'install', 'rollback'])
    parser.add_argument('--runtime', choices=['codex', 'claude-code'])
    parser.add_argument('--executable')
    parser.add_argument('--toolkit', type=Path)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--outbox', type=Path)
    parser.add_argument('--ticket', type=Path)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--command')
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        if args.operation == 'probe':
            result = inspect_runtime(args.runtime, args.executable)
        elif args.operation == 'pin':
            result = capture_core(args.toolkit)
        elif args.operation == 'prepare':
            result = prepare_ticket(json.loads(args.request.read_text()), args.outbox)
        elif args.operation in {'hook', 'retry'}:
            payload = None
            if args.operation == 'hook':
                raw = sys.stdin.read(1048577)
                try:
                    payload = json.loads(raw) if len(raw) <= 1048576 else None
                except ValueError:
                    payload = None
            result = deliver_ticket(args.ticket, payload, manual=args.operation == 'retry')
        elif args.operation == 'status':
            result = ticket_status(args.ticket)
        elif args.operation == 'install':
            result = configure_hooks(args.config, args.runtime, args.command, args.receipt, apply=args.apply)
        else:
            result = rollback_hooks(args.receipt)
    except Exception as error:
        result = dict(state='pending', exitCode=3, reason=str(error),
                      recovery='Preserve prepared ticket; inspect status and retry explicitly')
    if args.operation == 'hook':
        if result.get('exitCode', 0):
            print('PRS tracking pending; inspect the prepared ticket and retry.', file=sys.stderr)
        print('{}')
        return 0
    print(json.dumps(result, indent=2))
    return result.get('exitCode', 0)


if __name__ == '__main__':
    raise SystemExit(main())
