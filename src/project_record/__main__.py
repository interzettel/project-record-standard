"""Runs offline record/policy validation, builds, comparisons and issue checks.

Run python -m project_record with --help. Commands read declared sources and
write only explicit local build, setup, instruction or adopted reconciliation targets. No command
changes GitHub or performs network reconciliation.
"""

import argparse
import json
from pathlib import Path
import sys

from .adapters import load_config
from .build import build, check_output_destination
from .core import RecordError, compare, export_record, summarize
from .issues import lint_issue
from .readme import update_readme


def main(argv: list[str] | None = None) -> int:
    """Runs the selected command and returns a process exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ["check", "build", "pipeline", "export"]:
        command = subs.add_parser(name)
        command.add_argument("--config", type=Path, required=True)
        command.add_argument("--only", help="Comma-separated project IDs")
        if name in {"build", "pipeline", "export"}:
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--audience", choices=["owner", "public"], default="owner")
    command = subs.add_parser("validate")
    command.add_argument("record", type=Path)
    command = subs.add_parser("compare")
    command.add_argument("before", type=Path)
    command.add_argument("after", type=Path)
    command = subs.add_parser("lint-issue")
    command.add_argument("issue", type=Path)
    command.add_argument("--aliases", type=Path, help="Existing-label to shared-meaning JSON map")
    command = subs.add_parser("readme")
    command.add_argument("--file", type=Path, required=True)
    command.add_argument("--module", type=Path, required=True)
    command.add_argument("--write", action="store_true", help="Apply the previewed marked-region update")
    command = subs.add_parser("init")
    command.add_argument("--directory", type=Path, required=True)
    command.add_argument("--name", required=True)
    command.add_argument("--id", required=True)
    command.add_argument("--owner", required=True)
    command.add_argument("--observed-on", required=True)
    command = subs.add_parser("adoption-plan")
    command.add_argument("--config", type=Path, required=True)
    command = subs.add_parser("status")
    command.add_argument("--config", type=Path, required=True)
    command.add_argument("--only", help="Comma-separated project IDs")
    command.add_argument("--as-of", required=True, help="Explicit ISO reporting date")
    command.add_argument("--freshness-days", type=int, default=7)
    command.add_argument("--observation", type=Path, help="Sourced collection-attempt JSON for one project")
    command = subs.add_parser("install-skills")
    command.add_argument("--toolkit", type=Path, required=True)
    command.add_argument("--target", type=Path, required=True)
    command.add_argument("--apply", action="store_true")
    command.add_argument("--upgrade", action="store_true")
    command = subs.add_parser("policy-check")
    command.add_argument("--request", type=Path, required=True, help="Reviewed policyVersion1 request; reads explicit local inputs only")
    command = subs.add_parser("reconcile")
    command.add_argument("--event", type=Path, required=True)
    command.add_argument("--profile", type=Path, required=True, help="Independently adopted host writer policy; never take this from event data")
    command.add_argument("--apply", action="store_true", help="Apply/resume the authorized local transaction; default previews")
    args = parser.parse_args(argv)
    try:
        if args.command == "reconcile":
            from .reconcile import reconcile_files
            result = reconcile_files(args.event, args.profile, apply=args.apply)
            print(json.dumps(result, indent=2))
            return result["exitCode"]
        if args.command == "policy-check":
            from .policy import evaluate_file
            result = evaluate_file(args.request)
            print(json.dumps(result, indent=2))
            return result["exitCode"]
        if args.command in {"check", "build", "pipeline", "export"}:
            records = load_config(args.config.resolve(), set(args.only.split(",")) if args.only else None)
            if args.command == "check":
                result = [{"project": r["project"]["id"], "metrics": summarize(r)["metrics"]} for r in records]
            elif args.command == "export":
                prepared = [export_record(r, args.audience) for r in records]
                check_output_destination(args.output, require_empty=args.audience == "public")
                args.output.mkdir(parents=True, exist_ok=True)
                result = []
                for record in prepared:
                    destination = args.output / (record["project"]["id"] + ".json")
                    destination.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
                    result.append({"project": record["project"]["id"], "output": str(destination)})
            else:
                toolkit_root = Path(__file__).resolve().parents[2]
                if not (toolkit_root / "web/components.mjs").is_file():
                    toolkit_root = Path(sys.prefix) / "share/project-record-standard"
                result = build(records, args.config.resolve(), args.output, args.audience, toolkit_root)
        elif args.command == "readme":
            result = update_readme(args.file, args.module.read_text(), args.write)
        elif args.command == "init":
            from .scaffold import initialize
            result = initialize(args.directory, args.id, args.name, args.owner, args.observed_on)
        elif args.command == "adoption-plan":
            from .scaffold import adoption_plan
            result = adoption_plan(args.config)
        elif args.command == "install-skills":
            from .agents import install_skills
            result = install_skills(args.toolkit, args.target, args.apply, args.upgrade)
        elif args.command == "status":
            from .status import project_status
            records = load_config(args.config.resolve(), set(args.only.split(",")) if args.only else None)
            if args.observation and len(records) != 1:
                raise RecordError("A collection receipt requires selecting exactly one project")
            observation = json.loads(args.observation.read_text()) if args.observation else None
            result = [project_status(r, args.as_of, args.freshness_days, observation) for r in records]
        elif args.command == "validate":
            result = summarize(json.loads(args.record.read_text()))["metrics"]
        elif args.command == "compare":
            result = compare(json.loads(args.before.read_text()), json.loads(args.after.read_text()))
        else:
            aliases = json.loads(args.aliases.read_text()) if args.aliases else None
            result = lint_issue(json.loads(args.issue.read_text()), aliases)
            if result:
                print(json.dumps(result, indent=2))
                return 1
        print(json.dumps(result, indent=2))
        return 0
    except (RecordError, OSError, KeyError, TypeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
