# PMI alignment and tailoring

Reviewed against public PMI sources on 22 October 2026. This is a tailored implementation mapping, not a claim of PMI endorsement, certification or clause-by-clause conformance. The complete licensed standards were not supplied. The public Eighth Edition overview, contents, Lexicon and WBS standard overview support the distinctions below; the software and decisions in this kit are our implementation.

## Reference basis

- [PMBOK Guide, Eighth Edition](https://www.pmi.org/standards/pmbok): PMI's current public overview describes six principles and seven performance domains, with adaptable process guidance.
- [Eighth Edition contents](https://www.pmi.org/-/media/pmi/documents/public/pdf/publications/pmbok-guide-eighth-edition_table-of-contents.pdf): identifies the seven domains used in this mapping and treats operations alongside project governance and value delivery.
- [PMI Lexicon, Version 5.0](https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf?rev=447328d841c249af985d14177ddd5f95): terminology reference for work packages, milestones and approved baselines. Definitions here are brief paraphrases, not a reproduction of the glossary.
- [Practice Standard for Work Breakdown Structures, Third Edition](https://www.pmi.org/standards/work-breakdown-structures-third-edition): supports a scope breakdown across different delivery approaches.
- [PMI tailoring guidance, Seventh Edition](https://www.pmi.org/-/media/pmi/documents/public/pdf/pmbok-standards/pmi-tailoring.pdf): an explicitly older public reference for selecting an approach, adjusting it for organization/project needs, and improving it over time.
- [PMI project-governance paper](https://www.pmi.org/learning/library/project-governance-critical-success-9945): practitioner guidance on responsibilities, reporting, risk/issue handling and assurance; it is not itself the PMBOK standard.

## Terminology corrections

A **work package** is the lowest managed component of a deliverable-oriented work breakdown structure. This kit maps its work-item IDs into `governance.workPackages`; a work package earns no second progress credit. A bounded issue/PR is called a **delivery package**. It may implement part or all of a work package. Legacy repository usage keeps an explicit alias during adaptation.

A **milestone** is a significant checkpoint. The percentage beside it describes the supporting work toward that checkpoint. It does not mean that an event has a percentage duration. Roadmap/milestone/epic views are planning and reporting views, not an assertion that every hierarchy is a WBS.

A stored observation is a **snapshot**. An **approved baseline** additionally needs a decision by the designated authority. The comparison engine may compare snapshots without inventing a baseline approval. Scope-change detection is not change authorization.

## Implementation mapping

The domain names come from the Eighth Edition contents. The controls and acceptance tests in this table are this project's tailored design.

| Domain | Minimum useful record in this system | Implemented check or deliberate boundary |
| --- | --- | --- |
| Governance | Purpose/value, accountable owner, acceptance and change authorities, decision sources, tailoring choices. | `governance_errors` requires authorities and a reasoned status for every domain. Approval evidence remains attributed; a validator cannot authenticate a person. |
| Scope | Deliverables, WBS work packages, included/excluded leaves, acceptance criteria, observed/approved baselines and change requests. | Unique leaf ownership, reference checks, explicit WBS coverage and attributed approvals. History exposes additions, removals and denominator changes. |
| Schedule | Dependencies, target/forecast dates when used, constraints and observation date. | Dependency references and cycles are checked. Now/Next/Later is a horizon view; it does not establish a committed schedule. Dates remain unestimated until an accountable source supplies them. |
| Finance | Funding/cost limits, expenditure source and review authority when relevant. | Tailoring must say applied, not assessed or tailored out with a reason. No invented zero budget, actual cost, cost-performance index or completion forecast. |
| Stakeholders | Intended users, decision makers, reviewer/acceptor and communication route. | Charter and authority records identify responsibility. A public projection is a separate audience decision. The adapting agent records missing stakeholder mapping. |
| Resources | Owners, capacity, hardware/runtime constraints and agent authorization limits. | Work ownership and source evidence are retained. Workflow generation never launches inference, allocates budget or broadens an agent's permissions. |
| Risk | Event/condition, accountable risk owner, response, intervention trigger and state. | Risk entries require those fields. Existing issues, blocked work, risk and accepted debt remain distinct concepts. |

## Measurement limits

The default percentages count completed leaves or take an equal-milestone mean. They are deliberately labelled. They are not earned value, effort-weighted completion, cost/schedule performance or proof of business benefit. If a project adopts those measures later, it needs the relevant approved scope, schedule and cost data, a declared measurement method and separate validation. Do not relabel a 75% task ratio as 75% of project value delivered.

WBS coverage can be `partial` or `not-assessed` during hot adoption. Declaring it `complete` requires every declared leaf to map exactly once. This verifies the mapping of the recorded scope, not that every real-world obligation has been discovered. The owner must review omissions, including management, assurance, integration and operational handover work.

## Projects and continuing operations

Project work has a bounded outcome and acceptance. Continuing operations need service ownership, support/incident routes, observability, backup/rollback, data/privacy boundaries and maintenance responsibilities. Put these in `governance.operations` or link the existing runbook; do not create an endlessly growing project percentage for all future maintenance.

An operational incident is an existing condition to resolve, while a risk concerns an uncertain event or condition. Use separate types or mapped fields. A repeated maintenance action may create a bounded delivery package with its own scope and evidence. Closing that package does not establish permanent service health.

## Tailoring rule for the skills

Both cold and hot adaptation record the chosen development approach and, for each domain, `applied`, `not-assessed` or `tailored-out` with a reason. Small projects can keep this in one local JSON file. Larger projects link their accepted governance documents. The skill must preserve accepted local policy, identify conflicts and produce a reviewable mapping rather than claiming that installing a tracker makes the project compliant.
