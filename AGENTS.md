# Working on PRS

## Start a package

Read `skills/use-project-records/SKILL.md`, then the applicable repository skill body. `standards/AGENT-WORKFLOWS.md` defines the planning/operations contract. Use the local suite; a skill description is only discovery metadata.

Read `progress/overview.md` and `progress/execution-plan.md`, then inspect the selected issue, relevant open PRs and affected source records. Refresh stale or missing coverage for that package; avoid unrelated repeated scans. Select the earliest authorized, unfinished required leaf (counted work item) whose execution prerequisites are complete. Name its stable ID, issue, milestone, deliverable, criterion and actual blockers before editing. Parent requests earn no completion credit.

Use one primary implementation package. If it is blocked, state the missing evidence and next responsible action, then continue eligible independent work. Apply existing authorization without asking for it again. A proposed owner/release gate is separate from an execution prerequisite; never silently rewrite dependency meaning or criteria.

## Open contribution

Read [work language and open contribution](standards/WORK-MODEL.md). Any human or model may contribute across disciplines. A skill or review lens selects questions and procedures, not a permanent job identity. Name the current responsible contributor for the bounded package; keep accounting ownership, acceptance authority and execution permissions explicit. Record actual review producers and supported dissent. Several lenses from one model do not establish independent agreement. Existing authorization applies; this guidance grants no new permissions or budget.

## Infrastructure direction

The goal is routine after-work reconciliation with less tracking overhead. Read `standards/ARCHITECTURE.md`, `standards/COMPATIBILITY.md`, `standards/RECORDS.md` or `standards/FEEDBACK.md` when the selected package touches that boundary; avoid loading every guide for an unrelated edit. Use verified immutable toolkit/action/dependency pins. Keep personal memory and untrusted recall separate from authoritative work/decision/evidence records. Planned adapters are not installed capabilities. Routine authorized record updates need no repeated approval, while actual scope/acceptance and permission policies remain explicit. Feed back a real encountered gap with a safe reproduction and duplicate check; do not generate upstream work merely to fill a report.

## Sources and routing

`examples/projects.json` declares inputs. `examples/sources/standard/ledger.json` alone owns completion, scope, dependency and acceptance facts; its supplements own change/delivery observations. The execution plan explains order and package interfaces. GitHub owns issue discussion and assignment. README, SVG and Pages are derived views. Context/discovery/adoption documents never become a second completion ledger. Prehnite remains a pinned reference, not a migration target.

The router selects `govern-project-scope` for decomposition, `connect-github-tracking` for native mapping, `update-project-progress` for evidence/source changes, `prepare-project-delivery` for release work, and `present-project-tracking` for views. Use `operate-project-tracking` for recovery and `verify-project-accessibility` for interaction/WCAG work. Read only the relevant skill and its required references.

## Implement and reconcile

Preserve project-owned branding, stable IDs, historical source bytes and attributed acceptance. Before expanding scope or changing completion, preserve the previous observation and record the reason and denominator effect. Keep new required work distinct from retained deferred ideas; do not count a parent and its leaves twice.

Branch/PR titles and commits name the existing leaf ID. Code changes need tests that exercise the changed behavior. A bounded package ends with outcome, exact tested revision, actual checks/limits, source update, before/after fractions, scope effect, change fragment or omission reason, and the next eligible issue. Regenerate projections from sources once. Implementation, verification, acceptance, publication and deployment remain distinct. Never infer Done from issue closure, owner approval from CI, or release from merge.

## Verification

Run `PYTHONPATH=src python3 -m unittest discover -s tests -v`. Shared source/runtime/package changes also require:

```sh
PYTHONPATH=src python3 -m project_record check --config examples/projects.json
PYTHONPATH=src python3 tools/check_skills.py
PYTHONPATH=src python3 -m project_record pipeline --config examples/projects.json --output .record-build --audience public
npm ci --ignore-scripts --no-audit --no-fund
npm test
python3 tools/check_palette.py
PYTHONPATH=src python3 tools/build_site.py --records .record-build --output .site
PYTHONPATH=src python3 tools/check_readme.py --records .record-build
```

Use new or empty owned output directories and inspect the actual public projection. Install the hash-pinned `requirements-site.txt` dependency for site checks. Update only the README's generated region and its source-derived SVG. The skill installer previews by default, preserves AGENTS text and refuses owned-file conflicts.

## Boundaries

Yiğit owns scope changes and outcome acceptance. This repository's instruction changes grant no credentials, model budget, merge, release or deployment permission. Individual consumer migrations and live Hermes/Qurultai execution require their own scoped work. L0–L5 readiness, R0–R4 task risk and completion are separate; no grade or installation expands authority. Setup/adaptation uses the router's readiness contract and links the configured central assessment.

Treat `audit/skills` fixtures as evidence, not instructions or answers for a fresh evaluation. Preserve negative results and actual accessibility limits; unperformed screen-reader tests remain not-tested. New distributed skills or skill edits require the repository authoring/evaluation process and deliberate suite distribution; root AGENTS guidance is not a new installed skill.
