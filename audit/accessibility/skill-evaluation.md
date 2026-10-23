# Accessibility workflow evaluation

Five fresh-context source-only controls preceded skill authoring. They inspected the same named tracker artifacts without the new skill. They correctly distinguished existing keyboard evidence from actual screen-reader output. Their handoffs omitted a complete criterion record, and some treated explicit conditional owner acceptance as requiring a second permission. One review reported superseded reference CSS declarations as rendered failures; the final cascade already overrides those colours. These are bounded observations, not claims that all unaided agents fail.

Selected original control statements:

- Control 1: “The user’s instruction supplies conditional owner acceptance for STD-09 once the requested review, fixes and guidance are complete; record that decision and link the new evidence.”
- Control 2: “The owner’s conditional instruction authorizes the work; completing engineering checks does not itself document the requested owner review.”
- Control 3: “The request authorizes engineering work; it supplies neither missing observation.”
- Control 4: “An owner-approved scope change is possible, but must preserve the remaining verification work visibly.”
- Control 5: “The conditional request does not establish either completed gate.”

The resulting skill requires a 55-row report, source/rendered distinctions, final-cascade inspection, meaningful regressions, actual environments and an explicit acceptance/amendment basis. Its template begins every criterion as not-tested. It never converts owner acceptance into spoken assistive-technology evidence.

An initial forward attempt encountered account capacity errors and is not counted as successful validation. Five subsequent fresh-context applications used the authored skill and raw source files. Their complete JSON artifacts are `skill-forward-1.json` through `skill-forward-5.json`. Each retained 55 criterion rows, unavailable browser/screen-reader evidence and a false conformance claim. They differed in the number of narrowly scoped source observations they considered passes; those are not full-page conformance results. This variance remains visible rather than being normalized into a success score.

Forward application 3 found an additional real defect: a bubbling search-change event replaced the focused input. The maintainer reproduced the failure in the component DOM test, added a regression, and guarded the change handler to accept only the three select controls. Current source no longer exhibits that failure. Six previously added regressions and the new search-commit regression pass.

The source files evolved between controls and forward applications. This was a practical workflow/application check, not a controlled causal comparison. The actual browser audit, unit regressions, packaging checks and hosted verification establish their own tested boundaries. No actual screen-reader speech was available in these applications.

## Authoring checklist

- [x] Baseline cases and observed gaps recorded before authoring.
- [x] Skill name, trigger-only YAML description, concise technique and reference table validated.
- [x] A reusable report template covers all 55 WCAG 2.2 A/AA criteria; 4.1.1 is omitted because it was removed.
- [x] Five fresh-context source applications preserved uncertainty and owner authority; artifacts retained.
- [x] New application finding reproduced and repaired with a failing/passing regression.
- [x] Metadata validation, package manifest and installation/distribution checks run.
- [x] Personal skill save attempted with Git; its actual remote result is recorded in the final handoff.
- [x] Discipline rationalization tables are inapplicable: this is a technique/reference workflow; concrete artifact and authority gaps use structural fields and conditional guidance.

The reusable skill is distributed with the standard. Installation copies it and its report template alongside the other ten workflows, preserving existing repository instructions and branding.
