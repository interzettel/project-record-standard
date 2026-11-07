Selected workflows: `use-project-records` → `operate-project-tracking`. Read installed guidance, host instructions and toolkit `AUTOMATION.md`, `UPGRADING.md`, `AGENT-WORKFLOWS.md`, and `COMPATIBILITY.md`.

Actual read-only checks:

| Watcher observation | Required reaction |
|---|---|
| 0.4.1 → 0.4.2 ordinary patch | Proportionate triage; impact record or reasoned exact-target deferral |
| Same patch, security relevant | Prioritized assessment; remediation or bounded mitigation/deferral with risk owner |
| 0.4.1 → 0.5.0 minor | Applicability/compatibility assessment including intervening changes; apply required applicable changes under host policy |
| 0.4.1 → 1.0.0 major | Breaking-change assessment; reviewed, authorized migration or explicit hold |

These match actual `assess_update` outputs. None authorizes application or performs a vulnerability assessment.

**Retained last-known synthetic pin:** toolkit/suite **0.4.1**, contract **0.2.0**, commit `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, archive SHA-256 `57b2338458fe2bd515d5f6fcce4d0472d8b3510ad678f28f19566a3011ed975f`. Host version **2.3.0** remains separate.

`assess_upgrade(request.json)` returned **blocked-unknown**, report exit code **3**, no conflicts. Installed selected bytes match: three selected toolkit files, complete selected example skill, receipt and owned instruction section. Supplied provenance matches; publisher authentication is false, policy is unpinned, and unselected toolkit files/runtime support are not certified.

`request.json` explicitly sets target archive to `null` and coverage to `false`. Therefore unknowns are `archive-evidence-missing` and `intervening-release-coverage-incomplete`, despite the coverage source’s contradictory “complete” wording. Watcher coverage is only **page 1 of 3**, with target bytes/intervening metadata unobserved. Its “latest” recommendation cannot establish safe adoption.

`unsupported.json` additionally returns `host-contract-unsupported` for declared host contract **9.0.0**. Matching installed contract bytes do not establish support for that declaration.

RULE-1 remains the supplied `already-satisfied` semantic judgment with matching `notes/policy.md` evidence. That file contains only “locally authored rule”; the byte check does not independently establish semantic truth. No template replacement or completion credit follows.

**Exact proposed next action:** review the locally available `b.zip` as target evidence; its actual SHA-256 matches the target pin: `7bb6d16e9bc03dfd9dc28172fd063e8d6ec6d67f85c52ea22c3ab97346b21202`. Do not silently substitute it into the request.

**Remaining gates:** explicitly supplied target archive, complete attributed intervening-history coverage, resolved supported host contract and semantic applicability review. Only then consider preview and separately authorized application. Synthetic evidence cannot certify a real release. No files, network or GitHub state were changed.
