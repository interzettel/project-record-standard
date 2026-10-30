# Infrastructure execution plan

The owner requested a maintained, low-overhead infrastructure: install once, reconcile routine work automatically, preserve source authority and show progress, next work, failures and scope growth. The [architecture](../standards/ARCHITECTURE.md), [compatibility policy](../standards/COMPATIBILITY.md), [records profile direction](../standards/RECORDS.md) and [feedback route](../standards/FEEDBACK.md) define the selected maintainer design. The ledger remains the only completion/scope/dependency writer.

## Scope and release direction

The prior plan is preserved under `progress/history/2026-10-30-before-infrastructure/`; its exact ledger is `examples/sources/standard/pre-infrastructure-2026-10-30.json`. The expansion adds sixteen leaves: thirteen required, three deferred. Thirty-four post-release delivery leaves now comprise twenty-four required and ten deferred; five existing parent requests earn no extra credit. Existing historical completion and acceptance stay unchanged.

The [revised release direction](release-direction.md) proposes a foundations 0.5.0, opt-in 0.6.0-alpha previews and a supported 0.6.0 only after real-session/evaluation gates. It replaces the earlier sixteen-package single release batch. Versions remain candidates. #38 currently depends on final evaluation: preparing earlier releases needs explicit detailing/dependency reconciliation before publication, not an inferred bypass. Execution prerequisites and counted scope remain unchanged by this proposal.

## Ordered packages

Pick the earliest authorized required leaf whose execution prerequisites and actual holds/authority permit it. This order changes priority, not the meaning of existing `dependsOn`. #27 completed the bounded records investigation; #28 also completed the policy catalogue; #29 has completed the optional mapping/helpers; #30 has completed read-only pin/compatibility checks; #15 is now the earliest eligible unfinished package. #15 remains the first handoff implementation. Parallel independent preparation is allowed without creating permanent contributor roles.

