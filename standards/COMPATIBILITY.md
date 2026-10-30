# Version pins and upgrade decisions

## Available and planned

The published toolkit and eleven-skill suite are v0.4.1, with record contract 0.2.0 and readers for 0.1.0/0.2.0. Main also contains unreleased planning and integration improvements. The [revised release direction](https://github.com/interzettel/project-record-standard/blob/main/progress/release-direction.md) proposes foundations 0.5.0 followed by opt-in automation previews and separately proven support; no 0.5.0 tag, artifact, autonomous-tracking support or accepted candidate is claimed.

The v0.4.1 release source is `ebc6afb0b977ff3d7605893c73ac63021775c4d3`. Its source ZIP SHA-256 is `a46cdcea938eb987b936497a22db8eab07106aad7dd12a8cfe10b4ad41f74607`. Obtain it from the [release](https://github.com/interzettel/project-record-standard/releases/tag/v0.4.1), verify all assets and extracted checksums using [INSTALL](https://github.com/interzettel/project-record-standard/blob/main/INSTALL.md), and retain those identities in the adopter's dependency record. A tag name alone is not a byte identity; a checksum alone does not authenticate its publisher.

## One identity for each dimension

| Dimension | Authority and pin |
| --- | --- |
| Toolkit/runtime | Native package version plus immutable source commit/archive digest. |
| Cooperating skills | One suite version by default, with the installed suite/file digests and ownership receipt. Independent versions only for independently published modules. |
| Record contract | Its own contract version and reader/migration compatibility. It does not follow the application version automatically. |
| Policy and adapter | Exact policy revision/digest, adapter version, runtime capability profile and tested host version. The optional pinVersion 1 API checks selected bytes and reports provenance/support separately. |
| Host application / document | Preserve its own release, manuscript or experiment identity and meaning. |
| Generated view / observation | Input identity and observation time plus build revision/time; rebuilding does not refresh source facts. |

The existing `.project-record/agent-installation.json` records observed owned bytes and suite identity. An expected pin and an observed receipt are distinct facts. The host dependency policy owns `templates/adoption-pin.example.json` or its equivalent expected pin; the existing installer remains the sole writer of `.project-record/agent-installation.json`. The new read-only pinVersion 1 API reuses that receipt and never rewrites it. The template is a worked, explicitly unreleased source-pin example; it is not a receipt or an installed consumer.

## What an upstream change requires

| Change observed against a verified consumer pin | Required response | Application |
| --- | --- | --- |
| Major release | Recorded compatibility/breaking-change assessment. | Reviewed migration and actual authorization; incompatible or unsupported cases can remain held/deferred. |
| Minor release | Recorded applicability assessment, including intervening changes. | Apply required applicable changes under the host policy; optional or already-satisfied changes need no forced rewrite. |
| Security patch / relevant vulnerability | Prioritized assessment even when only PATCH changes. | Remediate or record a bounded mitigation/deferral and its risk owner; a previous ordinary deferral cannot hide a new security change. |
| Ordinary patch | Proportionate triage; record impact or a reasoned deferral when the watcher/profile applies. | No universal requirement to edit every consumer immediately. |
| Prerelease | Discoverable, opt-in test channel. | Never silently replace a stable pin. |
| Unverified/moved target, partial coverage or mixed install | Unknown/conflicted with retained last-known identity. | Do not certify or auto-apply from incomplete evidence. |

This assessment policy is PRS's local design. [SemVer 2.0.0](https://semver.org/) defines version meaning once a public API is declared; its 0.y.z period is initial development. PRS therefore treats 0.x minor changes as compatibility boundaries to inspect rather than assuming stability. Breaking changes to a declared stable API require a major bump after 1.0.0. Deprecation, removal and support windows must be stated in the release notes, not inferred from the number alone.

Automatic progress recording after an authorized work session is separate from automatically updating PRS itself. A consumer may opt into patch application only within its adopted policy, passing tests and conflict/recovery checks. Discovery never grants new merge, deployment, credential or scope authority. Minor/major assessment is mandatory under the selected profile; immediate migration is not.

## Current development baseline

Upstream releases were checked on 30 October 2026. Development CI selects Python 3.15.2 and Node 26.13.0, pinned official action commits and locked jsdom 30.1.3 and build backend setuptools 84.2.1. Markdown 3.11.2 remains the current inspected release with a hash pin. Exact adopted action revisions are retained in the compatibility audit and workflow comments; hosted CI proves only the revision it runs.

[Python's release table](https://www.python.org/downloads/) marks 3.10 end-of-life. The historical v0.4.1 archive and package declaration remain unchanged; new installations should use a supported Python, and the next release must make any minimum-version change explicit. [Node's release table](https://nodejs.org/en/about/previous-releases) identifies supported LTS branches. A current major does not itself prove dependency compatibility; install and behavioral checks must pass.

The published schema dialect remains [JSON Schema2020-12](https://json-schema.org/specification); the accessibility target remains the [WCAG2.2 Recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/), with actual coverage limits.

The skill format is checked against the [Agent Skills specification](https://agentskills.io/specification), with [AGENTS.md](https://agents.md/) as repository guidance. Provider metadata is an extension, not proof every agent discovers it. Future MCP work pins a protocol/SDK and records actual client support. SDK, hook API and runtime versions remain independent of PRS SemVer.

## Maintenance without floating installs

The repository uses weekly dependency-update proposals for Actions, npm and pip, retaining lockfiles and full action SHAs. A proposal does not auto-merge itself. [GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use) recommends full-commit action pins. Check upstream release identity, relevant migration notes and tests before adopting a new major. The host owns deployment and any fleet watcher; do not install a competing scheduler.

A future publication must derive the candidate version from native authorities, verify included changes/compatibility, exercise the archive from a fresh extraction and record actual publication. The historical v0.4.1-specific publisher is not proof of readiness to publish 0.5.0; #38 owns its replacement and guards.

## Read-only pin capture and verification

`project_record.pins.capture_pin` builds expected metadata from a reviewed toolkit and an explicit toolkit-file selection. It always pins the native `pyproject.toml` version source, the complete selected skill manifest/file table/suite digest and owned AGENTS section digest. An optional policy path has its own source commit and SHA-256. The host chooses where to save this expectation; capture does not install files, write a receipt, discover a release or authenticate its source arguments.

`validate_pin` accepts only immutable source commits and optional archive SHA-256, canonical relative paths and internally consistent suite identities. `main`, `latest` and a tag label alone cannot certify an installation. `verify_installation(pin, target, ...)` reads selected toolkit files, the existing installer receipt, owned suite folders and the marked AGENTS section. It preserves project text outside that section and ignores unrelated user skill namespaces. Missing inputs remain partial; existing malformed receipts, directory collisions and drift/mixed ownership remain conflicted, and untracked files in the selected skill folders are conflicts. Unsupported record contracts are reported separately; existing 0.1.0 and 0.2.0 readers remain unchanged.

| Report | Exact claim and limit |
| --- | --- |
| `bytes: selected-bytes-match` | The explicit toolkit selection, complete selected suite, its receipt/owned rules and any selected policy match expected digests. It makes no claim about unselected toolkit files or dependencies. Pin a release's full reviewed file inventory when full-kit coverage is required. |
| `provenance` | Missing, matching supplied origin identities, or conflicted. Caller-supplied release/checksum evidence is compared separately. Even a match leaves `publisherAuthenticated: false`; inspect the actual trusted channel/signature or attributed source independently. |
| `runtime`, `adapters` | Exact caller-observed versions/identities match declared support evidence, are unknown, or conflict. These inputs are not measured or authenticated by this helper. No adapter is supported merely because its descriptor exists. |
| `recordContract`, `policy` | The selected reader contract is known or unsupported; policy is included in byte checking or explicitly not pinned. A missing policy is never fabricated from a suite receipt. |
| `written`, `upgradeApplied` | Always false. No upgrade, consumer migration, credential or acceptance authority is granted. |

The source commit and suite/package/contract versions are independent identities. The native toolkit package version comes from `pyproject.toml`; the historical module `__version__` label is not used as a competing package-version authority. pinVersion 1 is an optional dependency-profile format, not a change to completion record contract 0.2.0. Live provenance, atomic write preconditions and the full semantic upgrade workflow remain separate boundaries owned by #32 and #20–#22.

Reports contain local selected paths and diagnostics. They are not automatically approved for public output. A byte-match result cannot authorize a write when provenance, runtime coverage, policy or the host's task grant remains unresolved. Existing installed bytes are not changed to make a result green; reconcile drift or preview a reviewed upgrade through the normal installer.

## Compatibility decisions without application

`assess_update(installed, available, security=False, deferral=None)` classifies supplied exact SemVer identities, including prerelease ordering and stabilization. Major/minor changes require compatibility assessment under PRS's adopted policy. Security relevance takes priority even with the same version or an existing ordinary deferral. A patch deferral needs an explicit reason bound to the exact from/to versions; it cannot hide another target or a new security finding. New prerelease candidates remain opt-in; equal prerelease precedence is no change. Build metadata does not change version precedence. Downgrades require review. Every result leaves `applicationAuthorized` and `upgradeApplied` false.

The API does not fetch release lists, validate vulnerability feeds, certify arbitrary release notes or implement the later multi-release migration comparison. Preserve the source/time/coverage of supplied observations. A new upstream release can require assessment without forcing every consumer to change files immediately.

## Runtime floor and current assessment

The dated [pin baseline assessment](https://github.com/interzettel/project-record-standard/blob/main/audit/pins/2026-10-30/baseline.json) rechecks the official Python/Node release tables, Agent Skills, JSON Schema, MCP and SemVer sources. Current CI selects Python 3.15.2 and Node 26.13.0; Node is a development DOM-test/build toolchain, not a dependency for offline record validation or static-page viewing. The local test environment is recorded separately from hosted CI.

This package does not change the historical `requires-python >=3.10` declaration or old release bytes. Python 3.10 is outside the supported security baseline; syntax compatibility does not establish maintenance support. Before the next publication, #38 must select and actually test an explicit supported minimum, update native metadata if required and document the consumer effect. The selected CI pin is not proof that every intermediate Python or Node version works. No optional MCP client/hook/runtime gains support from this research.

## Execution-guidance development change

PRS-AGENT-EXECUTION adds optional executionVersion1 read-only assessment and revises the installed marked instruction section. Skill bodies/suite metadata and completion contract remain unchanged. Existing installations must explicitly preview/apply an instruction upgrade when the rules digest differs, even if skill-file suite identity matches. PinVersion1 validation retains both the preceding writer and this instruction writer; verification compares the chosen expected rules digest against actual owned bytes. No historical pin, receipt or release asset is rewritten. This is unreleased development behavior, not an automatic migration or authorization token.
