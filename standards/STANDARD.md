# Shared meaning

Implementation: 0.4.1; contract: 0.2.0. Existing 0.1.0 records remain readable. This extends the intent of Personal Agent Stack ADR-008. An adapting agent must reconcile repository-local policies before adoption. See `PMI-ALIGNMENT.md` for the tailored PMI mapping.

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
| Implemented | The bounded code, configuration or content exists at an identified revision and location. | Establishes existence, not successful behavior, integration or acceptance. |
| Integrated | The change is merged into the project's declared integration branch. | Required for Done only when the item criterion or applicable quality policy requires it. |
| Verified | The stated check passed for the identified artifact, revision and environment. | Credit is limited to that check. |
| Accepted | The designated reviewer accepted the declared outcome. Some technical gates may be automated; owner-only decisions remain owner decisions. | Never inferred from an agent's opinion or issue closure. |
| Release candidate | A plan for a particular component/version/channel and its gates. | Does not prove publication. |
| Release | Published source or artifacts through a named channel at an identified revision. | One channel's publication does not prove another channel's availability. |
| Deployment | An observed artifact or revision in a named environment. | A merge or release does not prove deployment. |
| Changelog | The meaningful user/operator changes, assembled from authored change records. | Describes changes; its headings do not establish publication. |

A roadmap presents direction and milestone checkpoints. Epics optionally group work items; a WBS organizes deliverables and work packages. Milestone support, containment and execution prerequisites are different relations. There is no mandatory roadmap-to-task hierarchy. Phases, initiatives, features and user stories are optional host vocabulary with explicit mappings. Legacy IDs and names remain unchanged. See [work language and open contribution](WORK-MODEL.md) for the Agile/Scrum adaptation and delivery-claim distinctions.

## States

Execution states are Planned, Ready, In progress, In review, Done, Cancelled and Unknown. Blocked is a flag with a reason and next responsible action. Risk and accepted debt are attributes, not extra completion states. Existing labels can map to these terms through an explicit alias table.

A new Done claim means the work item's own criterion and its applicable project quality policy (Definition of Done) are met. The policy must fit the artifact; a project can require integration where relevant. Historical source claims retain their recorded meaning without recertification. Verification, milestone acceptance, publication and deployment are separate claims. A closed issue that was cancelled, rejected or superseded is not completed work. A specified capability is not automatically implemented. An experiment earns completion only against its own declared criterion. A useful negative result can complete a measurement task; a failed or unfinished acceptance check cannot become a pass.

## Evidence claims and dependency meanings

Implemented, Verified, Accepted and Released describe evidence about a deliverable. They do not replace execution states, form a mandatory linear lifecycle, or add fields to contract 0.2.0. Designed/Proposed can describe earlier work; Integrated, Deployed and Delivered remain separately inspectable claims. Readiness L0–L5 and delegated task risk R0–R4 measure different things and grant no authority from a claim or percentage.

| Claim | Minimum subject, evidence and writer | Remaining boundary |
| --- | --- | --- |
| Implemented | Identify the bounded code/configuration/content, exact revision and location; the implementation source establishes that it exists. | An unmerged artifact can be implemented. Presence alone does not establish correctness or the whole item's criterion. |
| Verified | Identify the named check, exact subject/revision, environment, result, producer/source and observation; the check observation owns that result. | A passing check of revision A does not certify revision B. A test of one behavior does not verify all behavior. |
| Accepted | Identify the declared outcome/gate and its designated decision authority's attributed acceptance record. | CI, implementation, deployment and issue closure cannot supply a missing owner decision. Structural validation cannot authenticate a producer. |
| Released | Identify the component/artifact, version, actual channel, exact revision/digest and sourced publication observation. | A candidate, tag or changelog heading alone does not prove the artifact is published. One channel does not prove another; release does not prove deployment. |

The canonical completion writer applies the item's **unchanged criterion plus applicable artifact quality policy** to new Done claims. It retains the evidence dimensions separately. A project can require integration or outcome acceptance for one item and omit them for a read-only research item. A useful negative measurement can meet a research criterion; a failed criterion cannot be relabelled a successful outcome. Historical Done claims keep their source meaning, IDs, states and denominators without retrospective recertification. [Delivery records](DELIVERY.md) specify publication/deployment receipts; [the handoff](HANDOFF.md) demonstrates absent acceptance.

| Relationship | Effect and handling |
| --- | --- |
| Execution prerequisite | Supplies something required to start the identified scope. Keep its declared meaning and source relationship; unfinished prerequisites do not become completed because a worker proceeds. |
| Completion gate | Must pass before the item's own Done claim. Preparation may proceed if execution authority and actual holds permit; the gate and criterion remain pending. |
| Outcome acceptance gate | Must pass before the declared outcome is accepted. Supporting implementation can be Done if its own criterion permits, while the outcome remains unaccepted. |
| Reusable input or parent grouping | Supports work or groups it; does not itself mean a start prerequisite, Done gate or second accounting credit. |
| Unknown legacy dependency meaning | Retain the original relationship and report the missing interpretation. Do not infer start permission or a contradiction from graph order alone. Resolve the host meaning before a dependent action. |

