"""Maps two existing ledgers into the shared contract without rewriting them."""

from hashlib import sha256
from pathlib import Path
import json
import re

from .core import RecordError


PREHNITE_DISPLAY_TITLES = {
    "P1-M01-R01": "Compare lawful models and applicable runtimes",
    "P1-M01-R02": "Approve the model and benchmark protocol",
    "P1-M02-E01": "Measure three identical SDXL generation runs",
    "P1-M02-A01": "Review the measured 8 GiB baseline",
    "P1-M03-R01": "Choose one measurable optimization",
    "P1-M03-B01": "Add a reversible optimization setting",
    "P1-M03-E01": "Compare the baseline and optimization",
    "P1-M04-B01": "Expose a ten-image recipe-to-export workflow",
    "P1-M04-B02": "Verify batch interruption and recovery",
    "P1-M04-E01": "Observe a real ten-image local batch",
    "P1-M05-A01": "Review useful-image yield and workflow value",
    "P1-M05-A02": "Accept the local installation and limitations",
    "P2-M01-R01": "Choose a licensed model and LoRA combination",
    "P2-M01-R02": "Define controlled experiments and privacy boundaries",
    "P2-M02-B01": "Pin model and LoRA identities in each recipe",
    "P2-M02-B02": "Build parameter grids and contact sheets",
    "P2-M02-E01": "Measure multi-seed style consistency",
    "P2-M03-B01": "Add local-only reference-image import",
    "P2-M03-E01": "Observe approved appearance variations",
    "P2-M03-A01": "Review identity consistency and requested variations",
}


def _prehnite_title(task: dict) -> str:
    """Summarizes the display title while retaining the source criterion."""
    if task["id"] in PREHNITE_DISPLAY_TITLES:
        return PREHNITE_DISPLAY_TITLES[task["id"]]
    text = re.sub(r"^(?:Previously verified|Original atomic work) [^:]+:\s*", "", task["acceptance"])
    return re.split(r"[.;]", text, maxsplit=1)[0].strip()


def _base(data: bytes, project: dict, source: dict) -> dict:
    return {"contractVersion": "0.2.0", "project": project,
            "source": {**source, "sha256": sha256(data).hexdigest()},
            "groups": [], "milestones": [], "items": [], "warnings": []}


def _item(identity: str, title: str, group: str, milestone: str | None,
          state: str, **extra) -> dict:
    return {"id": identity, "title": title, "groupId": group,
            "milestoneId": milestone, "state": state, "sourceState": state,
            "required": True, "blocked": False, "dependsOn": [],
            "unmappedDependencies": [], "evidence": [], "completionBasis": "source-reported",
            "kind": "implementation", "owner": None, "priority": None,
            "issueUrl": None, "criterion": None, "note": None,
            "deferReason": None, **extra}


def prehnite(data: bytes, project: dict, source: dict) -> dict:
    """Preserves milestone gates and typed task receipts in Prehnite v2."""
    raw = json.loads(data)
    record = _base(data, project, source)
    mapping = {"verified": "done", "planned": "backlog", "active": "active", "blocked": "backlog"}
    for milestone in raw["milestones"]:
        identity = milestone["id"]
        record["groups"].append({"id": identity + ":work", "title": milestone["workstream"], "panel": milestone["phase"]})
        record["milestones"].append({
            "id": identity, "title": milestone["title"], "goal": milestone["objective"],
            "horizon": "Now" if milestone["phase"] == "P1" else "Later",
            "groupIds": [identity + ":work"], "gateItemIds": milestone["gate_tasks"],
            "acceptanceRule": "source-state", "sourceAccepted": milestone["state"] == "verified",
            "nextAction": milestone["next_action"], "unscopedWork": [],
            "priority": "P" + str(milestone["priority"]),
            "sourceState": milestone["state"], "evidence": milestone.get("evidence", []),
        })
    for task in raw["tasks"]:
        if task["state"] not in mapping:
            raise RecordError("Unmapped Prehnite state: " + task["state"])
        evidence = [{"kind": e["type"], "source": e.get("url") or e.get("path") or e.get("description") or json.dumps(e, ensure_ascii=False), "sourceRecord": e} for e in task.get("evidence", [])]
        record["items"].append(_item(
            task["id"], _prehnite_title(task), task["milestone"] + ":work", task["milestone"],
            mapping[task["state"]], sourceState=task["state"], kind=task["kind"],
            blocked=task["state"] == "blocked", dependsOn=task["depends_on"],
            owner=task.get("owner"), criterion=task["acceptance"], evidence=evidence,
            completionBasis="typed-source-evidence" if evidence else "not-complete",
            issueUrl=f"https://github.com/{project['repository']}/issues/{task['issue']}" if task.get("issue") else None,
            note=task.get("note") or task.get("blocker"),
            titleOrigin="adapter-summary; full source criterion retained",
        ))
    record["warnings"].append("Milestone horizon groups follow source phases; task verification does not grant milestone acceptance.")
    return record


