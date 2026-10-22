# Project record standard

Shared work terminology, explicit percentages and traceable delivery. Each project keeps its brand, fonts, colours and website.

[Interactive example and guide](https://interzettel.github.io/project-record-standard/) · [Start here](standards/START-HERE.md) · [Hosted checks](https://github.com/interzettel/project-record-standard/actions/workflows/ci.yml)

<!-- project-record:start -->
[![Project record standard · current required scope](./assets/progress.svg)](https://interzettel.github.io/project-record-standard/)

| Measure | Completion | Meaning |
| --- | ---: | --- |
| Required work | 14/16 · 87.5% | Completed leaf items in the named required scope. |
| Accepted milestones | 2/4 · 50.0% | Milestones whose declared outcome gates passed. |

[Interactive roadmap](https://interzettel.github.io/project-record-standard/) · Source file: `examples/sources/standard/ledger.json` (content-addressed file snapshot).

Observed 2026-10-23 against `ac63312d`.
<!-- project-record:end -->

## What this repository supplies

- A JSON contract for scope, leaf work, milestones, evidence, risks, history, release plans and observed delivery.
- Calculation rules with named denominators, exact fractions and explanations for scope changes.
- Optional browser explorers, a brand-owned reference page and a generated README graphic.
- A Python CLI, composite action, reusable workflow, issue template and label vocabulary.
- Ten agent skills for scouting/setup, adaptation, scope, progress, status, GitHub, delivery, presentation and operations, with an additive rules installer.
- A tailored mapping to public PMI guidance, with stated evidence and compliance limits.

The standard's own tracker includes canonical delivery and pending acceptance. The Prehnite example uses its stated pinned public source; it does not replace Prehnite's website or claim to be a live feed.

## Run the public example

Python 3.10 or newer is required. The tracking runtime has no third-party dependencies.

```sh
PYTHONPATH=src python3 -m project_record check --config examples/projects.json
PYTHONPATH=src python3 -m project_record pipeline --config examples/projects.json --output .record-build --audience public
```

To build the documentation website and run all checks:

```sh
python3 -m pip install --require-hashes -r requirements-site.txt
PYTHONPATH=src python3 -m unittest discover -s tests -v
node --test tests/metrics.test.mjs
PYTHONPATH=src python3 tools/build_site.py --records .record-build --output .site
```

The Markdown package is a build dependency for the documentation, not for the tracking runtime. Public output directories must be new or empty. Open `standard/progress.html` in the record build for the standalone tracker, or serve `.site/` as a static website.

## Adapt without replacing the project

Use `presentation.renderer: host` to produce data and README output for the existing website. Preserve source IDs, acceptance authority, issue history and the brand. Reconcile before/after counts before a cutover.

Read [terminology and calculations](standards/STANDARD.md), [GitHub integration](standards/GITHUB.md), [automation](standards/AUTOMATION.md), [adaptation profiles](standards/ADAPTATION-PROFILES.md), [PMI alignment](standards/PMI-ALIGNMENT.md), and [upgrade notes](standards/UPGRADING.md).

The agent suite is versioned under `skills/`; [Agent workflows](standards/AGENT-WORKFLOWS.md) explains setup, scouting, growing scope and installation. Individual repository migrations remain a separate phase. Runtime checks cannot authenticate a human approval. Repository creation and successful CI do not award owner acceptance. [Delivery evidence](standards/DELIVERY.md) and [accessibility evidence](standards/ACCESSIBILITY.md) distinguish observed results from pending verification.
