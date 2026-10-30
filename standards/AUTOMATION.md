# Reusable automation

The root `action.yml` executes `tools/run_action.py`, the same entry point used locally. With Python 3.10 or newer, it validates local sources and generates normalized records, history, release readiness, a changelog and matching README output. It needs no runtime dependencies or token and makes no network request or GitHub write.

## Installation and reproduction

Vendor the versioned public toolkit under `tools/project-record-standard/`. Copy `.github/workflows/record-build.yml` to the consuming repository's workflow directory and adapt the caller example under `templates/.github/workflows/`. The reusable workflow uses the calling repository's checkout and the same vendored Python entry point. Its `toolkit-path` defaults to `tools/project-record-standard`; this standards repository passes `.` to verify itself. The root composite action is exercised separately by the canonical CI workflow. It does not assume that calling a workflow checks out the standards repository. A remote action reference can be introduced after the real standards repository and immutable release exist.

Do not vendor the owner-review bundle or private source fixtures into a public repository. Keep the toolkit version/checksum in the dependency record. Reuse existing site builds and the accepted generated-file policy instead of installing competing jobs.

```sh
PROJECT_RECORD_CONFIG=examples/projects.json PROJECT_RECORD_OUTPUT=/tmp/record-check PROJECT_RECORD_ONLY=prehnite PROJECT_RECORD_AUDIENCE=public python3 tools/run_action.py
```

The action requires a new or empty dedicated output directory for either audience, so an artifact upload cannot collect unrelated pre-existing files. Public CLI builds also require a new or empty output directory. Audience and render-preparation checks run before any generated output is written. A private supplement makes the projection private even when the repository is public. Input observation dates remain unchanged by regeneration.

## Authored change fragments

List individual JSON fragment files under a manifest entry's `changeFiles`, with each file's visibility, authority and observation date. Each fragment uses the shape in `templates/change.example.json`. The pipeline collects them deterministically and rejects duplicate IDs or a competing `changes` writer. Publication records refer to those IDs; unshipped fragments remain in Unreleased. The standard example lists its authored fragments explicitly in the manifest.

## Host website and README

Set `presentation.renderer` to `host` to emit data and README output without a replacement page. The adapting agent connects `record.json`, `history.json` and `delivery.json` to the existing site or the optional `mountExplorer` and `mountDelivery` components. Set the real `presentation.progressUrl` before publishing navigation.

Preview a marked README update:

```sh
PYTHONPATH=src python3 -m project_record readme --file README.md --module .project-record-build/example/README-module.md
```

The command writes only with `--write`; missing, repeated or reversed markers fail. The repository's generator-owner rule still applies. The action never commits files or pushes branches.

## Pages and other hosts

The pipeline produces artifacts. The existing website workflow owns deployment: copy reviewed public data into its existing route, run its normal build, then use its Pages or other host deployment steps. The tracking action needs only read access. Do not upload the owner-review `dist/` as a public Pages artifact. The example workflow uploads a private-to-the-repository build artifact; it does not publish a website.

On failed source reconciliation, preserve the last successful snapshot with its observation date and failure/coverage state. Do not replace inaccessible facts with zero or the current build time. External reconciliation remains a separate bounded integration, not a background write loop in the browser.

## Workflow provenance and verification boundary

Official GitHub action refs resolved on 22 October 2026: checkout v6 at `d23441a48e516b6c34aea4fa41551a30e30af803`, setup-python v6 at `ece7cb06caefa5fff74198d8649806c4678c61a1`, upload-artifact v4 at `ea165f8d65b6e75b540449e92b4886f43607fa02`. Updates require review.

