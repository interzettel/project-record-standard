# Feedback from real work

Agents adopting PRS should help improve it when an actual task exposes a shared-standard defect, ambiguity or missing reusable capability. The default objective is less tracking work for the adopter. There is no reporting quota, background idea-generation loop or obligation to create a ticket after an uneventful task.

## Encounter to report

Distinguish a host-project bug from a gap in PRS. Retain a minimal encounter record: the task and practical impact, exact known toolkit/contract/adapter/runtime pins, expected rule, observed result, evidence/reproduction, safe workaround and proposed change/check. A useful report can be an observed failure or a repeatable ambiguity; unsupported speculation and visual taste alone do not establish a defect.

Look for an existing issue/PR about the same root cause before creating another. Preserve its URL in the local encounter record. Reuse or amend that discussion when authorized; do not open duplicates on every session/retry. Partial retrieval is a coverage limit, not proof no report exists. Keep the local task moving with a documented workaround; upstream response is not an automatic blocker.

## Publication and privacy

The adopter's initial setup can grant a bounded upstream-feedback capability for the canonical PRS repository. That grant identifies allowed destinations, public-safe content and issue versus PR behavior. It does not authorize uploading private repository files, personal memory, credentials, identifying logs or unrelated project details. Minimize and redact; prefer a synthetic reproduction that preserves the failure. A proposed patch needs an actual scoped change and tests, not merely an instruction to another agent.

If publication is not authorized or the source cannot be safely shared, retain one local proposal and surface it in the normal handoff. Avoid repeated permission prompts for the same unchanged proposal. Routine recording can proceed under existing authority; acceptance, upstream merge and release remain their designated decisions.

## Issue / PR contract

Use a title such as `[feedback: <affected rule>] <observed problem>`. Include:

1. Context: the real task/outcome affected, without unnecessary private context.
2. Verified identities: toolkit/suite/contract and known host adapter/runtime versions; unknown stays unknown.
3. Expected versus observed behavior with the applicable rule/source.
4. Minimal reproduction, actual result and evidence limits.
5. Workaround, scope/count/permission effect and whether the issue blocks the host outcome.
6. Existing report search and related issue/PR IDs; propose a narrow remedy or explicit investigation.
7. For a PR, changed files, meaningful checks, compatibility and rollback implications.

These are report fields, not a second required completion checklist in every project. The canonical repository now offers an encountered-gap issue form and `templates/feedback.example.json`. #36 still owns runtime deduplication, permission tests and automatic routing. The current implementation does not yet submit such reports automatically.

## Overhead gate

Evaluate whether the system removes routine copying and duplicate status edits. Measure actual tracking time, owner interventions, stale/missed updates, report duplication and correction burden in the pilot. Preserve a negative outcome and simplify an adapter or feature when it adds more maintenance than it removes. Never use ticket count, model agreement or a green schema alone as evidence of usefulness.
