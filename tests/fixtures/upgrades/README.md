# Upgrade comparison fixtures

`tests/test_upgrades.py` authors tiny synthetic source kits, immutable ZIP bytes, selected pins, real disposable skill installations and host files. No future release or existing consumer adoption is claimed. Synthetic archives are generated inside each isolated test so edits, missing receipts, special files and stale reviews exercise actual filesystem behavior. The actual v0.4.1 archive smoke is separately recorded in `audit/upgrades/2026-11-07/real-installation.json`.

| Parent #10 case | #20 comparison coverage | Remaining gate |
| --- | --- | --- |
| 1 Vanilla / mandatory + optional | Mandatory/optional host judgment and exact source/archive digests; minor assessment due | #21 applies reviewed plan |
| 2 Already satisfied | Byte-bound semantic judgment; no writes/extra credit | Real consumer acceptance separate |
| 3 README-only/custom paths | Existing profile and custom policy path retained; no site output | #21 verifies any actual adaptation |
| 4 IDs/dependencies/history/counts | Before/after host byte snapshots include nonempty W1/W2 dependency, accepted history, release and1/2 fraction | Alias/transform/rollback proof in #21 |
| 5 Edited owned skill / ambiguous mapping | Mixed byte conflict, stale review conflict, malformed multiple decisions rejected | Apply refusal in #21 |
| 6 Missing release/history/contract | Missing archive/review/coverage/predecessor and unsupported contract unknown | No inferred migration |
| 7 Repeat / interrupt | Identical read-only reports, no new files/links/credit | Interrupted application/recovery in #21 |
| 8 Authority | Every report denies apply/write/authority/extra credit, including security/prerelease | No new permissions; #22 skill evaluation |

Additional negative tests: package-version metadata inconsistent with archive; target runtime unknown/unsupported; archive moved; cited source digest mismatch; unsafe path/symlink/FIFO; duplicate delta and unrelated stale decisions; real/synthetic mixed chain remains simulation-only. SemVer major/minor/security/ordinary patch/prerelease reactions reuse the pinned-policy helper rather than reimplement version ordering.

`tests/test_upgrade_apply.py` adds the #21 boundary: a staged existing-installer plan, exact grants, private per-file journal, guarded JSON formatting and reviewed text changes. It proves repeated apply/rollback, interruption at each host-file mutation, phase recovery, stale/mixed/ambiguous refusal, new-path collisions, complete unchanged-input preconditions, source-fact preservation, historical instruction writer selection, corrupt journal handling and preservation of later authored work. It grants no real-consumer migration permission. Unsupported semantic transforms and the #22 skill evaluation remain separate.
