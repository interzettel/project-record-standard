# PRS-INSPECT-02 offline inspector implementation plan

Responsible contributor: Codex, bounded package #18 / M6. The existing issue and execution plan are the design authority; this document details their already authorized implementation. #17 and #6 are complete. Live #34 sessions remain owner-deferred.

## Design

Generate one self-contained owner-local HTML file from explicit declarations. Reuse the bounded reader and shared core calculations. Link summaries to exact in-document JSON pointers with selected-file hashes and separately labelled source/render/inspection times. Static anchors and native disclosures work without JavaScript; a small optional enhancement filters the artifact index without hiding source detail or breaking deep links. No server, fetch, local storage, model, write action or graph dependency in the page. Keep PRS typography and semantic colours; use readable lists, tables and normal scrolling.

A separate-page design would complicate portable file links and require more output management. A client-fetch application would violate direct file opening and add a server dependency. The single-file renderer is the maintainer choice within the existing criterion, not a new owner decision.

The CLI is `inspector --root PATH --selection FILE --observed-at TIMESTAMP --output NEW_DIRECTORY --owner-local`. It explicitly includes selected raw contents, including private inputs and unsupported JSON in a visibly uninterpreted fallback. This differs from metadata-only inspect-inputs. No public output mode exists; #19 is the public/privacy and integration gate. Unknown schema/semantic coverage remains unknown. Input paths are never activated as URLs or followed. A source locator is rendered as text and exact source links are internal.

## Tasks and checks

1. Bounded payload handoff and semantic model (`inspector.py`, new `inspector_views.py`, `tests/test_inspector.py`). Preserve metadata-only behavior; capture each selected file once, capped at2MiB/file,16MiB/set,5000 source nodes/file, depth64. Reuse summarize and delivery_summary for validated records. Explicit shape-only discovery/readiness/evidence/collection views; no inference from filenames, recommendation, merge or failed CI. Unsupported families get fallback/coverage mappings. Red/green tests: incorrect cached metrics, missing/malformed/future/unsafe input, digest conflict, cross-source identity collision, exhausted render budget, unselected neighbor, timestamp separation.
2. Self-contained rendering/CLI (`inspector_views.py`, `__main__.py`, `web/inspector.mjs`, `web/inspector.css`, Python and DOM tests). Every summary and derived value has a source pointer. Raw source values escaped; no data URL/script/path execution. Existing output/input overwrite refused. Red/green tests: source joins, all view roles, hostile payload, output rollback, native anchor persistence, filter focus/no-results.
3. Documentation/package and real rendered inspection (`standards/RECORD-INSPECTOR.md`, `tools/package_standard.py`, package tests). Describe exact supported shapes and boundaries; package assets/fixture. Exercise file opening, desktop/390px, light/dark, doubled text, keyboard and Back/reload where available. Unobserved native zoom/screen-reader speech stay not-tested. No public inspector fixture or pipeline integration before #19.
4. Fresh whole-branch review and applicable full checks, then completion evidence and shared-writer source/history/README reconciliation only if original criterion is met. Required32/42 and retained32/52 are the baseline; milestone acceptance and versions unchanged. Reviewed integration under existing authorization; next #19 after complete.

## Review focus

- A valid record can contain extra fields or hostile values beyond core structural validation; rendering must remain bounded and inert.
- Same project/work identity in multiple declared snapshots must not produce an aggregate credited denominator.
- Shape-only diagnostics and readiness values must not appear authenticated or upgrade authority.
- Broken/deep/oversized input must preserve later rows and readable missing/error states.
- Source anchors must survive direct file opening, filtering and reload without network/module loading.

This is an execution document, not a parallel completion ledger. Actual checks and findings belong in dated evidence; source facts remain in the canonical ledger.
