Selected workflows: **use-project-records → operate-project-tracking**, following `standards/UPGRADING.md`, `AUTOMATION.md`, `AGENT-WORKFLOWS.md` and `COMPATIBILITY.md`.

Read-only checks establish:

- `journal/state.json` matches `plan.json`, records `status: applying`, and has no verification yet. Journal permissions are `0700/0600`; all preserved preimage hashes match.
- Actual host hashes show **1/4 planned files at postimage**: `.project-record/agent-installation.json`. `AGENTS.md`, `custom/prs/pyproject.toml` and `records.json` remain exact preimages. All unchanged input guards match. This is recoverable interruption, not evidence of completion.
- Toolkit `_validate_plan` and `_grant(..., "apply")` accept the existing plan/grant. Both archived release descriptors pass `_release` validation. The plan digest is `e64f75dfcc0781cc29b305dfaef73dfeabb80fa11b51ad6d6f3412dc04846394`.
- Records retain IDs `W1/W2`, dependency `W2 → W1`, `accepted: true`, release `host1`, and **1/2 completion**. The planned JSON transformation changes formatting only.
- `request.json` records RULE-1 as already satisfied, citing hashed `notes/policy.md`. That file contains “locally authored rule”; the catalogue sources contain generic synthetic migration/policy text. Byte checks confirm the cited evidence, not its semantic adequacy.

Exact proposed recovery command, **not executed**, from `/tmp/prs-upgrade-skill-controls/5/toolkit`:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m project_record upgrade-apply --plan /tmp/prs-upgrade-skill-controls/5/plan.json --grant /tmp/prs-upgrade-skill-controls/5/grant.json --journal /tmp/prs-upgrade-skill-controls/5/journal --mode apply
```

It would reuse the journal, inspect current bytes, skip the completed receipt replacement, apply the three remaining postimages, verify the selected target installation and record completion. Unknown edits would stop recovery.

Watcher handoff: reuse `existingAssessment: request.json` and proposal `local:upgrade-review-1` for `toy-host`; reconcile its existing interrupted operation rather than create a duplicate for the second observation. Recheck changed identities/evidence before reuse. `upstreamSuggestion` grants no automatic merge/deployment authority; retain the existing host watcher and exact-plan scope.

Rollback with the current grant is rejected: `rollback: false`. A separately attributed, same-plan grant with `rollback: true` and `allowSynthetic: true` is required. With that grant and unchanged guards, rollback would restore the receipt’s preserved preimage and skip already-original files, then verify the old installation. Later managed/guarded edits cause refusal; original approval history remains preserved.

Remaining gates: preparation forbids mutation now; subsequent execution remains synthetic, followed by host functional checks and owner outcome acceptance. No release, deployment or additional completion credit follows.
