Selected workflow: `use-project-records` → `upgrade-project-records`. This is an existing pinned installation assessment; neither adoption reconstruction nor operations repair applies.

Read-only check executed from `/tmp/prs-upgrade-skill-applications/1/toolkit`:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m project_record upgrade-assess --request /tmp/prs-upgrade-skill-applications/1/request.json
```

Result: **exit 3, blocked-unknown**. Selected installed bytes and receipt match the expected pin; both archive/source checks have no gaps. Host **2.3.0**, toolkit/suite **0.4.1 → synthetic 0.5.0**, and record contract **0.2.0 → 0.2.0** remain separate identities. Provenance matches supplied evidence but publisher identity is unauthenticated. Policy is not pinned; runtime maps are empty.

| Change | Source and host evidence | Applicability / disposition | Concrete next action |
|---|---|---|---|
| `RULE-1`, mandatory, records | Target commit `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`; `b.zip` SHA-256 `7e41cc35ab46b7774e6267cd51a3b57b9e6c696fab1f378ee9e2d003d3f4c2db`. Cited `migration.md` SHA `83aa9b8…25362`, `policy.md` SHA `475780d…af9d8`. Actual texts are only “Synthetic migration notes” and “Synthetic policy”. Host `notes/policy.md` contains “locally authored rule”, SHA `0d268730…f96467`. | Selected `readme-only` profile applies. Supplied byte-bound review says `applicable-needs-change`; this is attributed synthetic review, not independently established policy meaning. | Obtain/review the precise required policy replacement. Do not invent it or copy toolkit templates. Preserve authored policy authority. |
| `GUIDE-2`, optional, guidance | Same target/source members. `request.json` supplies no semantic judgment or host evidence for this ID. | **blocked-unknown**, not automatically deferred merely because optional. | Proposed disposition: `optional-deferred`, with an explicit reason and inspected host evidence bound to `notes/policy.md`’s exact SHA. Record only after reviewing that judgment. |

The immediate proposed action is to prepare a revised assessment request containing the reviewed `GUIDE-2` decision, then run the same `upgrade-assess` command against that request. Preparation-only scope means I have not written it.

Remaining gates: resolve `GUIDE-2`; specify a separately reviewed `RULE-1` transformation; then prepare an `upgrade-preview` wrapper containing request, transformations, authoritative-source guards and producer revision. Preserve `records.json` facts: IDs `W1/W2`, dependency, acceptance, release `host1`, and **1/2** completion. Review the plan/diff before any plan-bound grant; synthetic application additionally requires explicit `allowSynthetic`. No host/toolkit files, receipts, progress credit, GitHub state or network resources were changed.