# Personal memory and project records

PRS should help an agent find the right information without turning every remembered detail into a repository record. The host declares the home, writer, privacy, retention and retrieval rule for each class. Existing paths and terminology map into that profile; adoption does not require renaming an established repository.

The [#27 investigation](https://github.com/interzettel/project-record-standard/blob/main/audit/records/2026-10-30/investigation.md) compares selected primary implementations, inventories PRS and a scoped public host, and works through five routing counterexamples. Its [source identities](https://github.com/interzettel/project-record-standard/blob/main/audit/records/2026-10-30/sources.json) and verification limits are explicit. The optional layoutVersion 1 mapping now has read-only Python validation, lookup, index and migration-preview helpers. It is independent of record contract 0.2.0 and is not a memory backend or activated host enforcement.

Route a fact by purpose, audience, declared writer and lifecycle before selecting a filename. Memory may point to current sources; persistence, a namespace, search rank or an authoritative-sounding filename cannot establish approval, accuracy or permission. A record can be durable without being public, and a public document can be explanatory without owning a work field.

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
| Findings and evidence | Observation plus source/revision/method/result/limits. Preserve failures and historical evidence; follow-up action links to work. Sensitive material follows its declared retention/erasure policy, with an allowed amendment or tombstone when appropriate. |
| Runbooks | Operating, recovery, rollback and troubleshooting procedures, separate from the delivery plan. |
| Generated state | README modules, SVG, Pages, caches and event transport journals. Declare ownership; derived output does not become a second work source. |

## Existing approaches inspected

[Claude Code memory](https://code.claude.com/docs/en/memory) distinguishes instruction files from automatically recorded project memory, with different scopes and loading behavior. That is a host mechanism to map, not a reason to commit personal memory or make recall authoritative. [LangGraph's memory overview](https://docs.langchain.com/oss/python/concepts/memory) separates thread-scoped state from cross-thread memory and supports namespacing. PRS takes the useful scope distinction without requiring that database or asserting memory accuracy.

[MADR](https://adr.github.io/madr/) supplies a structured decision-record approach and illustrates numbered, descriptive filenames. Adopt its rationale/status/supersession ideas with an explicit local mapping; preserve existing decision IDs and naming conventions. [Diátaxis](https://diataxis.fr/) distinguishes tutorials, how-to guidance, reference and explanation by reader need. Those document purposes are different from authority, visibility or completion status.

These primary implementations were inspected on 30 October 2026. The investigation identifies Claude Code's observed v2.1.314 release, LangGraph 1.2.18 interfaces, MADR 4.0.0 and dated rolling documentation without treating current docs as exact-version runtime proof. It proposes storage, writer, trust, privacy, retention, retrieval and supersession rules for all ten classes. No private memory store was inspected and no memory-quality or agent-runtime experiment was performed.

## Resolve conflicting information

Read the applicable source revision, field authority and any correction/supersession links. An old plan paragraph is a historical observation when a later attributed amendment says so. A remembered approval is a lead to inspect, not the approval receipt. A generated index can locate evidence but cannot make it current or change its audience.

For a personal-only preference, keep the fact in its authorized private compartment. For a shared convention, update the existing repository guide under normal authority. For changed decisions, retain the prior decision and link the actual successor. For failed experiments, retain the failed observation alongside the correction. For generated status, repair the declared source or generator and rebuild; do not edit the percentage by hand.

Do not scan personal memory or publish its locators to prove that this separation exists. Select only relevant authorized sources. If the source writer or audience remains unresolved, leave the authoritative field unchanged, retain a local/private proposal and name the missing decision. Routine authorized updates need no new approval ceremony.

## Optional layout profile

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

`templates/record-layout.example.json` and the three synthetic hosts in `tests/fixtures/record_layout/` define the explicit mapping. Naming should make the record easy to find: stable ID, descriptive title and a date when it denotes an observation. File rename, document edition, source revision, experiment run and package release are separate changes. Keep semantic versions for released interfaces where useful; do not add a version number to every note. A superseded decision remains reachable. A generated index can help discovery without duplicating status.

The profile must test README-only research, private personal-agent and shared-repository cases, including conflicting names, stale recall, moved evidence, sensitive references and empty/generated directories. Migrations preview path/ID mappings and preserve history. #25/#26 consume this profile for broader conventions/brand integration rather than defining another records schema.

## Mapping format and read-only helpers

`layoutVersion: 1` identifies this optional mapping, independently of the toolkit release and completion-record contract. A host may keep its existing equivalent mapping; no automatic installer discovery or mandatory new profile file is introduced. The complete example is synthetic. Profiles containing private references stay private; a public consumer receives only a separately reviewed index.

| Field | Meaning |
| --- | --- |
| `stores` | Exactly one entry per class: personal-memory, session-context, instructions, knowledge, plan, work, decisions, evidence, runbooks and generated. Use an explicit unused home when a class is unnecessary. No folder must be created to satisfy this declaration. |
| `home` | `kind: repo` with literal relative `path` and `scope: file` or `directory`; `external` with a host-local `reference`; or `unused`. File anchors permit a README-only host. Whole-file Git/public selection must agree across all collocated sections and declared private directories; a private section cannot be hidden inside a selected public file. Directory scope is explicit, so dots in existing directory names work. |
| `writer`, `owns` | One declared writer per class; unique qualified field identities. Only work may own `work.*`; generated views own no authoritative fields. The profile points to existing authority and carries no work states, completion counts or approvals. |
| `visibility`, `git`, `publicIndex` | Explicit independent selections. Private entries cannot enter a public index. External/unused homes are never selected. Personal/session and transient stores are private; Git selection requires an attributed `gitApproval` decision and is never automatic. |
| `retention` | Host lifecycle/erasure rule. The helper requires a declaration; it does not delete or retain actual files. |
| `records` | Optional locator index: class-scoped stable ID, current path and revision, with `previousPaths` and same-class `supersededBy` where applicable. No content, private totals or duplicate completion state belongs here. |

Use `project_record.record_layout.validate_layout`, `layout_index`, `git_paths`, `resolve_record` and `migration_preview` from a reviewed checkout. They inspect supplied metadata only, never traverse a repository, open memory stores, stage files or perform a move. The module is included in the Python package; the optional profile is not silently added to `examples/projects.json` or the completion contract.

`layout_index(profile)` returns only explicit public repository locator fields. It omits private entries entirely, with no private totals, external references, retention strings, previous paths or arbitrary extension values. `layout_index(profile, 'owner')`, `git_paths` and `resolve_record` are for authorized local use and can reveal private repository metadata. Do not publish their results indiscriminately. Git paths are an explicit record selection for review, not a Git staging or ignore-rule engine.

Lookup by class and stable ID disambiguates reused names. Duplicate IDs within one class fail validation. A shared file or historical locator matching several records returns ambiguous; a missing ID returns unknown. A stale recalled revision is flagged and cannot replace the indexed current locator. Superseded decisions return their successor ID without deleting the earlier record. This does not authenticate a decision, prove a file exists or certify its current bytes.

A migration preview lists moves for stable identities, requires the previous locator on moved records, reports removed mappings as `unmapped-hold`, and flags changes to home/writer/visibility/selection/ownership/retention as `policy-change-hold`. This includes transient flags, Git grants and extension-field changes. Historical aliases cannot be dropped silently on repeated moves. Added references are reported explicitly. Nothing is applied; resolve holds and inspect real source/destination conflicts, symlinks, permissions and authorized audience before a separately implemented migration. Public sharing of a preview needs its own selection review.

## Naming, revisions and lifecycle

Keep native language, case, existing IDs and paths. An ID names the work/decision/experiment; a descriptive filename helps readers find it. A date denotes a specified observation or decision date, not automatic freshness. A Git revision/digest identifies source bytes; a document edition identifies its authored publication; an experiment run identifies a particular attempt; a package version identifies a released interface. These are separate fields and do not need to appear in every filename.

A generated index never becomes another completion ledger. Empty generated directories create no records. Preserve prior evidence identities and failures, record moved locators, and retain explicit successor links for decisions. A sensitive source may require erasure under its host policy: keep only an allowed amendment/tombstone and do not claim erased bytes remain reproducible. #25/#26 consume this mapping for broader conventions rather than introduce competing ownership.

The tests cover README-only research, private personal-agent and shared-repository metadata. They are synthetic local applications, not real host migrations, agent-memory effectiveness experiments or model/runtime conformance evidence. All actual host access and acceptance boundaries remain unchanged.
