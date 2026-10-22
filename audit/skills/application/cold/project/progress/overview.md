# Loomglass project overview

Observed 2026-10-22. Accountable owner, scope/change authority and physical acceptor: **Sam**, as recorded in `docs/brief.md` and the setup request. This is a private local proposal. No product acceptance, approved scope baseline or budget decision has been recorded.

## Purpose, users and value

Loomglass is an offline optical pattern notebook for a solo print designer. The brief describes storing optical studies, exporting a printable proof and recording physical inspection. A repeatable local workflow would let the designer compare a digital study with an identified physical proof and retain the result without requiring a hosted service.

## What works and what is known

- `README.md` and `site/index.html` identify the product. The existing burgundy (`#6f1430`), cream (`#faf6f0`) and Georgia/serif website remains the presentation authority.
- `docs/brief.md` reports that local file import works. Main contains no runnable importer or product test harness, so that claim has not been independently verified.
- Local branch `proof-export` at `c1a49a97af2c514ecae099ad3255beef6276225e` contains `proof.py`, a two-line `NotImplementedError` stub. It is unfinished work, not a working exporter. Main is `03782b5739f26041dbe109f3d9426412dcf77fba`.
- No tracking authority existed before this setup. No Git remote, remote-tracking ref or local tag is configured. Hosted issues, PRs, Projects, releases and deployment facts are inaccessible; their totals are unknown.

## Proposed next outcome and boundary

**LG-O1: One repeatable offline import-to-proof workflow, with an attributed physical inspection and usable local handoff.** This follows the brief's named next outcome. The decomposition and criteria below are proposed for Sam's review, not an approved baseline or an instruction to implement the product during tracking setup.

| Proposed deliverable | Included work and acceptance |
| --- | --- |
| LG-D1 — Agreed input and import record | Sam identifies a representative local fixture, the proof requirements and pass/fail conditions; the importer is located and exercised at an identified revision. |
| LG-D2 — Printable offline workflow | Review and resume the exporter branch, produce the agreed printable layout, and connect import to export with safe local file handling. |
| LG-D3 — Repeatability evidence | Repeat the documented workflow twice for the agreed input; record revisions, commands, output identity and equivalent content/layout, plus invalid-input and existing-output behavior. |
| LG-D4 — Physical inspection and handoff | Sam records the print conditions, inspected proof, findings and acceptance/rejection; local instructions cover use, output location, limitations and recovery. |

Excluded from this proposed outcome: cloud sync, user accounts, collaboration, a full study catalog redesign, batch export, new print formats beyond the chosen fixture, a website redesign, public tracking publication, hosted automation and unlimited continuing maintenance. These are discovery ideas only; none is a deferred accounting leaf. No pre-existing product capability earns completion credit merely from a prose claim.

## Proposed success and acceptance criteria

1. Sam records the representative input, supported format, intended paper/size/scale/layout, print conditions and explicit pass/fail criteria before scope is approved.
2. One documented local sequence imports that input and exports an identified printable proof without a network dependency.
3. A repeat run preserves the agreed content/layout, and invalid input or an existing output is handled without losing the original study or prior proof.
4. Evidence names the implementation revision, fixture/output identities, commands and results. The importer and print behavior remain unverified until such evidence exists.
5. Sam performs and records the physical inspection. Technical checks do not grant this acceptance.
6. The documented operating and recovery steps are reviewed with Sam, who separately accepts or rejects the milestone outcome.

The authored ledger maps this outcome to four deliverables, four WBS work packages, seven distinct leaves and three checkpoints. Each leaf has Sam as its accountable owner, one WBS accounting package and one primary milestone. Shared prerequisites are references, not duplicate credit.

## Constraints and decisions still open

Local-only tracking is authorized. Preserve the authored README, AGENTS instructions, product files, branch refs and website; the site has no tracking route. No GitHub integration, issue creation, branch deletion, merge, release or deployment is authorized by this setup. No budget, capacity, target dates, service levels or printer characteristics are invented.

Sam's next decisions: approve/amend LG-O1 and its seven-leaf proposal; choose the fixture, output format/layout and print conditions; identify the missing importer/runtime and availability for physical review; decide budget/resources and operating ownership; separately decide whether any future public projection or hosted integration is useful. The implementation and acceptance gates depending on these decisions stay pending. Preparation and validation of local tracking can finish independently.
