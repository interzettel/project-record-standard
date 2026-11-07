Selected workflow: installed `use-project-records` router → `upgrade-project-records`, specifically interrupted application recovery and read-only watcher handoff. No setup, output repair or mutation was performed.

All paths below are relative to `/tmp/prs-upgrade-skill-applications/5`.

Actual findings:

- `journal/state.json` is `applying`, with verification still null. Its embedded plan equals `plan.json`; the request matches `request.json`. Toolkit plan validation, apply-grant validation, both release verifications and all preserved backup hashes passed.
- Plan hash: `9468def3bf865f2546ed6113e1e20c65a8d88e9790ea0aa45037ae4bfe636487`. Request hash: `a85484aa2e9674833d81b2106acc2319a547927f9e5b275692fc22eb6dbc0bf3`.
- Actual destination hashes show `.project-record/agent-installation.json` already at its exact postimage. `AGENTS.md`, `custom/prs/pyproject.toml` and `records.json` remain exact preimages. All unchanged input guards match. This is a recoverable partial operation, not completed installation.
- The journal contains only `state.json`; directory/file permissions are `0700`/`0600`. Host/journal ancestors are not symlinks.
- `RULE-1` is mandatory and applicable to `readme-only`; the existing reviewed disposition is already satisfied, citing matching `host/notes/policy.md` bytes. Catalogue sources are the verified target archive’s `migration.md` and `policy.md`. These synthetic prose sources do not independently establish a real upstream rule.
- Current guarded facts remain IDs W1/W2, W2 depending on W1, accepted true, release `host1`, completion 1/2. Contract remains 0.2.0; declared host version is 2.3.0. Toolkit/suite 0.4.1 → 0.5.0 is explicitly synthetic.

Exact proposed recovery command, run from the toolkit directory after this preparation-only restriction ends:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m project_record upgrade-apply --plan /tmp/prs-upgrade-skill-applications/5/plan.json --grant /tmp/prs-upgrade-skill-applications/5/grant.json --journal /tmp/prs-upgrade-skill-applications/5/journal --mode apply
```

Per `upgrade_apply.py`, this reuses the original journal/grant, skips the completed receipt write, completes the other three entries and verifies selected target installation bytes. Do not regenerate the plan or replace the receipt.

Watcher: reuse `request.json` and proposal `local:upgrade-review-1` for consumer `toy-host`; two observations grant no additional authority. Source/time/last-success, enumeration coverage and security evidence are absent from `watcher.json`, so retain those gaps. Automatic merge/deploy remains unauthorized.

Rollback with the current grant fails before mutation (`rollback:false`). A separately attributed, same-plan rollback grant may later restore preserved preimages using this journal. Changed managed/guarded bytes stop restoration before overwrite.

Remaining gates: preparation restriction, then host functional checks and owner outcome acceptance; no deployment, publication or extra completion credit.