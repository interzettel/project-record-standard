# Cold and hot adaptation profiles

The `establish-project-tracking` and `adapt-project-tracking` skills implement these profiles. [Agent workflows](AGENT-WORKFLOWS.md) defines their overview, scouting, cleanup, growth and installation handoffs. Both profiles use the same terminology, calculators and evidence boundaries. Their discovery and cutover behavior differ.

| Concern | Cold: new project | Hot: existing project |
| --- | --- | --- |
| Starting evidence | Empty or newly created repository; no established tracking authority. | Existing plans, issues, Projects, sites, generated files and historical claims. |
| Initial action | Create a minimal local scaffold and list unresolved owner decisions. | Inventory and calculate the existing system before proposing edits. |
| Scope | Define intended value, deliverables, success criteria and acceptance. Empty scope stays Not measured. | Preserve IDs, denominators, exclusions, dependencies and source history; map unmapped meaning explicitly. |
| Brand and site | Let the project establish its identity and host; the tracker inherits them. | Preserve existing fonts, palettes, imagery, routes, navigation and working interaction. |
| Governance | Name owner, reviewer/change authority, approach and domain tailoring. Record the first approved baseline when approval actually occurs. | Respect accepted governance. An observed snapshot does not retroactively become an approved baseline. |
| Cutover | Connect one authoritative writer per field, the initial renderer and relevant checks. | Use an additive integration, calculation comparison, bounded PR and explicit rollback. Retire conflicting generated views after accepted cutover. |
| Repair/reestablishment | Re-run setup only while the destination is empty. | Replay declared sources at pinned revisions; rebuild only owned output. Preserve historical observations and human edits. Never reset a ledger to recover a broken UI. |

## Commands available now

Cold scaffold:

```sh
PYTHONPATH=src python3 -m project_record init --directory /path/to/new-project --id example --name "Example" --owner "Project owner" --observed-on 2026-10-22
```

The command refuses a nonempty destination. It writes a private, local, unapproved empty scope. It creates no GitHub repository, credential, workflow schedule, deployment or approval.

Hot inspection:

```sh
PYTHONPATH=src python3 -m project_record adoption-plan --config examples/projects.json
```

This returns source identities, current counts, history coverage and required review work. It makes no changes. The adapting agent writes a repository-specific adapter or deliberately migrates the source; there is no automatic lossless converter for arbitrary legacy trackers.

## Skill inputs and outputs

Required inputs: target path/repository, cold or hot intent, authorized write boundary, owner, chosen host, canonical sources and target audience. Discover facts from the repository before asking the owner. Ask only for unresolved decisions that change scope or authorization.

Required outputs: an authority map; brand/site references; tailoring record; immutable source/ID crosswalk; before/after fractions; exclusions and unresolved mappings; proposed changes; verification evidence; cutover/rollback; and an operations handoff. The result names the standard implementation and contract versions.

The same run is resumable and idempotent: inspect existing manifests and generated-file ownership first, then continue the recorded work. Do not create duplicate issues, labels, Projects or ledgers. A repair run must distinguish damaged derived output from damaged authored source and must not overwrite the latter.

## Verification gates

Test the skills on an empty project, a branded existing repository, an interrupted migration and a broken generated tracker. Verify repeated runs, partial histories, source failures, private/public projections, native GitHub field aliases and rollback. New owner approvals must remain explicit in all four cases. Tests must prove preservation of existing content and the absence of duplicate accounting.

The reusable action, offline commands and agent skills are versioned together. Scouting uses the agent’s available repository/GitHub capabilities; the runtime performs no autonomous network reconciliation. Per-service writes require task authorization. Individual repository migrations remain separate work.

## README-only presentation profile

Choose `presentation.renderer: readme` when the project wants its tracker in the repository README. This is a complete presentation choice: no Pages configuration, website, JavaScript, hosting account or deployment is required. The project still owns its branding, source writer, version authority and acceptance decisions. Keep an existing website untouched when it is outside this package.

Declare the project-owned theme and a graphic path relative to the README:

```json
{"renderer":"readme","theme":"theme.json","readmeImageUrl":"./assets/progress.svg"}
```

Omit `progressUrl`; a contradictory interactive route is refused. Add the existing `project-record:start` / `project-record:end` marker pair to the authored README. From the reviewed toolkit, preview the selected source-backed output:

```sh
PYTHONPATH=/reviewed/prs/src python3 -m project_record readme-profile --config /host/progress/projects.json --only example --readme /host/README.md --image /host/assets/progress.svg
```

Add `--write` to regenerate those two owned outputs. Add `--check` instead for a read-only parity gate: exit0 means current, exit1 means stale or invalid. It checks both the generated region and graphic against current declared inputs, rather than trusting a cached build. It does not install CI. An adopted host check can run it on source/manifest/theme changes without any Pages job. The older generic `readme` preview still returns success when its diff is nonempty; use this profile's parity command for the combined check.

Acceptance: exact named required and accepted-milestone fractions, retained/deferred scope, source date/full digest, a labelled SVG with equivalent readable text, and every retained leaf's stable ID, title, priority/state, criterion, owner, dependencies and evidence. Milestone next actions and publication-receipt counts keep work, outcome acceptance and release distinct. Missing evidence remains Not recorded; empty denominators remain Not measured. Tables/disclosures require no hover controls.

Only one explicit public project is selected. Private sources are refused; unselected source contents are not read. Outputs cannot overwrite any manifest-declared source/theme/supplement/snapshot or each other. The graphic stays under the README's repository subtree and its declared URL must match its actual path. Existing markers are required and outside-region bytes are preserved. Write uses a cooperative `.prs-lock` file beside the README; exclude those transport locks under host policy. An interruption between atomic image/README replacements can leave stale output; rerun `--check`, then `--write` from the same reviewed inputs. This is recovery by deterministic regeneration, not a two-file atomic transaction.

`tests/fixtures/readme-only/` is a synthetic minimal host with no site configuration, a checked-in SVG/README, source/evidence and preserved application version. The reusable generator ships in PRS; host-owned generators can keep their own composition if they meet the same source/parity contract. Neither setup nor a passing check awards owner acceptance or publishes a package.
