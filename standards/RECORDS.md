# Personal memory and project records

PRS should help an agent find the right information without turning every remembered detail into a repository record. The host declares the home, writer, privacy, retention and retrieval rule for each class. Existing paths and terminology map into that profile; adoption does not require renaming an established repository.

This is the researched direction for #27/#29. It is not a new enforced layout schema or an implemented memory backend. Investigation and three-host fixtures remain part of their acceptance.

## Classes and ownership

| Class | Purpose and default treatment |
| --- | --- |
| Personal agent memory | User preferences, personal context and cross-project reminders. Keep in the user's scoped/private memory system; public repository status must not reveal its contents, URLs or private totals. |
| Session context | Temporary reasoning, scratch output and conversation state. Treat as ephemeral or governed session history; it is not automatically durable project evidence. |
| Repository instructions | How to work here: AGENTS.md and runner-specific entry points. Version with the repository when appropriate. They guide behavior and reference authority; they cannot grant themselves broader credentials. |
| Shared repository knowledge | Reusable explanations and conventions with sources, scope and freshness. Recall is a pointer to inspect, not a substitute for current authoritative facts. |
| Overview and delivery plan | Purpose, scope, sequence and package interfaces. Link authoritative work; avoid a parallel status checklist. |
| Work records | Stable IDs, current criteria/state/dependencies, evidence links and scope history in the host-declared writer. |
| Decisions | Dated choice, reasons, alternatives, authority, status and explicit supersession. A remembered preference does not rewrite a recorded decision. |
| Findings and evidence | Observation plus source/revision/method/result/limits. Preserve failures and historical evidence; follow-up action links to work. |
| Runbooks | Operating, recovery, rollback and troubleshooting procedures, separate from the delivery plan. |
| Generated state | README modules, SVG, Pages, caches and event transport journals. Declare ownership; derived output does not become a second work source. |

## Existing approaches inspected

[Claude Code memory](https://code.claude.com/docs/en/memory) distinguishes instruction files from automatically recorded project memory, with different scopes and loading behavior. That is a host mechanism to map, not a reason to commit personal memory or make recall authoritative. [LangGraph's memory overview](https://docs.langchain.com/oss/python/concepts/memory) separates thread-scoped state from cross-thread memory and supports namespacing. PRS takes the useful scope distinction without requiring that database or asserting memory accuracy.

[MADR](https://adr.github.io/madr/) supplies a structured decision-record approach and illustrates numbered, descriptive filenames. Adopt its rationale/status/supersession ideas with an explicit local mapping; preserve existing decision IDs and naming conventions. [Diátaxis](https://diataxis.fr/) distinguishes tutorials, how-to guidance, reference and explanation by reader need. Those document purposes are different from authority, visibility or completion status.

These primary implementations were inspected on 30 October 2026. #27 must compare actual selected versions and an authorized host example, including private-source limits; this guide does not certify every memory product or prescribe one universal ontology.

## Proposed optional layout profile

| Home in a small host | Meaning and mapping rule |
| --- | --- |
| `README.md` | Public entry, availability, quick start, limitations and links. |
| `AGENTS.md` | Compact working instructions and skill/tool entry points. |
| `progress/overview.md` / `progress/execution-plan.md` | Outcome and explanatory sequence. |
| Host-declared ledger / manifest | One authoritative writer for each work field. Preserve a GitHub/Jira/native source where already declared. |
| `docs/decisions/` | Decision records; e.g. `ADR-0042-descriptive-title.md`, with stable ID and supersedes links. |
| `docs/reference/`, `docs/how-to/` or existing guides | Shared knowledge organized for the reader; optional routes, not a mandatory folder ladder. |
| `audit/<package>/<observation>/` or existing evidence store | Revision-linked evidence, controls and retained failures. Visibility is declared separately. |
| Private user/host memory store | Personal memory stays outside public selection. A repository stores at most an approved reference/profile, not a copy by default. |
| Owned output / cache / transport area | Generated and recoverable; never selected recursively as project truth. |

#29 will define the machine-readable mapping and fixtures. Naming should make the record easy to find: stable ID, descriptive title and a date when it denotes an observation. File rename, document edition, source revision, experiment run and package release are separate changes. Keep semantic versions for released interfaces where useful; do not add a version number to every note. A superseded decision remains reachable. A generated index can help discovery without duplicating status.

The profile must test README-only research, private personal-agent and shared-repository cases, including conflicting names, stale recall, moved evidence, sensitive references and empty/generated directories. Migrations preview path/ID mappings and preserve history. #25/#26 consume this profile for broader conventions/brand integration rather than defining another records schema.
