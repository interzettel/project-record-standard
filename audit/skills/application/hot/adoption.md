# Loomglass hot adaptation

Observed 2026-10-22. Owner: Sam. Local source revision: `17a9314a06e339c87b247db805be30b6d84f1c9c`. Implementation and contract: Project Record Standard 0.2.0. The canonical checkout reports `59396a891fbc740ffe0be095f02934dfae270d38` with local modifications; exact tested runtime and reference hashes, their refreshed observation and an owned recovery snapshot are in `progress/toolkit-pin.json`.

## Field authority and adapter

| Field | Authoritative source | Adaptation |
| --- | --- | --- |
| Purpose and selected outcome | README.md and docs/brief.md | Offline print-design notebook; reproducible import-to-proof workflow. |
| IDs, titles, groups, leaf completion, Later exclusions and native roadmap gates | legacy/plan.json | `portfolio-v3` projects the existing panels/groups/tasks/roadmap shape without rewriting it. |
| New product verification | Future criterion/revision-specific evidence | None supplied; historical Done remains `source-reported`, with no invented typed receipts. |
| Owner acceptance, approved baseline and scope changes | Sam's attributed decisions | None supplied. Proposed mapping is not an approved baseline. |
| Proposed WBS and tailored operating responsibility | progress/governance.json | One package per native group; references each leaf once; partial substantive coverage; Sam accountable, execution assignees unknown. |
| Hosted issue assignment/workflow/closure and delivery packages | Native hosted records, if later available | No remote or collection; no labels, issues or Projects created. |
| Brand and existing route | site/index.html; README.md | Preserve Loomglass, Georgia/serif, burgundy/cream and the existing site file. |
| Normalized output and calculations | Private projection generated from declared inputs | progress/derived/** only; it never writes back to the native plan. |

`portfolio-v3` matches the native leaf and Later semantics exactly. No custom adapter or source migration was needed. There is one unresolved acceptance distinction: the adapter names its all-native-gate-tasks result `accepted`; this is only a checklist checkpoint here. It cannot be presented as Sam acceptance. The generated README/SVG are unintegrated private previews and must not be published with that ambiguous label. Full acceptance parity/cutover remains blocked until Sam defines the applicable gate and supplies any required decision evidence.

There is no hosted repository identity. The runtime's Git source mode requires hosted `owner/repository` syntax and manufactures GitHub source URLs. The manifest therefore uses an honest content-addressed local projection with `repository: null`, `commit: null`, and the known full local Git revision, path, blob and digest retained in `source.originGit`. This schema accommodation does not hide the Git pin or refresh a stale source. `verify.py` requires HEAD, all refs and every original file digest to match; the complete local Git history is also replayable from `progress/rollback/pre-adoption.bundle`. Source `updatedOn` stays unknown. No remote URL is invented.

## Native crosswalk

| Native meaning | Runtime projection | Boundary |
| --- | --- | --- |
| `done` | `done` | Historical completion only; no new product verification. |
| `active` | `active` / In progress | Whole-leaf credit remains zero. |
| `planned` | `backlog` / Planned | Does not mean execution Ready. |
| `later` reason | `required: false`, original `deferReason` | Retained in whole-ledger accounting. |
| Undeclared dependencies | Empty projected links plus `dependencyCoverage: not-declared` | Unknown real prerequisites; not proof of independence. |
| Native milestone `gate` array | `all-gate-items` checkpoint | Separate from Sam acceptance. |

| IDs retained verbatim | Group / WBS package | Primary milestone | Native state | Required? |
| --- | --- | --- | --- | --- |
| LG-1, LG-2, LG-3, LG-4 | G1 Import / WBS-G1 | M1 / Now | done | Yes |
| LG-5 | G2 Proof / WBS-G2 | M2 / Next | active | Yes |
| LG-6 | G2 Proof / WBS-G2 | M2 / Next | planned | Yes |
| LG-7 | G3 Discovery / WBS-G3 | M3 / Later | done | No; preserve source Later reason |
| LG-8 | G3 Discovery / WBS-G3 | M3 / Later | planned | No; preserve source Later reason |

All eight leaf IDs, three group IDs and three milestone IDs keep identity aliases (the old ID is the new ID). No renamed or new accounting leaves, deletions, cancelled items or shared-prerequisite double counting were introduced. `tasks` is the native alias for accounting leaves. `groups` provides a planning group and provisional WBS mapping; packages are not counted again. Delivery packages are absent locally and hosted coverage is unknown.

## Count reconciliation

| Measure | Before, independent native count | After, toolkit check | Exclusions / evidence boundary |
| --- | --- | --- | --- |
| Required work | 4/6 = 66.7% | 4/6 = 66.7% | LG-7/LG-8 excluded; four historical Done claims in selected scope. |
| Retained ledger | 5/8 = 62.5% | 5/8 = 62.5% | Includes LG-7 historical Done and LG-8 planned. |
| Native checklist checkpoints | 1/3 = 33.3% | 1/3 = 33.3% | M1 4/4 gates; M2 0/2; M3 0/1. Not Sam acceptance. |
| Sam-accepted milestones | Unknown; 0 attributed decisions supplied / 3 milestones | Unknown | Do not publish 0/3 or 1/3 as a sourced owner-acceptance percentage. |
| Equal-milestone required-work mean | Not measured | Not measured | M3 required 0/0; undefined milestone fraction is not zero. |

Required state change: zero. Required denominator change: zero. Retained state change: zero. Retained denominator change: zero. No new baseline approval or retroactive receipt was created. Only one pinned local observation exists; intervening history and historical completion dates are unknown. `progress/evidence/native-before.json` provides independent source counts and `progress/evidence/verification.json` records comparison against toolkit output.

## Cleanup order and selected plan

1. Sam clarifies LG-5/LG-6 outcomes, criteria and dependency order. Their generic names block an executable proof plan. Keep both IDs and their distinct states.
2. Sam resolves native checkpoint versus owner acceptance before host cutover. Historical Done is not new assurance, and checklist completion does not certify the import-to-proof workflow.
3. If hosted integration is wanted, Sam supplies real repository identity/access; then collect every page, inspect unfinished PRs and branches, and map existing stable IDs before any write. No unavailable branch is proposed for deletion or PR for closure.
4. Sam reviews privacy and the additive host presentation; then verify relevant interaction and accessibility behavior. Existing README/site source counts already agree, so there is no source replacement to prioritize.
5. Preserve optional Discovery work and its history. No speculative product ideas enter the selected denominator.

Detailed reasons, evidence, outcomes, ownership and next actions are in `progress/discovery.json`. No local safety incident or extra unfinished implementation branch was found. Missing product criteria are a planning dependency, not a fabricated `blocked` state in the native ledger. Budget, resources and stakeholder completeness remain not assessed. Now/Next/Later horizons are retained; no delivery dates are invented.

## Completed and pending

Completed: inventory of every local authored file and all available refs; source/brand/claim preservation; matching adapter; private host manifest; proposed governance/WBS/operations handoff; independent before counts; `adoption-plan` and `check`; three empty-directory deterministic builds, including recovery with the owned runtime; source hash and Git bundle verification; private-to-public export refusal; full repeat-run verification.

Pending: Sam's detailed acceptance criteria and first actual approval if desired; owner-acceptance semantics; unavailable hosted inventory and hosted parity; public projection/privacy review; any additive site or README connection; real browser, keyboard, zoom and screen-reader evidence; deployment observation. These affect the stated cutover gates, not the completed local preparation.

The first verification stopped because four referenced canonical documents changed after discovery. Its exact observed failure and old/new hashes are preserved in `progress/evidence/failed-pin-attempt.json`; references were re-read and refreshed, and runtime bytes were unchanged. All drift checks remain enabled. One verifier assertion was corrected to compare package IDs as keys; its narrow correction is recorded separately. Successful receipts follow these preserved attempts.

## Incremental cutover and rollback

The current cutover is additive local preparation only: `renderer: host` emits data plus private README previews; it emits no replacement HTML page. Neither the README nor site was edited. No skills installation, workflow, schedules, credentials, commits, external effects or deployment were added.

For later cutover, Sam first resolves the pending claim/privacy/accessibility decisions, then connects reviewed data through the existing shell and route. Preserve all old content and the rollback artifact until that cutover is accepted. Hosted operations need an actual remote identity and their own scoped authorization. Do not publish the owner-only derived tree or resolve privacy by flipping `visibility`.

To roll back this preparation, leave the five original files and Git refs untouched; stop using the additive manifest/derived data and remove only the newly owned `progress/` and `tools/project-record-standard/` paths after retaining the rollback bundle elsewhere if needed. Restore an accidentally damaged original file from its exact matching `progress/rollback/original/` copy after reviewing the difference. Use the bundle in an empty recovery repository to inspect original history, rather than resetting the live ledger. `progress/HANDOFF.md` gives replay and generated-output recovery commands.
