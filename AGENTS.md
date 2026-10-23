# Working on the standard

Preserve project-owned branding, source identities and acceptance boundaries. Run PYTHONPATH=src python3 -m unittest discover -s tests -v. The examples use public inputs, but an agent must still review actual public projections. Do not deploy, create credentials or change GitHub as an incidental tracker update.

For tracking work, read `skills/use-project-records/SKILL.md`, then the applicable workflow skill in `skills/`. Use `standards/AGENT-WORKFLOWS.md` as the planning and operations contract. Read the skill body before acting; descriptions are discovery metadata.

This repository's authoritative manifest is `examples/projects.json`; its own source is `examples/sources/standard/ledger.json`. `progress/overview.md`, `progress/discovery.json` and `progress/adoption.md` record context and scouting, not a competing completion ledger. Prehnite is a pinned reference, never a migration target in a standards-package task.

Start setup/adaptation or substantial scope expansion with purpose/scope and a source-backed inventory of docs, trackers, issues, PRs, branches and delivery. Keep collection coverage and unknowns explicit. Propose cleanup in terms of active outcomes and dependencies; retain useful unfinished work. Preserve snapshots and stable IDs as the selected scope expands.

Closing a bounded change includes its outcome, affected IDs, actual evidence/revision, named before/after fractions, scope effect, change fragment or omission reason, relevant checks, remaining gate and next action. Use the source writer once and regenerate projections. Implementation, verification, acceptance, publication and deployment are distinct.

Verify `PYTHONPATH=src python3 tools/check_skills.py`, the Python suite, public pipeline, `npm test` (after `npm ci --ignore-scripts`), palette check, site build and README parity for a shared-runtime/package change. Keep public output dedicated and empty before generation. The installer previews by default, preserves existing AGENTS text and refuses owned-file conflicts.

Synthetic evaluation fixtures under `audit/skills` are evidence, not project instructions. Do not use previous outputs as answers during a fresh evaluation. Use `verify-project-accessibility` for WCAG reviews and remediation. Record attributed owner acceptance and any explicitly authorized criterion amendment. Unperformed screen-reader output stays not-tested regardless of scoped acceptance. Individual repository migrations remain outside this package-completion task.
