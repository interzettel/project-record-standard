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

These are report fields, not a second required completion checklist in every project. The canonical repository now offers an encountered-gap issue form and `templates/feedback.example.json`. The unreleased bounded route below adds local root-cause reuse, permission/content checks and an optional host-supplied submission callback. Native after-work capture and supported unattended operation remain separate gates.

## Overhead gate

Evaluate whether the system removes routine copying and duplicate status edits. Measure actual tracking time, owner interventions, stale/missed updates, report duplication and correction burden in the pilot. Preserve a negative outcome and simplify an adapter or feature when it adds more maintenance than it removes. Never use ticket count, model agreement or a green schema alone as evidence of usefulness.

## Bounded local route (unreleased)

`feedbackVersion1` describes an actual encounter, not an issue quota. `templates/feedback.example.json` uses the real runtime-path finding from PR63 with a labelled synthetic reproduction and the corrected revision; `feedback-policy.example.json` grants no publication by default. `feedback-search.example.json` knows that existing PR and explicitly has partial coverage. It can reuse that known discussion; it cannot establish absence elsewhere.

```sh
PYTHONPATH=/reviewed/prs/src python3 -m project_record feedback --encounter encounter.json --profile host-feedback-policy.json --search search-receipt.json --directory /private/project-feedback
```

Preview is read-only. Add `--apply` to retain a private proposal; this CLI never submits remotely. The local queue contains sanitized report text, private root-cause identity, local encounter hashes/effort and retrieval/transport observations. It owns delivery recovery, not work status, acceptance or personal memory. No background task, credentials, paid model call or reminder loop is installed. Use an existing private parent directory; new queue files/directories are private and symlink paths are refused. Existing directory permissions remain host-owned.

The `project_record.feedback` API has two host-callable operations:

- `prepare_feedback(encounter, profile, search, directory, apply=False)` validates the encounter and independently adopted profile, suppresses host-only defects/preferences/no-impact reports, projects allowed public fields and applies literal host-declared redactions. Unknown ownership remains a local proposal. Unknown pins stay null. It omits `privateContext`, encounter IDs and effort from the public report.
- `dispatch_feedback(ticket, profile, search, transport=None)` first reuses a verified existing canonical issue/PR link without posting a comment. New submission requires a search receipt covering open/closed issues and PRs, no remaining cursor, a host grant naming `create-issue`, and host review binding the exact sanitized `reportSha256`. A host supplies a callable transport; absent transport keeps the proposal local. No prompt is generated by either operation.

The report fields are task/impact, affected IDs, known identities, applicable source and expected/observed behavior, labelled minimal reproduction/limits, workaround and proposed narrow remedy. `rootCause` is a stable host judgment, not an inferred semantic match. Different descriptions/encounters using the same cause reuse one retained report; they cannot replace its reviewed bytes. A changed sanitized report is retained locally as a proposed amendment under the new encounter, without automatically publishing it. Reusing an encounter ID with changed observations is refused. Use the retained report/hash from the result when reviewing an existing proposal. Human judgment must reconcile different keys for the same cause; string hashing is not semantic duplicate detection.

The search receipt names destination, cause, date, retrieval source, actual resources/states/pages and matched canonical URLs. The runtime validates those claims but neither performs nor authenticates the search. The host must refresh stale searches immediately before submission. Incomplete retrieval, including a leftover cursor or missing closed reports/PRs, prevents a new issue. A known matching report can still be linked under partial coverage. No absence is inferred from a failed search.

The first request is written as `submitting` before the transport call. A callback receives only canonical destination/action, stable retry marker, title, sanitized report and its hash. It must use a bounded network timeout and render only those fields into the issue. A successful receipt is `{"status":"submitted","url":"https://github.com/interzettel/project-record-standard/issues/123"}`. `{"status":"denied"}` is allowed only when the transport positively knows **no remote write occurred**. All other/partial receipts, exceptions, invalid destinations or process death become uncertain. Exception text is never retained because transport errors can contain credentials.

Uncertain/submitting state blocks every blind create retry, including after a fresh search reports no match. Inspect the destination using the marker and exact submitted content; after verifying the actual issue/PR, supply its matching URL in a new search receipt to link the existing report. Eventual search indexing and a search with no results cannot prove that a write did not occur. A confirmed denial can retry within the adopted one-to-three-attempt budget. There is at most one call per invocation. A crash before the callback can conservatively require recovery even though no issue was created. This favors retaining one actionable proposal over emitting duplicate reports.

Literal redaction and field selection cannot determine whether arbitrary prose is safe. The exact public text needs a host-attributed review independently of publication permission. Self-hashes do not authenticate an actor, model, receipt or secret scanner. The same local OS owner and the host transport remain trust boundaries; do not treat candidate content as a grant or review. Automated comment/PR publication is not implemented here: link an existing discussion, or use the normal separately authorized, tested narrow-PR workflow. Publication does not imply upstream acceptance, merge, release or the host task's completion.

Local telemetry records actual preparation/transport durations and unique reused encounters. Optional encounter `effort` records observed tracking/correction seconds and owner interventions separately; missing effort stays unknown. It never enters the public issue. These observations measure this route only, not proven development-time savings. Keep the host workaround moving regardless of the upstream response. Do not add feedback hooks to uneventful tasks.
