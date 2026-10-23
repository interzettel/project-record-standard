# Upgrading the standard

## Current version and compatibility

Runtime and agent suite **0.4.1** retain record contract **0.2.0**. The validator still reads 0.1.0 and 0.2.0 records. Source IDs and project-owned presentation remain intact. This release adds no schema migration or mass issue renaming. Use [INSTALL.md](https://github.com/interzettel/project-record-standard/blob/main/INSTALL.md) for the verified, pinned source kit; use `pyproject.toml` and `skills/manifest.json` as the version authorities.

Keep the previous toolkit revision/digest, manifest, ownership receipt and generated output before upgrading. Verify the new archive and preview the installer. Apply with `--upgrade` only after reviewing the preview; reconcile edited owned files instead of overwriting them. Re-run source/count parity, semantic checks, history/delivery checks and the host’s relevant interaction checks. Compare immutable IDs and visible denominators.

A 0.4.1 setup/adaptation assessment records L0–L5 readiness, ten evidence dimensions, central assessment links and R0–R4 task limits. These are separate from completion and do not grant autonomy. Existing scope and approvals retain their original meaning.

## Safe update and recovery

Record the old toolkit version, checksum, manifest and generated output. Upgrade in an isolated change. Run source-count parity, semantic checks, history/release tests and the host's relevant interaction checks. Compare immutable IDs and all visible denominators. Keep the old renderer and output available for rollback until cutover is accepted.

Regenerate derived files from authored sources. Do not rewrite source observations to the upgrade date or reset done states. Recover an interrupted build by rerunning the same pinned inputs in an owned output directory. Public builds use an empty directory so stale owner-only files cannot enter the publish artifact.

No command automatically updates GitHub fields, creates a release, deploys a site or awards owner acceptance. These remain named delivery actions with their own authorization and observations.

## Historical 0.1.0 → 0.2.0 contract migration

The original migration note, including vocabulary aliases and renderer integration guidance, is preserved in [dated history](https://github.com/interzettel/project-record-standard/blob/main/progress/history/2026-10-23-before-release/standards--UPGRADING.md). Read it when adapting a 0.1.0 integration. Its implementation-version statement describes that historical package.
