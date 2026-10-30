# Project Record Standard

Know what works, what remains, what changed and what to do next. PRS connects a project's purpose, work, evidence, decisions and delivery history while preserving its own sources and visual identity.

The goal is a reviewed installation followed by automatic routine tracking after an agent works, with clear exceptions and scope-growth history. **That automation is planned.** The available v0.4.1 toolkit provides offline validation, progress/history/delivery projections, eleven guidance skills and an additive installer.

[Start here](standards/START-HERE.md) · [Public guide](https://interzettel.github.io/project-record-standard/) · [Interactive tracker](https://interzettel.github.io/project-record-standard/standard/progress.html) · [Install v0.4.1](INSTALL.md)

## Availability

| Available in v0.4.1 | Proposed next phase |
| --- | --- |
| Stable work IDs, exact fractions and source-backed history | Routine after-work reconciliation with recovery |
| Evidence, acceptance, release and deployment kept distinct | One policy/core used by CLI, host adapters and CI gates |
| Eleven project-tracking skills and owned-file installation | Verified installation pins and compatibility assessments |
| Branded README/static views and public-input boundaries | Measured cross-model/runtime support and quiet feedback |

Local MCP, remote hosting and icon/template improvements are optional work. No VPS or central account is required for core adoption. [Architecture and boundaries](standards/ARCHITECTURE.md) · [Ordered work plan](progress/execution-plan.md)

## Adopt a verified version

Use [release v0.4.1](https://github.com/interzettel/project-record-standard/releases/tag/v0.4.1) and follow [INSTALL.md](INSTALL.md) to verify all downloaded assets and extracted files.

| Identity | Published v0.4.1 |
| --- | --- |
| Source commit | `ebc6afb0b977ff3d7605893c73ac63021775c4d3` |
| Source ZIP SHA-256 | `a46cdcea938eb987b936497a22db8eab07106aad7dd12a8cfe10b4ad41f74607` |
| Skill suite / record contract | `0.4.1` / `0.2.0` |

Keep the verified toolkit and its dependency pin in the project. Give your agent this request:

```text
Read this project's AGENTS.md and the verified PRS toolkit's
skills/use-project-records/SKILL.md. Use the pinned v0.4.1 source kit.
Inspect existing sources and choose establishment or adaptation.
Keep stable IDs, source authority, private memory and project branding.
Prepare or update the overview, scoped work, evidence and useful views.
Use existing task authorization and ask only for blocking decisions.
Report actual checks, scope changes, next eligible work and remaining limits.
Do not claim the planned unattended tracking adapters are installed.
```

Preview the additive installer before applying it. It preserves existing instructions and refuses owned-file conflicts. A host that does not discover `.agents/skills/` needs its own supported entry point. The [compatibility policy](standards/COMPATIBILITY.md) explains exact pins and when to assess, apply or defer an upstream change. New minor/major releases require assessment under the adopted profile; discovery does not silently authorize migration.

## One source for each fact

A project declares whether its ledger, GitHub or another tracker owns each field. Plans explain the work; generated README, SVG and Pages display it. Personal memory, session context, shared knowledge, instructions, plans, decisions and immutable evidence have different homes and lifecycles. [Records and memory](standards/RECORDS.md) describes the researched profile direction.

Any human or model can contribute across disciplines. Temporary responsibility, review lenses and acceptance authority remain explicit. Multiple lenses from one model are not independent agreement. [Work language and open contribution](standards/WORK-MODEL.md)

## Run the current toolkit

The CLI has no runtime dependencies. Development versions are pinned in the repository; the released kit's requirements and verification steps remain in INSTALL.

```sh
PYTHONPATH=src python3 -m project_record check --config examples/projects.json
PYTHONPATH=src python3 -m project_record pipeline --config examples/projects.json --output .record-build --audience public
```

Use a new or empty output directory. For development/site checks, install the hash-pinned `requirements-site.txt`, run `npm ci --ignore-scripts --no-audit --no-fund`, the Python and JavaScript suites, then `tools/build_site.py` and `tools/check_readme.py`. [Automation](standards/AUTOMATION.md) · [Accessibility evidence](standards/ACCESSIBILITY.md) · [Delivery history](standards/DELIVERY.md)

## Improve PRS from actual work

When a real task exposes a shared-standard gap, check existing issues and report the expected rule, observed result, exact known pins, practical impact, safe reproduction and workaround. Keep private context out of public reports. A narrow tested PR is welcome. There is no ticket quota or routine idea-generation requirement. [Feedback contract](standards/FEEDBACK.md)

Weekly dependency proposals keep development pins reviewable; they do not auto-merge. The [release proposal](progress/release-direction.md) separates **0.5.0 foundations** from opt-in automation previews and proven unattended support. Real-session and cross-model evidence remains required for the supported automatic workflow. The source kit is MIT licensed; third-party assets keep their own licences.

## Project progress

The historical release remains 18/18 complete. The expanded plan separates newly required work from deferred ideas; the [overview](progress/overview.md) names both. The following source-derived figures include historical work and the larger current denominator; they do not measure effort or time remaining.

<!-- project-record:start -->
[![Project record standard · current required scope](./assets/progress.svg)](https://interzettel.github.io/project-record-standard/standard/progress.html)

| Measure | Completion | Meaning |
| --- | ---: | --- |
| Required work | 28/42 · 66.7% | Completed leaf items in the named required scope. |
| Accepted milestones | 4/13 · 30.8% | Milestones whose declared outcome gates passed. |

[Interactive roadmap](https://interzettel.github.io/project-record-standard/standard/progress.html) · Source file: `examples/sources/standard/ledger.json` (content-addressed file snapshot).

Observed 2026-10-30 against `7346a4d2`.
<!-- project-record:end -->
