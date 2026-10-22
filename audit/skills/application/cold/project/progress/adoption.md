# Loomglass local tracking adoption

Observed 2026-10-22. Cold establishment: product documentation and a site exist, but no tracking authority existed. Planning is **proposed**, private and unapproved. Sam owns scope, change decisions and physical acceptance. Local setup authorization does not supply product acceptance, budget or public approval.

## Authority and ownership

| Facts or files | Authoritative writer | Treatment |
| --- | --- | --- |
| Product purpose and constraints | `docs/brief.md`, `README.md`, `AGENTS.md` | Preserve original bytes; overview attributes its proposed interpretation. |
| Scope, completion, dependencies, evidence, WBS and acceptance | Authored `progress/ledger.json`, with Sam as decision authority | One writer; no issue/Project status competes with it. Approval requires an attributed underlying record. |
| Project/source identity and observation history | `progress/project-record.json` | Private file snapshots; source commit is null for uncommitted ledger, not borrowed from main. |
| Source scouting and historical starting state | `progress/discovery.json`, `progress/history/` | Preserve dated observations; append a new observation rather than rewriting the empty starting snapshot. |
| Brand and existing routes | `site/index.html` and authored README | Burgundy/cream and Georgia/serif. Keep site/index.html, title, markup and authored README intact. Host URL and tracking route are undecided. |
| Proposed fallback tokens | `progress/theme.json` | Derive existing brand colors/type, no shared skin and no global website CSS. Additional contrast roles are proposal only. |
| Generated output | Toolkit writes only `progress/generated/` | Rebuildable owner-audience record/history/delivery/SVG/README-module/build manifest. No progress.html with host renderer. Never edit these as source or copy them into the live site without review. |
| Toolkit and skill identity | `progress/toolkit-lock.json` | Checkout path, HEAD and hashes of used source/contract files; the checkout has local edits, so HEAD alone is insufficient. |
| Hosted issues/PRs/Projects, publications and deployment | Future identified hosted systems | Inaccessible, unknown totals. `hosted-coverage.json` remains unchanged. Integration preparation only. |

There are no legacy work IDs to rename. LG-O1 maps to the brief's next outcome. LG-D1–D4, LG-WP1–WP4, LG-M1–M3 and LG-001–LG-007 are new proposed stable IDs. `proof-export` maps to LG-003 at its pinned commit; no issue/PR identifier or URL is invented. Internal states use backlog/active/unknown with their recorded source meaning; only the source-reported exporter start is active. Active work receives no partial completion credit.

## Cleanup queue, in priority order

| Rank | Reason and evidence | Affected work | Owner and next action |
| --- | --- | --- | --- |
| 1 | Active-outcome blocker: acceptance parameters and runnable import source are missing. The brief reports import works but main contains no importer. | LG-001, LG-002 and all downstream work | Sam chooses fixture/print criteria and locates the importer/runtime; record evidence before coding assumptions. |
| 2 | Safety/data-loss prerequisite: repeatable output must not overwrite the original study or an earlier proof. No local output behavior has been demonstrated. | LG-004, LG-005 | Sam confirms output/recovery requirements; proposed implementation and checks enforce safe handling before a physical trial. This is a proposed acceptance control, not an observed defect. |
| 3 | Dependency unlock: unfinished exporter branch is the only supplied implementation lead. [proof-export review](evidence/proof-export-review.md) pins `c1a49a97af2c514ecae099ad3255beef6276225e:proof.py`, a stub. | LG-003 → LG-004 | Sam reviews/resumes this branch after LG-001. Retain it; no merge, deletion, reset or archival is performed. Author is Fixture author; review owner is Sam. |
| 4 | Contradictory claims would obscure readiness: import works is prose evidence, exporter start is not completion, and absent hosted data is not zero. | Current reporting | Local tracking records these limits now; Sam supplies the missing evidence. |
| 5 | Value/effort housekeeping: pre-existing untracked hosted-coverage.json may be worth committing after review. | Repository hygiene | Sam decides its disposition. Preserve it during setup. |
| 6 | Optional presentation and hosted work does not unblock the active workflow. | Future integration only | Sam separately selects a host/repository and public audience; retain the existing site in the meantime. |

There are no locally discovered stale PR links because PR retrieval is inaccessible. The branch reference above is locally inspectable; age alone gives no cleanup authority.

## Scope, checkpoints and metrics

