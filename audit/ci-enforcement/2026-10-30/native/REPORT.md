# Native CI enforcement observations

PRS-GATE-02 / issue #33 / canonical M10. Observed on 30 October 2026; read back again on 31 October. The owner imported ruleset **26242462**, [PRS main CI gates](https://github.com/interzettel/project-record-standard/rules/26242462). The agent changed no native setting.

## Configuration

The ruleset is active for only `refs/heads/main`. It requires pull requests, zero mandatory approvals, an up-to-date branch and checks `verify`, `reusable / record`, `PRS policy`, each from GitHub Actions app15368. The bypass list is empty; the connector read-back says `current_user_can_bypass: never`. `main` reports `protected: true`. Its classic branch-protection summary remains disabled; that summary does not describe the active ruleset.

GitHub supplied additional defaults: no required reviewers, no dismissal restriction and all three ordinary merge methods allowed. `require_extra_approval_for_unattributed_changes: true` applies to Copilot PRs only when the required approval count is nonzero, according to the [current REST schema](https://docs.github.com/en/rest/repos/rules). It adds no approval requirement to this zero-count profile. All explicitly proposed fields match the imported rule. Organization deletion/transfer policy was left intact.

## Controlled probe

[PR #56](https://github.com/interzettel/project-record-standard/pull/56) was non-draft, conflict-free and based on `9b309574c577d8d6e0afda81705f1f531b2654f5` throughout. Its commits were created through the connector, bypassing local hooks. All phases used the same trusted base workflow/checker. The PR was closed without merging. No merge API request or direct push to main was attempted.

| Candidate | Actual check result | Native result |
| --- | --- | --- |
| `cce2472dd686b7aa777ab4de5a0114f90e678303` | JSON parse failure caused by a truncated probe transfer | Blocked; retained construction error, not duplicate-predicate evidence |
| `f43b5b4d0dfd2dc951e280baf8f12964281dc1ee` | Duplicate items ID; policy run41134755846 and ordinary run41134757982 failed | `mergeable: true`, `mergeable_state: blocked`; UI marked all three failing checks Required and disabled Merge |
| `361966d2d2ea363c052ab07dc5ade245bafd7bc5` | Exact source restored, `[skip ci]`; policy run41134877784 passed; ordinary checks absent | Conflict-free but blocked; UI marked verify/reusable Expected and Required, with Merge disabled |
| `caaaa994dea9e344884a6cc427f6d022d46df2bb` | Same restored tree without skip message; runs41134998309 and41134998509 passed all three required jobs | `mergeable_state: clean`; UI enabled Merge with no mandatory reviews |

The restored source blob is `4d74f31254084be346ed0a3ae2962e8d47606858`, exactly the main source. The probe marker was never integrated. Native refusal here means observed required-check blocking and a disabled merge control, corroborated by the active ruleset and conflict-free/non-draft state. It is not an attempted unsafe merge or proof of every Git transport/actor path.

## Event-policy limit

The repository's Actions Policies UI showed no custom policies and a **2 December 2026** restriction notice for `pull_request_target`. Policy insights showed seven visible runs in **Evaluate / Would block**. This is an observed upcoming incompatibility, not merely an inaccessible setting. The [upstream guide](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) confirms the default restriction and recommends assessing whether the event is necessary.

The current required-check boundary works. It will fail closed if the policy job becomes unavailable; that protects merging but interrupts delivery. Supported unattended adoption must resolve this event-policy compatibility before relying on this profile across that deadline. Options are a separately reviewed event/transport redesign or an explicit narrow Actions policy decision. This evidence grants neither a security exception nor permission to turn on unsafe fork checkout. Keep this limitation visible in #33 and the #34 pilot entry conditions rather than claiming permanent support from a passing run.

## Coverage and trust limits

| Boundary | Evidence and limit |
| --- | --- |
| Local hook bypass | Actual connector commits still triggered server jobs and required-check blocking. |
| Skip/path filters | Actual skip probe left two required checks pending and blocked merge; workflows have no path filters. |
| Unavailable checks | Actual Expected/Required checks blocked merge; runner outage itself was not injected. |
| Fork/untrusted input | Existing unit tests cover candidate non-execution, host-selected profile, traversal/symlink rejection and the workflow's fork guard. Forks are deliberately held before checkout; no live fork certification. |
| Workflow/pin/policy replacement | Protected-path notices and trusted-base data checks exist. Notices do not prevent changing future workflows; app binding identifies the producer app, not an immutable workflow. |
| Bypass actors | None configured in this branch ruleset; connector reports never, and the signed-in owner's UI disabled Merge for failing/missing checks. No actor was granted bypass. Other actors, deploy keys and direct-push rejection were not exercised. |
| Administrators | Ability to edit/delete policy remains a trust boundary; no protection against an administrator changing the rules is claimed. |
| Merge queues | Unsupported until merge-group event behavior is configured and tested. |
| Acceptance/release | Owner milestone acceptance, release and runtime adoption remain separate; no version or release change. |

Historical preparation/probe files remain unchanged. The `native/` records supplement them with actual host observations. Completion disposition follows review against the unchanged leaf criterion; the known event-policy compatibility limit must remain visible whatever that disposition is.
