# Import the PRS main ruleset

Use `main-ci.json` in **interzettel/project-record-standard**. It is the import copy of the reviewed #33 activation proposal. Importing and saving it changes GitHub policy; storing this file in Git does not activate it.

## Import

You need repository administration access. Download [main-ci.json](main-ci.json) with GitHub's **Download raw file** control. Keep the filename and JSON contents intact.

1. Open [repository ruleset settings](https://github.com/interzettel/project-record-standard/settings/rules).
2. Select **New ruleset > Import a ruleset** and open `main-ci.json`.
3. Review the settings in the following table. If a ruleset named **PRS main CI gates** already exists, compare and update it instead of creating a duplicate.
4. Select **Create** to activate the reviewed ruleset.
5. Tell the working agent that the import is complete, or give it the new ruleset URL. The agent will read back the settings and run the remaining checks.

| Setting | Expected value |
| --- | --- |
| Enforcement | Active |
| Target | Branch; only `refs/heads/main` |
| Bypass list | Empty |
| Pull request | Required |
| Required approvals | 0 |
| Required checks | `verify`, `reusable / record`, `PRS policy` |
| Check producer | GitHub Actions; app ID `15368` for every check |
| Up-to-date branch | Required |

The names and app ID come from actual PRS check runs. If GitHub rejects a field or cannot resolve a check, preserve the error and hand it back to the agent. Do not substitute **Any source**, add a bypass actor or disable a required check to make the import succeed. Existing organization rules remain in effect.

GitHub documents this procedure in [Importing a ruleset](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/managing-rulesets-for-a-repository#importing-a-ruleset). The fields follow the [repository ruleset REST schema](https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset), checked on 30 October 2026. Server acceptance of this particular file remains untested until import.

## Agent verification after import

The owner performs the import. The working agent owns collection, comparison, controlled probes, evidence recording and issue reconciliation under #33 (`PRS-GATE-02`, M10). The [verification checklist](../../audit/ci-enforcement/2026-10-30/post-import-checklist.json) records the remaining observations; it is **not another ruleset to import**.

Read the new ruleset and inherited rules, compare every field with `main-ci.json`, and record the native ID, URL, timestamp and response. Observe effective `main` protection separately. Read the actual repository/organization Actions event policy if accessible; an inaccessible setting stays unknown. No event-policy exception or unsafe-checkout option is included in this import.

Use controlled, unmerged probe PRs to inspect native refusal for failing and unavailable required checks, then observe corrected checks and merge readiness. Capture the exact actor, head/base revisions, check IDs and native rule evidence. A draft restriction, conflict, stale branch or insufficient actor permission cannot stand in for required-check refusal. **Never submit a merge request containing failing data to main**: first establish the active boundary through native read-back and non-mutating mergeability/rule evidence. If that evidence cannot distinguish the blocking rule, retain the gap; an isolated test branch needs its own explicitly reviewed ruleset before a destructive probe.

The existing [probe PR #54](https://github.com/interzettel/project-record-standard/pull/54) proves the trusted job rejects duplicate data and accepts corrected bytes, including a `[skip ci]` commit created without local hooks. It was closed without merging. Its results predate native activation and do not prove merge refusal. A fresh ordinary PR must receive all three required checks; `[skip ci]` can leave the two ordinary checks unavailable and should block readiness after activation.

Confirm that the imported bypass list is empty. Do not grant an actor bypass just to test bypass behavior. Administrators who can edit or delete policy remain a trust boundary. Record unavailable actor/runtime coverage, fork rejection before checkout, protected-file review notices and unsupported merge queues. Check producer binding identifies the app, not an immutable workflow; notices do not prevent an administrator from replacing a workflow.

Only reconcile the canonical #33 completion record after its criterion is supported. Until then, #33 remains blocked, #34 remains dependent on it, and #36/M11 is the next eligible independent package. No version bump or release follows from import.

## Recover from an import problem

Preserve the imported ruleset URL/export and the failure. Fix a typo through a reviewed edit to this same ruleset. Retry or restore a missing check through its workflow; a runner outage is not a reason to drop a gate. If policy recovery requires weakening or disabling the ruleset, describe the exact temporary change and obtain the owner's decision first. Leave unrelated organization policy intact and retain the earlier export for comparison.

This handoff was prepared on 30 October 2026 by the PRS working agent. The owner imports; the agent verifies. The dated audit retains the observations and limits.