| Order | Issue / stable leaf | Checkpoint | Scope | Execution prerequisites |
| ---: | --- | --- | --- | --- |
| 01 | [#27](https://github.com/interzettel/project-record-standard/issues/27) · `PRS-RECORDS-01` · Investigate personal memory and project record lifecycles | M13 | Required | None |
| 02 | [#28](https://github.com/interzettel/project-record-standard/issues/28) · `PRS-POLICY-01` · Specify the rule catalogue and enforcement boundaries | M10 | Required | `PRS-RECORDS-01` |
| 03 | [#29](https://github.com/interzettel/project-record-standard/issues/29) · `PRS-RECORDS-02` · Define portable file layouts and record naming profiles | M13 | Required | `PRS-RECORDS-01`, `PRS-POLICY-01` |
| 04 | [#30](https://github.com/interzettel/project-record-standard/issues/30) · `PRS-PIN-01` · Implement verified installation pins and compatibility assessment | M10 | Required | `PRS-POLICY-01`, `PRS-RECORDS-02` |
| 05 | [#15](https://github.com/interzettel/project-record-standard/issues/15) · `PRS-HANDOFF-01` · Pin the record boundary and prove one offline handoff | M5 | Required | None |
| 06 | [#16](https://github.com/interzettel/project-record-standard/issues/16) · `PRS-HANDOFF-02` · Prove adversarial handoff reconciliation and record the exit gate | M5 | Required | `PRS-HANDOFF-01` |
| 07 | [#6](https://github.com/interzettel/project-record-standard/issues/6) · `PRS-EVIDENCE-STAGES` · Define evidence stages and dependency meanings | M5 | Required | None |
| 08 | [#3](https://github.com/interzettel/project-record-standard/issues/3) · `PRS-AGENT-EXECUTION` · Select canonical work and reconcile bounded delivery | M5 | Required | `PRS-EVIDENCE-STAGES` |
| 09 | [#31](https://github.com/interzettel/project-record-standard/issues/31) · `PRS-GATE-01` · Expose deterministic policy checks through the shared CLI | M10 | Required | `PRS-POLICY-01`, `PRS-PIN-01`, `PRS-EVIDENCE-STAGES` |
| 10 | [#32](https://github.com/interzettel/project-record-standard/issues/32) · `PRS-RECONCILE-01` · Reconcile completed work automatically with a resumable journal | M10 | Required | `PRS-GATE-01`, `PRS-AGENT-EXECUTION`, `PRS-RECORDS-02` |
| 11 | [#33](https://github.com/interzettel/project-record-standard/issues/33) · `PRS-GATE-02` · Verify the CI enforcement profile and its bypass limits | M10 | Required | `PRS-GATE-01`, `PRS-PIN-01` |
| 12 | [#34](https://github.com/interzettel/project-record-standard/issues/34) · `PRS-HOOK-01` · Pilot after-work adapters in supported agent runtimes | M10 | Required | `PRS-RECONCILE-01`, `PRS-GATE-02` |
| 13 | [#35](https://github.com/interzettel/project-record-standard/issues/35) · `PRS-RECONCILE-02` · Prove unattended tracking and recovery in real work sessions | M10 | Required | `PRS-HOOK-01`, `PRS-GATE-02` |
| 14 | [#36](https://github.com/interzettel/project-record-standard/issues/36) · `PRS-FEEDBACK-01` · Route encountered standards gaps into deduplicated feedback | M11 | Required | `PRS-POLICY-01`, `PRS-RECORDS-02`, `PRS-AGENT-EXECUTION` |
| 15 | [#37](https://github.com/interzettel/project-record-standard/issues/37) · `PRS-EVAL-01` · Challenge automatic tracking across models and runtimes | M10 | Required | `PRS-RECONCILE-02`, `PRS-AGENT-EXECUTION`, `PRS-FEEDBACK-01` |
| 16 | [#38](https://github.com/interzettel/project-record-standard/issues/38) · `PRS-RELEASE-01` · Prepare the next versioned release and adopter handoff | M11 | Required | `PRS-EVAL-01`, `PRS-HANDOFF-02`, `PRS-EVIDENCE-STAGES`, `PRS-FEEDBACK-01` |
| 17 | [#2](https://github.com/interzettel/project-record-standard/issues/2) · `PRS-TAILOR-README` · Support README-only tracking and suite-level versioning | M6 | Required | None |
| 18 | [#17](https://github.com/interzettel/project-record-standard/issues/17) · `PRS-INSPECT-01` · Inventory declared JSON producers and define inspector coverage | M6 | Required | None |
| 19 | [#18](https://github.com/interzettel/project-record-standard/issues/18) · `PRS-INSPECT-02` · Render traceable semantic views in one offline inspector | M6 | Required | `PRS-INSPECT-01`, `PRS-EVIDENCE-STAGES` |
| 20 | [#19](https://github.com/interzettel/project-record-standard/issues/19) · `PRS-INSPECT-03` · Enforce inspector privacy and verify integration profiles | M6 | Required | `PRS-INSPECT-02`, `PRS-TAILOR-README` |
| 21 | [#20](https://github.com/interzettel/project-record-standard/issues/20) · `PRS-UPGRADE-01` · Compare immutable releases against real host installations | M7 | Required | None |
| 22 | [#21](https://github.com/interzettel/project-record-standard/issues/21) · `PRS-UPGRADE-02` · Implement reviewed upgrade receipts and recoverable application | M7 | Required | `PRS-UPGRADE-01` |
| 23 | [#22](https://github.com/interzettel/project-record-standard/issues/22) · `PRS-UPGRADE-03` · Distribute and evaluate the semantic upgrade workflow | M7 | Required | `PRS-UPGRADE-02`, `PRS-AGENT-EXECUTION`, `PRS-TAILOR-README` |
| 24 | [#39](https://github.com/interzettel/project-record-standard/issues/39) · `PRS-OPS-01` · Implement quiet release-drift monitoring with freshness recovery | M11 | Required | `PRS-PIN-01`, `PRS-UPGRADE-01` |
| 25 | [#1](https://github.com/interzettel/project-record-standard/issues/1) · `PRS-AGENT-AUTHORITY` · Distinguish agent capability from autonomy and authority | M8 | Deferred | `PRS-EVIDENCE-STAGES` |
| 26 | [#40](https://github.com/interzettel/project-record-standard/issues/40) · `PRS-MCP-01` · Evaluate a thin local MCP adapter over the shared core | M12 | Deferred | `PRS-GATE-01`, `PRS-PIN-01` |
| 27 | [#23](https://github.com/interzettel/project-record-standard/issues/23) · `PRS-CONTROL-01` · Specify dependency readiness and impact formulas with fixtures | M8 | Deferred | `PRS-EVIDENCE-STAGES`, `PRS-AGENT-EXECUTION` |
| 28 | [#24](https://github.com/interzettel/project-record-standard/issues/24) · `PRS-CONTROL-02` · Build the optional dependency view and prove reuse | M8 | Deferred | `PRS-CONTROL-01` |
| 29 | [#25](https://github.com/interzettel/project-record-standard/issues/25) · `PRS-CONVENTIONS-01` · Specify optional repository and release convention references | M8 | Deferred | `PRS-TAILOR-README`, `PRS-UPGRADE-01` |
| 30 | [#26](https://github.com/interzettel/project-record-standard/issues/26) · `PRS-CONVENTIONS-02` · Verify convention profiles across three synthetic consumers | M8 | Deferred | `PRS-CONVENTIONS-01` |
| 31 | [#41](https://github.com/interzettel/project-record-standard/issues/41) · `PRS-TEMPLATE-01` · Improve tracker icons and visual templates accessibly | M8 | Deferred | `PRS-TAILOR-README` |
| 32 | [#42](https://github.com/interzettel/project-record-standard/issues/42) · `PRS-HOST-01` · Decide whether remote hosting solves a measured need | M12 | Deferred | `PRS-MCP-01`, `PRS-OPS-01` |
| 33 | [#8](https://github.com/interzettel/project-record-standard/issues/8) · `PRS-PROJECTIONS` · Define optional physical projection references and freshness | M9 | Deferred | `PRS-EVIDENCE-STAGES` |
| 34 | [#7](https://github.com/interzettel/project-record-standard/issues/7) · `PRS-DISCOVERABILITY` · Audit approved public documentation discoverability | M9 | Deferred | None |

## Package boundaries and verification

Each issue names outcome, paths, criterion, direct evidence, execution prerequisites and next action. Internal slices can be separate reviewable commits/PRs but earn no separate accounting points. Test new behavior with nonempty discovered cases; metadata, installer success and example-ledger validation are supplements when they do not exercise it. Preserve the execution-readiness review's findings and actual negative evidence. Future paths/tests are planned, not implemented merely because a command is listed.

The policy/core is shared by CLI, hooks, CI and optional MCP. A journal/outbox is recovery transport, not a second ledger. Normal work must not require manual copying or duplicate tracker edits; capture actual tracking time, interventions, failed/missed updates and recovery in #35/#37. Stable IDs, source and artifact revisions, claim boundaries and scope admission are explicit. Human-only acceptance stays separate from configured routine record writes.

Record and memory classification (#27/#29) precedes path/pin and write policy. #25/#26 consume that profile for broader conventions and brand references. #41 owns optional icons/template polish with pinned licences, labels and real accessibility evidence. #36 owns evidence-based, deduplicated upstream feedback from actual work; no quota or background idea generation is required. Existing #20-#22 own semantic upgrades; the watcher #39 remains a thin host-scheduled observer rather than a competing migration engine. #40/#42 are conditional transport/hosting investigations; no VPS is needed for core adoption.

Use repository skills: `use-project-records` routes, `govern-project-scope` maintains decomposition, `connect-github-tracking` maps native objects, `update-project-progress` records evidence/history, `operate-project-tracking` handles recovery, and `prepare-project-delivery` owns release work. `present-project-tracking` and `verify-project-accessibility` govern public views. Any distributed skill edit follows the existing authoring/evaluation process. The eleven released skill bodies remain unchanged by this planning expansion.

## Authority, pins and source history

Expected pins, observed installation receipts, work completion and model recall are different facts with declared writers. Current development dependencies/actions are reviewed against upstream and pinned; weekly dependency proposals are bounded and do not auto-merge. Existing v0.4.1 release bytes, consumer pins and historic receipts are unchanged. A new release may require assessment without immediate application; read the compatibility matrix for minor/major/security/ordinary patch and prerelease handling.

The requested consolidation authorizes reviewed PR integration and public Pages updates. It does not accept new product outcomes or grant every future adapter credentials, infrastructure spending or autonomous scope. Detailed new baselines remain proposed. No new work item is Done from this structuring task.

## Counts and next work

Before→after: required 18/29 (62.1%)→18/42 (42.9%); retained 18/36 (50.0%)→18/52 (34.6%); accepted declared milestones 4/9→4/13 (30.8%). At expansion, newly required work was0/24 and its six milestone outcomes0/6. Added scope explains the ratio change; no historical completed ID or acceptance is removed.

New native milestones6,7,8,9 map to canonicalM10,M11,M12,M13. Existing native1-5 map toM5-M9. GitHub milestone closure counts include parent requests and are not the canonical percentages. No due dates or effort/value forecasts are invented.

After the records investigation in [PR #43](https://github.com/interzettel/project-record-standard/pull/43), required work is19/42 (45.2%), retained work19/52 (36.5%) and newly required work1/24; accepted milestones stay4/13. No scope or required denominator changed. The comparison and five routing cases are in `audit/records/2026-10-30/`; M13 acceptance and #29 remain pending.

Policy/control ownership is now specified by #28. Next, execute **PRS-RECORDS-02 / #29 / M13** to map optional paths and naming with three-host fixtures. Do not start by provisioning a service or mass-updating consumer repositories.

## Policy completion and next package

PR44 completes #28 with17 rules,5 paired tests and explicit unenforced boundaries. Required19/42→20/42 (47.6%); retained19/52→20/52 (38.5%); newly required2/24; accepted milestones remain4/13. No criteria/dependencies/scope changed. Next: **PRS-RECORDS-02 / #29 / M13**. The release proposal separates foundations, experimental integration and supported operation; earlier release preparation remains held for #38 detailing.

## Optional records mapping completion

PR45 completes #29 with three synthetic hosts, read-only mapping/index/preview helpers and20 layout tests. Four material review findings were reproduced and fixed;60 Python tests pass. Required20/42→21/42 (50.0%); retained20/52→21/52 (40.4%); newly required3/24; accepted milestones remain4/13. No scope or criterion/dependency changed. M13 work gates complete without inferred outcome acceptance. Next: **PRS-PIN-01 / #30 / M10**. Earlier narrative handoffs retain their dated sequence; this is the current next action.

## Pin verification completion

PR46 completes #30 with24 pin tests, existing-receipt preservation and explicit provenance/runtime/application limits. Required21/42→22/42 (52.4%); retained21/52→22/52 (42.3%); newly required4/24; accepted milestones remain4/13. No scope, criteria, dependencies or runtime floor changed. Four regression failures from review were reproduced and corrected. Current next action: **PRS-HANDOFF-01 / #15 / M5**. #38 must select/test the supported minimum before publication; no old release bytes are rewritten.
