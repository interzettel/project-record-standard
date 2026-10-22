# Cold and hot adaptation profiles

This is the executable contract for the adaptation skill we will write later. It is not an installed skill. Both profiles use the same terminology, calculators and evidence boundaries. Their discovery and cutover behavior differ.

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

This returns source identities, current counts, history coverage and required review work. It makes no changes. The later agent writes a repository-specific adapter or deliberately migrates the source; there is no automatic lossless converter for arbitrary legacy trackers.

## Future skill inputs and outputs

Required inputs: target path/repository, cold or hot intent, authorized write boundary, owner, chosen host, canonical sources and target audience. Discover facts from the repository before asking the owner. Ask only for unresolved decisions that change scope or authorization.

Required outputs: an authority map; brand/site references; tailoring record; immutable source/ID crosswalk; before/after fractions; exclusions and unresolved mappings; proposed changes; verification evidence; cutover/rollback; and an operations handoff. The result names the standard implementation and contract versions.

The same run is resumable and idempotent: inspect existing manifests and generated-file ownership first, then continue the recorded work. Do not create duplicate issues, labels, Projects or ledgers. A repair run must distinguish damaged derived output from damaged authored source and must not overwrite the latter.

## Completion gates for skill authoring

Before calling the future skill finished, test it on an empty project, a branded existing repository, an interrupted migration and a broken generated tracker. Verify repeated runs, partial histories, source failures, private/public projections, native GitHub field aliases and rollback. New owner approvals must remain explicit in all four cases. Tests must prove preservation of existing content and the absence of duplicate accounting.

The reusable action and offline commands are implemented in this version. Autonomous discovery, per-service writes and the installed adaptation skill remain future work; these profiles define their acceptance boundary.
