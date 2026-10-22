"""Explains progress changes without confusing scope growth with completion."""

from copy import deepcopy

from .core import RecordError, compare, summarize


def comparison(before: dict, after: dict) -> dict:
    """Separates state and membership effects using the earlier denominator.

    Args:
        before: The earlier normalized source snapshot.
        after: The later snapshot for the same project.

    Returns:
        The exact counts, changes and additive percentage-point bridge.
    """
    if before["project"]["id"] != after["project"]["id"]:
        raise RecordError("History cannot compare different projects")
    delta = compare(before, after)
    old = {i["id"]: i for i in before["items"]}
    new = {i["id"]: i for i in after["items"]}
    bridges = {}
    for mode, key in [("required", "work"), ("ledger", "ledger")]:
        baseline = [i for i in old.values() if i["state"] != "cancelled" and (mode == "ledger" or i["required"])]
        bridged_done = sum(new.get(i["id"], i)["state"] == "done" for i in baseline)
        left, right = delta["before"][key], delta["after"][key]
        initial = 100 * left["done"] / left["total"] if left["total"] else None
        bridge = 100 * bridged_done / len(baseline) if baseline else None
        final = 100 * right["done"] / right["total"] if right["total"] else None
        bridges[key] = {
            "before": left, "afterStateChanges": {"done": bridged_done, "total": len(baseline)},
            "after": right,
            "stateEffectPP": round(bridge - initial, 4) if initial is not None and bridge is not None else None,
            "scopeEffectPP": round(final - bridge, 4) if final is not None and bridge is not None else None,
            "totalChangePP": round(final - initial, 4) if final is not None and initial is not None else None,
            "method": "Apply retained-item state changes on the previous denominator; then change membership. Removed items keep their earlier state in the intermediate step. This is an accounting explanation, not earned value.",
        }
    return {**delta, "bridges": bridges,
            "moved": [{"id": i, "from": old[i].get("milestoneId"), "to": new[i].get("milestoneId")}
                      for i in sorted(old.keys() & new.keys()) if old[i].get("milestoneId") != new[i].get("milestoneId")],
            "regressions": [c for c in delta["stateChanges"] if c["from"] == "done" and c["to"] != "done"],
            "sourceRevisions": {"before": before["source"].get("commit") or before["source"]["sha256"],
                                "after": after["source"].get("commit") or after["source"]["sha256"]}}


def make_timeline(records: list[dict]) -> dict:
    """Summarizes ordered observations and adjacent snapshot comparisons."""
    if not records:
        raise RecordError("A history needs at least the current snapshot")
    points, seen = [], set()
    previous_date = None
    for record in records:
        normalized = summarize(record)
        identity = (record["source"].get("commit"), record["source"]["sha256"])
        if identity in seen:
            raise RecordError("History repeats a source identity")
        seen.add(identity)
        observed = record["source"]["observedOn"]
        if previous_date and observed < previous_date:
            raise RecordError("History observations must be chronological")
        if record["project"]["id"] != records[0]["project"]["id"]:
            raise RecordError("History mixes projects")
        previous_date = observed
        points.append({"observedOn": observed, "source": deepcopy(record["source"]),
                       "metrics": normalized["metrics"]})
    return {"coverage": "Only the listed pinned observations; intervening events are unknown.",
            "snapshots": points,
            "comparisons": [comparison(a, b) for a, b in zip(records, records[1:])]}
