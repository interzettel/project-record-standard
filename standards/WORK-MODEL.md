# Work language and open contribution

PRS supports a person working alone, a group, and work assisted by agents. The project declares its outcomes, sources, quality policy and decision authority. Contributors can bring any relevant knowledge to a selected package.

## Agile and Scrum terminology

The [Agile Manifesto](https://agilemanifesto.org/) and its [principles](https://agilemanifesto.org/principles.html) describe values and principles. PRS borrows attention to useful results, sustainable work, simplicity and reflection. Agile does not prescribe a universal work-item hierarchy.

The [November 2020 Scrum Guide](https://scrumguides.org/scrum-guide.html) specifies Product Owner, Scrum Master and Developers as accountabilities within a cross-functional, self-managing Scrum Team. These are not job titles. Its Product Backlog is ordered work toward a Product Goal. A Sprint Backlog combines a Sprint Goal, selected work and a delivery plan. An Increment meets a Definition of Done. Sprints last at most a month; the Sprint Review is not a release gate. Scrum requires its whole framework. A solo maintainer using agents and selected practices should describe the result as an Agile-informed PRS adaptation, not claim Scrum conformance from terminology alone. [Scrum.org's explanation of accountability and roles](https://www.scrum.org/resources/accountability-responsibility-and-roles) helps distinguish accountability from delegated responsibility.

Sources inspected on 30 October 2026. These summaries guide the adaptation; the linked sources govern claims about Scrum and Agile.

## Contribution, responsibility and authority

Any human or model can propose an explanation, challenge an assumption, design, implement, test or review across disciplines. A review lens selects questions to investigate; it does not restrict the contributor's knowledge or identity. Backend, artist, architect and manager are possible backgrounds or current activities, not exclusive agent identities required by PRS.

A delivery package names its current responsible contributor, affected artifacts, criteria, permissions and next handoff. Responsibility can move through an explicit handoff. Acceptance authority identifies who may decide a declared gate. An accounting owner identifies where work is counted once. These meanings remain separate even when one person performs all three activities.

Open contribution does not itself grant write access, a model budget, permission to spawn agents, or authority to merge, release or accept an outcome. Existing task authorization still applies. When multiple perspectives are actually obtained, record the known model/provider/revision or named human and the inspected sources. Several lenses used by one model are one producer's review, not independent agreement. Different models may share errors; diversity is a reason to investigate, not proof of correctness. Preserve a supported dissent even when other contributors agree.

## Work structure and selection

An outcome states the change sought for users or operators. A capability states a lasting ability. An epic may group related work. A feature names a useful product behavior; a user story may express a user's need and value. A task describes an execution step. Projects may use these forms when useful, with an explicit mapping to their stable accounting leaves. No mandatory epic–feature–story–task ladder applies.

A parent relation groups work. A prerequisite relation constrains execution. A milestone checks an outcome through exit criteria. A roadmap presents direction and checkpoints. A milestone can summarize supporting work without becoming its decomposition parent or a fixed date. Views should distinguish containment from prerequisites.

Order work by the active outcome, prerequisites, current blockers, risk, value and available capacity. A leaf is eligible only when its prerequisites and actual authority, holds and capacity allow it; missing evidence leaves eligibility unknown. Graph depth shows a structural distance, not a duration or a delivery forecast. Finite, goal-based work cycles and output reviews can help a solo maintainer. Adopt a cadence only when it helps decisions; discuss process improvements separately from product acceptance.

## Criteria, quality and delivery claims

An acceptance criterion states an observable result, the check and required evidence. A project Definition of Done states the applicable shared quality policy for that kind of artifact. Code, research, a design and an operational procedure can require different proof. The item's criterion and applicable quality policy together govern a new Done claim. A negative experimental result can satisfy a measurement criterion.

| Claim | Evidence and boundary |
| --- | --- |
| Implemented | The identified change exists in a named artifact/revision; a specification alone cannot establish implementation. |
| Integrated | The change is merged into the declared integration branch, if the project uses that policy. |
| Verified | A named check passed for its subject, revision and environment. |
| Done | The item's criterion and applicable project quality policy are met. |
| Accepted | The designated authority recorded the declared acceptance decision. |
| Published / deployed | A named channel contains the artifact / a named environment runs the observed revision. |
| Delivered | Availability to the intended audience is established under the project's declared delivery policy, with supporting channel or environment evidence. |

These are separately inspectable claims, not a mandatory linear state machine or new required schema fields. A project may require integration before Done; PRS does not redefine all implementation as merging. A documentation preview can exist before merge, and deployment can precede acceptance. Historical source claims retain their original meaning without recertification.

## Facts, findings and decisions

Each fact has one authoritative writer declared by the host. PRS itself keeps completion, scope and dependencies in its canonical ledger; GitHub owns discussion and assignment. Another host may choose a tracker with an explicit authority map. A delivery plan explains sequence and links work; a runbook explains operation, recovery and troubleshooting. Neither maintains a parallel completion checklist.

A finding records an observation and evidence. Continuing action links to an existing work item or becomes deliberately scoped work; the observation stays intact. A decision records a choice, reason, alternatives and decision authority. A later decision explicitly supersedes the earlier one. A review finding is advisory until its disposition is recorded by the authorized maintainer.

Planned or emergent describes origin. Defect, obstacle, threat, opportunity, debt or change describes an effect or kind. A current blocker differs from a possible future risk. Grouping, requires, supports, emerged-from, resolves, supersedes and duplicates describe different relationships. These are vocabulary for explicit host mappings; adopting this guide does not silently add runtime enums, alter dependency semantics or create required labels. The existing execution plan assigns remaining schema and view work.
