# GitHub language and delivery

## Titles and labels

Use **`[stable-ID] Verb + concrete outcome`** for a bounded implementation, experiment or acceptance package. Keep the title within 120 characters. Keep the original ID through a rename or rescope.

Good examples:

- `[P1-M02-E01] Measure repeatable SDXL generation on the laptop`
- `[Y04.03] Verify the project page at a narrow viewport`
- `[PRINT-TRUST] Record the remaining physical-print acceptance gates`

Avoid titles such as “Phase III fixes”, “Improve everything”, “Tracker stuff” and unexplained acronyms. Questions and discussions can use a question title; the delivery-package convention applies when a bounded delivery is assigned.

Core label families are `type:*`, `area:*` and `priority:P0` through `priority:P3`. Use one type and one priority. Areas are project-owned and may have aliases to existing labels. `blocked` is an optional attention label with a reason. Declare one writer for workflow status. When a Project owns it, other status displays are projections; a host without a Project can retain its existing authoritative workflow source.

Suggested types: feature, bug, documentation, research, experiment, decision, maintenance, release. Define P0 as a current blocker to the agreed active outcome or a serious defect; P1 as the next required work; P2 as subsequent scoped work; P3 as deferred/discovery. Priority is local to the project and is not a portfolio-wide urgency score.

Do not turn every milestone ID into a label. Put the IDs in structured issue fields/body and native milestone/parent relationships. Reuse valid existing labels through a reviewed mapping instead of recreating the whole taxonomy.

## Relationships and Project views

Use native parent/sub-issue and blocking relationships when they fit the work. A delivery package names the affected ledger IDs. Each accounting leaf has one primary milestone; shared prerequisites link other scopes without duplicate credit. Accepted decision links can inform work without becoming blocking dependencies. Parent/sub-issue grouping does not imply a blocking relationship. Preserve typed links for support, origin, resolution, supersession and duplication in the host mapping rather than converting every link to `dependsOn`. The [work model](WORK-MODEL.md) distinguishes optional origin and effect vocabulary from workflow status.

Reuse the existing Project when present; creating one is optional. Start with the views a maintainer uses: active work, milestone roadmap, blockers and release readiness. Status, Priority, Area, Assignee, milestone and parent issue are sufficient initially. Add scope/capability IDs when needed for joins. Completion and acceptance fields are read-only projections if present.

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

## Cooperating suite and independent module versions

Use one suite SemVer by default for cooperating skills/tools released together. Keep member inclusion, draft/available state, compatibility and actual publication receipts separate from that version. A skill name, file edit, review result or successful installation does not need a new independent version. Do not add per-skill SemVer/tag machinery merely because a suite contains several folders.

A module needs its own version only when it is independently published and supported. Name its package/channel, public interface, native version authority, supported suite/record/runtime compatibility and immutable release bytes. An illustrative independent-module example is not a release receipt. The host application's version remains under its existing authority; a PRS adoption does not rewrite it to the toolkit version.

For PRS's cooperating distribution, `pyproject.toml` owns the native release version and `skills/manifest.json` mirrors it as `suiteVersion`. `tools/check_skills.py` rejects drift. The record contract version and suite-manifest schema version remain different meanings. The check reads only the selected toolkit, not a consumer application's metadata; it does not change versions or prove behavior. `tests/fixtures/readme-only/version-policy.example.json` contrasts a cooperating host suite with an independently published module without claiming either was released.

Follow [Semantic Versioning2.0.0](https://semver.org/spec/v2.0.0.html) for the declared package interface; major-zero development requires explicit compatibility assessment rather than assumptions of stability. Released bytes stay immutable; a changed package requires a new publication/version. Pin the observed commit/digest independently of the version label and use [the existing update policy](COMPATIBILITY.md) to assess/apply/defer. One cooperating suite version is a PRS policy, not a requirement to align unrelated projects.

The [Agent Skills specification](https://agentskills.io/specification), inspected5 November2026, requires name/description and permits optional metadata, including a version example. It does not mandate independent SemVer for every skill. No new frontmatter/version field is introduced into PRS skill bodies here. Skill behavior evaluation, package validation, owner acceptance, release and downstream installation remain separate gates.

[Diakrisis PR15](https://github.com/interzettel/diakrisis/pull/15) supplies merged README-only consumer evidence. [PR16](https://github.com/interzettel/diakrisis/pull/16) corrects its initial per-skill machinery to a single suite. These historical consumer changes inform this policy; they do not prove a new consumer migration or reviewer effectiveness.
