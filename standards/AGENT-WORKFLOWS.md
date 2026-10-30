# Agent workflows

An agent starts with the project’s purpose and scope, scouts its actual state, and turns the evidence into a manageable plan. The tracker and website show that plan and its progress. They evolve when the project discovers or accepts more work.

## Open contribution and bounded responsibility

Use [work language and open contribution](WORK-MODEL.md) to separate temporary package responsibility, accounting ownership, review lenses and acceptance authority. Any contributor can bring ideas or work across disciplines. Skill routing chooses useful questions and procedures, not exclusive job roles. Record actual producers and dissent; multiple lenses from one model do not establish independent review. Existing authorization governs execution.

A goal-based cycle can select a bounded outcome, inspect the actual result, and reflect on the process. A solo maintainer chooses a useful cadence without claiming full Scrum adoption. Keep criteria and project quality policy explicit for the artifact being made.

## Start or reestablish a project

Use `establish-project-tracking` when tracking authority has not been established, even if the repository already has a README and website. Use `adapt-project-tracking` when plans, IDs, claims or generated tracking already exist. An interrupted installation resumes from its recorded state. Damaged generated output uses `operate-project-tracking`; it does not justify resetting the ledger.

Both setup paths include an [L0–L5 readiness assessment](READINESS.md) before planning autonomous operation. Inspect current evidence first, then ask about unresolved target level, task-risk R0–R4 delegation, environments and acceptance decisions. The installed router carries the portable assessment contract and empty JSON record. Detailed assessments stay in the configured central store; overview/adoption link their current/target level, date/revision, authority limits, blockers and next review. Selected readiness gaps become bounded work; readiness never substitutes for completion percentages or actual authority.

Both setup paths produce the same planning artifacts:

| Artifact | What the next agent needs |
| --- | --- |
| `progress/overview.md` | Intended users/value, product overview, what works today, included/excluded scope, success criteria, acceptance authority, constraints and unresolved decisions. Facts and proposed scope are distinguished. |
| `progress/discovery.json` | Source-backed inventory of docs, existing trackers, issues, open/leftover PRs, local and remote branches, releases, website, CI and generated ownership. Coverage and inaccessible sources remain visible. |
| `progress/adoption.md` | Source/field authority, ID and state crosswalk, brand/routes, cleanup queue, before/after fractions, incremental cutover, completed/pending steps, verification and rollback. |
| Ledger and manifest | The actual scoped work, relationships, criteria, evidence and provenance consumed by the runtime. Existing formats can keep their authority through adapters. |

Use connected GitHub tools for hosted inventory and exhaust pagination before treating a collection as complete. Local Git proves only its fetched state. Record which default and other branches were inspected, their exact revisions and whether remote data was fetched. Record limits on inaccessible discussions, deleted branches or unavailable history. Do not scan credentials or private material into a public report.

Inspect unfinished work for useful code and decisions before proposing replacements. A stale branch may contain the only implementation of an agreed feature. Link it to the relevant work item, identify its author/reviewer and propose resume, merge, supersede or archive. A cleanup proposal is separate from permission to delete branches or close others’ work.

Rank cleanup by its effect on the active outcome: safety/data-loss and active blockers first, then dependencies that unlock useful work, contradictory sources and abandoned duplication, then value/effort and optional housekeeping. Write the reason, affected outcome, evidence, owner and next action. Age is evidence to investigate, not a priority score by itself.

## Turn the findings into a plan

Write the overview before decomposing the work. Start with intended outcomes and deliverables. A WBS divides the recorded scope into managed work packages. Accounting leaves describe bounded work with criteria and evidence. An issue or PR is a delivery package that implements or verifies one or more leaves. Milestones are outcome checkpoints; the roadmap places them into horizons, dependencies and any sourced dates.

Give each leaf one accounting owner and primary milestone. Link shared prerequisites without counting them again. Include management, integration, assurance and operational handover work when they belong to the outcome. An experiment can finish successfully by producing an honest negative result if that is its criterion. Discovery ideas do not silently enter the required denominator.

Propose unknown scope in concrete language, proceed with authorized preparation, and retain the designated authority’s actual approval boundary. An observed snapshot is useful before a baseline is approved. A working setup is not proof that the plan is complete or accepted.

## Select and reconcile an implementation package

At an implementation turn, use the existing authorized queue and its authoritative source. Inspect the selected scope's issue/PR observations, local instructions and current plan. Preserve coverage/date/revision; refresh only relevant missing or stale observations. A new bounded feature does not require rescanning every repository, private memory store or unrelated branch. Setup or substantial scope expansion still uses the wider scouting process above. Missing service access remains unknown and keeps the last observation visible.

