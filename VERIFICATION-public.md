# Public-source distribution verification

## Current scope — 0.4.1, 23 October 2026

The canonical implementation contains 18/18 completed required items and 4/4 completed milestone gates, with eleven skills and record contract 0.2.0. [Run 40003462737](https://github.com/interzettel/project-record-standard/actions/runs/40003462737) verified, deployed and published revision `ebc6afb0b977ff3d7605893c73ac63021775c4d3`. All four hosted gates passed, including 35 Python tests, 14 JavaScript tests, skill distribution, 20 palette pairs, public site generation, README parity and extracted-package checks. The v0.4.1 tag and all four uploaded asset digests were read back and match the local verified build. [The receipt](progress/releases/v0.4.1.json) preserves exact identities and times.

The public source kit excludes private inputs and audit fixtures. Its deterministic archive contains per-file SHA-256 checksums. Release publication adds an archive checksum, changelog and installation instructions. The publishing job verifies a fresh extraction, its public pipeline and additive/repeated skill installation before publication.

Readiness integration was exercised against five fresh guided scenarios; [the evaluation](https://github.com/interzettel/project-record-standard/blob/main/audit/readiness/EVALUATION.md) explains the synthetic setup and limits. This is practical workflow evidence, not a blinded causal study. Neither task completion nor skill installation awards L5 or deployment permission.

## Native zoom verified; Narrator confirmed by owner

On 23 October 2026, the owner set local Edge to 200% and 400%. The agent observed device-pixel ratios 2 and 4 and viewport widths 1276 and 638 CSS px, respectively, from a 2552px-wide baseline. At 200%, root content/scroll width stayed 1268/1268; at 400%, 634/634. The standard tracker, guide start and Prehnite reference had no horizontal page overflow in the inspected states.

Checks covered tracker skip navigation, filtered-out inspector closure to Find work, search commit to Work map, readable-list selection/inspector, release and changelog views, guide skip navigation and the Prehnite inspector. At 400%, settled Close bounds were y47–91 in a 358px-high viewport. The Prehnite 200% settled bounds were y362–406 in 717px. An earlier immediate measurement during smooth scrolling was outside the viewport; it was not treated as a settled focus failure.

The owner reported: “done. narrotor works dont worry”. Narrator is therefore recorded as **owner-reported working**, alongside the directly observed native zoom checks. The agent did not hear or record speech; browser/screen-reader versions and a speech transcript remain unavailable. This is scoped acceptance, not a full WCAG conformance claim. Native 400% produced 638 CSS px; earlier 320px fixture checks remain separate evidence.

The [completion receipt](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/native-completion.json) preserves the original STD-18 criterion and accepted scope. Detailed [200%](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/native-200-observation.json) and [400%](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/native-400-observation.json) observations are retained. Required work moves 17/18→18/18 (100%); milestone gates 3/4→4/4. Earlier blocked attempts below remain historical. The personal accessibility skill save was already verified.


## Accessibility scope and retained evidence

The [WCAG 2.2 audit](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/wcag22-audit.json) records all 55 A/AA criteria as scoped pass, not applicable or not tested. Twenty-six rendered Chrome scenarios covered independent brands, light/dark modes, text stress and CSS widths including 320 px. DOM checks cover semantics and focus regressions; they do not exercise speech or native rendering. OS forced-colour/reduced-motion settings were not exercised.

The original [owner acceptance](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/owner-acceptance.json) and [native completion](https://github.com/interzettel/project-record-standard/blob/main/audit/accessibility/native-completion.json) receipts preserve original criteria and attributed amendments. Personal accessibility-skill persistence was fetched back successfully after earlier HTTP422 failures.

Historical candidates, intermediate counts, failed native-control attempts and earlier save failures remain in [dated verification history](progress/history/2026-10-23-before-release/VERIFICATION-public.md). They are historical observations, not unresolved current blockers. No individual repository migration is included.
