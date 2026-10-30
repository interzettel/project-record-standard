# Version pins and upgrade decisions

## Available and planned

The published toolkit and eleven-skill suite are v0.4.1, with record contract 0.2.0 and readers for 0.1.0/0.2.0. Main also contains unreleased planning and integration improvements. The proposed next feature cut is 0.5.0; no 0.5.0 tag, artifact, autonomous-tracking support or accepted candidate is claimed.

The v0.4.1 release source is `ebc6afb0b977ff3d7605893c73ac63021775c4d3`. Its source ZIP SHA-256 is `a46cdcea938eb987b936497a22db8eab07106aad7dd12a8cfe10b4ad41f74607`. Obtain it from the [release](https://github.com/interzettel/project-record-standard/releases/tag/v0.4.1), verify all assets and extracted checksums using [INSTALL](https://github.com/interzettel/project-record-standard/blob/main/INSTALL.md), and retain those identities in the adopter's dependency record. A tag name alone is not a byte identity; a checksum alone does not authenticate its publisher.

## One identity for each dimension

| Dimension | Authority and pin |
| --- | --- |
| Toolkit/runtime | Native package version plus immutable source commit/archive digest. |
| Cooperating skills | One suite version by default, with the installed suite/file digests and ownership receipt. Independent versions only for independently published modules. |
| Record contract | Its own contract version and reader/migration compatibility. It does not follow the application version automatically. |
| Policy and adapter | Exact policy revision/digest, adapter version, runtime capability profile and tested host version. Future #30 defines the formal pin check. |
| Host application / document | Preserve its own release, manuscript or experiment identity and meaning. |
| Generated view / observation | Input identity and observation time plus build revision/time; rebuilding does not refresh source facts. |

The existing `.project-record/agent-installation.json` records observed owned bytes and suite identity. An expected pin and an observed receipt are distinct facts; #30 must map their writers explicitly and reuse the receipt rather than adding another writer for installed state. `templates/adoption-pin.example.json` illustrates the dependency facts only; it is not a new validated runtime format.

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

Upstream releases were checked on 30 October 2026. Development CI selects Python 3.15.2 and Node 26.13.0, pinned official action commits and locked jsdom 30.1.3. Markdown 3.11.2 remains the current inspected release with a hash pin. Exact adopted action revisions are retained in the compatibility audit and workflow comments; hosted CI proves only the revision it runs.

[Python's release table](https://www.python.org/downloads/) marks 3.10 end-of-life. The historical v0.4.1 archive and package declaration remain unchanged; new installations should use a supported Python, and the next release must make any minimum-version change explicit. [Node's release table](https://nodejs.org/en/about/previous-releases) identifies supported LTS branches. A current major does not itself prove dependency compatibility; install and behavioral checks must pass.

The published schema dialect remains [JSON Schema2020-12](https://json-schema.org/specification); the accessibility target remains the [WCAG2.2 Recommendation](https://www.w3.org/TR/2024/REC-WCAG22-20241212/), with actual coverage limits.

The skill format is checked against the [Agent Skills specification](https://agentskills.io/specification), with [AGENTS.md](https://agents.md/) as repository guidance. Provider metadata is an extension, not proof every agent discovers it. Future MCP work pins a protocol/SDK and records actual client support. SDK, hook API and runtime versions remain independent of PRS SemVer.

## Maintenance without floating installs

The repository uses weekly dependency-update proposals for Actions, npm and pip, retaining lockfiles and full action SHAs. A proposal does not auto-merge itself. [GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use) recommends full-commit action pins. Check upstream release identity, relevant migration notes and tests before adopting a new major. The host owns deployment and any fleet watcher; do not install a competing scheduler.

A future publication must derive the candidate version from native authorities, verify included changes/compatibility, exercise the archive from a fresh extraction and record actual publication. The historical v0.4.1-specific publisher is not proof of readiness to publish 0.5.0; #38 owns its replacement and guards.
