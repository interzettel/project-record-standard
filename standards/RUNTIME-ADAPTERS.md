# Runtime adapter pilot

This is unreleased preparation for **PRS-HOOK-01 / #34**, not supported automatic operation. No actual Codex or Claude Code lifecycle session has been verified in the development environment. Exact runtime versions, native trigger receipts and runtime permission/trust behavior remain live acceptance gates. A synthetic envelope or successful `--version` probe proves neither a native hook nor model effectiveness.

## Boundaries

The adapter delivers a host-prepared event to the [existing local writer](AUTOMATION.md#opt-in-local-work-result-writer). That writer alone evaluates authority, evidence, source preconditions, discovered scope and completion policy. Runtime text, transcripts and hook stdin cannot supply a replacement event/profile, mark work Done or grant permissions. Personal memory and transport state remain outside authoritative records.

This pilot handles one immutable ticket per bounded result. The host prepares it after evidence is available and before its intended lifecycle trigger. Start capture, automatic preparation from arbitrary agent work, discovery/dispatch across tickets, hook removal after delivery, fleet maintenance and end-to-end model proof are not implemented here. A missed trigger needs explicit retry. This is a deliberately limited experiment, not the intended install-and-forget product.

| Runtime | Documented events used | Pilot limitation |
| --- | --- | --- |
| Codex | Stop, Interrupt, SessionEnd | Session and turn must match; native hooks require host review/trust. |
| Claude Code | Stop, StopFailure, SessionEnd | Session must match; no verified per-turn identifier or generic cancellation hook. SessionEnd can carry a prepared cancellation; otherwise use an explicitly labeled retry. |

Research references: [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Claude Code hooks](https://code.claude.com/docs/en/hooks), inspected 4 November 2026. Documentation coverage is separate from tested support. StopFailure and Interrupt can deliver only matching failed/blocked or cancelled/blocked prepared outcomes. SessionEnd cannot claim a completed result. Stop delivers an already evidenced terminal result; the trigger itself supplies no completion evidence. A continued Stop (`stop_hook_active: true`) is held.

## Prepare and pin

Run the tool from a reviewed source checkout, using an explicitly selected Python interpreter. All request paths are absolute. `probe` only invokes the CLI's `--version`; it does not launch a model session. `pin` captures the complete local core Python source set, both adapter entrypoints and package metadata. These hashes detect changes against host-adopted bytes; they do not authenticate provenance or replace verified installation pins.

```sh
python3 tools/run_runtime_adapter.py probe --runtime codex
python3 tools/run_runtime_adapter.py probe --runtime claude-code
python3 tools/run_runtime_adapter.py pin --toolkit /absolute/reviewed/prs
```

Create a private JSON request with exactly these fields:

| Field | Value |
| --- | --- |
| `adapterVersion` | Integer `1`, independent of the record and package versions |
| `runtime` | `codex` or `claude-code` |
| `runtimeVersion` | Exact host-observed CLI version; no support-range inference |
| `runtimeExecutable` | Reviewed absolute executable path, or `null` to resolve PATH during the probe |
| `sessionId` | Exact observed session identifier |
| `turnId` | Exact Codex turn identifier; `null` for this Claude adapter |
| `workspace`, `toolkit`, `python` | Absolute host-selected workspace, reviewed checkout and interpreter paths |
| `coreFiles` | Complete object returned by `pin` after host review |
| `timeout` | Positive shared-worker budget in seconds, at most 60; choose within the runtime hook's shorter total budget |
| `event`, `profile` | Exact eventVersion1 and host-adopted reconcileVersion1 objects described in AUTOMATION |

```sh
python3 tools/run_runtime_adapter.py prepare --request /private/request.json --outbox /private/prs-outbox
python3 tools/run_runtime_adapter.py status --ticket /private/prs-outbox/TICKET_HASH
```

Preparation writes `request.json` before any trigger, with private modes for newly created files/directories, plus pending `state.json`. Reusing an event ID with different request bytes is refused. Use a private existing parent: this tool does not change permissions on host-owned directories. Do not put credentials, transcript text or personal memory in these records. Tickets contain policy and evidence and are not public exports.

## Preview, trust review and rollback

Build the POSIX command with `project_record.runtime_adapters.hook_command(ticket, toolkit, python)` or use equivalent shell quoting for these host-owned absolute paths. Runtime payload fields must never be interpolated into shell commands. Windows shell configuration has not been implemented or verified.

```sh
python3 tools/run_runtime_adapter.py install --runtime codex --config /host/project/.codex/hooks.json --command '/absolute/python -I /absolute/reviewed/prs/tools/run_runtime_adapter.py hook --ticket /private/prs-outbox/TICKET_HASH' --receipt /private/install-receipt.json
```

The default is a preview. Review its before/after JSON, command, affected events, runtime policy and exact toolkit bytes before repeating with `--apply`. For Claude Code, select `--runtime claude-code` and its project `.claude/settings.json` explicitly. This tool does not discover or modify global configuration, inline TOML or managed policy. Existing event groups and unrelated settings are preserved; unsupported shapes are refused. Other config layers may disable or duplicate hooks and require actual runtime inspection.

Apply saves exact prior bytes in a separate new receipt before replacing the selected JSON file. Interrupted installation can be rolled back using that receipt. Review/trust Codex hooks through its native mechanism; this installer does not bypass trust prompts or change runner permission policy. A config write is not proof of activation.

```sh
python3 tools/run_runtime_adapter.py rollback --receipt /private/install-receipt.json
```

Rollback restores exact prior bytes, or removes a file created by this install. Later edits are preserved by refusing rollback if current bytes match neither the before nor after image. Keep the receipt for recovery; a new installation attempt needs a new receipt. Retire this ticket's hook through reviewed configuration cleanup after the pilot; delivered-ticket deduplication prevents repeated ledger writes, but does not remove the configuration entry.

## Recovery and verification

Hook mode reads at most 1 MiB of JSON stdin. It prints `{}` and exits zero even when transport is pending, so tracking failure does not block/continue the agent's work or leak private reconciler output into hook protocol output. Explicit `retry` reports failure with exit3. A successful hook process exit is not tracking success: inspect `state.json` and `last-core-result.json`.

```sh
python3 tools/run_runtime_adapter.py retry --ticket /private/prs-outbox/TICKET_HASH
```

Manual retry bypasses native session/version observations and is permanently labeled `manual-retry`. It still checks the core pin and shared writer policy. It is not a native runtime test. The immutable request survives a missed event, malformed/wrong session, unavailable CLI/core, changed pin, timeout, core refusal or hook failure. Resolve the recorded reason and retry the same ticket. Do not edit a pending request to fit newer sources; reconcile the conflict through the shared writer's recovery contract and prepare a separately identified new result where appropriate.

An OS advisory lock serializes cooperative deliveries. Duplicate delivered tickets return the historical receipt without re-awarding credit. If the shared core commits and transport receipt writing fails, its event journal deduplicates the subsequent retry. The transport outbox is not a second work ledger. It does not detect a later malicious edit or source rollback as a new work result. A single local OS owner, reviewed interpreter/core, honest host-prepared evidence and cooperative configuration writers remain trust assumptions; self-hashes are not authentication. Symlink paths are refused, but noncooperating same-user file races are not a sandbox boundary.

Installer event handlers request three-second timeouts. Actual native limits can be shorter, especially Interrupt/SessionEnd. Runtime probing and core work share that outer budget; choose a smaller worker timeout and expect recovery when the host terminates a hook first. Hard termination can leave `awaiting-trigger` or an in-progress attempt without a final error receipt; immutable prepared bytes and the writer journal remain the recovery sources. Neither a hook nor the core is guaranteed to finish within the native budget.

Before claiming support, record for **each actual runtime** its executable/version, model identity where relevant, exact toolkit revision/hashes, reviewed config/trust policy, session/turn, native trigger payload, shared writer result, source before/after and duplicate/failure recovery. Preserve failures and clearly label wrapper/manual fallbacks. Run the adapter tests and shared suite, then perform the native sessions under existing scoped model/credential authorization. No new model budget or consumer migration is granted by this guide.

The #33 Actions condition also remains: before unattended use across **2 December 2026**, resolve the observed `pull_request_target` event-policy incompatibility through a reviewed compatible design or explicitly authorized narrow policy decision. This local adapter makes no GitHub policy exception, hosted scheduler, MCP service or deployment claim.
