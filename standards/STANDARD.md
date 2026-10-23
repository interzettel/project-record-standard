# Shared meaning

Implementation: 0.4.0; contract: 0.2.0. Existing 0.1.0 records remain readable. This extends the intent of Personal Agent Stack ADR-008. An adapting agent must reconcile repository-local policies before adoption. See `PMI-ALIGNMENT.md` for the tailored PMI mapping.

## Vocabulary

| Term | Shared meaning | Counting rule |
| --- | --- | --- |
| Roadmap | The direction of the project, expressed through milestones and Now/Next/Later horizons. | A named summary of its milestones; the aggregation method is visible. |
| Milestone | A checkpoint with a user or operator outcome and explicit exit criteria. | Reached only when its declared gates pass. |
| Epic | A coherent group of related work items. | Contains leaves; is not counted again as an extra leaf. |
| Work item | A stable, independently checkable leaf in the ledger. | One item has one primary accounting scope. |
| Work package | The lowest managed component in a deliverable-oriented work breakdown structure. It maps to the affected leaf IDs. | A package and its underlying leaves must not both earn progress credit. |
| Delivery package | A bounded implementation, experiment or review assigned through an issue/PR. It can implement part or all of a work package. | References existing leaves; earns no duplicate credit. |
| Task | An execution step or a repository's legacy name for a work item. | Only a declared accounting leaf enters the percentage. |
| Scope | The boundary of an outcome or package: inclusions, exclusions, dependencies and criteria. | Scope changes are recorded; it is not another mandatory hierarchy level. |
| Capability | A lasting thing the product can do. | Can improve across milestones and releases; not automatically an accounting leaf. |
| Gate | A criterion and its required evidence or designated acceptance. | All required criteria pass; a high work percentage cannot substitute. |
| Verified | The stated check passed for the identified artifact, revision and environment. | Credit is limited to that check. |
| Accepted | The designated reviewer accepted the declared outcome. Some technical gates may be automated; owner-only decisions remain owner decisions. | Never inferred from an agent's opinion or issue closure. |
| Release candidate | A plan for a particular component/version/channel and its gates. | Does not prove publication. |
| Release | Published source or artifacts through a named channel at an identified revision. | One channel's publication does not prove another channel's availability. |
| Deployment | An observed artifact or revision in a named environment. | A merge or release does not prove deployment. |
| Changelog | The meaningful user/operator changes, assembled from authored change records. | Describes changes; its headings do not establish publication. |

The usual planning view is **roadmap → milestone → epic → work item**. It is not a mandatory WBS hierarchy. A milestone is a checkpoint; its displayed work percentage describes the supporting scope. A small project may omit epics. A WBS organizes deliverables and work packages separately when needed. Phases and initiatives are optional grouping views. Legacy IDs and names remain unchanged in the source, with explicit aliases for differing terms.

## States

Execution states are Planned, Ready, In progress, In review, Done, Cancelled and Unknown. Blocked is a flag with a reason and next responsible action. Risk and accepted debt are attributes, not extra completion states. Existing labels can map to these terms through an explicit alias table.

Done means the work item's own criterion is complete. Verification, milestone acceptance, publication and deployment are separate claims. A closed issue that was cancelled, rejected or superseded is not completed work. A specified capability is not automatically implemented. An experiment earns completion only against its own declared criterion. A useful negative result can complete a measurement task; a failed or unfinished acceptance check cannot become a pass.

## Percentages

Percentages are first-class information. Every displayed percentage names its measure, scope, numerator, denominator, exclusions and observation.

| Measure | Formula | Suitable use |
| --- | --- | --- |
| Required work progress | Completed required leaves / required leaves × 100 | An active milestone, epic or declared current scope. |
| Retained ledger progress | Completed retained leaves / retained leaves × 100 | A whole-ledger view that includes deferred work. |
| Accepted milestones | Accepted milestones / declared milestones × 100 | Outcome acceptance. |
| Exit criteria met | Passed declared gates / declared gates × 100 | Showing the remaining gap within one milestone. |
| Equal-milestone roadmap progress | Mean of each milestone's required-work fraction × 100 | Giving each milestone equal weight despite different leaf counts. |

An equal-milestone mean, retained-ledger progress and required-scope progress are different named measures. Each project selects the measures its readers need, with exact counts and exclusions visible.

Calculate from exact fractions and round only the final displayed number, normally to one decimal place. In-progress work gets no fractional credit. Do not average a work percentage with acceptance or environment health. A zero denominator is Not measured, not 0% or 100%. A cancelled item is outside successful-delivery accounting. Optional and deferred work remain visible outside the required denominator, with a reason. The retained ledger and required scope can be shown together when clearly named.

Do not remove a denominator because its percentage looks inconvenient. Record additions, splits, removals and deferrals with stable IDs and a reason. Preserve the previous baseline. Known work without leaf records is listed beside the percentage and is not silently counted as zero completed tasks. Weighted effort is a separate optional measure with declared weights and a versioned formula; this implementation uses leaf counts and equal-milestone means.

## Evidence and sources

Each fact has one authoritative writer. Reviewed plans own scope, criteria and acceptance records. Repository-local ledgers can continue to own completion. Issues own discussion, assignment, closure and native relationships. Projects own workflow and iteration. Change fragments own the authored change summary. Channel and deployment observations own publication and runtime claims.

The normalized record is a projection. It retains original IDs, source state, source path, commit, file digest, observation date, declared source-update date, evidence and unmapped meaning. A newly generated file cannot make an old observation fresh. Missing, unknown, inaccessible and zero are distinct.

Evidence policies declare `allOf` required kinds and `anyOf` alternatives. Empty policies cannot certify a claim. A passed receipt must match its subject and relevant revision; failed, partial, superseded or mismatched receipts remain visible but do not satisfy the policy. JSON validation cannot authenticate an owner's approval or prove a historical measurement occurred. Retain the underlying attributed record.

Migration preserves historical source claims and identifies incomplete mappings. Do not manufacture typed evidence for an old `done` field. New completion claims must carry the repository's required proof. Acceptance is never upgraded merely because an adapter was installed.

## Authority and privacy

Public Pages consumes an explicitly approved public projection. Private source material, private URLs and revealing private totals are excluded by policy. Public export refuses private inputs. A later adapting agent must author and review its public projection; changing a visibility flag is not evidence of a privacy review.

The public page is read-only. Source and issue links lead to the authoritative editing surface. No visitor token, background model call, remote write, drag-to-change status or live GitHub request is required to view the latest successful build.

## Percentage rounding

Display percentages to one decimal place with upward ties: 13/16 is 81.3%. Compute from exact counts; average unrounded milestone shares before rounding. Empty scope is Not measured. Python, browser calculations and release readiness use this rule. Four-decimal history effects are explanatory percentage points, not a second completion metric.
