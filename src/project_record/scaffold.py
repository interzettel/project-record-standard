"""Bootstraps empty projects and reports non-destructive adaptation work."""

from datetime import date
import json
from pathlib import Path
import re

from .adapters import load_config
from .core import RecordError, summarize
from .governance import DOMAINS


def initialize(directory: Path, identity: str, name: str, owner: str, observed_on: str) -> dict:
    """Creates an unapproved empty scope without replacing existing files.

    Args:
        directory: A new or empty project directory.
        identity: The stable project ID used for output paths.
        name: The project's display name.
        owner: The named person or role accountable for setup.
        observed_on: The explicitly supplied ISO calendar date.

    Returns:
        Created paths and the remaining owner decisions.
    """
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", identity):
        raise RecordError("Project ID must be a safe output-directory name")
    date.fromisoformat(observed_on)
    if directory.exists() and any(directory.iterdir()):
        raise RecordError("Cold setup requires an empty directory; use the hot adoption plan for existing work")
    governance = {"purpose": "Define the intended value with the owner before approving scope.",
                  "owner": owner, "acceptanceAuthority": owner, "changeAuthority": owner,
                  "approach": "adaptive", "successCriteria": [], "wbsCoverage": "not-assessed",
                  "workPackages": [], "baselines": [], "changeRequests": [], "risks": [],
                  "tailoring": {d: {"status": "not-assessed", "reason": "Owner setup decision remains open."} for d in DOMAINS},
                  "operations": {"status": "not-assessed", "reason": "Define service ownership, support and rollback before operation."}}
    ledger = {"contractVersion": "0.2.0", "items": [], "groups": [], "milestones": [],
              "warnings": ["Scope has not been defined or approved. Empty progress is not measured."], "governance": governance}
    theme = {"font": "system-ui, sans-serif", "light": {"background":"#ffffff", "surface":"#ffffff", "text":"#202020", "muted":"#555555", "border":"#aaaaaa", "accent":"#202020", "accentText":"#ffffff", "signal":"#202020", "signalText":"#202020"},
             "notes": "Neutral README fallback only. The host owns its presentation; replace these tokens with its approved brand."}
    config = {"projects": [{"adapter": "normalized-v1", "sourceFile": "ledger.json",
                           "project": {"id":identity, "name":name, "repository":None, "visibility":"private"},
                           "source": {"kind":"file-snapshot", "path":"progress/ledger.json", "commit":None, "observedOn":observed_on, "updatedOn":observed_on, "authority":"Authored local ledger; no approved baseline yet"},
                           "presentation": {"renderer":"host", "theme":"theme.json", "readmeMetric":"work", "progressUrl":None}}]}
    files = {"progress/ledger.json": ledger, "progress/project-record.json": config, "progress/theme.json": theme}
    for relative, content in files.items():
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content, indent=2) + "\n")
    (directory / "README.md").write_text(f"# {name}\n\nDefine the project's purpose and operating boundary.\n\n<!-- project-record:start -->\nTracking setup is awaiting scoped work and owner decisions.\n<!-- project-record:end -->\n")
    return {"mode":"cold", "created":list(files) + ["README.md"], "remaining":["Define value, stakeholders and success criteria.", "Define deliverables, work packages and evidence gates.", "Tailor the seven management domains and operations responsibilities.", "Review visibility and establish the first approved scope baseline.", "Install the vendored action and connect the existing or new host renderer deliberately."]}


def adoption_plan(config: Path) -> dict:
    """Reports a hot adoption plan without editing sources or issuing approvals."""
    records = load_config(config.resolve())
    return {"mode":"hot", "writesPerformed":False, "projects":[{
        "id":r["project"]["id"], "source":r["source"], "before":summarize(r)["metrics"],
        "governanceMapped":"governance" in r, "historyObservations":len(r.get("history", {}).get("snapshots", [])),
        "requiredReview":["Inventory existing authority, brand, site routes and generated-file ownership.",
                          "Map stable IDs and native GitHub fields without renaming them by default.",
                          "Record old/new counts, exclusions, unmapped meaning and approval boundaries.",
                          "Prepare additive integration, an explicit cutover and a rollback to the previous renderer.",
                          "For repair, replay the pinned sources and preserve history instead of resetting progress.",
                          "Review public output, keyboard interaction, text zoom and existing site behavior."]} for r in records]}
