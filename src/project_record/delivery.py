"""Assembles changelogs and release readiness from explicit local records."""

from copy import deepcopy

from .core import RecordError, policy_satisfied


def release_readiness(record: dict, plan: dict) -> dict:
    """Evaluates declared gates without granting acceptance or publication.

    Args:
        record: The validated source record and its current work states.
        plan: The candidate's work IDs and explicitly declared evidence gates.

    Returns:
        Per-gate status, missing proof and a candidate-readiness summary.
    """
    index = {i["id"]: i for i in record["items"]}
    gates = []
    for identity in plan.get("workItemIds", []):
        item = index.get(identity)
        if item is None:
            raise RecordError("Release plan refers to unknown work: " + identity)
        gates.append({"id": "work:" + identity, "label": item["title"],
                      "status": "passed" if item["state"] == "done" else "pending",
                      "basis": item["completionBasis"], "workItemId": identity})
    for gate in plan.get("gates", []):
        evidence = gate.get("receipts", [])
        policy = gate.get("policy", {})
        passed = policy_satisfied(policy, evidence, gate["id"], plan.get("revision"))
        failed = any(r.get("result") == "failed" and r.get("subject") == gate["id"]
                     and r.get("revision") == plan.get("revision") and not r.get("supersededBy") for r in evidence)
        gates.append({"id": gate["id"], "label": gate["label"],
                      "status": "passed" if passed else "failed" if failed else "pending",
                      "policy": deepcopy(policy), "receipts": deepcopy(evidence)})
    passed_count = sum(g["status"] == "passed" for g in gates)
    return {"id": plan["id"], "component": plan["component"], "channel": plan["channel"],
            "version": plan.get("version"), "revision": plan.get("revision"),
            "gates": gates, "passed": passed_count, "total": len(gates),
            "percent": round(100 * passed_count / len(gates), 1) if gates else None,
            "status": "ready-for-publication-review" if gates and passed_count == len(gates) else "not-ready" if gates else "not-assessed",
            "published": False}


def delivery_summary(record: dict) -> dict:
    """Keeps unshipped changes, candidates, publications and deployments distinct."""
    released = {c for r in record.get("releases", []) for c in r.get("changeIds", [])}
    return {"coverage": record.get("deliveryCoverage", "Publication and deployment channels have not been reconciled."),
            "unreleased": [deepcopy(c) for c in record.get("changes", []) if c["id"] not in released],
            "plans": [release_readiness(record, p) for p in record.get("releasePlans", [])],
            "releases": deepcopy(record.get("releases", [])),
            "deployments": deepcopy(record.get("deployments", []))}


def changelog_markdown(record: dict) -> str:
    """Renders authored changes by observed component and publication channel."""
    index = {c["id"]: c for c in record.get("changes", [])}
    summary = delivery_summary(record)
    lines = ["# Generated delivery history", "", summary["coverage"], "", "## Unreleased", ""]
    def append_change(change: dict) -> None:
        text = change["summary"].replace("\n", " ").replace("\r", " ")
        lines.append(f"- {change['id']} · {change['component']} · {change['type']}: {text}")
    for change in summary["unreleased"]:
        append_change(change)
    if not summary["unreleased"]:
        lines.append("No authored unreleased changes mapped. This does not establish that there are no changes.")
    for release in sorted(summary["releases"], key=lambda r: (r.get("publishedAt") or "", r["component"], r["channel"], r["version"]), reverse=True):
        lines += ["", f"## {release['component']} {release['version']} / {release['channel']}", "",
                  "Publication time: " + (release.get("publishedAt") or "Unknown") + ". Observed: " + release["observedAt"] + ".", "",
                  "Source identity: `" + (release.get("revision") or release.get("artifactDigest")) + "`.", ""]
        for identity in release.get("changeIds", []):
            append_change(index[identity])
    lines += ["", "Candidate readiness and deployment observations are separate from this changelog.", ""]
    return "\n".join(lines)
