# Repository and delivery evidence

## Current package — 0.4.1

The implementation scope is complete at 18/18 required items and 4/4 milestone gates. The package has eleven skills, the portable readiness contract and record contract 0.2.0. [Verification](https://github.com/interzettel/project-record-standard/blob/main/VERIFICATION-public.md) states the evidence and its limits. Completion, a release plan, publication and deployment remain separate observations.

The GitHub release channel is [v0.4.1](https://github.com/interzettel/project-record-standard/releases/tag/v0.4.1). It was published at **2026-10-23T18:28:27Z** from `ebc6afb0b977ff3d7605893c73ac63021775c4d3`, with **4/4 hosted gates (100%)** passed in [run 40003462737](https://github.com/interzettel/project-record-standard/actions/runs/40003462737). The tag and all four asset digests were read back and matched the verified local build. Its publication record is in `examples/sources/standard/delivery.json`; a link alone does not establish publication. The release assets are the versioned public source ZIP, `CHANGELOG.md`, `INSTALL.md` and `SHA256SUMS`. The ZIP also carries per-file `checksums.sha256`.

Use [the installation procedure](https://github.com/interzettel/project-record-standard/blob/main/INSTALL.md) to verify and extract the package. Record both its commit and archive digest in the consuming project. [Upgrading](UPGRADING.md) describes compatibility and recovery. Installation prepares guidance; the agent still scouts the project and resolves project-specific decisions.

Archive SHA-256: `a46cdcea938eb987b936497a22db8eab07106aad7dd12a8cfe10b4ad41f74607`. [The publication receipt](https://github.com/interzettel/project-record-standard/blob/main/progress/releases/v0.4.1.json) lists every asset, digest and hosted job. The tagged kit retains its pre-publication source observation; this subsequent receipt records what was actually published without replacing those bytes.

## Verification and publication gates

The canonical CI workflow checks authored records, the composite action, Python and JavaScript suites, skills, palette roles, site generation and README parity. It also exercises the reusable workflow. Pages depends on both verification jobs.

The explicit v0.4.1 release commit invoked a publication job only after verification, reusable build and Pages succeed on that exact commit. The job builds the public source archive, checks a fresh extraction and every contained hash, runs the extracted CLI and public pipeline, previews/applies the skill installer and proves a second installation has no changes. It creates an exact-commit tag (failing if that tag already exists), creates a draft GitHub release, uploads all four assets, then publishes it. Existing release tags are never overwritten.

Source checks retain `contents: read`. Only the publication job receives `contents: write`; only Pages deployment receives `pages: write` and `id-token: write`. Pull requests cannot publish or deploy. No job updates another repository or commits generated status.

The website builder accepts public, hash-matching files listed in the record build manifest. It renders guide navigation and independently branded references without fetching fresh source observations. Private audit fixtures are outside the distribution and Pages.

## Scoped acceptance and history

Native Edge 200%/400% zoom was inspected. Narrator operation is owner-confirmed, without agent-captured speech, versions or transcript. The 400% viewport was 638 CSS px; the separate 320px fixture evidence stays separate. The scoped WCAG review does not establish full conformance. See [accessibility](ACCESSIBILITY.md) and the linked verification receipts.

Historical release plans and deployment receipts keep their original revisions and missing gates. Current publication does not retroactively certify those earlier candidates. Superseded delivery narrative is preserved in [dated history](https://github.com/interzettel/project-record-standard/blob/main/progress/history/2026-10-23-before-release/standards--DELIVERY.md).
