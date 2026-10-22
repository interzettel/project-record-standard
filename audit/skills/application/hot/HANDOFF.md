# Loomglass ownership and recovery handoff

As of 2026-10-22, local preparation is verified. Sam owns project acceptance, scope decisions, collection retrieval and recovery. The native plan remains completion authority. The tested source revision is `17a9314a06e339c87b247db805be30b6d84f1c9c`, source SHA-256 `77dfd50ba719b8ec64e018444aeb2211f1364bd97118f5b8b9c04f179f3659ca`. The five original files and all local Git refs are unchanged. Toolkit 0.2.0 effective bytes are pinned in `progress/toolkit-pin.json`; its Git HEAD alone is insufficient because that checkout was modified.

| Artifact | Responsibility / use |
| --- | --- |
| legacy/plan.json | Native completion, IDs, source states, exclusions and roadmap gates; Sam authorizes substantive changes. |
| README.md, docs/brief.md, site/index.html, AGENTS.md | Original project-owned content; preserved byte for byte. Do not regenerate these files. |
| progress/overview.md, discovery.json, adoption.md | Local planning handoff, evidence coverage, field mapping and cutover limits. Sam reviews unresolved product decisions. |
| progress/project-record.json, governance.json, theme.json | Authored adapter configuration, proposed WBS/authorities and observed existing brand. Keep one writer per field. |
| progress/derived/** | Pipeline-owned, private derived preview only. No replacement page or public route is connected. |
| progress/evidence/** | Native counts, actual command results, repeat/recovery evidence and preserved failed pin attempt. Do not treat output generation as new source observation or product evidence. |
| progress/rollback/** | Immutable pre-adaptation source copies, source digests and complete available local Git bundle. No prior manifest or generated tracker existed. |
| tools/project-record-standard/** | Exact owned runtime, five web assets and used reference snapshot. Update only through a deliberate pinned upgrade. |
| progress/verify.py | Offline source/count/identity, repeat-run and recovery verification. It makes no hosted call. |

Run the complete local verification from the project root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 progress/verify.py
```

It verifies original file hashes, source HEAD/refs, rollback bundle, exact toolkit hashes, all native-to-projected leaves and exclusions, one WBS owner per leaf, independent 4/6 and 5/8 fractions, native milestone gates, private export refusal and external collection `not-reconciled`. It runs `adoption-plan`, `check`, `status`, two canonical empty-directory builds and one owned-runtime recovery build. The three build trees must be byte-identical. A repeat checks the existing derived tree instead of overwriting it. Temporary build path names are normalized in the saved command receipt; every actual build uses a fresh empty destination.

If the external canonical checkout is unavailable, explicitly select the owned recovery snapshot:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 progress/verify.py --toolkit tools/project-record-standard
```

Do not change source dates or relax pin checks to make a failed run pass. Toolkit/reference drift needs a separate reviewed pin update, retained previous observation and rerun. A source change needs a new explicit source observation and before/after denominator bridge while keeping the old snapshot reachable. The first reference-drift failure during this preparation is retained in `progress/evidence/failed-pin-attempt.json`.

For damaged derived output, preserve the damaged tree for inspection and build into a **new, empty** path. Run from the owned toolkit root (`tools/project-record-standard`):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m project_record adoption-plan --config ../../progress/project-record.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m project_record check --config ../../progress/project-record.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m project_record pipeline --config ../../progress/project-record.json --output ../../progress/recovery-new --audience owner
```

`progress/recovery-new` must not contain existing files. Compare the rebuilt file hashes with `progress/evidence/verification.json` before replacing only the owned `progress/derived` tree. Preserve the last successful output if the source cannot be read or a comparison fails. Never reset `legacy/plan.json` or create a second ledger to repair generated output. The retained bundle can reconstruct the old repository in an empty recovery directory; it is not permission to reset current work. No original source restoration was needed in this application.

For rollback of the additive preparation, stop consuming `progress/project-record.json` and remove only the newly created progress/toolkit-snapshot paths after preserving the immutable bundle elsewhere when needed. The original README/site are still the live local presentation, so there is no renderer or route switch to reverse. No external effects need reversing. Review any difference before restoring an original file from `progress/rollback/original/`.

Sam's next product action is to clarify LG-5 and LG-6 acceptance criteria and dependency order, confirm the proposed WBS/users, and decide what owner acceptance requires. Retain LG-7 and LG-8 outside the six-leaf required denominator. Native gate completion is 1/3; Sam acceptance is unknown, with no attributed approvals or approved baseline. The private generated SVG/README label native gates as accepted according to the adapter and must not be integrated unchanged as an owner-acceptance measure.

There is no remote. Last successful local observation: 2026-10-22; one source snapshot and one reachable local commit. Last successful hosted observation: none. Hosted totals, pages expected, PR/issue/Project/release/CI/deployment status remain unknown. Retrieval owner: Sam. Retrieval action: provide a real hosted identity/access if wanted; then inventory all pages, preserve stable IDs, inspect leftover work and retain failures/partial pages without overwriting the successful local counts. Hosted inventory and writes remain unavailable in this handoff.

Before any public or site cutover, Sam reviews an explicit public projection and the acceptance label, then verifies the unchanged brand/route integration at desktop and 390px, 200% text zoom, keyboard operation, contrast and actual screen-reader output. None of those acceptance observations is supplied by JSON validation or the offline build. No website, README cutover, workflow, schedule, credential, release, external write or deployment was performed.
