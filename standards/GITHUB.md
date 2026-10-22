# GitHub language and delivery

## Titles and labels

Use **`[stable-ID] Verb + concrete outcome`** for a bounded implementation, experiment or acceptance package. Keep the title within 120 characters. Keep the original ID through a rename or rescope.

Good examples:

- `[P1-M02-E01] Measure repeatable SDXL generation on the laptop`
- `[Y04.03] Verify the project page at a narrow viewport`
- `[PRINT-TRUST] Record the remaining physical-print acceptance gates`

Avoid titles such as “Phase III fixes”, “Improve everything”, “Tracker stuff” and unexplained acronyms. Questions and discussions can use a question title; the delivery-package convention applies when a bounded delivery is assigned.

Core label families are `type:*`, `area:*` and `priority:P0` through `priority:P3`. Use one type and one priority. Areas are project-owned and may have aliases to existing labels. `blocked` is an optional attention label with a reason. Workflow status lives in the Project rather than being independently maintained in another family of status labels.

Suggested types: feature, bug, documentation, research, experiment, decision, maintenance, release. Define P0 as a current blocker to the agreed active outcome or a serious defect; P1 as the next required work; P2 as subsequent scoped work; P3 as deferred/discovery. Priority is local to the project and is not a portfolio-wide urgency score.

Do not turn every milestone ID into a label. Put the IDs in structured issue fields/body and native milestone/parent relationships. Reuse valid existing labels through a reviewed mapping instead of recreating the whole taxonomy.

## Relationships and Project views

Use native parent/sub-issue and blocking relationships when they fit the work. A delivery package names the affected ledger IDs. Each accounting leaf has one primary milestone; shared prerequisites link other scopes without duplicate credit. Accepted decision links can inform work without becoming blocking dependencies.

Reuse the existing Project. Start with the views a maintainer uses: active work, milestone roadmap, blockers and release readiness. Status, Priority, Area, Assignee, milestone and parent issue are sufficient initially. Add scope/capability IDs when needed for joins. Completion and acceptance fields are read-only projections if present.

The manifest records field ownership. A repository-local ledger can own completion while GitHub owns discussion and assignment. An adapting agent must preserve that model or propose an explicit cutover. No repeated two-way sync overwrites human edits from an older snapshot.

## Package completion

A package closes with its bounded result, affected IDs, evidence and tested revision, remaining limits, change fragment or reason none is needed, and next action. The package updates the authoritative source once. Derived README/Pages views are regenerated. An agent reports the acceptance effect rather than awarding owner approval to itself.

## Change, release and deployment records

Write one small change fragment for a meaningful user/operator change. It names the component, change type, summary, capability/work IDs, PR and compatibility or migration effect when relevant. The fragment generates development history and Unreleased; a publication records the actual included changes and bytes.

Keep planned versions, repository tags, GitHub releases, registry publications and deployments distinct. Each publication has component, channel, version, source revision, source URL, actual publication time and artifact digest where available. Source merges and changelog headings establish neither publication nor deployment. A no-release project says so; inaccessible publication data stays unknown.

Use the native package version source instead of imposing another competing `VERSION` file. Websites may use a deployment ID and commit. Multi-component projects name each channel. Historical release facts are corrected through a sourced amendment, never silently retargeted.

## CI and synchronization

Tracker changes run the offline record/schema/reference checks and relevant render checks. They do not run GPU experiments or unrelated application suites. Changed shared build code and application paths follow the repository's own gates. No workflow bypasses branch protection or triggers paid inference.

After merge, build from a known revision. Follow the repository's accepted generated-file policy: build artifacts directly or use a generated update PR; preserve owner decisions such as the portfolio's generator-owner rule. The included CI file is an adaptation example and is not installed in any repository.

Optional GitHub reconciliation is a separate bounded job with source/observation time, coverage, pagination and an error state. Authentication or quota failure keeps the last successful snapshot visibly stale. A freshly generated page cannot claim a fresh observation. No scheduled job or credential is created by this kit.
