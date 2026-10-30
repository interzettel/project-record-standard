# Proposed release boundaries

The previous plan grouped the first sixteen packages into one proposed 0.5.0 release. Yiğit challenged that boundary on 30 October 2026 because foundations, experimental integration and proven unattended operation are separately useful outcomes. This proposal replaces that single batch, without publishing or assigning a new package version.

[SemVer 2.0.0](https://semver.org/) ties versions to the public interface, not issue count or effort. Its 0.y.z period permits unstable interfaces. PRS will still document compatibility, preserve exact pins and provide migration guidance. A large feature can be a minor release; splitting delivery improves review and adoption independently of the size of the numeric increment.

| Candidate | Included boundary | Exit evidence and consumer effect |
| --- | --- | --- |
| 0.5.0 · foundations | #27–#30, #15/#16, #6/#3 and #31: records/policy/layout, pins, handoff/evidence/selection and common checks | Tested offline interfaces, extracted-kit installation, compatibility matrix and release preparation for this specific scope. Consumers can assess/adopt foundations without enabling unattended writes. No automatic-tracking support claim. |
| 0.6.0-alpha.N · opt-in automation preview | #32–#34 and relevant #36 feedback integration | Pinned, explicitly experimental adapters; bounded failure/replay tests and CI-boundary evidence. No silent stable-pin replacement or fleet rollout. Only adopted/authorized runtime paths may execute writes. |
| 0.6.0 · supported automatic workflow | #35/#37, completed #36 and final #38 handoff | Real work sessions, recovery, actual multiple producer/runtime paths, measured interventions/tracking burden and declared supported set. Stabilizing the same preview interface does not require an arbitrary 0.7.0 bump. If the interface changes materially, reassess the candidate instead. |
| Later independent releases | #2/#17–#19 readable records; #20–#22 upgrades; #39 monitoring | Select actual version from their compatibility effects when ready. No promised 0.7/0.8 numbering or universal 1.0 completion checklist. Optional MCP/hosting/visuals remain separate. |

These are candidate release scopes, not dates, release plans accepted by the owner, or proof that any package is complete. The existing execution order remains useful for implementation. A release may include fewer completed changes than the future programme; its candidate record must enumerate exact changes and gates.

## Release preparation is an explicit hold

#38 currently has execution prerequisites requiring the full automatic-workflow evaluation. That cannot certify or prepare an earlier foundation release. Before any earlier publication, refine that same release work into bounded foundation/preview/final delivery slices, or propose separately accounted leaves with approved denominator effects. Record the changed dependency/authority decision and acceptance criterion before executing such slices. This proposal does not silently remove those prerequisites, create duplicate credit, activate the old v0.4.1-specific publisher or claim the foundation release is ready.

#38's final completion still requires its existing criterion and final dependencies. Earlier release plumbing is a visible planning hold, not hidden work forced into #28. The selected next implementation after #28 remains #29. No new counted scope, package version, tag, consumer pin or published artifact changes here.

## Version and compatibility decisions

Keep a single toolkit/cooperating-skill suite version while those components ship together. Record-contract versions remain independent; changing documentation does not automatically bump the contract. Host applications retain their own versions. Experimental adapters identify their tested runtime/protocol versions and exact source pins.

Within 0.x, use a new minor line for a deliberately selected interface/capability boundary and patches for compatible corrections under PRS's stated policy. Record breaking changes explicitly even before 1.0. Use prerelease identifiers for opt-in unstable candidates. After 1.0, apply normal SemVer major/minor/patch rules to the declared public interface.

Consider 1.0 when that interface, support/deprecation policy, tested compatibility and migration/recovery commitments are fit for reliance. Neither finishing all optional features nor accumulating a large number of changes is sufficient by itself. Minor/major discovery triggers a consumer applicability assessment; actual upgrades follow the adopted authority/conflict/recovery policy.
