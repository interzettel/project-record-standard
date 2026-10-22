"""Validates distinct change, publication and deployment observations."""

from datetime import datetime
import re
from urllib.parse import urlparse


def _identity(value: dict) -> bool:
    revision, digest = value.get("revision"), value.get("artifactDigest")
    return bool((isinstance(revision, str) and re.fullmatch(r"[a-fA-F0-9]{40}", revision))
                or (isinstance(digest, str) and re.fullmatch(r"sha256:[a-fA-F0-9]{64}", digest)))


def _timestamp(value: str | None) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except (TypeError, ValueError):
        return False


def history_errors(record: dict) -> list[str]:
    """Returns inconsistencies between plans, publications and deployments."""
    errors = []
    ids = set()
    for name in ["changes", "releasePlans", "releases", "deployments"]:
        if not isinstance(record.get(name, []), list) or any(not isinstance(r, dict) for r in record.get(name, [])):
            errors.append(name + " must be an array of objects")
    if errors:
        return errors
    for change in record.get("changes", []):
        if not all(isinstance(change.get(k), str) and change[k] for k in ["id", "component", "type", "summary"]):
            errors.append("A change needs ID, component, type and summary")
        if not isinstance(change.get("id"), str):
            errors.append("Change ID must be a string")
            continue
        if change.get("id") in ids:
            errors.append("Duplicate change ID")
        ids.add(change.get("id"))
    plans = set()
    work_ids = {i["id"] for i in record.get("items", []) if isinstance(i, dict) and isinstance(i.get("id"), str)}
    for plan in record.get("releasePlans", []):
        if not all(isinstance(plan.get(k), str) and plan[k] for k in ["id", "component", "channel"]):
            errors.append("Release plan needs string ID, component and channel")
            continue
        if plan["id"] in plans:
            errors.append("Duplicate release plan ID")
        plans.add(plan["id"])
        revision = plan.get("revision")
        if not isinstance(revision, str) or not re.fullmatch(r"(?:[a-fA-F0-9]{40}|sha256:[a-fA-F0-9]{64})", revision):
            errors.append("Release readiness needs an exact revision or content digest")
        references = plan.get("workItemIds", [])
        if not isinstance(references, list) or any(not isinstance(i, str) for i in references) or len(set(references)) != len(references):
            errors.append("Release work references must be distinct string IDs")
        elif any(i not in work_ids for i in references):
            errors.append("Release refers to unknown work")
        gates = plan.get("gates", [])
        if not isinstance(gates, list) or any(not isinstance(g, dict) for g in gates):
            errors.append("Release gates must be objects")
            continue
        gate_ids = set()
        for gate in gates:
            if not all(isinstance(gate.get(k), str) and gate[k] for k in ["id", "label"]) or gate.get("id") in gate_ids:
                errors.append("Release gates need unique IDs and labels")
                continue
            gate_ids.add(gate["id"])
            policy = gate.get("policy", {})
            if not isinstance(policy, dict) or any(not isinstance(policy.get(k, []), list) or any(not isinstance(v, str) for v in policy.get(k, [])) for k in ["allOf", "anyOf"]):
                errors.append("Gate policy must list evidence kinds")
            receipts = gate.get("receipts", [])
            if not isinstance(receipts, list) or any(not isinstance(r, dict) for r in receipts):
                errors.append("Gate receipts must be objects")
                continue
            for receipt in receipts:
                if not all(isinstance(receipt.get(k), str) and receipt[k] for k in ["kind", "subject", "revision", "source"]):
                    errors.append("Receipt needs kind, subject, revision and source")
                if receipt.get("result") not in {"passed", "failed", "partial", "unknown"}:
                    errors.append("Receipt result must be passed, failed, partial or unknown")
    releases = set()
    for release in record.get("releases", []):
        key = tuple(release.get(k) for k in ["component", "channel", "version"])
        if any(not isinstance(k, str) for k in key):
            errors.append("Publication component/channel/version must be strings")
            continue
        if not all(key) or key in releases:
            errors.append("Publication component/channel/version must be present and unique")
        releases.add(key)
        if not _identity(release):
            errors.append("Publication needs an exact source revision or artifact digest")
        url = release.get("url")
        if not isinstance(url, str) or urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc:
            errors.append("Publication needs an observed channel URL")
        if "publishedAt" not in release or not _timestamp(release.get("publishedAt")):
            errors.append("Publication time must be an explicit zoned time or unknown/null")
        if not release.get("observedAt") or not _timestamp(release.get("observedAt")):
            errors.append("Publication needs a separate observation time")
        if release.get("status") in {"planned", "candidate", "unreleased"}:
            errors.append("A release plan belongs in releasePlans, not observed releases")
        changes = release.get("changeIds", [])
        if not isinstance(changes, list) or any(not isinstance(c, str) or c not in ids for c in changes) or len(set(changes)) != len(changes):
            errors.append("Publication refers to an unknown change")
    deployment_ids = set()
    for deployment in record.get("deployments", []):
        if not all(deployment.get(k) for k in ["id", "environment", "observedAt"]):
            errors.append("Deployment needs ID, environment and observation time")
        if not _identity(deployment) or not _timestamp(deployment.get("observedAt")):
            errors.append("Deployment needs observed exact bytes/revision and a zoned timestamp")
        if deployment.get("health") not in {"healthy", "degraded", "failed", "unknown", None}:
            errors.append("Deployment health must be a named observation or unknown")
        identity = deployment.get("id")
        if not isinstance(identity, str) or identity in deployment_ids:
            errors.append("Deployment ID must be a unique string")
        else:
            deployment_ids.add(identity)
    return errors
