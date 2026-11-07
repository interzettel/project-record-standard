# Upgrading the standard

## Current version and compatibility

Published runtime and agent suite **0.4.1** retain record contract **0.2.0**. The validator still reads 0.1.0 and 0.2.0 records. Source IDs and project-owned presentation remain intact. This release adds no schema migration or mass issue renaming. Use [INSTALL.md](https://github.com/interzettel/project-record-standard/blob/main/INSTALL.md) for the verified, pinned source kit; use `pyproject.toml` and `skills/manifest.json` as the version authorities.

Keep the previous toolkit revision/digest, manifest, ownership receipt and generated output before upgrading. Verify the new archive and preview the installer. Apply with `--upgrade` only after reviewing the preview; reconcile edited owned files instead of overwriting them. Re-run source/count parity, semantic checks, history/delivery checks and the host’s relevant interaction checks. Compare immutable IDs and visible denominators.

A 0.4.1 setup/adaptation assessment records L0–L5 readiness, ten evidence dimensions, central assessment links and R0–R4 task limits. These are separate from completion and do not grant autonomy. Existing scope and approvals retain their original meaning.

## Safe update and recovery

Record the old toolkit version, checksum, manifest and generated output. Upgrade in an isolated change. Run source-count parity, semantic checks, history/release tests and the host's relevant interaction checks. Compare immutable IDs and all visible denominators. Keep the old renderer and output available for rollback until cutover is accepted.

Regenerate derived files from authored sources. Do not rewrite source observations to the upgrade date or reset done states. Recover an interrupted build by rerunning the same pinned inputs in an owned output directory. Public builds use an empty directory so stale owner-only files cannot enter the publish artifact.

No command automatically updates GitHub fields, creates a release, deploys a site or awards owner acceptance. These remain named delivery actions with their own authorization and observations.

## Historical 0.1.0 → 0.2.0 contract migration

The original migration note, including vocabulary aliases and renderer integration guidance, is preserved in [dated history](https://github.com/interzettel/project-record-standard/blob/main/progress/history/2026-10-23-before-release/standards--UPGRADING.md). Read it when adapting a 0.1.0 integration. Its implementation-version statement describes that historical package.

## Current compatibility and maintenance policy

Read [pins and update decisions](COMPATIBILITY.md) for the next-phase minor/major/security/ordinary-patch matrix and expected-versus-observed installation identities. A host may automate routine progress under its adopted policy without automatically migrating PRS itself. [Records and memory](RECORDS.md) keeps recall and private information separate from source authority; [feedback](FEEDBACK.md) routes only encountered shared gaps.

## Read-only release-to-host assessment (unreleased)

`project_record.upgrades.assess_upgrade(request)` and `upgrade-assess --request /absolute/path/request.json` compare selected immutable ZIP archives against an actual local installation. They reuse `verify_installation` and `assess_update`; no second installer, network discovery, source transformer or scheduler is added. Exit0 means the bounded assessment is ready (or explicitly simulation-only),1 means conflict,3 means unknown. Invalid input is rejected. These are main-only interfaces, not a newly published release.

An `upgradeVersion:1` request has exactly these fields:

| Field | Supplied evidence |
| --- | --- |
| `installedPin` | Existing pinVersion1 expectation; selected toolkit files, complete selected suite and owned instruction digest. |
| `host`, `hostVersion`, `recordContractVersion`, `profile` | Explicit local host root, separate declared host/record versions and existing `readme-only`, `host-branded` or `private-offline` choice. Host/record versions are declarations, not discovered measurements. |
| `runtime`, `provenance` | Exact caller-observed runtime map and supplied source commit/archive digest; matching identities do not authenticate a publisher or execution. |
| `releases` | Ordered descriptors, beginning with the exact installed pin and an empty anchor delta. Each has `kind` (`published` or `synthetic`), `pin`, local `archive` (or null), `archivePrefix`, attributed `source`, preceding `fromCommit` (anchor null), `changes`, and `review` with reviewer/source. |
| `coverage` | `complete` boolean and attributed `source` for release enumeration/intervening-history review. Missing history remains unknown; the helper cannot prove an upstream list is complete. |
| `decisions` | Change-ID keyed semantic host judgments, each with `decision`, `reason`, and nonempty `evidence` references (`path`, `sha256`) to actual selected host files. No judgment is inferred from prose. |

Each change row has `id`, `kind` (mandatory/optional/deprecated/removed/security), `dimension` (toolkit/suite/contract/runtime/layout/records/guidance/renderer/ci/authority), `summary`, applicable `profiles`, and nonempty `sources` references to exact members of that release archive. Review both migration notes and affected specifications/implementation when authoring a catalogue. Their hashes establish the bytes considered; they do not prove completeness or the semantic truth of the author's interpretation. Change IDs are unique across the selected chain. The request digest binds the complete supplied matrix and judgments.

Archive SHA-256, selected toolkit members, the complete selected skill namespaces, native package version, suite manifest and cited source members must match the selected pin. Overlapping toolkit/suite hash expectations are checked separately. In this assessment format, a release pin’s recordContractVersion identifies its manifest contract; a host still using readable0.1.0 declares that separately in the request. Unsupported installed contracts cannot yield a ready assessment. Archives are read without importing or executing their code. A missing archive, catalogue review, intervening predecessor, source coverage, runtime observation or supported record contract keeps the assessment unknown. Target adapter descriptors remain unknown until actual native support evidence is available; their metadata alone cannot certify runtime support. Moved bytes, incompatible observed runtime, mixed/edited installation or stale host evidence conflict. Selected file coverage is explicit; an omitted toolkit file is never certified. Supplied `published` and reviewer labels are attribution, not authenticated identities.

Host decisions are `already-satisfied`, `applicable-needs-change`, `not-applicable`, `optional-deferred`, `conflict-requires-owner` or `blocked-unknown`. Optional deferral is restricted to optional changes; security changes keep prioritized assessment. A reviewed profile exclusion is not applicable. An already-satisfied rule can use a custom path and must cite its inspected bytes; no template replacement or extra work credit follows. Ambiguous mapping requires a conflict or unknown judgment. The helper verifies byte preconditions, leaving semantic interpretation with the reviewer. A green row cannot override a global installation/history conflict or unknown.

Major/minor and security reactions reuse the compatibility policy. Toolkit, suite, record-contract, runtime and host identities stay separate. Reports contain local paths and potentially private summaries: they are owner-local diagnostics, not approved public projections. Synthetic archives taint the whole comparison as `simulation-only`; they are never evidence that v0.5.0 exists. Read-only repeats return the same report without modifying files or awarding completion/acceptance. All results have `written`, `upgradeApplied`, and `applicationAuthorized` false.

The filesystem check is bounded and refuses selected symlinks/special files; it does not reserve paths against a hostile concurrent process. The comparison is a point-in-time observation, not an atomic installation snapshot. #21 owns reviewed apply, migration receipts, interruption recovery and rollback; #22 owns a deliberately evaluated/distributed upgrade skill. The #20 comparison delivery left the then-eleven skill bodies and suite/contract/package versions unchanged; the later #22 development identity is recorded below. Real consumer migration requires its own scoped authority.

Run `PYTHONPATH=src python3 -m unittest discover -s tests -p test_upgrades.py -v`. [Fixture coverage](https://github.com/interzettel/project-record-standard/blob/main/tests/fixtures/upgrades/README.md) maps parent #10's eight cases to this assessment boundary and the later apply/skill gates.

## Reviewed local application and recovery (unreleased)

`preview_upgrade(request, transformations, guards, producer_revision)` produces an `upgradePlanVersion:1` plan from a ready #20 comparison. `apply_upgrade(plan, grant, journal, mode='apply'|'rollback')` returns an `upgradeReceiptVersion:1` result. Both are available through `project_record.upgrades`; mutation/recovery code lives separately in `upgrade_apply.py`. This adds no network transport, GitHub writes, merge, deployment or release operation.

Preview stages only selected archive members in a disposable directory, copies selected host installation files there, and calls the existing `install_skills(..., upgrade=True)`. That installer alone generates skill bytes, its marked instruction section and ownership receipt. Its optional `rules_sha256` selects a supported exact historical/current instruction writer; default installation behavior stays unchanged. Unsupported writer digests and retirement/relocation needs are held rather than silently rewritten. Host roots are normalized to absolute paths; dotdot and symlink roots are refused before lock/containment checks. The plan includes exact from/to request identities, producer revision, changed paths/preimages/postimages, input/source guards, transformations and synthetic status. Preview changes no host bytes or permissions. The complete plan digest binds its review; reports and staging/journal inputs can contain private material and are owner-local.

Transformations have canonical relative `path` and exact `beforeSha256` (null only for an absent new file). `format-json` retains every parsed JSON value while changing layout; duplicate keys, nonfinite numbers and unsupported depth are refused. `replace-text` has explicit `text` for a separately reviewed authored file. Declare authoritative JSON sources under `guards`; guarded transformations must preserve canonical JSON facts, distinguishing booleans from numbers. No facts are inferred from filenames, prose or source format. Missing/ambiguous source mappings require reconciliation before approval. Unsupported semantic/schema/alias transformations need a separately designed project-owned adapter, not a universal automatic migrator. Selected guards do not certify undisclosed host sources.

A separate grant has exactly `planSha256`, attributed `source`, and boolean `apply`, `rollback`, `allowSynthetic`. Each operation needs its own true flag. A later same-plan rollback grant is supported without requiring rollback permission at initial apply; the journal preserves the original approval and every operation-grant change. A synthetic chain additionally requires explicit simulation permission and remains labelled synthetic in every receipt. These supplied facts record existing host authority; this API does not authenticate the actor or expand the process's permissions. An upstream capability or release arrival grants nothing.

Use the CLI explicitly:

```sh
PYTHONPATH=src python3 -m project_record upgrade-preview --request preview-request.json
PYTHONPATH=src python3 -m project_record upgrade-apply --plan reviewed-plan.json --grant grant.json --journal /private/external/upgrade-journal --mode apply
PYTHONPATH=src python3 -m project_record upgrade-apply --plan reviewed-plan.json --grant grant.json --journal /private/external/upgrade-journal --mode rollback
```

The preview wrapper contains `request`, `transformations`, `guards`, `producerRevision`; save and review its stdout before creating the separate grant. Apply has no default mode. Invalid, stale or conflicting inputs fail without forcing an overwrite. Use an isolated branch/worktree for an actual consumer upgrade and retain its functional-check/owner-acceptance gates.

The external journal contains one owner-only `state.json` with the plan, grant, exact preimages, current phase and verification. It is outside the host tree so snapshots cannot accidentally absorb it. Each host has an advisory cooperating-writer lock. Before any host writes, the helper checks changed paths, unchanged selected installation inputs, decision evidence and source guards; a new toolkit path cannot replace an unowned collision, and a new skill namespace cannot absorb existing unowned host content. Resume accepts only exact planned pre/postimages and inspects actual bytes rather than assuming a phase implies completion. Edited/mixed files stop recovery without overwriting them. Unknown journal neighbors or corrupt backups are retained and refused.

Each file replacement is atomic and flushed; the operation is not an all-or-nothing multi-file transaction. Partial phases remain `applying` or `rolling-back` until selected installation verification succeeds. Tests force real process exits after every implemented host write, plus exceptions at journal/pre-write/verification/completion boundaries. A kill inside the lower-level temporary-file write may leave a temporary neighbor requiring explicit inspection; an empty/incomplete initial journal likewise needs inspection. No arbitrary OS-instruction, power-loss, malicious concurrent-process or native Windows guarantee is claimed.

Rollback uses preserved preimages only when every selected current byte is a known pre/postimage. Later edits to managed/guarded files cause a recoverable conflict before any restore; unrelated authored files remain untouched. New files are removed only when their exact reviewed postimages remain; empty created directories may remain. Successful repeat calls write no host files; a rolled-back plan is not silently reapplied. A new reviewed plan/grant is needed to reconcile later changes.

Receipts distinguish actual per-file apply/rollback, selected-byte verification and remaining host functional/owner gates. They include from/to pins, request/plan hashes, producer revision, paths, guard identities, attributed approval and synthetic status. Local verification does not authenticate provenance, recertify history, award milestone acceptance or change denominators. #22 owns evaluated/distributed agent guidance. The #21 application delivery left the then-eleven skill bodies and package/suite/contract versions unchanged; #22 adds the separately evaluated development suite below.

Verify with `PYTHONPATH=src python3 -m unittest discover -s tests -p test_upgrade_apply.py -v`, alongside the comparison suite. The tests preserve nonempty IDs, dependency, accepted history, release identity and1/2 fraction, verify rollback after authored edits, and inspect bytes after interruption/refusal rather than counting exceptions as success.

## Agent entry point and watcher handoff

Use the main-only `upgrade-project-records` skill for semantic release assessment, reviewed migration and interrupted upgrade/rollback. The router selects it separately from `adapt-project-tracking` for establishing/reconstructing source authority and `operate-project-tracking` for damaged outputs, environment/collection failure and ordinary operational recovery. The cooperating main toolkit/suite identity is0.6.0-alpha.0, with12skills; the published0.4.1 archive still has11. This development identity is not a publication or a supported-runtime claim. Python wheel metadata uses normalized0.6.0a0; native source/suite identity and exact archive hashes remain separately recorded.

Consume an existing Hermes/host watcher observation as read-only input. Retain consumer identity, installed pin, observed target identity, source/attempt/last-success clocks, enumeration coverage, existing assessment/proposal and security-relevance evidence. Reuse the existing consumer/release assessment when its identities still match; new security evidence or changed bytes/coverage requires renewed assessment. Prepare the existing upgradeVersion1 request from reviewed release/host evidence rather than treating a watcher label as verified provenance. A partial observation keeps the last known pin and unknown gaps visible. This is a documented handoff, not a new watcher format/parser, scheduler or fleet database; #39 owns quiet monitoring and durable discovery semantics.

Read the complete eight-case evaluation and limits in [the repository evaluation](https://github.com/interzettel/project-record-standard/tree/main/audit/upgrade-skill/2026-11-07) before inferring a tested upgrade path. Deterministic distribution/byte tests, source-only agent decisions, real immutable0.4.1 same-release smoke and synthetic future migrations remain separately attributed. A new skill cannot make an unavailable semantic migrator, acceptance receipt or real future release exist.