Select an existing required, unfinished **accounting leaf**, following the host's declared order (which can express outcome, horizon and priority), execution prerequisites, actual holds, authorization and capacity. Use the [evidence/dependency meanings](STANDARD.md#evidence-claims-and-dependency-meanings). A parent groups work, and a completion or acceptance gate does not automatically become a start prerequisite. Retain unknown meaning/evidence; do not infer eligibility. If an earlier item is blocked or unknown, explain it and continue known eligible independent work under the existing authorization. If none is eligible, report the missing fact/decision and responsible next action. A new idea remains a proposal until scoped; it cannot displace the authorized queue or earn an extra completion point.

Start with the leaf ID, issue URL/number, **canonical** milestone ID, exact criterion, bounded deliverable, dependency status and actual remaining gate. A native milestone number is an observed host mapping, never a number guessed from the canonical ID. A missing mapping can prompt a bounded detailing/repair pass within existing authority; retain the ID/criterion/denominator, and seek a decision only for an actual scope or permission change. Branch/PR titles and commits use the existing stable ID. Internal steps earn no duplicate credit.

At package end, preserve the previous source/observation and record actual implementation/check/review revisions, results and limitations. Update the canonical writer once; reconcile relevant issue discussion/status under the task's authorization and regenerate README/graphic/site projections through their owners. Keep issue closure, Done, outcome acceptance, release and deployment separate. Report source/issue mapping gaps, unchanged or changed named fractions, actual blockers, remaining owner/release gates and the **next eligible leaf + issue + milestone + action**. Routine authorized recording does not need repeated approval. A production writer, journal and host scheduling are separate packages, not effects of these instructions.

### Optional read-only assessment API

`project_record.execution.select_work` and `check_alignment` consume an existing loaded record plus an optional **executionVersion1** local assessment profile. This does not extend record contract0.2.0 or create a second completion ledger. The profile supplies a complete order for that selected record's leaves, a source SHA-256, per-leaf authorized/hold/capacity observations, explicit dependency meanings, optional native mapping, explicitly obsolete artifact URLs and optional milestone evidence policies. Every leaf occurs once; undeclared, duplicate or omitted IDs are rejected. Missing conditions/dependency meaning remain unknown. Done/cancelled/deferred leaves are not selected. No universal priority formula or permission is inferred from a state label.

```python
from project_record.adapters import load_config
from project_record.execution import select_work, check_alignment

record = load_config(config_path)[0]
start = select_work(record, profile, current_source_sha256=current_hash,
                    as_of=report_date)
alignment = check_alignment(record, profile, issue_snapshot, as_of=report_date,
                            readme=readme_path, expected_module=current_generated_module)
```

These variables are host-supplied inputs, not a new configuration mandate. `current_hash` is the actually observed current canonical source hash; missing/mismatched/stale source identity cannot support current selection. `authorized` is an observation of existing task authority, not a grant, signature or credential. Holds and capacity remain separate. This helper does not execute bounded dependency exceptions: an explicit blocked flag remains blocking; resolve the host's allowed scope before assessing it. Completion/acceptance edge labels do not erase their later gates.

Issue snapshots contain `projectId`, `source`, `observedOn`, an explicit `complete` coverage boolean and interpreted rows with `url`, `leafId`, `milestoneId`, optional `nativeMilestone` and `artifactUrls`. A host adapter owns interpretation of actual issue bodies. No snapshot is fetched, authenticated or silently refreshed. An absent row is a mismatch only for declared fresh complete coverage; partial, stale or unavailable coverage stays unknown. Unmapped observed issues, including parents, are diagnostic references, never added work rows. Conflicting explicit canonical body linkage is reported even if native linkage matches. An actual historical commit URL is not stale merely because it is old; only explicitly configured obsolete refs are flagged.

`check_alignment` reports canonical/issue mapping gaps, configured obsolete refs, accepted outcomes with unassessed/unsatisfied declared evidence, and actual marked README drift against the **supplied current generator module**. It never overwrites legacy acceptance: no policy means unassessed, not newly rejected; supplied matching metadata still cannot authenticate an owner. README checks inspect the marked text only; SVG/layout checks remain separate. Diagnostics may expose local/private URLs and are not an approved public projection. They are not a CI enforcement claim or an automatic reconciliation service.

The synthetic `tests/fixtures/execution/` uses actual public issue URL identities with **invented** work states/mappings. It demonstrates one blocked earlier item, an unknown prerequisite, an eligible leaf, a deferred idea and an uncounted parent, with deliberate stale issue/milestone/artifact refs. No current native issue state is asserted. Run `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_agents.py' -v`; actual installed-guidance application is recorded separately from installer/metadata success.

## Let the system grow with the project

Revisit the overview and scouting record when the outcome changes, new substantial work appears, a release closes, sources conflict or a repo has accumulated unfinished work. Ordinary bounded progress updates can use the existing map. Scope changes refresh the affected map and priorities.

Preserve the previous observation before editing its authoritative source. Record added, removed, deferred, cancelled and split/merged work through stable identities and explicit aliases. Record why the change occurred, its effect on acceptance, dependencies, resources, schedule/risk and the selected denominator. Recompute metrics using the toolkit and retain the before/after bridge. Keep completed archived work and source evidence reachable.

