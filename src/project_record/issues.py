"""Checks delivery-package issue conventions without changing GitHub."""

import re


def lint_issue(issue: dict, aliases: dict | None = None) -> list[str]:
    """Returns naming, taxonomy and acceptance gaps in one issue snapshot."""
    problems = []
    title = issue.get("title", "")
    labels = [v if isinstance(v, str) else v.get("name", "") for v in issue.get("labels", [])]
    labels = [(aliases or {}).get(v, v) for v in labels]
    issue_type = [v for v in labels if v.startswith("type:")]
    if len(issue_type) != 1:
        problems.append("Use exactly one type:* label")
    elif issue_type[0] not in {"type:" + v for v in ["feature", "bug", "documentation", "research", "experiment", "decision", "maintenance", "release"]}:
        problems.append("Map the issue type to the shared type vocabulary")
    if not any(re.fullmatch(r"area:[a-z0-9][a-z0-9-]*", v) for v in labels):
        problems.append("Set an area:* label or declare a repository-local alias")
    if len([v for v in labels if re.fullmatch(r"priority:P[0-3]", v)]) != 1:
        problems.append("Use one priority:P0 through priority:P3 label")
    if len(title) > 120 or not re.fullmatch(r"\[[A-Za-z0-9_.:-]+\] [A-Z][^\n]{8,110}", title):
        problems.append("Use [stable-ID] Verb + concrete outcome, within 120 characters")
    body = issue.get("body", "")
    for heading in ["Outcome", "Scope", "Acceptance", "Evidence", "Dependencies"]:
        if not re.search(r"^###? " + heading + r"\s*$", body, re.MULTILINE):
            problems.append("Missing section: " + heading)
    return problems
