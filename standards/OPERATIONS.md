# Quiet release-drift observations (unreleased)

PRS-OPS-01 is an offline, source-attributed observer over existing host collection/scheduling. It reuses selected-byte pin verification and `assess_update`, keeps one durable attention-assessment entry per consumer/target version, and grants no application authority. Full semantic comparison stays in `upgrade-project-records`/#20; reviewed changes and rollback stay #21. It creates no fleet database, network collector, remote notification, GitHub issue, credential, cron job or deployment.

## Host contract

`observe_releases(request, as_of, state=None)` consumes exact `watchVersion:1` fields. `watch_files(request_path, state_directory, as_of, write=False)` previews or updates one private external state.json. `release-watch --request ... --state ... --as-of ... [--write]` exposes the same implementation. Exit0 means current collection/selected pin health,3 means degraded/stale/exhausted attention,1 invalid/conflicted input. A current collection does not mean every release assessment is resolved.

| Field | Meaning |
| --- | --- |
| consumerId | Stable host identity; state cannot be reused for another consumer |
| host, pin, provenance, runtime | Actual local host and expected pinVersion1; supplied origin/runtime claims remain unauthenticated |
| policy | Explicit intervalSeconds/freshnessSeconds/retrySeconds, maxRetries0–10 and reasoned exact from/to deferrals |
| collection | attemptedAt with zone, success/partial/failed/unknown status, source, pagesRead/pagesExpected, releases list and error string/null |
| Each release | Exact version, sourceCommit/archiveSha256/notesSha256 or explicit null, security boolean, securitySource/null and attributed source |

The host bounds its network requests, pages, timeout and credentials before providing this envelope. A complete observation needs success, known matching page counts and no error. A supplied complete flag/label cannot override contradictory pagination. Release references are observed metadata, not downloaded/archive-verified byte claims or authenticated publishers. Security relevance is supplied evidence, not vulnerability verification. Unknown bytes/history must still be resolved before full semantic assessment/application.

## Freshness and quietness

lastAttempt retains the supplied attempt clock/source/error/coverage; lastSuccess changes only on complete collection with matching selected installed bytes and supplied origin. It retains the last successful release count even if later collection fails or returns partial zero. A genuinely complete empty response is distinct. nextDue derives from the observation clock, never rebuild time. Late attempts and missed nextDue are visible; source age beyond the host threshold is stale. Failed/degraded attempts receive at most maxRetries bounded retry suggestions, then nextDue is null until a host-authorized later attempt. These are suggestions to the existing scheduler, not an installed timer.

Repeated observation is quiet and does not refresh source facts. One entry per consumer/version carries a revision and sourced version-policy assessment. Changed release metadata, applicable deferral, security evidence, selected pin or completeness can renew attention; unrelated deferrals do not. New security relevance bypasses an ordinary deferral. Once observed, unresolved security attention remains conservative rather than silently cleared by ordinary metadata. A changed known immutable commit/archive identity remains conflicted until explicit operator reconciliation; unknown identity becomes anchored on first observation. Historical/current-pin ordinary releases create no upgrade notice; no downgrade is proposed just because older releases remain listed.

notices are returned once for each changed relevant assessment. They are not sent externally. The caller must persist the returned state and provide its own reviewed delivery/outbox if external notification is desired. No exactly-once remote delivery is claimed; repeat committed input returns no new notice. Attention assessment readiness is not semantic compatibility or migration success.

## Durable state and recovery

Explicit --write owns exactly one external directory/state.json, owner-only0700/0600 on POSIX. Other files, symlinks, host/request collisions, mismatched consumer, digest corruption, changed same-time attempts and time regression are refused. Reads and state/release counts are bounded. The state checksum detects accidental changes; it authenticates no actor. Cooperating writers share an advisory canonical-path lock; state replacement is single-file atomic. Process/OS trust remains required. Unknown temporary neighbors or an incomplete initial directory require inspection rather than deleting user files. No power-loss or hostile concurrent-process guarantee is made.

No source ledger, source observation, host installation, expected pin or project counts are rewritten. Last-success collection counts and work completion percentages are separate measures. State/requests/results can reveal private paths, release attention and host metadata; keep them out of public artifacts and logs.

## Existing scheduler integration

`templates/.github/workflows/release-watch.yml` is a manual trusted-Linux-runner example with full action pin, read-only permissions and persistent host-owned private state. Its request must already exist; it does not collect the GitHub API or download releases. It redirects private output to a private runner file, not public job logs/artifacts. No schedule is enabled. Reuse Hermes, CI or another existing host scheduler; do not provision a VPS or competing cron merely to use PRS. Hosts choose their own retention, result delivery and incident owner before activation.

GitHub documents that scheduled workflows can be delayed/dropped under load, run on the default branch and be disabled after inactivity in public repositories: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule . A schedule declaration is not observed execution. Actual clocks/coverage and missed-run evidence remain required. No live schedule/fleet effectiveness is claimed by local tests or the template.

Main remains toolkit/suite0.6.0-alpha.0 (wheel0.6.0a0), contract0.2.0; published0.4.1 unchanged. #34 actual sessions stay deferred; unattended lifecycle and model proof remain #35/#37. Verify with `PYTHONPATH=src python3 -m unittest discover -s tests -p test_collection.py -v`.
