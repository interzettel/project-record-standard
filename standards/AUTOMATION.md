# Reusable automation

The root `action.yml` executes `tools/run_action.py`, the same entry point used locally. With Python 3.10 or newer, it validates local sources and generates normalized records, history, release readiness, a changelog and matching README output. It needs no runtime dependencies or token and makes no network request or GitHub write.

## Installation and reproduction

Vendor the versioned public toolkit under `tools/project-record-standard/`. Copy `.github/workflows/record-build.yml` to the consuming repository's workflow directory and adapt the caller example under `templates/.github/workflows/`. The reusable workflow uses the calling repository's checkout and the same vendored Python entry point. Its `toolkit-path` defaults to `tools/project-record-standard`; this standards repository passes `.` to verify itself. The root composite action is exercised separately by the canonical CI workflow. It does not assume that calling a workflow checks out the standards repository. A remote action reference can be introduced after the real standards repository and immutable release exist.

Do not vendor the owner-review bundle or private source fixtures into a public repository. Keep the toolkit version/checksum in the dependency record. Reuse existing site builds and the accepted generated-file policy instead of installing competing jobs.

```sh
PROJECT_RECORD_CONFIG=examples/projects.json PROJECT_RECORD_OUTPUT=/tmp/record-check PROJECT_RECORD_ONLY=prehnite PROJECT_RECORD_AUDIENCE=public python3 tools/run_action.py
```

Use a new or empty output directory for public builds. Audience and render-preparation checks run before any generated output is written. A private supplement makes the projection private even when the repository is public. Input observation dates remain unchanged by regeneration.

## Authored change fragments

List individual JSON fragment files under a manifest entry's `changeFiles`, with each file's visibility, authority and observation date. Each fragment uses the shape in `templates/change.example.json`. The pipeline collects them deterministically and rejects duplicate IDs or a competing `changes` writer. Publication records refer to those IDs; unshipped fragments remain in Unreleased. The standard example uses four authored fragments.

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
