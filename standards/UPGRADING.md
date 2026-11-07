# Upgrading the standard

## Current version and compatibility

Runtime and agent suite **0.4.1** retain record contract **0.2.0**. The validator still reads 0.1.0 and 0.2.0 records. Source IDs and project-owned presentation remain intact. This release adds no schema migration or mass issue renaming. Use [INSTALL.md](https://github.com/interzettel/project-record-standard/blob/main/INSTALL.md) for the verified, pinned source kit; use `pyproject.toml` and `skills/manifest.json` as the version authorities.

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

The filesystem check is bounded and refuses selected symlinks/special files; it does not reserve paths against a hostile concurrent process. The comparison is a point-in-time observation, not an atomic installation snapshot. #21 owns reviewed apply, migration receipts, interruption recovery and rollback; #22 owns a deliberately evaluated/distributed upgrade skill. Existing eleven skill bodies and suite/contract/package versions are unchanged. Real consumer migration requires its own scoped authority.

Run `PYTHONPATH=src python3 -m unittest discover -s tests -p test_upgrades.py -v`. [Fixture coverage](https://github.com/interzettel/project-record-standard/blob/main/tests/fixtures/upgrades/README.md) maps parent #10's eight cases to this assessment boundary and the later apply/skill gates.