def portfolio(data: bytes, project: dict, source: dict) -> dict:
    """Retains portfolio milestones, Later exclusions and equal weighting."""
    raw = json.loads(data)
    record = _base(data, project, source)
    milestones = raw.get("roadmap", {}).get("milestones", [])
    group_owner = {g: m["id"] for m in milestones for g in m["groups"]}
    mapping = {"done": "done", "active": "active", "planned": "backlog", "blocked": "backlog"}
    for panel in raw["panels"]:
        for group in panel["groups"]:
            record["groups"].append({"id": group["code"], "title": group["name"], "panel": panel["name"]})
            for task in group["tasks"]:
                if task["state"] not in mapping:
                    raise RecordError("Unmapped portfolio state: " + task["state"])
                record["items"].append(_item(
                    task["id"], task["name"], group["code"], group_owner.get(group["code"]),
                    mapping[task["state"]], sourceState=task["state"],
                    required="later" not in task, deferReason=task.get("later"),
                    blocked=task["state"] == "blocked", dependsOn=task.get("dependsOn", []),
                    dependencyCoverage="declared" if "dependsOn" in task else "not-declared",
                    owner=task.get("owner"), priority=task.get("priority"), note=task.get("note"),
                    aliases=task.get("was", []),
                ))
    for milestone in milestones:
        record["milestones"].append({
            "id": milestone["id"], "title": milestone["name"], "goal": milestone["goal"],
            "horizon": milestone["horizon"], "groupIds": milestone["groups"],
            "gateItemIds": milestone["gate"], "acceptanceRule": "all-gate-items",
            "sourceAccepted": None, "nextAction": None, "unscopedWork": milestone.get("unscoped", []),
            "priority": None, "evidence": [], "sourceState": None,
        })
    known = {i["id"] for i in record["items"]}
    for item in record["items"]:
        item["unmappedDependencies"] = [i for i in item["dependsOn"] if i not in known]
        item["dependsOn"] = [i for i in item["dependsOn"] if i in known]
    record["warnings"].append("Legacy done claims retain their source meaning; note-based evidence is not re-certified as typed receipts.")
    record["warnings"].append("Later items remain in the retained ledger but leave the active required denominator, following the source renderer.")
    return record


def normalized(data: bytes, project: dict, source: dict) -> dict:
    """Reads a native shared ledger while retaining its authored fields."""
    raw = json.loads(data)
    forbidden = {"project", "source", "metrics", "history", "deliverySummary"}.intersection(raw)
    if forbidden:
        raise RecordError("Native ledger identity belongs in the manifest: " + ", ".join(sorted(forbidden)))
    return {**_base(data, project, source), **raw}


ADAPTERS = {"prehnite-v2": prehnite, "portfolio-v3": portfolio, "normalized-v1": normalized}


def load_config(config_path: Path, only: set[str] | None = None) -> list[dict]:
    """Reads configured source snapshots without changing repository files."""
    config = json.loads(config_path.read_text())
    project_ids = [e["project"]["id"] for e in config["projects"]]
    if len(set(project_ids)) != len(project_ids):
        raise RecordError("Manifest repeats a project ID")
    if only and only - set(project_ids):
        raise RecordError("Unknown project IDs: " + ", ".join(sorted(only - set(project_ids))))
    records = []
    for entry in config["projects"]:
        if only and entry["project"]["id"] not in only:
            continue
        adapter = ADAPTERS.get(entry["adapter"])
        if adapter is None:
            raise RecordError("Unknown adapter: " + entry["adapter"])
        data = (config_path.parent / entry["sourceFile"]).read_bytes()
        record = adapter(data, entry["project"], entry["source"])
        record["presentation"] = entry["presentation"]
        previous = []
        for point in entry.get("snapshots", []):
            previous.append(adapter((config_path.parent / point["sourceFile"]).read_bytes(), entry["project"], point["source"]))
        if entry.get("previousSourceFile"):
            previous.append(adapter((config_path.parent / entry["previousSourceFile"]).read_bytes(), entry["project"], entry["previousSource"]))
        record["inputVisibility"] = [entry["project"]["visibility"]]
        record["supplementSources"] = []
        for supplement in entry.get("supplements", []):
            content = (config_path.parent / supplement["path"]).read_bytes()
            overlay = json.loads(content)
            allowed = {"changes", "releasePlans", "releases", "deployments", "deliveryCoverage", "governance", "decisions"}
            if set(overlay) - allowed:
                raise RecordError("Supplement cannot overwrite source identity or accounting fields")
            if any(key in record for key in overlay):
                raise RecordError("Supplement overlaps another authoritative writer")
            record.update(overlay)
            record["inputVisibility"].append(supplement.get("visibility", "private"))
            record["supplementSources"].append({**supplement, "sha256": sha256(content).hexdigest()})
        if entry.get("changeFiles"):
            if "changes" in record:
                raise RecordError("Change fragments and another changes writer cannot overlap")
            record["changes"] = []
            for fragment in entry["changeFiles"]:
                content = (config_path.parent / fragment["path"]).read_bytes()
                record["changes"].append(json.loads(content))
                record["inputVisibility"].append(fragment.get("visibility", "private"))
                record["supplementSources"].append({**fragment, "sha256": sha256(content).hexdigest()})
        from .timeline import make_timeline
        record["history"] = make_timeline(previous + [record])
        records.append(record)
    return records
