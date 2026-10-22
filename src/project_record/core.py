"""Validates project records and calculates their declared denominators."""

from collections import Counter
from copy import deepcopy
from datetime import date
import re
from statistics import mean

from .history import history_errors
from .governance import governance_errors


class RecordError(ValueError):
    """A project record has inconsistent structure or unsupported claims."""


def percentage(numerator: int, denominator: int) -> float | None:
    """Returns a percentage, or None when there is no defined denominator."""
    if denominator < 0 or numerator < 0 or numerator > denominator:
        raise RecordError("Percentage requires 0 <= numerator <= denominator")
    return round(100 * numerator / denominator, 1) if denominator else None


def progress(items: list[dict], mode: str = "required") -> dict:
    """Counts completed leaf items without granting partial workflow credit.

    Args:
        items: The distinct leaf records in the selected scope.
        mode: The denominator: required work or the whole retained ledger.

    Returns:
        The counts, percentage, exclusions and denominator description.

    Raises:
        RecordError: If the mode is unsupported or an item is duplicated.
    """
    if mode not in {"required", "ledger"}:
        raise RecordError("Progress mode must be required or ledger")
    if len({i["id"] for i in items}) != len(items):
        raise RecordError("Duplicate leaf items cannot earn duplicate credit")
    retained = [i for i in items if i["state"] != "cancelled"]
    selected = [i for i in retained if mode == "ledger" or i["required"]]
    counts = Counter(i["state"] for i in selected)
    return {
        "done": counts["done"], "total": len(selected),
        "percent": percentage(counts["done"], len(selected)),
        "active": counts["active"], "review": counts["review"],
        "blocked": sum(bool(i["blocked"]) for i in selected),
        "unknown": counts["unknown"],
        "excluded": len(items) - len(selected),
        "method": "completed-leaves / " + ("required-leaves" if mode == "required" else "retained-ledger-leaves"),
    }


def policy_satisfied(policy: dict, receipts: list[dict], subject: str,
                     revision: str | None) -> bool:
    """Checks all-required evidence and alternatives against applicable receipts.

    Args:
        policy: The allOf and anyOf evidence-kind requirements.
        receipts: The attributed observations, including failed attempts.
        subject: The exact work item or gate being certified.
        revision: The implementation revision to certify, or None for no pin.

    Returns:
        True if every required kind and an alternative pass; false otherwise.
    """
    required = set(policy.get("allOf", []))
    alternatives = set(policy.get("anyOf", []))
    if not required and not alternatives:
        return False
    available = {
        r["kind"] for r in receipts
        if r.get("result") == "passed" and r.get("subject") == subject
        and not r.get("supersededBy")
        and (revision is None or r.get("revision") == revision)
    }
    return required <= available and (not alternatives or bool(alternatives & available))


