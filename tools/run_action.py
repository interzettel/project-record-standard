"""Runs the composite action's exact pipeline locally or on a CI runner."""

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from project_record.__main__ import main


def run() -> int:
    """Builds explicit inputs without evaluating them as shell source."""
    config = os.environ.get("PROJECT_RECORD_CONFIG")
    output = os.environ.get("PROJECT_RECORD_OUTPUT", ".project-record-build")
    audience = os.environ.get("PROJECT_RECORD_AUDIENCE", "owner")
    if not config:
        print("PROJECT_RECORD_CONFIG is required", file=sys.stderr)
        return 1
    arguments = ["pipeline", "--config", config, "--output", output, "--audience", audience]
    only = os.environ.get("PROJECT_RECORD_ONLY")
    if only:
        arguments += ["--only", only]
    status = main(arguments)
    if status == 0:
        manifest = str((Path(output) / "build-manifest.json").resolve())
        if os.environ.get("GITHUB_OUTPUT"):
            if "\n" in manifest or "\r" in manifest:
                raise ValueError("Output path cannot contain a newline")
            with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
                stream.write("manifest=" + manifest + "\n")
        print(json.dumps({"manifest":manifest, "githubWrites":False}))
    return status


if __name__ == "__main__":
    raise SystemExit(run())
