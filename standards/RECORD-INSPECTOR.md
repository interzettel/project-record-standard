# Declared record inventory and inspector coverage

PRS emits several JSON families and consumes others. A file extension, title or successful JSON parse cannot establish its schema, audience, authority or freshness. The #17 inventory underpins the owner-local offline views implemented by #18 below. Public export and integration remain gated by #19.

## Producer evidence and ownership

The [machine-readable coverage table](https://github.com/interzettel/project-record-standard/blob/main/standards/inspector-inventory.json) names29 reviewed families with paths, producer/adapter, released versus main-only availability, source/derived writer, sensitivity, actual schema/unsupported status and planned inspector view. Its path patterns explain producer destinations; they are **not scan instructions**. Only a separate explicit selection lists files to inspect.

Released baseline: v0.4.1 at `ebc6afb0b977ff3d7605893c73ac63021775c4d3`. Main-only additions were inventoried at `4030b63c3cf6487ae7ea659be8d6962e795a16f5`. Main still carries package/suite0.4.1 metadata, but that does not make new code part of the immutable published release. The inventory diagnostic and owner-local HTML inspector on main are explicitly unreleased.

| Family | Real producer or supplied input | Ownership and coverage |
| --- | --- | --- |
| Normalized `record.json` / exported project JSON | Released adapters, build/export | Derived record; declared source owns work/scope/acceptance. Existing core contract checks0.1.0/0.2.0. |
| `history.json` / `delivery.json` | Released timeline/delivery/build | Derived pinned observations and authored delivery evidence. No standalone JSON schema; limited shape recognition. |
| `build-manifest.json` / site `record-build-manifest.json` | Released build and verified site copies | Generator owns output identities; not an approval or hosted-health receipt. |
| `website-build.json` / copied project JSON | Released site builder | Public only through the accepted public-input pipeline; site build differs from deployment observation. |
| `agent-installation.json` | Released opt-in skill installer | Local ownership/file/rule digests; private by default. Shape/version checks are not actual installed-file verification. |
| Schema and public source-kit copies | Released schema generator/packager | Definitions or filtered copies retain their source meaning; archive inspection is not automatic. |
| Raw adapter ledger, source manifest and theme | Adopter-authored; released cold init seeds three JSON files | Canonical source/config/brand ownership, not three normalized record exports. Initial scope is private and unapproved. |
| Fragments, supplements, discovery, native snapshots and collection receipts | Explicit adopter/observer inputs | Templates are examples; runtime does not automatically collect GitHub or produce external health receipts. |
| Pin/layout/execution/policy API results | Unreleased main APIs; some results exist only if caller captures them | Declared expected/observed identities and bounded checks; no generic file writer or permission grant. |
| Reconciliation journal, runtime tickets/config receipts, feedback queue | Unreleased explicit local writers | Private transport/recovery and host-authored evidence; not another work ledger or native-session proof. |
| Monitoring/MCP/hosting/live-session receipt examples | Planned or synthetic unless actually evidenced | Unsupported; a proposed receipt never establishes an installed producer or completed work. |

The release smoke test runs the pinned build/scaffold/installer modules on disposable synthetic input and records artifact/producer hashes in `audit/inspector/2026-11-05/released-producer-proof.json`. The portable [fixture provenance witness](https://github.com/interzettel/project-record-standard/blob/main/tests/fixtures/inspector/provenance.json) is also included in the public source kit, which intentionally excludes the audit directory. It verifies those bounded producers, not every command/channel or a real consumer migration. Code inspection covers the other named entry points. No recursive repository/downstream JSON census was performed or claimed.

## Explicit selection contract

Use `selectionVersion1` with `records`, a list of at most128 literal declarations. Each entry needs unique stable `id`, relative POSIX `path`, explicit `kind`, and declared `visibility` (`public` or `private`). Paths end in `.json`; absolute paths, traversal, glob patterns, aliases and symlinks are refused. There is no directory scan, schema guessing by filename, reference following, archive extraction or network fetch.

Optional metadata: `sourceObservedOn`, `sourceUpdatedOn`, `renderedAt`, `producerRevision`, `expectedSha256`, `synthetic`. Unknown values stay null/absent; producer revisions and expected hashes have explicit formats. Source observation and update dates, caller-declared render time and actual supplied inspection time are distinct. Inspection never refreshes source dates or authenticates any metadata. Stable artifact IDs do not become new work IDs or earn progress credit.

The initial selector supports these explicitly declared kinds:

| Kind | Check performed | Meaning of success |
| --- | --- | --- |
| `project-record` | Existing core validator, supported contract0.1.0/0.2.0 | `validated`: existing core contract checks passed; provenance/authority/publication are not authenticated. |
| `project-manifest` | `projects` entry-point shape only | `recognized-shape`: does not load referenced source files or validate the full manifest. |
| `history`, `delivery` | Named top-level fields/types | `recognized-shape`: no full schema or semantic recalculation. |
| `build-manifest` | List/project/file/hash entry-point shape | `recognized-shape`: does not follow output paths or verify other files. |
| `skill-suite`, `installation-receipt` | Producer schemaVersion1 and entry-point shape | `recognized-shape`: does not read skill files, compare native versions or inspect installation targets. |

All other kinds remain `unsupported-kind` without reading their body, including raw adapter ledgers and hypothetical receipts. The catalogue records these unresolved schema/view mappings instead of pretending they are normalized exports. Known family shape recognition is intentionally weaker than full validation.

```sh
PYTHONPATH=/reviewed/prs/src python3 -m project_record inspect-inputs --root /host/declared-records --selection /host/inspector-selection.json --observed-at 2026-11-05T14:00:00Z
```

The selection file is limited to128KiB. Each declared regular file is read once, up to2MiB; oversize input is reported without a fabricated full digest. Strict UTF-8 JSON rejects duplicate members/nonfinite values. A supplied expected digest mismatch stays a conflict. The limits belong to this initial local tool, not the record contract or a promise that every larger project fits.

Diagnostics distinguish missing, unavailable, unsafe/nonregular paths, malformed JSON, unsupported kind/version, invalid record/shape, digest conflict, oversize and validation-unavailable. A valid-shaped large dependency chain can exhaust the existing recursive core validator; that row remains unknown and later rows still run. No new second validation engine is introduced. A malformed/deep/oversized selection is rejected before data inspection.

Exit0 means the nonempty **selected set** was inspected with the stated validation limits. Exit3 means partial/unsupported/empty coverage; exit1 means an invalid selection/command failure. None means that every repository JSON file or planned inspector view is covered. Diagnostics include observed-byte hashes and per-row `contentRead`, never input bodies. Unselected coverage is always Not inspected, not zero. No data file is changed.

## Privacy, authority and handoff

The report is an **owner-local diagnostic** with `publishable:false`. Declared private files may be read only when the host explicitly selects them under its actual authority. Paths, stable IDs, audience labels and digests can themselves be sensitive. There is no public export mode, automatic issue submission, privacy certification, owner acceptance or permission upgrade here. Do not publish this diagnostic because it looks like JSON metadata. #19 must implement/test the public projection contract; #18 must keep raw/owner context separate while building views.

Filesystem names/symlink checks prevent ordinary accidental escape; a cooperating host/local OS owner remains a trust boundary. Observed-byte hashes do not authenticate records or guarantee an atomic snapshot against noncooperating same-user races. The inspector does not execute commands, deserialize code, follow schema URLs or import provider-specific adapters from record contents.

`tests/fixtures/inspector/` includes released-code-produced synthetic record/history/delivery/build/installation samples, stable declarations, old source observation versus a separate render/inspection timestamp, plus missing, malformed, unsupported and undeclared-private cases. Its selection is a test input, not a completed validation report or grant. `templates/inspector-selection.example.json` illustrates that fixture; tailor explicit paths for a real host rather than copying it as a production manifest.

The coverage table remains the pinned #17 inventory. The #18 renderer maps every family to a conditional view or explicit uninterpreted fallback; its mapping does not rewrite historical producer evidence. Raw adapter mapping and full non-record schemas remain unsupported. #19 owns privacy/publication and integration-profile proof. Live runtime sessions (#34), model agreement, adoption, release and milestone acceptance are not inferred from either tool.

## Owner-local offline views · unreleased main

The `inspector` command writes one self-contained `index.html` in a **new** dedicated directory. Open that file directly from disk. There are no external assets, fetches, server, tokens, model calls, browser storage or client write actions. Exact source fragment links, readable records and navigation remain present without JavaScript; the small optional script filters only the declared-file index. Browser Back and reload use native fragments. The renderer uses PRS reference font/palette roles; it does not replace a host site's design or public pipeline.

```sh
PYTHONPATH=/reviewed/prs/src python3 -m project_record inspector --root /host/declared-records --selection /host/inspector-selection.json --observed-at 2026-11-06T00:15:00+01:00 --output /host/private-inspector-new --owner-local
```

**This differs from `inspect-inputs`: it includes the parsed selected contents**, including private JSON and readable unsupported JSON. `--owner-local` acknowledges that output choice; it is not a permission grant. Treat the file like the most sensitive selected input. There is no `--audience public` option. Do not add its output to Pages or public uploads. No generated inspector HTML is included in the source kit or website build. #19 must implement and verify the separate projection/privacy/integration contract before public use.

Views keep source observation, caller-declared render time and supplied inspection clock distinct. Each artifact retains its selected path, digest and status. Claims link to in-document JSON Pointer fields in the exact selected input; the digest identifies exact selected bytes, while the page displays parsed JSON values. Strings use inert JSON escapes, null differs from a missing field, and numeric literals follow Python JSON parsing (floating-point literals can round or underflow). Input URLs, schema references, personal memory, manifests and filesystem paths are never followed or activated. Artifact and work IDs remain distinct. Multiple snapshots of the same work are separate observations, with no cross-file credited total.

| View | Interpretation and limits |
| --- | --- |
| Work/milestones | Validated normalized records use shared `summarize`; cached metrics are ignored. Containment fields and prerequisite links remain distinct. Criteria, owners, state, completion basis, evidence and source fields stay nearby. Acceptance follows the declared existing rule. |
| Provenance | Selected source/manifests/build identities; declared authority and references are not authenticated or followed. |
| Discovery | Explicit `discovery` entry point: projectId, sources, cleanupQueue, unresolvedDecisions. Shape-only structured coverage/findings/action/decision values. |
| Readiness | Explicit `readiness-assessment`: recordKind=repository-readiness-assessment, readinessLevel, dimensions, autonomy. Shape-only; no new level, risk or authority calculation. Normalized governance remains supplied context; additional embedded history/discovery/operations fields get separate shape-only labels, or an unvalidated fallback when their mapped shape is absent. |
| Evidence | Existing work evidence, or explicit `evidence-record` with a receipts array. Supplied subject/revision/kind/result retained; shape recognition is not verified proof. |
| History | Exact supplied snapshots/comparisons and coverage. Unknown intervals stay unknown; standalone history metrics are supplied observations, not recomputed from missing source snapshots. |
| Delivery | Validated record candidates use shared `delivery_summary`; candidate gates, changes, publications and deployments are separate. Standalone delivery projections are labelled supplied/shape-only. |
| Operations | Suite/install receipts, or explicit `collection-observation` with projectId/status/attemptedAt/source/coverage. Failed/partial attempts remain distinct from last successful source dates. No external collector, runtime activation or health check is performed. |
| Uninterpreted | Other declared strict JSON, unsupported versions or invalid mapped shapes. Exact safe fields remain readable without semantic promotion or work credit. |

The four added assessment kinds are recognized **only by the HTML builder**, under explicit declarations and entry-point shape checks. The metadata-only diagnostic's seven-kind boundary and refusal to read unknown bodies remain unchanged. Generic future receipts, raw ledgers, native snapshots and other unmapped families remain uninterpreted even when their text claims approval. No field or kind is guessed from a filename.

Both tools retain 128 declarations and 2MiB/file. The HTML builder additionally limits selected reads to16MiB plus a single overflow-detection byte, source rendering to5000 nodes/depth64 per file, individual keys to2048 characters, string values to32768 characters, and cumulative pointer/value representation cost to512KiB/file. Resource refusal is `set-limit` or `render-limit`, without a misleading partial body; later rows continue where budget permits. HTML expansion is capped incrementally at4MiB per rendered subtree/view and32MiB/page; an expansion refusal aborts the command before creating output and asks for a narrower selection. Work receipts are linked rather than copied into every candidate. A final guard also refuses output above32MiB before writing. Unrenderable Unicode content becomes a per-file unknown state; malformed Unicode declarations fail preflight. New POSIX output uses an owner-only directory0700 and file0600 even under a permissive umask; non-POSIX host ACLs remain the host responsibility. Existing output directories and symlinks are refused; rendering finishes before a new directory is created. Output writes never edit source records. Local same-user races remain a host trust boundary.

Exit0 means a nonempty selected set was rendered with its stated validation limits; exit3 means partial/unsupported/empty coverage. Exit1 is a command or output failure. None establishes owner acceptance, schema authentication, publication, freshness or complete repository coverage. `tests/fixtures/inspector-views/` supplies synthetic shape-only assessments and copied pinned released samples for all view roles; these are test inputs, not real adoption receipts or a public inspector export.

Verification records distinguish static/DOM checks from actual browser, reflow, native zoom and screen-reader observations. The historical reference-view accessibility results do not transfer to this new page. Native tests blocked or not performed remain not-tested, and #19 must prove the actual integrated profiles.

## Managed profiles and reviewed public fields · unreleased main

`inspector-profile` adds preview, explicit `--write`, and read-only `--check` around two fixed generated files: `index.html` and `inspector-output.json`. The older `inspector --owner-local` command still requires a new directory and includes parsed private contents; it has no public mode.

```sh
PYTHONPATH=/reviewed/prs/src python3 -m project_record inspector-profile --root /host/records --selection /host/selection.json --output /host/private-view --observed-at 2026-11-06T10:00:00+01:00 --profile private-offline --audience owner --check
```

Without `--write` or `--check`, the command previews whether output would change. A missing output is stale. Check returns1 for stale bytes and never writes. Reuse the same explicit observation clock to compare the same build; rebuilding never refreshes source dates. Exit3 retains partial owner-local input coverage. An explicit write regenerates only these owned outputs, refusing unrelated neighbors, symlinks, mismatched ownership/profile and source/config/review/brand collisions. The ownership receipt declares a generated namespace; it is not actor authentication. POSIX output is0700/0600; host ACLs and cooperating local-owner behavior remain host responsibilities. Per-file atomic replacements plus parity detection make interruption between replacements detectable and recoverable; no multi-file atomic transaction is claimed. Unexpected temporary neighbors after a hard process kill are refused for explicit inspection. Review/brand/ownership inputs must be regular bounded JSON objects with explicit node/depth/text limits, independent of the Python decoder’s recursion behavior.

### Public review boundary

Public output is initially limited to **normalized project-record**. Other families stay owner-local; there is no public uninterpreted fallback. A public declaration alone is insufficient. Private declarations and unmapped kinds are refused before content reads. Existing public export validation also refuses private project/inputVisibility values. A structural allowlist then retains only contract/project/source/work/group/milestone fields and typed evidence metadata. It removes extra memory, notes in unsupported extensions, cached metrics, governance, history, delivery, operations and other unimplemented channels. Public view coverage explicitly names these omissions. Work IDs, criteria, prerequisites and source acceptance rules keep their existing meanings; the shared core recalculates metrics.

A separate host-adopted review must bind each selected artifact ID, the exact raw SHA-256, and every published primitive or empty-container JSON Pointer. Missing/stale/mismatched reviews fail before output writes. Wildcards, whole-subtree shortcuts, extra unknown pointers and omitted published fields are refused. Raw path and arbitrary render/producer metadata from the selection are not copied; public artifact locators use their reviewed ID. Source locators inside the normalized record remain explicitly reviewed data. Unsupported extensions are stripped even if they appear in the original file; changing any input bytes still invalidates the digest review.

```json
{"publicReviewVersion":1,"reviewer":"Host-designated reviewer","decisionSource":"Actual host decision/evidence location","records":[{"id":"REC","sha256":"exact lowercase SHA-256 of reviewed input","pointers":["/contractVersion","/project/id","all other explicitly approved published leaf pointers"]}]}
```

This abbreviated example is not a valid approval. The synthetic complete test review is in `tests/fixtures/inspector-public/review.json`. `public_field_pointers` can enumerate the structurally projected field set; enumeration is not review, permission or an automated secret audit. Reviewer/decision attribution is host-supplied and not authenticated by PRS. The host must adopt the review independently of untrusted input content. Do not generate approvals from record prose or treat a forged attribution as a real owner decision. A private source needs a separately authored/reviewed public source; this command does not declassify private inputs.

```sh
PYTHONPATH=/reviewed/prs/src python3 -m project_record inspector-profile --root /host/public-records --selection /host/public-selection.json --review /host/adopted-public-review.json --brand /host/brand.json --output /host/owned-inspector-route --observed-at 2026-11-06T10:00:00+01:00 --profile host-branded --audience public --write
```

`publishable:true` means the selected reviewed projection passed this bounded contract. It is not publication, full privacy certification, outcome acceptance, native-runtime activation or permission to deploy to a new destination. Text remains escaped, URLs remain inert source strings, and schema/manifest references are never followed. The page has no network, model, browser storage or source-write path. Public source field pointers describe the parsed projection; the input digest identifies the reviewed original bytes, including omitted fields. Parsing/Unicode/size limits from the owner-local reader remain explicit.

### Three integration profiles

| Profile | Supported integration and verification boundary |
| --- | --- |
| README-only | Reuse `readme-profile` and `presentation.renderer: readme`. Preserve authored text/brand/source identities and check README/SVG parity without producing HTML or configuring Pages. The inspector does not override that choice. |
| Host-branded | An explicitly owned sidecar route can inherit a strict host brand token file. Local system/serif/mono stacks and six-digit palette values prevent arbitrary CSS or remote fonts. The host keeps its existing shell, navigation and deployment writer. This profile does not inject a compulsory dashboard into the host or claim arbitrary inline integration support. |
| Private-offline | Owner-local managed HTML retains full bounded views and error states. It requires no Pages, server, login or model. Its file and receipt remain private; it is never an input to the public site builder. |

Brand tokens use `brandVersion:1`, a short escaped `name`, `font` (`system`, `serif`, `mono`) and `light`/`dark` objects containing `background`, `text`, `link` as explicit six-digit hex values. Tokens do not themselves certify contrast; test the rendered cascade. The synthetic public fixture's brand differs from the PRS shell without modifying its navigation or application version.

The canonical website's isolated `qa/inspector/index.html` route is generated only from the checked-in authored toy record and its exact review; it never reads a user's owner-local output or a supplied review directory. Private/offline fixtures are excluded from this site path. This public integration surface is distinct from the earlier blocked local file inspection, with no private context made public. Whole #19 completion still requires named browser observations and a reviewed disposition of their actual limits. A passing DOM test or this public test page cannot invent private file-opening, native zoom or screen-reader evidence.