For example, 3/4 required leaves is 75%; completing one leaf and adding two leaves can produce 4/6, or 66.7%. Completion increased while scope expanded. The history explains both. Neither the chart nor a new baseline should erase that explanation.

Reprioritization follows the project’s authority model. Use the approval already supplied for a task; seek a missing decision only when it affects dependent work. Never manufacture an approval receipt from a general instruction to continue.

## Skills and agent rules

| Skill | Trigger and result |
| --- | --- |
| `use-project-records` | Find authority and route tracking requests or interrupted work. |
| `establish-project-tracking` | Scout a project without established tracking and create its overview and plan. |
| `adapt-project-tracking` | Reconcile existing sources, preserve IDs/brand, and prepare an incremental cutover. |
| `govern-project-scope` | Decompose or expand scope, tailor management domains, and record decisions/risks. |
| `update-project-progress` | Apply evidence-backed progress once and preserve history and changed denominators. |
| `answer-project-status` | Answer questions with named fractions, source dates, blockers and evidence limits. |
| `connect-github-tracking` | Prepare or apply authorized issue/label/Project mappings and bounded reconciliation. |
| `prepare-project-delivery` | Prepare changes, candidate gates and separately observed publication/deployment. |
| `present-project-tracking` | Integrate interactive tracking into the project’s own README and website. |
| `operate-project-tracking` | Recover generated output, verify CI, manage collection health and upgrade safely. |
| `verify-project-accessibility` | Audit WCAG 2.2 A/AA criteria, remediate tracker interactions and preserve actual test/acceptance limits. |

Repository instructions select these skills before relevant work. Deterministic constraints stay in the runtime: unique accounting, reference/cycle checks, approval attribution fields, candidate revision matching, private-input export refusal and generated-output ownership. Skills handle discovery, meaning, priorities and judgment. Instructions do not technically constrain an agent’s credentials or authenticate a person.

## Install the skills in a repository

Use a reviewed toolkit checkout and run from its root. Installation defaults to a preview:

```sh
PYTHONPATH=src python3 -m project_record install-skills --toolkit . --target /path/to/project
PYTHONPATH=src python3 -m project_record install-skills --toolkit . --target /path/to/project --apply
```

The installer writes `.agents/skills/`, appends a marked section to the existing `AGENTS.md`, and records exact file and suite hashes in `.project-record/agent-installation.json`. Existing instructions and unrelated files remain intact. A repeat run has no changes. An interrupted installation can resume when the partially written files match the selected suite.

Review an upgrade with `--upgrade`, then use `--upgrade --apply`. A changed owned instruction digest also requires that explicit upgrade even when skill-file bytes and suite label are unchanged. Existing pinVersion1 readers recognize the preceding instruction writer as well as the execution-guidance writer; an old expected pin still checks its own bytes and never authorizes an upgrade. Changed project-owned skill files cause a conflict; reconcile them deliberately. The installer does not delete retired skills, overwrite local edits, vendor the runtime, create a workflow, edit the ledger, schedule a job or deploy a site. Vendor/pin the toolkit separately under the repository’s dependency policy. Repositories whose agent runner uses another discovery directory can point it to `.agents/skills/` or install the same reviewed folders using that runner’s documented mechanism.

## Status and operational telemetry

Use an explicit reporting date. This command reads local sources without changing them:

```sh
PYTHONPATH=src python3 -m project_record status --config examples/projects.json --only prehnite --as-of 2026-10-22 --freshness-days 7
```

The result includes named metrics, source identity/date/age, blockers, milestone next actions, history, candidate readiness, publications and deployments. The threshold is a local reporting choice, not a service-level objective. Without a collection receipt, external health is `not-reconciled`.

An optional `--observation attempt.json` adds a sourced collection outcome for exactly one selected project. Use the shape in `templates/collection-attempt.example.json`. Partial pages, failures and unknown totals degrade collection health; they never replace the last successful counts or refresh `observedOn`. A successful attempt receipt also does not modify the underlying observation. The command validates the supplied receipt; it does not perform or authenticate a network fetch.

Build/run time, source observation time, collection attempts, publication time and observed deployment health are different facts. Keep them separate in reports. This telemetry concerns project operations; visitor analytics are a separate project decision.

## Verification evidence

The skills are authored with the [Superpowers writing-skills process](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/writing-skills/SKILL.md). The [versioned evaluation record](https://github.com/interzettel/project-record-standard/blob/main/audit/skills/EVALUATION.md) describes actual controls, application cases and limitations. Synthetic setup/adaptation runs use disposable fixtures; no individual project migration is implied.

Owner acceptance and actual screen-reader output require their own evidence. A successful skill test, local suite or hosted CI run establishes only its tested boundary.

The 0.4.0 suite adds the accessibility skill and its 55-criterion report template. Its source-only forward applications and live audit are recorded separately from the original ten-skill evaluation. `npm ci --ignore-scripts` installs locked DOM test dependencies for development checks; the tracking runtime and published pages keep no runtime dependency on those packages.
