# Historical document — captured 23 October 2026 before release preparation

This verbatim document contains successive observations. Its former “current” statements apply only to their original scopes; use the current overview and delivery guide for present status.

# Upgrading the standard

## 0.1.0 to 0.2.0

The implementation version is 0.2.0. The semantic validator reads both 0.1.0 and 0.2.0 records. Existing Prehnite and portfolio source IDs and source files are unchanged. Their adapters emit 0.2.0 projections.

The 0.2.0 schema allows pinned histories, delivery summaries, supplement provenance and tailored governance. A cold project may use a `file-snapshot` with a content digest and a null Git commit before a repository exists. A Git observation still requires an exact 40-character source revision. Do not replace a known Git identity with a local file identity to hide a stale source.

The term work package now follows the deliverable/WBS meaning. The former issue/PR meaning is delivery package. Preserve existing repository terminology through an alias; do not mass-rename historical issues merely to install the new vocabulary.

Install the five `web/` assets together. Existing `mountExplorer` integrations continue to work. `mountDelivery` is optional. Projects can render the exported `history.json` and `delivery.json` themselves. Set `presentation.renderer` to `host` when the project owns its renderer; set real README image/route URLs for its file locations.

## Safe update and recovery

Record the old toolkit version, checksum, manifest and generated output. Upgrade in an isolated change. Run source-count parity, semantic checks, history/release tests and the host's relevant interaction checks. Compare immutable IDs and all visible denominators. Keep the old renderer and output available for rollback until cutover is accepted.

Regenerate derived files from authored sources. Do not rewrite source observations to the upgrade date or reset done states. Recover an interrupted build by rerunning the same pinned inputs in an owned output directory. Public builds use an empty directory so stale owner-only files cannot enter the publish artifact.

No command automatically updates GitHub fields, creates a release, deploys a site or awards owner acceptance. These remain named delivery actions with their own authorization and observations.
