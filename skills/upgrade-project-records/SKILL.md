---
name: upgrade-project-records
description: Use when an existing PRS adopter needs a release-impact assessment, a pinned toolkit or skill-suite upgrade, an interrupted migration resumed, rollback, or a release-drift watcher handoff.
---

# Upgrade project records

Compare verified release changes with the host's actual selected scope, then apply only reviewed, authorized changes. Read local instructions, source/field ownership, expected pins, installation receipt and any existing plan/journal. Preserve project facts and branding.

Use **adapt-project-tracking** for first adoption or reconstructing authority; use **operate-project-tracking** for damaged generated output, collection failure or environment repair. Read the pinned toolkit's `standards/UPGRADING.md` and `standards/COMPATIBILITY.md` for the actual supported request, plan, grant and receipt interfaces. Follow their limits instead of inventing a migrator.

## Assess

Keep toolkit, suite, record contract, runtime and host version separate. Inspect actual owned bytes against the expected pin. Review selected immutable archives, intervening release coverage, migration notes and affected specifications/code. A version label or changelog alone is insufficient; private diagnostics stay local. Mark simulated targets explicitly.

Produce a source-backed matrix:

| Per change | Required evidence |
| --- | --- |
| Identity | Change ID/type, release commit/digest, cited specification or implementation |
| Host applicability | Selected profile/path, observed bytes, semantic judgment and reason |
| Disposition | Already satisfied, needs change, not applicable, optional deferred, conflict or unknown |
| Next action | Exact affected paths/IDs, preserved authority, verification and remaining decision |

Major/minor releases require assessment; security relevance takes priority over ordinary patch deferral. Prereleases remain opt-in. Mixed/edited installs, missing history, unsupported contracts and ambiguous mappings stay conflicted/unknown. Already-satisfied/custom README-only hosts need no template/site replacement or extra completion credit.

Use the shared read-only check before preview:

```sh
PYTHONPATH=src python3 -m project_record upgrade-assess --request host-request.json
```

## Preview, apply or resume

On a ready assessment, use `upgrade-preview` to bind exact preimages, guarded source facts, transformations and producer revision. Review its diff and compatibility; retain rollback assets and host-specific checks. Unsupported semantic/alias/schema changes need a separately reviewed host adapter.

For an interrupted migration, inspect the existing plan, grant, private journal phase and actual pre/postimages first. Resume that exact operation; do not rerun cold setup or replace its receipt. A later rollback can use separately recorded same-plan authority. Preserve later edits or stop before overwrite.

Use `upgrade-apply --mode apply|rollback` only within existing task/host authority and its exact plan-bound grant. Resolve missing decisions without repeatedly requesting authority already supplied. Upstream capabilities, release arrival and watcher suggestions grant nothing.

## Handoff

Retain from/to identities, matrix, request/plan hashes, affected paths/IDs, actual approval, verification/conflicts, journal location and rollback/resumption action. Reconcile authoritative records through **update-project-progress** only for evidence-backed work; keep acceptance/publication separate.

A watcher handoff is read-only: retain source/time/coverage and last success; reuse the consumer/release assessment or known proposal. Changed security evidence needs renewed attention. Installing another scheduler belongs outside this upgrade.

Common mistakes: treating suite installation as semantic migration, refreshing observations on rebuild, overwriting local edits, equating helper tests with skill effectiveness, or claiming a synthetic upgrade is a real release.