def validate(record: dict) -> None:
    """Rejects duplicate credit, invalid references and circular prerequisites.

    Args:
        record: The normalized project record to inspect without mutating it.

    Raises:
        RecordError: If an identity, reference, state or dependency is invalid.
    """
    if not isinstance(record, dict):
        raise RecordError("Record must be an object")
    if record.get("contractVersion") not in {"0.1.0", "0.2.0"}:
        raise RecordError("Unsupported contractVersion")
    for field in ["project", "source", "items", "groups", "milestones"]:
        if field not in record:
            raise RecordError("Missing field: " + field)
    if any(not isinstance(record[field], dict) for field in ["project", "source"]):
        raise RecordError("Project and source must be objects")
    if any(not isinstance(record[field], list) or any(not isinstance(row, dict) for row in record[field]) for field in ["items", "groups", "milestones"]):
        raise RecordError("Items, groups and milestones must be arrays of objects")
    for field in ["id", "name", "visibility"]:
        if not isinstance(record["project"].get(field), str) or not record["project"][field].strip():
            raise RecordError("Missing project identity: " + field)
    if record["project"]["visibility"] not in {"public", "private"}:
        raise RecordError("Visibility must be public or private")
    commit = record["source"].get("commit")
    local = record["source"].get("kind") == "file-snapshot" and commit is None
    if not local and (not isinstance(commit, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", commit)):
        raise RecordError("Source commit must identify an exact Git revision")
    repository = record["project"].get("repository")
    if not local and (not isinstance(repository, str) or not re.fullmatch(r"[\w.-]+/[\w.-]+", repository)):
        raise RecordError("A Git source needs its repository identity")
    for field in ["path", "authority"]:
        if not isinstance(record["source"].get(field), str) or not record["source"][field].strip():
            raise RecordError("Source needs " + field)
    if not isinstance(record["source"].get("sha256"), str) or not re.fullmatch(r"[a-fA-F0-9]{64}", record["source"]["sha256"]):
        raise RecordError("Source revision and digest are required")
    try:
        date.fromisoformat(record["source"]["observedOn"])
    except (KeyError, TypeError, ValueError) as error:
        raise RecordError("Source observation needs an ISO calendar date") from error
    errors = history_errors(record) + governance_errors(record)
    if errors:
        raise RecordError("; ".join(errors))
    indexes = {}
    for kind in ["items", "groups", "milestones"]:
        rows = record[kind]
        if not isinstance(rows, list):
            raise RecordError(kind + " must be an array")
        if any(not isinstance(r.get("id"), str) or not r["id"] for r in rows):
            raise RecordError("Every " + kind + " record needs a stable ID")
        index = {r["id"]: r for r in rows}
        if len(index) != len(rows):
            raise RecordError("Duplicate " + kind + " ID")
        indexes[kind] = index
    for item in record["items"]:
        for name in ["title", "groupId", "sourceState", "completionBasis", "kind"]:
            if not isinstance(item.get(name), str) or not item[name].strip():
                raise RecordError("Missing or invalid work field: " + name)
        if not isinstance(item.get("dependsOn"), list) or not all(isinstance(v, str) for v in item["dependsOn"]) or len(set(item["dependsOn"])) != len(item["dependsOn"]):
            raise RecordError("Dependencies must be distinct string IDs")
        if not isinstance(item.get("evidence"), list) or any(not isinstance(e, dict) or not isinstance(e.get("kind"), str) or not isinstance(e.get("source"), str) for e in item["evidence"]):
            raise RecordError("Evidence must retain typed, source-linked records")
        if not isinstance(item.get("state"), str) or item["state"] not in {"done", "active", "review", "ready", "backlog", "cancelled", "unknown"}:
            raise RecordError("Unsupported work state")
        if type(item.get("required")) is not bool or type(item.get("blocked")) is not bool:
            raise RecordError("required and blocked must be explicit booleans")
        if item["groupId"] not in indexes["groups"]:
            raise RecordError("Unknown group for " + item["id"])
        if item.get("milestoneId") and item["milestoneId"] not in indexes["milestones"]:
            raise RecordError("Unknown milestone for " + item["id"])
        if item["state"] == "done" and item["blocked"]:
            raise RecordError("Completed work cannot also be blocked")
        if not item["required"] and not item.get("deferReason"):
            raise RecordError("Work outside the required denominator needs a reason")
        if item["state"] == "cancelled" and not item.get("note"):
            raise RecordError("Cancellation needs a retained reason")
        for dependency in item["dependsOn"]:
            if dependency not in indexes["items"]:
                raise RecordError("Unknown prerequisite: " + dependency)
    visiting, visited = set(), set()

    def visit(item_id: str) -> None:
        if item_id in visiting:
            raise RecordError("Dependency cycle through " + item_id)
        if item_id in visited:
            return
        visiting.add(item_id)
        for dependency in indexes["items"][item_id]["dependsOn"]:
            visit(dependency)
        visiting.remove(item_id)
        visited.add(item_id)

    for item_id in indexes["items"]:
        visit(item_id)
    for milestone in record["milestones"]:
        for field in ["title", "goal", "horizon", "acceptanceRule"]:
            if not isinstance(milestone.get(field), str) or not milestone[field]:
                raise RecordError("Milestone needs " + field)
        for field in ["groupIds", "gateItemIds", "unscopedWork"]:
            if not isinstance(milestone.get(field), list) or any(not isinstance(v, str) for v in milestone[field]):
                raise RecordError("Milestone lists must contain string values")
        if len(set(milestone["groupIds"])) != len(milestone["groupIds"]) or len(set(milestone["gateItemIds"])) != len(milestone["gateItemIds"]):
            raise RecordError("Milestone references must be unique")
        for item_id in milestone["gateItemIds"]:
            if item_id not in indexes["items"]:
                raise RecordError("Unknown milestone gate: " + item_id)
        for group_id in milestone["groupIds"]:
            if group_id not in indexes["groups"]:
                raise RecordError("Unknown milestone group: " + group_id)
        if milestone["acceptanceRule"] not in {"source-state", "all-gate-items", "unknown"}:
            raise RecordError("Unsupported milestone acceptance rule")
        if milestone["acceptanceRule"] == "all-gate-items" and not milestone["gateItemIds"]:
            raise RecordError("An empty gate cannot establish acceptance")
        if milestone["acceptanceRule"] == "source-state" and milestone["sourceAccepted"]:
            gates = [indexes["items"][i] for i in milestone["gateItemIds"]]
            if not gates or any(i["state"] != "done" for i in gates):
                raise RecordError("Accepted source milestone has an unfinished declared gate")
    for group in record["groups"]:
        if not all(isinstance(group.get(field), str) and group[field] for field in ["title", "panel"]):
            raise RecordError("Group needs a title and panel")
        owners = [m["id"] for m in record["milestones"] if group["id"] in m["groupIds"]]
        if len(owners) > 1:
            raise RecordError("A group cannot earn progress in two milestones")
        for item in record["items"]:
            if item["groupId"] == group["id"] and item.get("milestoneId") != (owners[0] if owners else None):
                raise RecordError("Milestone membership disagrees with group ownership")


def summarize(record: dict) -> dict:
    """Adds work, milestone and equal-milestone metrics to a validated copy."""
    validate(record)
    result = deepcopy(record)
    item_index = {i["id"]: i for i in result["items"]}
    for group in result["groups"]:
        own = [i for i in result["items"] if i["groupId"] == group["id"]]
        group["progress"] = progress(own)
        group["ledgerProgress"] = progress(own, "ledger")
    for milestone in result["milestones"]:
        own = [i for i in result["items"] if i.get("milestoneId") == milestone["id"]]
        milestone["progress"] = progress(own)
        gates = [item_index[i] for i in milestone["gateItemIds"]]
        milestone["gateProgress"] = progress(gates, "ledger") if gates else None
        if milestone["acceptanceRule"] == "all-gate-items":
            milestone["accepted"] = all(i["state"] == "done" for i in gates)
        elif milestone["acceptanceRule"] == "source-state":
            milestone["accepted"] = milestone["sourceAccepted"]
        else:
            milestone["accepted"] = None
    milestones = result["milestones"]
    known = [m for m in milestones if m["accepted"] is not None]
    values = [100 * m["progress"]["done"] / m["progress"]["total"]
              if m["progress"]["total"] else None for m in milestones]
    result["metrics"] = {
        "work": progress(result["items"]),
        "ledger": progress(result["items"], "ledger"),
        "milestones": {
            "done": sum(m["accepted"] is True for m in known),
            "total": len(milestones), "known": len(known),
            "percent": percentage(sum(m["accepted"] is True for m in known), len(milestones)) if len(known) == len(milestones) else None,
            "method": "accepted-milestones / declared-milestones",
        },
        "roadmapMean": {
            "percent": round(mean(values), 1) if values and all(v is not None for v in values) else None,
            "method": "arithmetic-mean-of-required-work-percentages-per-milestone",
            "milestoneCount": len(milestones),
        },
    }
    return result


def compare(before: dict, after: dict) -> dict:
    """Compares immutable IDs and denominator changes between two snapshots."""
    left, right = summarize(before), summarize(after)
    old = {i["id"]: i for i in left["items"]}
    new = {i["id"]: i for i in right["items"]}
    return {
        "added": sorted(new.keys() - old.keys()),
        "removed": sorted(old.keys() - new.keys()),
        "stateChanges": [{"id": i, "from": old[i]["state"], "to": new[i]["state"]}
                         for i in sorted(old.keys() & new.keys()) if old[i]["state"] != new[i]["state"]],
        "scopeChanges": [{"id": i, "fromRequired": old[i]["required"], "toRequired": new[i]["required"]}
                         for i in sorted(old.keys() & new.keys()) if old[i]["required"] != new[i]["required"]],
        "before": left["metrics"], "after": right["metrics"],
    }


def export_record(record: dict, audience: str) -> dict:
    """Rejects public export of a private source without a reviewed projection."""
    if audience not in {"owner", "public"}:
        raise RecordError("Audience must be owner or public")
    if audience == "public" and (record["project"]["visibility"] != "public" or "private" in record.get("inputVisibility", [])):
        raise RecordError("Private source requires an explicit reviewed public projection")
    return summarize(record)