These distinctions are host mappings, not new runtime edge enums. Existing `dependsOn` values and blocked flags remain intact. The current core checks references/cycles and explicit state structure; it does **not** infer dependency meaning, interpret prose criteria, select eligible work, authenticate authorization, or enforce all completion gates. `policy_satisfied` matches supplied metadata only and must receive the exact revision when revision applicability matters. A schema-valid record is not evidence that a newly authored Done claim is justified.

A designated authority can record a **bounded execution exception**: affected work, original prerequisite, allowed actions/environment, decision source/authority, and remaining restrictions/gates. Such an exception permits only its declared preparation. It does not delete `dependsOn`, change Done criteria, accept outcomes or grant merge/release/deployment permission. Use an existing authorized exception without repeated approval requests. A missing exception or authority stays unresolved; do not manufacture one from a request to continue. A genuine scope/criterion change follows the host's source/history/approval policy separately.

### Worked cases

Each row is a separate synthetic project. Fractions concern that project's unchanged required scope; they are not an aggregate portfolio metric. Exact revisions, criteria, receipts and expected results are in `tests/fixtures/evidence_stages/cases.json`, exercised through the existing reader/validator/calculator/evidence policy by `tests/test_evidence_stages.py`.

| Case | Supported claims | Done and remaining gate |
| --- | --- | --- |
| Built but unmerged | LG-1 exporter implementation and exact-revision tests exist on branch B. Its criterion also requires main integration and maintainer outcome acceptance; neither exists. | **0/1**. Preserve implementation/verification; integration and acceptance remain pending. No release/deployment claim. |
| Wrong-revision verification | OB-1 implementation is integrated at C; only A's tests passed. An old v0.1.0 publication at A is retained as history. | **0/1**, active. Test C. Neither old tests nor old publication certify C; this criterion requires no owner acceptance or release. |
| Authorized build-first, accept-later | BUILD depends on ACCEPT as a declared execution prerequisite. Owner Mira's sourced EX-7 allows implementation/offline tests in a disposable branch only. They pass at D, while BUILD's unchanged Done criterion still requires ACCEPT's owner decision. | **0/2**, both In review. Keep the edge and both criteria; prepare review under EX-7, obtain the missing owner decision. No merge/publication/live deployment authorized. |
| Completed negative research | NEG-1's criterion requires comparison, retained measurements/report, method review and applicable quality checks; all pass at E, finding no improvement. | **1/1 can be recorded Done**. Retain the negative result. No criterion requires proving improvement, software release or owner outcome acceptance. If a different criterion required improvement, this result would not satisfy it. |
| Deployed without acceptance | TF-1 code is integrated/tested at F and an authorized staging deployment is healthy. Its criterion still requires owner acceptance, which is absent. | **0/1**. Report staging deployment and missing acceptance separately. No release observation, criterion change or production permission follows. |

Reproduce the deterministic cases with `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_evidence_stages.py' -v`. They check the supplied source/policy boundaries; agent application evidence is separate from these checks and from `check_skills.py` metadata validation. No host runtime permission, publication or completed historical release changes through this clarification.

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

Each fact has one authoritative writer. Reviewed plans own scope, criteria and acceptance records. Repository-local ledgers can continue to own completion. Issues own discussion, assignment, closure and native relationships. Projects own workflow and iteration when the host declares that authority; a Project is optional. Change fragments own the authored change summary. Channel and deployment observations own publication and runtime claims.

The normalized record is a projection. It retains original IDs, source state, source path, commit, file digest, observation date, declared source-update date, evidence and unmapped meaning. A newly generated file cannot make an old observation fresh. Missing, unknown, inaccessible and zero are distinct.

Evidence policies declare `allOf` required kinds and `anyOf` alternatives. Empty policies cannot certify a claim. A passed receipt must match its subject and relevant revision; failed, partial, superseded or mismatched receipts remain visible but do not satisfy the policy. JSON validation cannot authenticate an owner's approval or prove a historical measurement occurred. Retain the underlying attributed record.

Migration preserves historical source claims and identifies incomplete mappings. Do not manufacture typed evidence for an old `done` field. New completion claims must carry the repository's required proof. Acceptance is never upgraded merely because an adapter was installed.

## Authority and privacy

Public Pages consumes an explicitly approved public projection. Private source material, private URLs and revealing private totals are excluded by policy. Public export refuses private inputs. A later adapting agent must author and review its public projection; changing a visibility flag is not evidence of a privacy review.

The public page is read-only. Source and issue links lead to the authoritative editing surface. No visitor token, background model call, remote write, drag-to-change status or live GitHub request is required to view the latest successful build.

## Percentage rounding

Display percentages to one decimal place with upward ties: 13/16 is 81.3%. Compute from exact counts; average unrounded milestone shares before rounding. Empty scope is Not measured. Python, browser calculations and release readiness use this rule. Four-decimal history effects are explanatory percentage points, not a second completion metric.
