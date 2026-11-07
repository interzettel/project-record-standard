Selected workflow: installed `use-project-records` router → `upgrade-project-records`. This is release assessment with installation drift; no evidence of an interrupted apply plan/journal warrants resume or rollback.

Both inputs describe a **synthetic** toolkit/suite 0.4.1 → 0.5.0 minor upgrade, host 2.3.0, unchanged record contract 0.2.0, and `readme-only` profile. They do not establish a real 0.5.0 release.

| Input | Actual result and evidence | Resumable action / gate |
|---|---|---|
| `request.json` | Read-only `upgrade-assess` exits 1, `overall: conflicted`; request hash `dadfe13b2b1bc27e3f1e317f042caf09bd25bea75aa5e76f364d41e45ee4b615`. Only reported installation conflict: `.agents/skills/example/SKILL.md`. Actual content is `Locally authored owned skill edit`, SHA-256 `2c2c56fa05055d4fe1478e32264b3479d5501de0cdc0245fed204fff463c4f34`; installed pin and receipt expect `87481dff3714321184cd7d135cfea555dc141792a3a381980f4f0146d9ca64e0`. | Review and reconcile this local edit under host authority; preserve it before any restoration. Do not overwrite, change expected hashes merely to pass, replace the receipt, or preview/apply while conflicted. |
| `ambiguous.json` | Assessment exits 1 with `Host judgment needs decision, reason and evidence`. `decisions.RULE-1` is a **list**, whereas `upgrades.py:262–264` requires one object with exactly those three fields. No valid assessment matrix is produced. | Reviewer must supply one explicit supported judgment object. If mapping remains unresolved, use `blocked-unknown` or `conflict-requires-owner` with reason and evidence. Correcting JSON shape alone still leaves the same owned-file conflict. |

`RULE-1` cites the verified synthetic archive’s `migration.md` and `policy.md`. For the valid request, the helper accepts its **supplied** `already-satisfied` judgment against custom `notes/policy.md`, whose actual SHA-256 matches `0d2687308c6063d47adc8214d6658ef82b3f69ac8c4616764a501ab962f96467`. These short synthetic texts do not independently establish real policy semantics. No template/site replacement or completion credit follows.

Exact next read-only command for both:

```sh
diff -u /tmp/prs-upgrade-skill-applications/3/kit-a/skills/example/SKILL.md /tmp/prs-upgrade-skill-applications/3/host/.agents/skills/example/SKILL.md
```

After authorized reconciliation and explicit judgment correction, rerun from `.../3/toolkit`:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m project_record upgrade-assess --request /absolute/path/reviewed-request.json
```

Only a ready assessment can proceed to reviewed preview, guards, plan-bound grant including synthetic permission, and external journal. Preserve `records.json` IDs W1/W2, dependency, acceptance, host release and 1/2 fraction. Preparation performed no writes or network actions.
