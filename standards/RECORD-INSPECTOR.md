# Declared record inventory and inspector coverage

PRS emits several JSON families and consumes others. A file extension, title or successful JSON parse cannot establish its schema, audience, authority or freshness. This inventory prepares the unified offline inspector (#18); it does not implement that UI or the publication/integration gate (#19).

## Producer evidence and ownership

The [machine-readable coverage table](https://github.com/interzettel/project-record-standard/blob/main/standards/inspector-inventory.json) names29 reviewed families with paths, producer/adapter, released versus main-only availability, source/derived writer, sensitivity, actual schema/unsupported status and planned inspector view. Its path patterns explain producer destinations; they are **not scan instructions**. Only a separate explicit selection lists files to inspect.

Released baseline: v0.4.1 at `ebc6afb0b977ff3d7605893c73ac63021775c4d3`. Main-only additions were inventoried at `4030b63c3cf6487ae7ea659be8d6962e795a16f5`. Main still carries package/suite0.4.1 metadata, but that does not make new code part of the immutable published release. This package's new inventory diagnostic is explicitly unreleased.

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

The coverage table is the handoff to #18. Still unresolved there: typed/raw adapter source views, non-record schemas, safe source/edit/declared-error navigation, actual interaction/keyboard/reflow behavior, and how views label shape-only validation. #19 owns privacy/publication and integration-profile proof. Existing reference README/Pages views remain available. New UI, full JSON-family support, live runtime sessions (#34), model agreement, adoption, release and milestone acceptance are not inferred from this inventory.
