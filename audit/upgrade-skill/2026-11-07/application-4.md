Selected workflow: installed `use-project-records` router → `upgrade-project-records`, specifically release assessment and read-only watcher handoff. No adaptation, repair, scheduler, or installation is justified.

| Observation from `release-observations.json` | Required reaction |
|---|---|
| 0.4.1 → 0.4.2 ordinary patch | Proportionate triage; reasoned deferral is possible. |
| Same patch with security relevance | Prioritized assessment; ordinary deferral cannot hide new security evidence. Remediate or record bounded mitigation/deferral and risk owner. |
| 0.4.1 → 0.5.0 minor | Recorded applicability/compatibility assessment, including intervening changes. |
| 0.4.1 → 1.0.0 major | Recorded breaking-change/compatibility assessment; reviewed migration requires actual authority. |

These reactions match actual `assess_update` outputs and `standards/COMPATIBILITY.md`. All return `applicationAuthorized:false`; “latest should be installed” grants nothing.

Actual checks:

- Both supplied requests returned **`blocked-unknown`, exit 3**. `request.json` lacks the selected target archive and declares `coverage.complete:false`, despite its contradictory “complete two-release fixture” source label.
- `unsupported.json` additionally reports **`host-contract-unsupported`** for declared host contract `9.0.0`. Its installation subsection’s `readable` refers to pinned contract `0.2.0`, not support for the host’s `9.0.0`.
- Selected installed toolkit bytes, complete selected suite, owned rules and receipt match the expected synthetic **0.4.1** pin. Preserve commit `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, archive SHA-256 `18274458ef3b134a353224cc82d0d4f50cfff35b2546856e5a2528a220aaf26a`. No unselected toolkit, runtime, publisher authenticity, or policy certification follows.
- Local `b.zip` actually matches expected target SHA-256 `7e41cc35ab46b7774e6267cd51a3b57b9e6c696fab1f378ee9e2d003d3f4c2db`. A read-only in-memory reassessment binding this archive removed the archive gap; **incomplete intervening coverage still blocks readiness**.
- `RULE-1` retains supplied `already-satisfied` attribution against `notes/policy.md` hash `0d2687308c6063d47adc8214d6658ef82b3f69ac8c4616764a501ab962f96467`. The actual cited upstream prose is only “Synthetic migration notes” / “Synthetic policy”; semantic adequacy is not independently established.

Exact next action: obtain/review the missing watcher pages **2–3**, target/intervening identities and security evidence, retaining `attempt:"partial page1of3"` and `lastSuccessfulPin:"0.4.1"`; observation/last-success timestamps are absent. Prepare a separately reviewed request binding verified `b.zip`, then rerun `upgrade-assess`.

Remaining gate: complete attributed coverage, substantiated semantic applicability, and supported host contract/adapter evidence. Preview/application remain held. All evidence is synthetic; no writes, network actions, completion credit, or acceptance occurred.
