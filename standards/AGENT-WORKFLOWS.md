# Agent workflows

An agent starts with the project’s purpose and scope, scouts its actual state, and turns the evidence into a manageable plan. The tracker and website show that plan and its progress. They evolve when the project discovers or accepts more work.

## Start or reestablish a project

Use `establish-project-tracking` when tracking authority has not been established, even if the repository already has a README and website. Use `adapt-project-tracking` when plans, IDs, claims or generated tracking already exist. An interrupted installation resumes from its recorded state. Damaged generated output uses `operate-project-tracking`; it does not justify resetting the ledger.

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

Repository instructions select these skills before relevant work. Deterministic constraints stay in the runtime: unique accounting, reference/cycle checks, approval attribution fields, candidate revision matching, private-input export refusal and generated-output ownership. Skills handle discovery, meaning, priorities and judgment. Instructions do not technically constrain an agent’s credentials or authenticate a person.

## Install the skills in a repository

Use a reviewed toolkit checkout and run from its root. Installation defaults to a preview:

```sh
PYTHONPATH=src python3 -m project_record install-skills --toolkit . --target /path/to/project
PYTHONPATH=src python3 -m project_record install-skills --toolkit . --target /path/to/project --apply
```

The installer writes `.agents/skills/`, appends a marked section to the existing `AGENTS.md`, and records exact file and suite hashes in `.project-record/agent-installation.json`. Existing instructions and unrelated files remain intact. A repeat run has no changes. An interrupted installation can resume when the partially written files match the selected suite.

Review an upgrade with `--upgrade`, then use `--upgrade --apply`. Changed project-owned skill files cause a conflict; reconcile them deliberately. The installer does not delete retired skills, overwrite local edits, vendor the runtime, create a workflow, edit the ledger, schedule a job or deploy a site. Vendor/pin the toolkit separately under the repository’s dependency policy. Repositories whose agent runner uses another discovery directory can point it to `.agents/skills/` or install the same reviewed folders using that runner’s documented mechanism.

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
