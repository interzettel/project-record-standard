# Historical document — captured 23 October 2026 before release preparation

This verbatim document contains successive observations. Its former “current” statements apply only to their original scopes; use the current overview and delivery guide for present status.

# Public-source distribution verification

## Native zoom verified; Narrator confirmed by owner

On 23 October 2026, the owner set local Edge to 200% and 400%. The agent observed device-pixel ratios 2 and 4 and viewport widths 1276 and 638 CSS px, respectively, from a 2552px-wide baseline. At 200%, root content/scroll width stayed 1268/1268; at 400%, 634/634. The standard tracker, guide start and Prehnite reference had no horizontal page overflow in the inspected states.

Checks covered tracker skip navigation, filtered-out inspector closure to Find work, search commit to Work map, readable-list selection/inspector, release and changelog views, guide skip navigation and the Prehnite inspector. At 400%, settled Close bounds were y47–91 in a 358px-high viewport. The Prehnite 200% settled bounds were y362–406 in 717px. An earlier immediate measurement during smooth scrolling was outside the viewport; it was not treated as a settled focus failure.

The owner reported: “done. narrotor works dont worry”. Narrator is therefore recorded as **owner-reported working**, alongside the directly observed native zoom checks. The agent did not hear or record speech; browser/screen-reader versions and a speech transcript remain unavailable. This is scoped acceptance, not a full WCAG conformance claim. Native 400% produced 638 CSS px; earlier 320px fixture checks remain separate evidence.

The [completion receipt](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/native-completion.json) preserves the original STD-18 criterion and accepted scope. Detailed [200%](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/native-200-observation.json) and [400%](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/native-400-observation.json) observations are retained. Required work moves 17/18→18/18 (100%); milestone gates 3/4→4/4. Earlier blocked attempts below remain historical. The personal accessibility skill save was already verified.


## Personal save resolved; native checks awaiting direct evidence

The accessibility skill was saved successfully to the personal Skills collection on 23 October 2026. A subsequent remote fetch verified the persisted skill and matching report-template hash. The earlier HTTP422 save failure below is historical. The receipt is in [native check follow-up](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/native-check-followup.json).

Native zoom was attempted in the connected local Edge browser using zoom/reset shortcuts and Ctrl+wheel. The observed viewport width and device-pixel ratio did not change, so neither 200% nor 400% was established. This is an unavailable native-control test, not a passing resize check. No screen-reader speech or version can be observed through the available browser controls.

The owner requested these checks after the scoped package acceptance. STD-18 records that expanded scope: 17/17 becomes 17/18 (94.4%), with 3/4 milestone gates accepted. Original STD-13 acceptance is retained. Completing the remaining check requires actual native zoom plus versioned Narrator/NVDA speech observations.

### Direct check sequence

1. In the live tracker, use Edge’s native menu to set zoom to 200%. Inspect all controls and the item inspector; repeat at 400% for reflow. Keep the zoom percentage visible and retain any clipping, overlap or lost controls. Reset to 100% afterward.
2. Start a real screen reader, record its name/version and the Edge version. On Windows, Narrator starts/stops with Windows+Ctrl+Enter. Record what it actually says as you use the skip link, reach the main content, traverse milestone/filter controls and open/close a work item.
3. Change Find work and Status. Confirm a short result update is announced, control names and selected states are understandable, and focus returns to the matching item or Find work after closure. Also check the guide navigation and the history table. Report failures and exact observed phrases; semantic inspection alone does not pass this check.

Native control and listening evidence must come from the actual browser/screen reader. There is no requirement for exact identical spoken phrasing across screen readers.


## Readiness setup integration — 0.4.1

