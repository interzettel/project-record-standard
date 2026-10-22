"""Writes the interoperable structure for normalized project records."""

import json
from pathlib import Path


def main() -> None:
    """Writes schemas whose cross-record rules are enforced by the validator."""
    text = {"type": "string", "minLength": 1}
    nullable = {"type": ["string", "null"]}
    ids = {"type": "array", "items": text, "uniqueItems": True}
    metric = {"type": "object", "required": ["done", "total", "percent"], "properties": {
        "done": {"type": "integer", "minimum": 0}, "total": {"type": "integer", "minimum": 0},
        "percent": {"type": ["number", "null"], "minimum": 0, "maximum": 100}}, "additionalProperties": True}
    project = {"type": "object", "required": ["id", "name", "repository", "visibility"], "properties": {
        "id": text, "name": text, "repository": nullable, "visibility": {"enum": ["public", "private"]}}, "additionalProperties": True}
    source = {"type": "object", "required": ["path", "commit", "observedOn", "sha256", "authority"], "properties": {
        "path": text, "commit": {"type": ["string", "null"], "pattern": "^[a-fA-F0-9]{40}$"}, "kind": {"enum": ["git-snapshot", "file-snapshot"]},
        "observedOn": {"type": "string", "format": "date"}, "updatedOn": {"type": ["string", "null"]},
        "sha256": {"type": "string", "pattern": "^[a-fA-F0-9]{64}$"}, "authority": text}, "additionalProperties": True}
    item_properties = {"id": text, "title": text, "groupId": text, "milestoneId": nullable,
        "state": {"enum": ["backlog", "ready", "active", "review", "done", "cancelled", "unknown"]},
        "sourceState": text, "required": {"type": "boolean"}, "blocked": {"type": "boolean"},
        "dependsOn": ids, "unmappedDependencies": ids, "completionBasis": text,
        "kind": text, "owner": nullable, "priority": nullable, "issueUrl": nullable,
        "criterion": nullable, "note": nullable, "deferReason": nullable,
        "evidence": {"type": "array", "items": {"type": "object", "required": ["kind", "source"], "properties": {"kind": text, "source": text}, "additionalProperties": True}}}
    item = {"type": "object", "required": list(item_properties), "properties": item_properties, "additionalProperties": True}
    group = {"type": "object", "required": ["id", "title", "panel"], "properties": {
        "id": text, "title": text, "panel": text, "progress": metric, "ledgerProgress": metric}, "additionalProperties": True}
    milestone = {"type": "object", "required": ["id", "title", "goal", "horizon", "groupIds", "gateItemIds", "acceptanceRule", "sourceAccepted", "unscopedWork"], "properties": {
        "id": text, "title": text, "goal": text, "horizon": {"enum": ["Now", "Next", "Later"]},
        "groupIds": ids, "gateItemIds": ids, "acceptanceRule": {"enum": ["source-state", "all-gate-items", "unknown"]},
        "sourceAccepted": {"type": ["boolean", "null"]}, "accepted": {"type": ["boolean", "null"]},
        "unscopedWork": {"type": "array", "items": text}, "nextAction": nullable, "progress": metric}, "additionalProperties": True}
    source["allOf"] = [{"if": {"properties": {"commit": {"type": "null"}}}, "then": {"required": ["kind"], "properties": {"kind": {"const": "file-snapshot"}}}}]
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "urn:project-record:0.2.0", "title": "Shared project record 0.2.0", "description": "Structural interoperability with 0.1 read compatibility. Run the semantic validator for references, cycles, unique ownership, approvals and denominator rules.",
        "type": "object", "required": ["contractVersion", "project", "source", "items", "groups", "milestones"],
        "properties": {"contractVersion": {"enum": ["0.1.0", "0.2.0"]}, "project": project, "source": source,
            "items": {"type": "array", "items": item}, "groups": {"type": "array", "items": group},
            "milestones": {"type": "array", "items": milestone}, "warnings": {"type": "array", "items": text},
            "presentation": {"type": "object"}, "metrics": {"type": "object"},
            "history": {"type": "object", "required": ["snapshots", "comparisons", "coverage"]},
            "deliverySummary": {"type": "object"}, "deliveryCoverage": text,
            "inputVisibility": {"type": "array", "items": {"enum": ["public", "private"]}},
            "supplementSources": {"type": "array", "items": {"type": "object"}},
            "governance": {"type": "object", "required": ["purpose", "owner", "acceptanceAuthority", "changeAuthority", "approach", "tailoring"], "properties": {"approach": {"enum": ["adaptive", "predictive", "hybrid"]}, "tailoring": {"type": "object", "required": ["governance", "scope", "schedule", "finance", "stakeholders", "resources", "risk"]}, "workPackages": {"type": "array", "items": {"type": "object", "required": ["id", "deliverable", "owner", "acceptance", "workItemIds"]}}}},
            "capabilities": {"type": "array", "items": {"type": "object", "required": ["id", "title"], "properties": {"id": text, "title": text}}},
            "changes": {"type": "array", "items": {"type": "object", "required": ["id", "component", "type", "summary"]}},
            "releasePlans": {"type": "array", "items": {"type": "object", "required": ["id", "component", "channel", "gates"]}},
            "releases": {"type": "array", "items": {"type": "object", "required": ["component", "channel", "version", "url", "publishedAt", "observedAt"]}},
            "deployments": {"type": "array", "items": {"type": "object", "required": ["id", "environment", "observedAt"]}},
            "decisions": {"type": "array", "items": {"type": "object", "required": ["id", "summary", "source"]}}}, "additionalProperties": False}
    destination = Path(__file__).resolve().parents[1] / "schemas/record.schema.json"
    destination.write_text(json.dumps(schema, indent=2) + "\n")


if __name__ == "__main__":
    main()
