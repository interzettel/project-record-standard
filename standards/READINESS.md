# Agent readiness in project setup

The setup conversation establishes both a project plan and the conditions under which agents can work on it. L0–L5 describes repository readiness; percentages describe completed work. A project can be 100% complete within its current scope while lacking evidence for autonomous operation.

## The levels

| Level | Meaning | What the assessment must demonstrate |
| --- | --- | --- |
| L0 | Opaque | L1 has not yet been demonstrated. Unknown evidence stays unknown. |
| L1 | Reproducible | A clean environment, canonical bootstrap and verification baseline work without undocumented rescue. |
| L2 | Legible | L1 plus clear tasks, current repository knowledge, ownership and discoverable constraints. |
| L3 | Verifiable | L2 plus reliable checks and meaningful integration/runtime evidence. |
| L4 | Constrained | L3 plus enforced architectural, tooling, security and delivery boundaries, appropriate environment separation and proven rollback. |
| L5 | Measured | L4 plus observability, held-out tasks and real-task outcome metrics that meet defined thresholds, with active drift and autonomy controls. |

Levels are cumulative. The weakest required gate caps the grade; there is no averaged readiness percentage. A README, installed skill or green badge alone does not establish a level.

## During new setup or existing adaptation

The agent first inspects evidence, including previous assessments, bootstrap/check commands, CI/runtime results and relevant execution/deployment boundaries. It then asks what work you want to delegate, what target level serves that work, who accepts/merges/deploys, and which environment or metric decisions remain unresolved. Existing instructions and evidence should answer as much as possible.

The required assessment has ten dimensions: work definition, repository knowledge, reproducible environment, verification loop, architectural constraints, machine-usable tooling, security boundaries, small-batch reviewability, runtime observability, and evaluation/governance. Each gets pass, partial, fail or unknown with evidence and gaps.

The agent records the current level and proposed target separately. It prepares bounded remediation tasks for selected gaps, links them to milestones, and preserves scope history as required work expands. There is no requirement to push every small project to L5.

Detailed assessments belong in the configured central assessment store. Personal Agent Stack-managed repositories use `assessments/owner__repo/` with latest JSON/Markdown and dated history. The target project keeps a short assessment reference and readiness summary in its overview/adoption record. Private evidence stays out of public README and Pages projections. An inaccessible central store means persistence is pending, not successful.

## Readiness and permission

Task risk is separate: R0 information/docs, R1 localized changes, R2 ordinary behavior, R3 sensitive paths such as authentication/billing/migrations, R4 privileged or destructive operations. Actual authority is bounded by readiness, risk, current operational health and repository/owner policy. An existing bounded task authorization remains valid; installing guidance does not grant more authority.

L4 can make explicitly allowed low-risk work eligible for unattended merge/deploy only when checks, independent review, enforced delivery controls, rollback and health requirements hold. L5 may justify wider delegation through measured outcomes and explicit policy. Higher-risk work retains stronger controls. Changing a grade cannot change credentials, rulesets or approvals.

Important applications need evidence of dev/test isolation, separate production identity/secrets/data and a protected promotion path, with staging/preview where the risk warrants it. Shared production credentials or network routes from ordinary coding/test environments block L4. A small static site can use a reduced topology with a documented reason.

## Reassess as the project changes

Reassess during onboarding, before increasing autonomy, after major runtime/build/security changes, incidents or undocumented rescue. Actively autonomous projects use weekly drift checks and at least monthly full review; these are policy expectations, not jobs created by installing the toolkit. Lost controls, unreliable verification or rising incidents/intervention reduce affected authority until evidence supports restoration.

The complete portable [assessment contract](https://github.com/interzettel/project-record-standard/blob/main/skills/use-project-records/references/readiness-contract.md) and [empty JSON record](https://github.com/interzettel/project-record-standard/blob/main/skills/use-project-records/references/readiness-assessment.json) ship with the installed router skill. These are planning and assessment instructions; the runtime does not calculate a readiness grade or enforce an autonomy policy.

## Source and adaptation

This integration follows the owner-requested L0–L5 model from Personal Agent Stack, inspected at revision `d53545f4274fac8c32203be63e070d0e3ab3534a`: `docs/agent-readiness/{README,RUBRIC,AUTONOMY_POLICY,SANDBOX_STANDARD,ENVIRONMENT_STANDARD,EVALUATION}.md` and ADR-006. The upstream repository may require access. This public guide describes the reusable setup model; it does not publish upstream assessments, deployment configuration or private operational records.
