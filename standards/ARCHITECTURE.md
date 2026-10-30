# Infrastructure that keeps up with the work

The product goal is one reviewed installation followed by routine automatic reconciliation after authorized work. A maintainer should see what works, what remains, the next eligible task, failures, encountered constraints and scope growth without retyping progress into several tools. Tracking time, correction burden and missed updates are product outcomes to measure.

**Available:** v0.4.1 has an offline record/runtime toolkit, eleven guidance skills, validation, owned-file installation and generated views. **Planned:** unattended after-work reconciliation, policy adapters, cross-model conformance, optional MCP and release-drift monitoring. This architecture selects a direction; its work items and acceptance gates do not claim those capabilities already exist.

## Approaches and selected direction

| Approach | Benefit | Cost and decision |
| --- | --- | --- |
| Guidance and manual commands | Small installation; usable in many agents. | Relies on remembering the tracking step. Keep as fallback, not the unattended target. |
| Shared local core with thin host adapters | Same rules and records for skills, CLI, CI, completion hooks and optional tool transports. Works without a central account. | Needs explicit lifecycle and conformance tests. Selected maintainer design for the next phase. |
| Hosted control service | Can supply multi-device coordination and availability. | Introduces identity, tenancy, uptime, cost and recovery work. Defer until a measured need survives comparison with local/CI operation. |

This design retains Python and the existing validator/adapters, JSON contracts, GitHub integration and static projections. It does not create another agent orchestrator, memory engine or universal project database. Hermes and Qurultai can call the shared interface and retain their own scheduling/execution responsibilities. Any contributor can work across disciplines.

## Guidance and enforcement

| Mechanism | Intended job | Boundary and failure behavior |
| --- | --- | --- |
| Skills / AGENTS.md | Explain purpose, judgment, correct work selection and unusual cases. | Useful guidance; not an authorization or integrity boundary. Missing discovery is reported. |
| Shared CLI/library | Check identity, unique accounting, source/evidence revisions, scope history, pins and public-output rules. | Deterministic core; emits scoped pass/fail/unknown with rule IDs. A check cannot authenticate an owner merely from a string. |
| Local Git / agent hooks | Capture work results and run the same checks early. | Opt-in host adapter; native support, fallback, timeout and bypass are explicit. No second rule engine. |
| Required CI / host protection | Reject changes at the declared merge/release boundary. | Execution of a job is separate from actual required-check settings and permitted bypass actors. Unsupported/inaccessible settings remain unknown. |
| Scheduled reconciliation | Detect missed events, pin/release drift and stale observations. | Bounded, read-only collection by default; preserve last success and show missed/delayed runs. Scheduler ownership stays with the host. |
| Optional local MCP | Expose the same status/check/plan interface to clients. | Thin transport; scope and process permissions still apply. Tool discovery alone cannot force a model to call it. |
| Optional remote service | Address demonstrated multi-device or availability needs. | Requires a separate hosting decision, authentication, isolation, operations and budget. Not required for adoption. |

Official [AGENTS.md guidance](https://agents.md/) describes a place for coding-agent instructions. [OpenAI's repository-review guidance](https://developers.openai.com/blog/custom-code-review-rules-for-codex) distinguishes model review from tests and branch protections. [Git's hook documentation](https://git-scm.com/docs/githooks) states that pre-commit can be bypassed. These are different control surfaces, not interchangeable guarantees.

[Claude Code hooks](https://code.claude.com/docs/en/hooks-guide) supply lifecycle commands, but post-tool checks occur after the action and hook failure behavior needs configuration. [Codex rules](https://learn.chatgpt.com/docs/agent-configuration/rules) govern matching command prefixes; project trust and actual runner permissions matter. Neither source establishes a universal cross-agent hook. Runtime/version support must be observed before PRS labels an adapter supported.

The [policy catalogue](POLICY.md) assigns stable rules to guidance, current checks and future enforcement points. It records existing authority gaps rather than treating structural validation as authentication.

## Automatic after-work reconciliation

The proposed event vocabulary covers start, completion, failure, cancellation, blockage and discovered scope. The event identifies the stable work item, source revision/digest, artifact revision, actual check results and known producer. The unreleased #32 writer defines eventVersion1 for completed, failed, cancelled and blocked results plus discovered scope; this is independent of record contract0.2.0. Start capture and live lifecycle adapters remain #34. See the [local writer and recovery contract](AUTOMATION.md#opt-in-local-work-result-writer).

A thin host adapter captures the result. A local journal/outbox retains it through interruption; the journal is transport and recovery evidence, not a second authoritative work ledger. The core deduplicates the event, checks its source preconditions and authority, then applies the host-authorized record update. Derived views and permitted GitHub projections follow from that source. A stale/concurrent event cannot overwrite newer authored facts. A failed update remains pending with a specific next recovery action.

The default product path should require no manual copying, status retyping or repeated permission prompts for already authorized routine recording. Human-only acceptance, new permissions and work outside the adopted scope envelope remain distinct decisions. An event saying work finished cannot invent a passing test or an acceptance receipt. A local success cannot imply release or deployment.

Discovered work records origin, evidence, effect and disposition. It enters required accounting only through the declared scope authority or a previously authorized bounded admission policy. Views show before/after fractions and why the denominator changed. Rejected, deferred and superseded work stays traceable. A useful negative experiment can complete its own criterion.

Normal, failed, cancelled, disconnected and concurrent sessions must be tested. Missed lifecycle events must be detectable through scoped source/revision reconciliation. Retry is bounded and idempotent; temporary failure should not force an owner to reconstruct the session manually. Surface actionable exceptions instead of a report after every unchanged scan.

## Pins, compatibility and current standards

[Compatibility](COMPATIBILITY.md) separates verified current pins from discovery of a newer release and application of an upgrade. [Records and memory](RECORDS.md) separates personal recall, shared knowledge, decisions, plans, evidence and generated files. [Feedback](FEEDBACK.md) routes only encountered shared-standard gaps upstream. These are inputs to automatic reconciliation rather than additional manual trackers.

The current standards inventory includes Agent Skills, AGENTS.md, JSON Schema, MCP, host hook/permission APIs, SemVer and GitHub workflow/ruleset behavior. A compatibility receipt records source URL, observed date, selected version/revision, actual tested versions and gaps. Recheck at release and on relevant upstream changes. Current stable support is a tested set, not a promise that every floating latest API works.

The [MCP stdio specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio) describes a client-launched subprocess. [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http) has protocol and authentication implications distinct from stdio. The inspected 2026-07-28 revision changes older transport behavior; pin protocol/SDK and test real client negotiation. A local wrapper does not imply a VPS requirement.

[GitHub schedules](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows) may be delayed or dropped. They suit drift checks with freshness/retry records, not exact-time safety guarantees. [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) can require checks but have configurable bypass behavior. A future activation receipt must prove the actual boundary, not just that a YAML file exists.

## Completion and support claims

The [revised release direction](https://github.com/interzettel/project-record-standard/blob/main/progress/release-direction.md) separates foundations from experimental integration and supported automatic operation. The supported automatic workflow requires real end-to-end sessions and at least two actual model/runtime paths with known coverage. Synthetic events, one model's multiple lenses and correct metadata cannot certify those claims. Missing client/model access remains a pending gate.

README-only presentation, the full JSON inspector, semantic upgrade tooling and fleet monitoring continue in their existing bounded packages. Icons and reference-template polish are optional. The [execution plan](https://github.com/interzettel/project-record-standard/blob/main/progress/execution-plan.md) owns the ordered interfaces; the ledger owns state and credit. The initial research and documentation prepare implementation, not completion of the future product.
