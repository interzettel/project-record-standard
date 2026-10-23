# Historical document — captured 23 October 2026 before release preparation

This verbatim document contains successive observations. Its former “current” statements apply only to their original scopes; use the current overview and delivery guide for present status.

# Repository and delivery evidence

## Completed scoped accessibility review — 0.4.0

Candidate `a8e7b07c3d3a4e4a1d6b15d3720507996be00b36` passed [hosted verification, reusable workflow and Pages](https://github.com/interzettel/project-record-standard/actions/runs/39918534195). Pages reported success at 2026-10-23T07:33:55.2831426Z. The audit covers all 55 WCAG 2.2 A/AA criteria with scoped results and explicit unknowns: [audit record](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/wcag22-audit.json).

Cloud Chrome 155 on Linux exercised 26 rendered scenarios: both branded references in light/dark with authored, spaced and doubled text at 320 CSS px; three guides with those text settings; and all five pages at 1280 px. Every scenario had equal client/scroll width and no measured button, input, select or summary target below 24 px. All eleven guides passed DOM structure checks. The [review fixture](../qa/accessibility.html) makes these measurements repeatable.

Keyboard retesting confirmed skip links, filtered Close → Find work → Tab to Work map, search commit without focus loss, readable-list selected state, and filtered dependency closure. The earlier filtered Close failure focused BODY. The repaired status node survives result updates; seven component regression tests supplement seven calculation tests. The Python suite contains 35 tests. Default component contrast is checked separately from the 20 reference palette pairs.

Yiğit explicitly authorized STD-09 and STD-13 closure after audit, fixes and skill integration. The [acceptance receipt](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/owner-acceptance.json) preserves the original STD-13 criterion and its authorized scoped amendment. The same 16 required IDs move from 14/16 (87.5%) to 16/16 (100%); milestones from 2/4 (50%) to 4/4 (100%). This is bounded package completion, not a full WCAG conformance certification.

Actual screen-reader speech, native browser zoom and OS forced-colour/reduced-motion settings were not exercised. Computed doubled fonts are only a text stress check. Earlier open-gate observations below remain historical. All eleven skills, including accessibility, are packaged in the canonical repository; the additional personal Skills save was rejected HTTP422. Individual repository migrations remain separate.


The canonical repository is [interzettel/project-record-standard](https://github.com/interzettel/project-record-standard). This record distinguishes source installation, hosted checks, website deployment and owner acceptance.

| Work | Evidence status |
| --- | --- |
| Canonical repository | [Public source installed](https://github.com/interzettel/project-record-standard/tree/10a9e6501a9ed64f57ad139a56e3fc9fdd8b99ef). Private owner fixtures are excluded. |
| Composite action | Passed in [hosted verification](https://github.com/interzettel/project-record-standard/actions/runs/39800961253/job/119901169586): 18 Python tests and six browser-calculation tests. |
| Reusable workflow | Passed in the [reusable record job](https://github.com/interzettel/project-record-standard/actions/runs/39800961253/job/119901170257), including artifact upload. |
| Example website | [Pages deployment succeeded](https://github.com/interzettel/project-record-standard/actions/runs/39800961253/job/119901281252) at 2026-10-22T15:02:47Z. Tracker, guide and Prehnite routes were opened in Edge. |
| Keyboard verification | Native Edge keyboard checks exercised skip links, filters, item inspection, focus restoration and view controls. The milestone-card focus fix passed deployed retesting in the standard and Prehnite views, including at narrow width. |
| Screen-reader verification | Actual spoken output has not been verified. Accessibility names and landmarks have been inspected. |
| Owner acceptance | Pending. Repository creation does not imply approval of the standard. |

## Complete agent package

Implementation 0.3.0 keeps contract 0.2.0 and supplies ten saved/distributed skills, additive installation, source-backed status and collection telemetry, scope-growth history, and the agent planning guide. The [evaluation record](https://github.com/interzettel/project-record-standard/blob/main/audit/skills/EVALUATION.md) includes preparation controls, cold/hot executable applications and limitations. Individual project migrations remain outside this delivery.

[Run 39866474910](https://github.com/interzettel/project-record-standard/actions/runs/39866474910) passed verification, the composite action, the reusable record workflow and deployment for candidate `9b02b4380da76d16cabfe801fc368302d5ae5297`. The expanded checks include 35 Python tests, seven browser-calculation tests, the ten-skill suite, 20 colour-role pairs, the site build and README parity. [Pages reported success](https://github.com/interzettel/project-record-standard/actions/runs/39866474910/job/120129913901) at 2026-10-22T22:39:27.6365785Z. Its tracker and agent guide were opened in Edge; the scoped native keyboard checks passed.

The authored 0.3.0 review plan retains that exact candidate revision. Five of seven declared readiness gates passed: STD-14 through STD-16, hosted verification and native keyboard review. Actual screen-reader and owner reviews are missing, so readiness is 71.4%, not approval to claim those outcomes. Earlier candidate/deployment observations remain historical. There is no observed tagged release or registry publication.

The evidence update closes STD-16 and preserves the published 13/16 source before generating 14/16 (87.5%) required progress. It adds no work or behavior, so it uses the existing CH-0.3-AGENTS fragment. STD-09 and STD-13 stay pending. `VERIFICATION-public.md` and `audit/skills/hosted-observation.json` record the checks and boundaries.

## Reproduce and deploy

The `Verify and publish the standard` workflow tests the Python runtime, compares browser calculations with the public records, exercises the root composite action and calls the reusable workflow. The Pages deployment depends on both verification jobs.

Only the deploy job receives `pages: write` and `id-token: write`. Source checks use `contents: read`. Pull requests build an artifact but do not deploy. No workflow commits generated status or edits another repository.

The website builder accepts only public, hash-matching files listed in the record build manifest. It renders the standard's guide and adds site navigation to the independently branded reference pages. It does not fetch fresh project data or infer publication from a plan.

The first run exposed an artifact-upload failure because the output directory begins with a dot. The corrected run explicitly includes generated hidden-directory contents. This was a hosted integration finding; it was not covered by the local entry-point test.

The focus fix was deployed from `8ca75f2fdcf8da51d554fd9c3a0ca1ef551cd976` in [run 39802018009](https://github.com/interzettel/project-record-standard/actions/runs/39802018009). The deploy job completed successfully at 2026-10-22T15:09:16Z. Browser retesting confirmed that milestone activation focuses the visible selected heading.
