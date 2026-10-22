"""Checks tailored governance records without inferring human authorization."""


DOMAINS = ("governance", "scope", "schedule", "finance", "stakeholders", "resources", "risk")


def governance_errors(record: dict) -> list[str]:
    """Reports incomplete authority, scope ownership and change-control records."""
    value = record.get("governance")
    if value is None:
        return []
    if not isinstance(value, dict):
        return ["Governance must be an object"]
    errors = []
    for field in ["purpose", "owner", "acceptanceAuthority", "changeAuthority"]:
        if not isinstance(value.get(field), str) or not value[field].strip():
            errors.append("Governance needs " + field)
    if value.get("approach") not in {"adaptive", "predictive", "hybrid"}:
        errors.append("Governance approach must be explicitly tailored")
    tailoring = value.get("tailoring", {})
    for domain in DOMAINS:
        decision = tailoring.get(domain, {}) if isinstance(tailoring, dict) else {}
        if not isinstance(decision, dict) or decision.get("status") not in {"applied", "not-assessed", "tailored-out"} or not decision.get("reason"):
            errors.append("Tailoring needs status and reason for " + domain)
    for field in ["workPackages", "baselines", "changeRequests", "risks"]:
        if not isinstance(value.get(field, []), list) or any(not isinstance(v, dict) for v in value.get(field, [])):
            errors.append("Governance " + field + " must be an array of objects")
    if errors:
        return errors
    work_ids = {i["id"] for i in record.get("items", []) if isinstance(i.get("id"), str)}
    packages = value.get("workPackages", [])
    package_ids, assigned = set(), set()
    for package in packages:
        identity = package.get("id")
        if not isinstance(identity, str) or not identity or identity in package_ids:
            errors.append("WBS work package needs a unique ID")
            continue
        package_ids.add(identity)
        for field in ["deliverable", "owner", "acceptance"]:
            if not package.get(field):
                errors.append("WBS work package needs " + field)
        references = package.get("workItemIds", [])
        if not isinstance(references, list) or any(not isinstance(i, str) for i in references):
            errors.append("WBS work references must be string IDs")
            continue
        if len(set(references)) != len(references) or assigned.intersection(references):
            errors.append("WBS work cannot be accounted in two packages")
        if set(references) - work_ids:
            errors.append("WBS package refers to unknown work")
        assigned.update(references)
    coverage = value.get("wbsCoverage", "not-assessed")
    if coverage not in {"complete", "partial", "not-assessed"}:
        errors.append("WBS coverage must be explicit")
    if coverage == "complete" and assigned != work_ids:
        errors.append("Complete WBS mapping must cover all declared leaves")
    for baseline in value.get("baselines", []):
        if not baseline.get("id") or baseline.get("status") not in {"observed", "proposed", "approved", "superseded"}:
            errors.append("Baseline needs an ID and explicit approval state")
        if baseline.get("status") in {"approved", "superseded"} and not all(baseline.get(k) for k in ["approvedBy", "approvedAt", "approvalSource"]):
            errors.append("Approved baseline needs attributed approval evidence")
    for change in value.get("changeRequests", []):
        if not all(change.get(k) for k in ["id", "reason", "impact", "status"]):
            errors.append("Scope change needs ID, reason, impact and status")
        if change.get("status") not in {"proposed", "approved", "rejected", "implemented"}:
            errors.append("Unsupported scope-change status")
        if change.get("status") in {"approved", "implemented"} and not all(change.get(k) for k in ["approvedBy", "approvedAt", "approvalSource"]):
            errors.append("Approved scope change needs attributed approval evidence")
    for risk in value.get("risks", []):
        if not all(risk.get(k) for k in ["id", "event", "owner", "response", "trigger", "status"]):
            errors.append("Risk needs event, owner, response, trigger and status")
    return errors