Primary references: [composite actions](https://docs.github.com/en/actions/tutorials/create-actions/create-a-composite-action), [workflow metadata](https://github.com/github/docs/blob/main/content/actions/reference/workflows-and-actions/metadata-syntax.md), and [custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). The executable local action path can be verified without hosted execution; a GitHub run and deployment remain distinct observations.

## Accessibility regression checks

Run `npm ci --ignore-scripts --no-audit --no-fund`, then `npm test`. The locked development-only DOM environment checks mounted announcements, search/focus continuity, filtered-item closure, map/list state parity and default colour contrast. These tests do not render layout or exercise screen-reader speech. The generated `/qa/accessibility.html` fixture loads the real public pages at selected CSS widths and applies explicitly labelled text stress for browser review.

## Current development maintenance

The 30 October 2026 refresh uses reviewed full-SHA action pins, Python 3.15.2 and Node 26.13.0 from the version files, with npm lock and hash-pinned site dependency. `.github/dependabot.yml` proposes weekly Actions/npm/pip updates; it does not merge or migrate adopters. The earlier workflow-provenance paragraph is a dated historical observation. Read [architecture](ARCHITECTURE.md) for future after-work adapters and [compatibility](COMPATIBILITY.md) for assessment/application boundaries.

## Opt-in local work-result writer

Unreleased `project_record.reconcile.reconcile(event, profile, apply=False)` and `reconcile_files(event_path, profile_path, apply=False)` implement the bounded #32 local transaction. They share the record/policy/history/build/README implementations. The initial writer supports a selected **normalized-v1** source in an existing manifest. It refuses other source adapters rather than rewriting their native formats. No remote issue update, hook, scheduler, consumer migration or automatic PRS upgrade is performed. #33 owns actual host enforcement; #34 owns lifecycle capture, and #35/#37 own real-session effectiveness/support claims.

```sh
PYTHONPATH=src python3 -m project_record reconcile --event /host/work-result.json --profile /host/adopted-writer.json
PYTHONPATH=src python3 -m project_record reconcile --event /host/work-result.json --profile /host/adopted-writer.json --apply
```

Preview validates and renders in temporary scratch space without changing host sources, output destinations or journal. Apply is a local writer operation under existing host authorization. Relative profile paths resolve from the process working directory, not the event/profile file location. The example templates are synthetic: `templates/work-result.example.json` pins the bundled fixture bytes; `templates/reconciliation-profile.example.json` leaves routine authority **unknown**, so it cannot authorize application. Copy the fixture to an isolated host and adopt the actual policy before testing a write. Do not toggle the example into a policy for a real repository.

| Input | Meaning and boundary |
| --- | --- |
| `eventVersion: 1` | Exact event ID, canonical project/work IDs, expected raw source and manifest SHA-256, immutable artifact revision, result, producer/source/date, summary, typed receipts and discoveries. An event contains no authority or path-selection fields. |
| `reconcileVersion: 1` | Independently adopted host profile: selected manifest/project, separate private journal and owned output roots, audience, attributed routine-recording decision, per-work applicable evidence policies, bounded admission map and optional existing marked README. |
| Completion policy | A completed event needs its configured allOf/anyOf evidence kinds against this exact work/artifact revision. The writer evaluates metadata; it does not run tests, authenticate producers or interpret the criterion prose. Capture verified observations through the host's actual trust boundary. |
| Negative results | Failed, blocked and cancelled **sessions** retain typed work-result evidence without awarding Done. Blocked sets the unfinished leaf's blocked flag. Session cancellation does not cancel a leaf or remove it from the denominator. Existing Done/cancelled/deferred work requires reviewed correction/scope handling rather than routine overwrite. |
| Discovered work | Each proposal has an item plus origin, reason and source. Without an exact host admission it stays proposed in the private journal/result, outside accounting. A grant pins the new ID's required flag, group, milestone and attributed admission source. Admitted work starts backlog with provenance and a visible denominator effect; it cannot arrive Done or alter existing criteria, dependencies, milestones or owner acceptance. |

The host profile is a policy input selected by trusted host code or an operator, protected by the host's file/OS permissions. It is not authenticated merely because its `source` string looks plausible. Never accept the profile from an untrusted event or model output without the host's normal adoption process. A policy-check scope result remains unknown about identity authentication even when this writer finds an explicit matching host admission. The writer records that separate decision; it never changes the check to pass.

### Transaction and recovery

Each selected manifest has one persistent sibling `.prs-lock` file and a temporary `.prs-pending.json` marker. A nonblocking OS advisory lock serializes cooperating PRS writers using that manifest. It is released on process exit. Expected source/manifest hashes and the selected theme/supplement/history input hashes are checked before writing and throughout recovery. The source's parent holds immutable `reconciliation-history/<before-sha256>.json`; the manifest registers those exact before bytes and retains any previous history. The private journal also retains the exact previous metadata/normalized observation, event, profile, plan integrity digest, per-file before/after bytes and eventual result. It is transport/recovery evidence, never another authoritative work ledger.

Apply prepares the recovery marker and journal, preserves the prior raw source, atomically replaces source and manifest files, installs a complete generated-view directory for the event, then updates only the configured README's marked region. File data and supported directory metadata are flushed. Each individual file/directory replacement is atomic on the tested local filesystem; the whole multi-file transaction is **not atomic**. During interruption the marker/journal make partial state explicit. Other events are held until the original event and profile resume. Consumers that require a consistent cross-file view must honor that marker or wait for the writer result; bare readers are not a transaction coordinator.

Retry with the exact event/profile. Each current target must equal its preserved before or planned after bytes. A newer authored edit, changed dependency, corrupted journal or mixed/unowned projection produces a conflict and preserves those bytes. Do not delete the marker, reset the source or replace journal contents to make retry green. Reconcile the conflict through the host's source authority. If the journal cannot be recovered, preserve it and the authored files for a reviewed repair; no automatic rollback discards later work.

An event ID plus matching payload/profile can commit once. Reusing that ID with other data conflicts. A replay of an already committed event returns its historical result, even when later work has advanced the source; it does not rewrite newer facts or pretend to be a fresh observation. A crash after commit but before marker cleanup resumes as a duplicate and clears only its own recovery marker. A crash before the prepared journal is durable can rebuild the plan under the original unchanged preconditions. Temporary staging directories left by a hard process kill are unpublished; cleanup/retention remains host-owned and must not delete journal/history evidence blindly.

| Result / exit | Meaning |
| --- | --- |
| `preview`, `applied`, `duplicate` / 0 | Valid preview, completed transaction, or exact historical replay. `written` distinguishes these. |
| `rejected`, `conflict` / 1 | Invalid required predicate or conflicting source/identity; no certification. A pending conflict may already include partial writes. |
| `invalid-input` / 2 | Unsupported/malformed event/profile/CLI input. |
| `held`, `recoverable` / 3 | Missing authority/evidence, competing writer or interrupted transaction requiring recovery. `recoveryPending` identifies a prepared transaction; `written: null` means partial writes are possible, not that nothing changed. |

Local journal/result data can contain private context and is not an approved public projection. Only the existing public-export guard and explicit selected inputs govern generated public views; there is no content classifier. No journal is included in the public kit or recursively published by this writer.

The tested boundary is cooperating local processes and injected process interruption. Advisory locking cannot stop a noncooperating editor, malicious process or changed host permissions. Rechecks catch observed drift but are not a kernel compare-and-swap against arbitrary external writers. Network-filesystem locking, Windows runtime behavior, sudden power loss, real agent hooks, cross-model evidence and reduced tracking burden require separate actual verification. The Windows lock branch is an implementation path, not a supported-runtime receipt.

## CI data policy and host activation

The unreleased #33 preparation adds `tools/run_policy_ci.py` and a `PRS policy` job. It calls the same `policy-check` CLI through the trusted toolkit. A host-selected ciProfileVersion1 profile declares one manifest/project, visibility, completion evidence policy, protected-path review notices and any previously adopted exact-input scope/acceptance decisions. Candidate files cannot supply that profile. Requests and reports remain separate from record contract0.2.0.

The proposed main-branch checks are `verify`, `reusable / record` and `PRS policy`, bound to the observed GitHub Actions app15368. The activation proposal under `audit/ci-enforcement/2026-10-30/` targets only `refs/heads/main`, requires pull requests with zero mandatory approvals and up-to-date checks, and adds no bypass actor. Zero approval count preserves the solo/agent working model; it is not human approval or independent review. Existing organization deletion/transfer rules remain untouched. **The proposal is not an activated ruleset.** The owner can import [`.github/rulesets/main-ci.json`](../.github/rulesets/main-ci.json) using the [import handoff](../.github/rulesets/README.md). The agent handles read-back, probes and reconciliation; the separate dated checklist is not a ruleset import file. The observed branch was unprotected; the integration could not read administrative protection details, and the browser was blocked by another extension panel.

The workflow uses the base branch's workflow and exact base SHA on pull requests. The candidate checkout is interpreted only as JSON data: no candidate Python imports, tests, installers, hooks, caches or build scripts run in this job. Checkouts do not retain credentials; the job declares contents-read only and references no secrets. Workflows, toolkit, pins, policy and skill changes are reported for review. This is a scoped data gate, not approval of a future replacement workflow or runtime. GitHub administrators who can edit repository policy remain a trust boundary, even with an empty configured bypass list.

Fork input is explicitly held before checkout until a reviewed data-only transport is adopted. This initial profile does not enable checkout's unsafe fork opt-out or claim tested fork support. Missing/unavailable checks and exit3 remain non-successful; they cannot authorize merge after required checks are actually activated. Merge queues are not supported by this profile until their event and check behavior are separately configured/tested. Only the declared main boundary is covered.

GitHub's [current pull_request_target guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) documents a default public-repository event policy, currently in evaluate mode, scheduled for enforcement on 2December2026. Inspect the actual repository/organization event policy before activation. No event-policy opt-out is applied here. Whether this trusted-base, read-only data job should use an explicit narrow allow policy or a different data transport remains an activation decision, with actual capabilities and risks visible. Do not disable platform protections just to make a job green.

The job has no path filters and no continue-on-error. The basic reusable-workflow example also runs without path filters. [Skip instructions](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs) can suppress push/pull_request workflows, leaving required checks pending; pull_request_target is not skipped by those messages. Workflow disablement, event policies, runner outages and alternate branches still need native boundary verification. A successful local unit test or job cannot establish that GitHub requires its result.

### Data checks and authority decisions

The checker reads declared source/snapshot/supplement/change files inside each checkout, rejects symlinks/traversal, and retains the exact ordered prior observations. It compares the current candidate against the trusted base and checks each newly Done leaf's declared implementation revision and evidence against the host completion policy. Empty/missing evidence stays unknown, wrong proof and duplicate credit fail, and changed scope/acceptance cannot silently pass. The immutable base source is the before-write precondition observation; candidate identities are separately computed from actual candidate bytes.

Ordinary unchanged-scope recording needs no new owner prompt. If an actual scope or owner-acceptance decision is needed, the host may adopt an `approvedChanges` entry in its trusted profile **before** evaluating the changed candidate. It binds `beforeCanonicalSha256` and `afterCanonicalSha256` from the report, allowed rules limited to SCOPE/ACCEPT and an attributed decision source. Canonical identities include loaded supplements and their hashes, not only raw ledger bytes. The original policy result remains unknown about identity authentication; the CI report separately records the host's exact-input decision. Failed predicates and missing evidence cannot be exempted. A candidate-supplied profile/decision does not become trusted in its own PR. Updating the trust configuration itself remains a reviewed host operation, with the underlying actor/permissions explicit.

```sh
python3 /trusted/prs/tools/run_policy_ci.py --base /checkouts/base --candidate /checkouts/head --profile /trusted/prs/.github/prs-policy.json
```

Exit0 covers selected data predicates and applicable previously adopted decisions only. Failure exits1, unknown exits3, and parser/shared-request errors exit2. Local diagnostics are not an approved public projection. The checkout/profile selection and GitHub context are supplied by the host; this command does not fetch GitHub settings or authenticate their source.

### Activation and evidence still required

First install/review the workflow without claiming required enforcement. Its initial introducing PR cannot be certified by a base-branch workflow that did not exist yet. After integration, use an isolated, unmerged probe PR to demonstrate rejected duplicate data and corrected data passing through the same trusted-base checker revision. Creating commits through the connector bypasses local hooks but still exercises the server job. Record the actual GitHub revisions/runs and preserve negative results. Do not merge the failing probe into main.

Before completing #33, inspect native rules and event-policy settings, review/apply the narrow activation diff through authorized administration, read it back, and prove the configured merge boundary refuses a nonpassing/unavailable required result. Record configured bypass actors and actual tests or missing coverage for each relevant actor. A current unprotected branch, inaccessible setting or blocked browser is not enforcement evidence. #33 stays incomplete until its actual remaining criterion is evidenced. #34 depends on that result; eligible independent preparation can continue under the existing queue.