Both cold/hot workflow skills now require the portable L0–L5 assessment contract and empty JSON record. The record keeps all ten dimensions unknown until inspected, current/target grades separate, R0–R4 task authority explicit, central assessment/history references and reassessment triggers. Five fresh guided scenario applications, all 35 Python tests, installer/source-package checks and the twelve-page guide build verify the integration; see [evaluation](https://github.com/interzettel/project-record-standard/blob/main/audit/readiness/EVALUATION.md). All eleven skills retain their names; contract 0.2.0 is unchanged.

Scope grows from 16/16 to 17/17 through completed STD-17; no old ID is removed. This evidence awards no readiness grade or autonomous authority. No individual repository migration or private upstream assessment publication occurred. Earlier accessibility limits remain explicit.


## Completed scoped accessibility review — 0.4.0

Candidate `a8e7b07c3d3a4e4a1d6b15d3720507996be00b36` passed [hosted verification, reusable workflow and Pages](https://github.com/interzettel/project-record-standard/actions/runs/39918534195). Pages reported success at 2026-10-23T07:33:55.2831426Z. The audit covers all 55 WCAG 2.2 A/AA criteria with scoped results and explicit unknowns: [audit record](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/wcag22-audit.json).

Cloud Chrome 155 on Linux exercised 26 rendered scenarios: both branded references in light/dark with authored, spaced and doubled text at 320 CSS px; three guides with those text settings; and all five pages at 1280 px. Every scenario had equal client/scroll width and no measured button, input, select or summary target below 24 px. All eleven guides passed DOM structure checks. The [review fixture](../qa/accessibility.html) makes these measurements repeatable.

Keyboard retesting confirmed skip links, filtered Close → Find work → Tab to Work map, search commit without focus loss, readable-list selected state, and filtered dependency closure. The earlier filtered Close failure focused BODY. The repaired status node survives result updates; seven component regression tests supplement seven calculation tests. The Python suite contains 35 tests. Default component contrast is checked separately from the 20 reference palette pairs.

Yiğit explicitly authorized STD-09 and STD-13 closure after audit, fixes and skill integration. The [acceptance receipt](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/owner-acceptance.json) preserves the original STD-13 criterion and its authorized scoped amendment. The same 16 required IDs move from 14/16 (87.5%) to 16/16 (100%); milestones from 2/4 (50%) to 4/4 (100%). This is bounded package completion, not a full WCAG conformance certification.

Actual screen-reader speech, native browser zoom and OS forced-colour/reduced-motion settings were not exercised. Computed doubled fonts are only a text stress check. Earlier open-gate observations below remain historical. All eleven skills, including accessibility, are packaged in the canonical repository; the additional personal Skills save was rejected HTTP422. Individual repository migrations remain separate.


Implementation 0.3.0, contract 0.2.0. Latest local checks: 23 October 2026.

The ten saved workflow skill bodies match the canonical distribution. Five preparation samples per workflow and executable cold/hot fixture applications are documented in [the evaluation record](https://github.com/interzettel/project-record-standard/blob/main/audit/skills/EVALUATION.md), including limitations, the corrected alias-direction failure and capacity interruptions. Final runtime replay preserved both fixture inputs, installed all ten skills additively and repeated with no changes.

The expanded local suite passed 35 Python tests, seven browser calculation/filter tests and 20 colour-role checks (minimum tested contrast 5.31). Public pipeline, 11-page guide/site build and README graphic/text parity passed. New checks cover installer collisions/interruption/upgrades, operational collection receipts, distributed skill installation and shared upward-tie percentage rounding. The extracted 106-file source distribution passed six check/build/test commands. A 0.3.0 wheel was built, installed separately and its status command verified. Local checks and hosted delivery have separate evidence; neither awards actual screen-reader verification or owner acceptance.

## Agent-package hosted observation

[Run 39866474910](https://github.com/interzettel/project-record-standard/actions/runs/39866474910) completed successfully for candidate `9b02b4380da76d16cabfe801fc368302d5ae5297`. Its verification, reusable record and deployment jobs all passed. Pages reported success at 2026-10-22T22:39:27.6365785Z. The deployed tracker showed 13/16 required leaves (81.3%), and its agent guide served the ten skills and lifecycle instructions. Native Edge checks covered skip links, milestone focus, the item inspector, closing/focus restoration and readable-list activation. Exact observations are in `audit/skills/hosted-observation.json` and `standards/ACCESSIBILITY.md`.

Recording that evidence completes STD-16, moving required progress to 14/16 (87.5%) and completed milestone gates to 2/4 (50%). The exact preceding 13/16 source is retained in `examples/sources/standard/agent-package-local-0.3.json`. No scope was added or removed. The candidate's declared release gates are 5/7 (71.4%): three work items and two technical checks passed; screen-reader and owner reviews remain open. This evidence update does not assert a tagged release or registry publication, and does not retarget the tested candidate to an untested revision.

## Earlier 0.2.0 verification

The source kit has an explicit file selection and per-file SHA-256 checksums. Its examples use public inputs. Owner-review output, private fixtures, browser screenshots and generated Python metadata are excluded.

The included tests cover scope/state accounting, observation order, evidence gates, release-channel distinctions, governance approvals and WBS ownership, private-input guards, marked README preservation, cold setup, non-destructive hot inspection, host-owned rendering, manifest hashes, action execution and deterministic packaging. The full owner review additionally exercises the repository-specific reference adapters and browser calculation parity.

The source archive is extracted and its included Python tests, pipeline and repackaging command are run in that extraction. A Python wheel is also built, installed in an isolated environment and used to build the standard reference with its installed browser assets. These are local observations, not hosted GitHub Actions or deployment observations.

The browser review checks real-data history/drill-down, candidate gates, changelog/coverage states, narrow layouts, appearance and doubled-text reflow. See `standards/ACCESSIBILITY.md` for exact scope and remaining keyboard/assistive-technology checks. Review evidence does not award owner acceptance.

No native project fields, issues, labels, target websites, releases or schedules were changed by those checks. The adaptation skills were authored and saved in the subsequent 0.3.0 work; individual repository migrations remain separate. PMI alignment is a documented tailoring map based on the cited public sources; it is not an endorsement or full-standard compliance assessment.


## Canonical hosted observation

The public repository's [second hosted run](https://github.com/interzettel/project-record-standard/actions/runs/39800961253) passed the verification and reusable record jobs. The verification job ran 18 Python tests, six JavaScript calculation/filter tests and 20 colour-role checks. Pages reported success at 2026-10-22T15:02:47Z for source revision `5f653c78d131e1a5ef1de734f53d189f6666d4db`. The first hosted run's upload-path failure is recorded in the delivery guide. Native keyboard observations and the screen-reader limitation are in the accessibility guide.
