# Post-release execution plan

The owner requested the executable structure on 30 October 2026. The canonical manifest is `examples/projects.json`; `examples/sources/standard/ledger.json` owns scope, state, dependencies, issue mapping and criteria. This document explains the execution order and file ownership. It does not award completion. The source baseline is proposed in PR #14.

## Scope and checkpoints

| Checkpoint | Native GitHub milestone | Horizon | Required leaves | Deferred leaves | Outcome |
| --- | --- | --- | ---: | ---: | --- |
| M5 | [1](https://github.com/interzettel/project-record-standard/milestone/1) | Now | 4 | 0 | Offline handoff plus evidence and work-selection semantics |
| M6 | [2](https://github.com/interzettel/project-record-standard/milestone/2) | Next | 4 | 0 | README-only profile and readable offline records |
| M7 | [3](https://github.com/interzettel/project-record-standard/milestone/3) | Next | 3 | 0 | Tested semantic upgrade assessment, application and distribution |
| M8 | [4](https://github.com/interzettel/project-record-standard/milestone/4) | Later | 0 | 5 | Optional authority, dependency views and convention profiles |
| M9 | [5](https://github.com/interzettel/project-record-standard/milestone/5) | Later | 0 | 2 | Optional physical projections and public discoverability |

Five existing requests (#9, #13, #10, #11, #12) are parent containers for twelve new issues (#15-#26). Six existing requests (#6, #3, #2, #1, #8, #7) remain independently reviewable leaves. Parents and their checklists earn no progress credit. Native milestone closure percentages include request containers and must not be reported as PRS percentages.

The first three checkpoints are the selected eleven-leaf required preparation. Seven P2/P3 leaves remain deferred. No release version or due date is promised. The #9 handoff exit can pass after #15/#16 without waiting for the whole M5 milestone, #1, the inspector or the upgrade suite.

## Work order

An agent selects the earliest unfinished required leaf whose execution prerequisites are complete and whose scope is authorized. Source `dependsOn` contains execution prerequisites; separately stated owner/review/release gates do not silently become start blockers. Existing issue criteria and actual permissions still apply. Limit implementation to one primary package; useful independent preparation is allowed when the selected package is blocked.

| Order | Issue and stable leaf | Deliverable | Checkpoint | Priority | Execution prerequisites |
| --- | --- | --- | --- | --- | --- |
| 01 | [#15](https://github.com/interzettel/project-record-standard/issues/15) · `PRS-HANDOFF-01` | Pin the record boundary and prove one offline handoff | M5 | P1 | None |
| 02 | [#16](https://github.com/interzettel/project-record-standard/issues/16) · `PRS-HANDOFF-02` | Prove adversarial handoff reconciliation and record the exit gate | M5 | P1 | `PRS-HANDOFF-01` |
| 03 | [#6](https://github.com/interzettel/project-record-standard/issues/6) · `PRS-EVIDENCE-STAGES` | Define evidence stages and dependency meanings | M5 | P1 | None |
| 04 | [#3](https://github.com/interzettel/project-record-standard/issues/3) · `PRS-AGENT-EXECUTION` | Select canonical work and reconcile bounded delivery | M5 | P1 | `PRS-EVIDENCE-STAGES` |
| 05 | [#2](https://github.com/interzettel/project-record-standard/issues/2) · `PRS-TAILOR-README` | Support README-only tracking and suite-level versioning | M6 | P1 | None |
| 06 | [#17](https://github.com/interzettel/project-record-standard/issues/17) · `PRS-INSPECT-01` | Inventory declared JSON producers and define inspector coverage | M6 | P1 | None |
| 07 | [#18](https://github.com/interzettel/project-record-standard/issues/18) · `PRS-INSPECT-02` | Render traceable semantic views in one offline inspector | M6 | P1 | `PRS-INSPECT-01`, `PRS-EVIDENCE-STAGES` |
| 08 | [#19](https://github.com/interzettel/project-record-standard/issues/19) · `PRS-INSPECT-03` | Enforce inspector privacy and verify integration profiles | M6 | P1 | `PRS-INSPECT-02`, `PRS-TAILOR-README` |
| 09 | [#20](https://github.com/interzettel/project-record-standard/issues/20) · `PRS-UPGRADE-01` | Compare immutable releases against real host installations | M7 | P1 | None |
| 10 | [#21](https://github.com/interzettel/project-record-standard/issues/21) · `PRS-UPGRADE-02` | Implement reviewed upgrade receipts and recoverable application | M7 | P1 | `PRS-UPGRADE-01` |
| 11 | [#22](https://github.com/interzettel/project-record-standard/issues/22) · `PRS-UPGRADE-03` | Distribute and evaluate the semantic upgrade workflow | M7 | P1 | `PRS-UPGRADE-02`, `PRS-AGENT-EXECUTION`, `PRS-TAILOR-README` |
| 12 | [#1](https://github.com/interzettel/project-record-standard/issues/1) · `PRS-AGENT-AUTHORITY` | Distinguish agent capability from autonomy and authority | M8 | P2 | `PRS-EVIDENCE-STAGES` |
| 13 | [#23](https://github.com/interzettel/project-record-standard/issues/23) · `PRS-CONTROL-01` | Specify dependency readiness and impact formulas with fixtures | M8 | P2 | `PRS-EVIDENCE-STAGES`, `PRS-AGENT-EXECUTION` |
| 14 | [#24](https://github.com/interzettel/project-record-standard/issues/24) · `PRS-CONTROL-02` | Build the optional dependency view and prove reuse | M8 | P2 | `PRS-CONTROL-01` |
| 15 | [#25](https://github.com/interzettel/project-record-standard/issues/25) · `PRS-CONVENTIONS-01` | Specify optional repository and release convention references | M8 | P2 | `PRS-TAILOR-README`, `PRS-UPGRADE-01` |
| 16 | [#26](https://github.com/interzettel/project-record-standard/issues/26) · `PRS-CONVENTIONS-02` | Verify convention profiles across three synthetic consumers | M8 | P2 | `PRS-CONVENTIONS-01` |
| 17 | [#8](https://github.com/interzettel/project-record-standard/issues/8) · `PRS-PROJECTIONS` | Define optional physical projection references and freshness | M9 | P3 | `PRS-EVIDENCE-STAGES` |
| 18 | [#7](https://github.com/interzettel/project-record-standard/issues/7) · `PRS-DISCOVERABILITY` | Audit approved public documentation discoverability | M9 | P3 | None |

## Package instructions

Every leaf issue contains Outcome, Scope, Acceptance, Evidence, Dependencies and Next action. Its intended paths and targeted command are implementation seams, not claims that those future files or tests already exist. An implementer inspects the relevant source before choosing private function signatures. The issue's outcome and acceptance remain the scope boundary.

For each selected leaf, the worker reads its parent request when present, then records the intended change and actual prerequisite state. Code-bearing work begins with a meaningful failing test. The worker implements the bounded outcome, runs its targeted checks and the applicable shared gates, and records exact revision-bound evidence. End-of-package reconciliation updates the canonical source once, preserves its prior observation, regenerates projections, updates the issue/PR and names the next eligible issue. Review and owner acceptance remain attributed decisions.

The first package is **PRS-HANDOFF-01 / #15 / M5**: inspect the record loader, validator and existing evidence policies; map their fields in `standards/HANDOFF.md`; add a synthetic pinned source and a deterministic offline handoff fixture in `tests/test_handoff.py`. Its targeted command is `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_handoff.py' -v`. #16 then adds adversarial reconciliation and the bounded exit verdict. There is no live-agent launch or consumer data ingestion in either package.

## Shared file ownership

| Paths | Primary package | Integration rule |
| --- | --- | --- |
| `standards/STANDARD.md`, evidence vocabulary | #6 | #8 and later views reuse the definitions; they do not fork them. |
| Root `AGENTS.md` | Maintainer operation in PR #14 | #3 owns portable selection/install guidance; root rules route to that guidance. |
| `src/project_record/agents.py`, portable agent instructions | #3, then #21/#22 | Sequence changes to this shared installer; reconcile ownership/conflict tests. |
| README-only profile, marked README rendering | #2 | #19 consumes the profile and retains authored bytes. |
| Inspector source index, semantic tables and audience boundary | #17-#19 | #24 may reuse these parts; graph calculations remain in #23/#24. |
| Upgrade comparisons, transformations and receipts | #20-#22 | Hermes only supplies read-only release/pin observations; it does not become another migration engine. |
| Suite manifest/router/distribution | #22 | Version the future suite deliberately and apply repository skill-authoring/evaluation rules. This plan edits no distributed skill. |
| Brand/profile assets | Zettlerei-owned source | #25/#26 define optional references and fixtures; licensed neutral fallbacks can proceed without brand approval. |

The inspector can render actual installation receipts and explicitly synthetic upgrade receipts before #22 exists. The dependency view is optional and cannot hold the inspector. #23 must resolve cancelled/support denominators, milestone acceptance rules and dependency meanings before #24 freezes calculations. No shared package creates a second ledger or forces a new publisher.

## Authority and GitHub mapping

The ledger owns completion and acceptance fields. GitHub owns discussion and assignment; native milestone numbers and parent links are navigation. Labels use one `type:*`, one `priority:*`, an `area:*`, `tracking:leaf` or `tracking:parent`, and `scope:required` or `scope:deferred`. They are not a second execution-state writer. The repository had no linked GitHub Project when inspected; milestones and filtered issue lists provide the work queue without adding another management system.

Native parent readback confirms #9→#15/#16, #13→#17/#18/#19 and #10→#20/#21. The browser connection ended before the remaining five native links could be saved: #10→#22, #11→#23/#24 and #12→#25/#26. All twelve relationships are already explicit in both the parent tasklists and child issue bodies; all issues have their native milestone. Completing these optional UI links is a bounded bookkeeping action, not a product implementation prerequisite or another accounting leaf.

The historical release snapshot remains `examples/sources/standard/pre-post-release-2026-10-30.json`: **18/18 required and 4/4 milestones**. The expanded authored snapshot is **18/29 required (62.1%)**, **18/36 retained (50.0%)** and **4/9 declared milestones**. Newly selected required work is **0/11** and its milestone outcomes are **0/3**. Adding scope explains the lower ratios; no historical completion was removed. All new milestone acceptance records start false and require Yiğit's attributed decision.

Runtime/suite v0.4.1, contract 0.2.0, old tags/assets, consumer repositories and deployment permissions remain unchanged. The structuring task creates no product implementation credit. Detailed baseline review is separate from the owner's authorization to prepare and organize this plan.

## Verification and resumption

The repository validator checks source identities, unique leaves, WBS coverage, references and cycles. Validate new issue drafts with `project-record lint-issue`. Run the Python suite, skill check, public pipeline, JavaScript tests, palette check, site build and README parity before integrating this shared-source change. Compare the preserved normalized observation against the new export and inspect actual public output. Checks prove their tested boundaries, not live interoperability or owner acceptance.

Resume from #15 unless fresh issue/PR evidence or owner direction changes the eligible queue. Read only the relevant workflow and sources; full portfolio rescans, schema redesign, paper/printer work and native runtime deployment are outside this first package.

## Open contribution and work-language refinement · 30 October 2026

The owner requested an assessment using Diakrisis, official Scrum/Agile terminology and the supplied *Unified Work Management Model*. The [bounded review and decisions](diakrisis-review-2026-10-30.md) explain the adopted and declined parts. [WORK-MODEL](../standards/WORK-MODEL.md) is the shared terminology home. This delivery package contributes documentation to existing leaves; it completes none of their full criteria.

The eleven required leaves and seven deferred leaves keep their identities, order and prerequisites. The first eligible product package remains `PRS-HANDOFF-01` (#15). Any contributor may participate across disciplines; temporary responsibility and actual authority govern execution. The rows below refine the existing interfaces, not a second backlog or new schema commitment.

| Existing package | Guidance for its implementation and review |
| --- | --- |
| #6 · `PRS-EVIDENCE-STAGES` | Keep implementation, integration, verification, Done, acceptance and availability inspectable; test a built but unmerged artifact and deployment without acceptance. Specify artifact-appropriate quality policy and preserve historical meanings. |
| #3 · `PRS-AGENT-EXECUTION` | Select by outcome, prerequisites, holds, authority and capacity; retain unknown evidence. Permit cross-disciplinary contributions and handoffs. Do not infer independence from several review lenses. |
| #1 · `PRS-AGENT-AUTHORITY` (deferred) | Separate task responsibility, capability, risk, accounting ownership and permission. Review scope never locks an agent to a profession. |
| #17/#18 · `PRS-INSPECT-01/02` | Map each field's authoritative writer; distinguish findings from resulting action and decisions from observations. Show containment and prerequisites separately with source freshness. |
| #23 · `PRS-CONTROL-01` (deferred) | Define readiness inputs and unknowns before formulas. Keep structural/remaining depth distinct from duration, critical-path scheduling or permission to execute. |
| #20 · `PRS-UPGRADE-01` | Inventory sources and historical claims before proposing migration. Preserve IDs and authority; preview changes in waves without silently rewriting accepted history. |
| #25 · `PRS-CONVENTIONS-01` (deferred) | Map optional epic/feature/story/task and typed origin/effect/relationship vocabulary. A milestone is a checkpoint; a parent does not imply a prerequisite. Keep the delivery plan separate from an operations runbook. |

The documentation and distribution correction changes no leaf state, acceptance, required/deferred scope or runtime contract. Before and after: new required work 0/11; expanded required work 18/29 (62.1%); retained work 18/36 (50.0%); declared milestone outcomes 4/9. No model roster, fixed cadence, new required tracker, global merge-first rule or permanent agent roles are introduced. Remaining product behavior belongs to the linked packages and their existing gates.

## Execution-readiness correction · 30 October 2026

The [execution-readiness review](execution-readiness-review-2026-10-30.md) distinguishes a valid issue structure from fully detailed execution and reliable skill behavior. #15 is a bounded next mapping/fixture package. #6, #3, #2 and #17–#22 now have internal slices or more direct verification expectations in their existing issue bodies; those slices earn no additional accounting credit. The seven deferred leaves remain progressively detailed when selected.

A package begins with its deliverable, inputs/authority, unresolved decisions and a check that tests the new behavior. Existing metadata, installer or example-ledger checks are supplements where they do not exercise that behavior. Finish a reviewable slice before taking another primary package, preserving partial results without awarding the entire leaf Done. A case/discovery table can be the first result where the contract itself is the work. This does not require line-by-line implementation plans or fixed agent jobs.

Skill metadata and source/package tests pass their tested boundary; the published synthetic application records do not establish universal reliability or causal improvement. Portable work selection, README-only behavior and semantic upgrades remain #3, #2 and #22. Current root guidance is not a completed portable-suite upgrade.

The release workflow is pinned to v0.4.1. No next release cut/version has been selected. Before publication, use `prepare-project-delivery` to define included changes and candidate gates and to update/test the version-bound publication path. A proposed 0.5.0 is not an existing release or a promise that M5–M7 equal its release scope. This review changes no ledger state, prerequisite, denominator or acceptance.
