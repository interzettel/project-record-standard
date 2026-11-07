Selected workflows: **use-project-records → operate-project-tracking**. Existing installation and a toolkit upgrade call for assessment, not setup or reinitialization.

Executed read-only from `/tmp/prs-upgrade-skill-controls/1/toolkit`:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m project_record upgrade-assess --request /tmp/prs-upgrade-skill-controls/1/request.json
```

Actual result: **`blocked-unknown`, exit 3**, exclusively because `host-review-missing:GUIDE-2`. No conflicts; selected installed bytes match. Host version remains `2.3.0`; the selected suite transition is synthetic `0.4.1 → 0.5.0`; record contract remains readable `0.2.0`. Policy is unpinned. Supplied provenance matches, but publisher and semantic judgments are unauthenticated.

| Delta | Source-backed applicability | Handling |
| --- | --- | --- |
| `RULE-1` | Mandatory, records; applies to `readme-only`. Existing request judgment: `applicable-needs-change`, bound to inspected `host/notes/policy.md`, SHA-256 `0d2687308c6063d47adc8214d6658ef82b3f69ac8c4616764a501ab962f96467`. | Retain as required. Reconcile the actual host rule before preparing an authored transformation. Do not relabel optional or assume installing toolkit files implements it. |
| `GUIDE-2` | Optional, guidance; also applies to `readme-only`. No host judgment supplied, so currently unknown. | Review explicitly; proposed disposition is `optional-deferred`, with reason “Optional guidance postponed while preparing the required policy migration,” citing inspected host policy bytes. This is a proposal, not a recorded decision. |

Both catalogue rows cite verified target archive members: `migration.md` SHA-256 `83aa9b8e…25362`, and `policy.md` SHA-256 `475780d8…f9d8`. Their actual contents are merely “Synthetic migration notes” and “Synthetic policy”; these establish reviewed bytes but provide no concrete replacement rule. Host policy says “locally authored rule.” A specific required semantic edit cannot honestly be derived from those texts.

**Exact next action:** obtain the intended `RULE-1` before/after policy wording and complete the explicit `GUIDE-2` judgment in a reviewable request proposal. Then rerun the assessment command above against that reviewed request. Do not invoke preview against the current blocked request.

After resolution, prepare `upgrade-preview` with explicit transformations, `guards: ["records.json"]`, and an immutable producer revision. Preserve the actual record identities `W1/W2`, dependency `W2 → W1`, accepted history, `1/2` fraction and `host1` release identity.

Remaining gate: preparation only authorizes no application. A later reviewed plan needs separate, plan-bound apply authority, explicit synthetic permission, rollback preparation and host functional/owner checks. All observed write/application flags remain false; completion credit and scope delta remain zero.