The ledger's proposed outcome decomposes into four deliverables and four WBS work packages, covering all seven declared leaves once. The groups are planning views, not extra accounting leaves. LG-M1 (Now) checks fixture/import readiness; LG-M2 (Next, depends on LG-M1) checks repeatable printable proof; LG-M3 (Later within this outcome, depends on LG-M2) checks physical inspection and handoff. All seven leaves remain proposed required scope; horizon does not remove a denominator. Shared prerequisites use `dependsOn` once. Dates and effort remain unestimated.

| Named measure, observed 2026-10-22 | Empty scaffold observation | Proposed authored scope |
| --- | --- | --- |
| Required work progress | 0/0 — Not measured | 0/7 — 0.0%; seven proposed required leaves |
| Retained ledger progress | 0/0 — Not measured | 0/7 — 0.0%; no deferred/cancelled leaves |
| Accepted milestones | 0/0 — Not measured | 0/3 — 0.0%; each explicitly pending Sam |
| Equal-milestone roadmap progress | Not measured | 0.0%; mean of 0/2, 0/3 and 0/2 |

This denominator change records seven proposed leaves and three proposed checkpoints; it is not product completion or an approved baseline. Empty→proposed percentage-point change is undefined, not a regression. Discovery ideas have no leaf IDs and stay outside both denominators. No cost, schedule or value percentage is claimed.

## Local sequence and integration preparation

1. Read project instructions, product brief, all local files and both branch revisions; record absence/inaccessibility explicitly.
2. Author overview, discovery and this adoption plan before filling the ledger.
3. Initialize a new empty staging directory inside the disposable project, never the project root. Check/export the empty scaffold, then merge only absent tracking files. Preserve its empty ledger as a dated observation.
4. Author the seven-leaf proposal, governance tailoring, dependencies, criteria and owner gates. Store the source digest and compare empty/proposed counts through the toolkit.
5. Run private owner-audience pipeline with `renderer: host`; validate the normalized output and compare its metrics with the source. Generated output stays outside the website/README. Record file-preservation and ref checks.
6. Preview `install-skills` before any application. This setup leaves the preview unapplied: the local skill is already available and no AGENTS change is necessary. The preview receipt records exact proposed changes; no unfinished approval flow is invented.
7. Future hosted preparation: when Sam names a repository, enumerate issues, PRs, branches, releases and Projects through connected tools with full pagination before assigning IDs or writing. Proposed issue title `[LG-003] Complete the printable proof exporter`; suggested families `type:feature`, `area:proof`, `priority:P1`. Reconcile existing labels first. Local ledger remains completion/scope authority unless Sam approves a separate cutover; GitHub can own discussion/assignment, Project can own workflow. No workflow, credential, schedule, repository or hosted item is created now.
8. Future public presentation requires Sam's audience decision, authored public projection/privacy review and a chosen progress route. Use the existing branded host, review keyboard/reflow/contrast and update README only through a reviewed marked region. Technical preparation is not public approval or deployment.

## Governance and operation

Use a proposed adaptive approach with one bounded user workflow. Governance, scope, schedule, stakeholders, resources and risk controls are recorded locally; finance remains not assessed because no budget decision exists. Capacity and committed dates are not invented. Operations are partially assessed: Sam is proposed local handoff owner, with documented output, recovery and limitations required by LG-007; continuing support/incident or service commitments remain undecided. This is a tailored record, not a certification.

## Verification, rollback and resumption

Exact executed commands and results are in `progress/verification.json`. Toolkit runtime checks verify contracts, IDs, references, dependency cycles, WBS coverage and source metrics; they do not authenticate Sam, run the missing importer or inspect a physical print. Preserve all pending product/physical/hosted/public gates.

For a routine update, retain the current ledger and source digest as a new immutable snapshot before changing scope/status. Replay the pinned toolkit and source manifest; rebuild only progress/generated/. Re-run checks and compare named counts. If the same setup is resumed, inspect progress/project-record.json and the ownership record; do not call init on this nonempty project or create parallel ledgers. This becomes an adaptation/update, not another cold establishment.

Rollback is additive: remove only the newly created progress/ tree after reviewing or preserving any later authored edits. No original tracked file, original untracked hosted-coverage.json, branch, tag, product code, README, website or AGENTS content needs restoration. Do not delete user edits merely because they appear under an old generated directory; validate the ownership manifest first. The temporary scaffold is removed after its starting snapshot is retained.

Completed: local discovery, proposed scope decomposition, tracking artifacts, private generation, validation and installer preview. Pending: Sam's scope/acceptance/fixture/resource decisions, actual product work and evidence, physical inspection, any hosted integration and any public review. Sam's next action is LG-001 plus locating the LG-002 importer; no permission question is needed to finish local preparation.
