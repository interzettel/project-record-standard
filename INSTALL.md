# Install Project Record Standard 0.4.1

Use Python 3.10 or newer. The CLI has no runtime dependencies. The complete source kit includes the agent skills, examples, renderer and build tools; a Python-only package is not a substitute for it.

## Verify and extract

Download these four assets from [release v0.4.1](https://github.com/interzettel/project-record-standard/releases/tag/v0.4.1) into one empty directory: `project-record-standard-0.4.1.zip`, `CHANGELOG.md`, `INSTALL.md` and `SHA256SUMS`. On Linux or a compatible shell with `sha256sum`:

```sh
sha256sum -c SHA256SUMS
python3 -m zipfile -e project-record-standard-0.4.1.zip .
cd project-record-standard
sha256sum -c checksums.sha256
PYTHONPATH=src python3 -m project_record check --config examples/projects.json
PYTHONPATH=src python3 -m project_record pipeline --config examples/projects.json --output ../record-smoke --audience public
```

On stock macOS, use `shasum -a 256 -c SHA256SUMS` and `shasum -a 256 -c checksums.sha256` in place of the two `sha256sum` commands.

Use a new empty output path for each public build. The release job runs these checks on a fresh extraction. `SHA256SUMS` checks the downloaded bytes; record the release commit as well. Checksums do not independently establish publisher identity.

On PowerShell, compare `(Get-FileHash .\project-record-standard-0.4.1.zip -Algorithm SHA256).Hash` with the corresponding SHA256SUMS entry. Extract with `Expand-Archive`, set `$env:PYTHONPATH = 'src'`, and run the same Python commands without the `PYTHONPATH=src` prefix. Use `Get-FileHash` to compare the remaining assets and extracted files when verifying the whole kit.

## Prepare the project

Keep the verified toolkit at a recorded path, commonly `tools/project-record-standard/` inside the target repository. From the toolkit root, replace `/absolute/path/to/project` with the target path:

```sh
PYTHONPATH=src python3 -m project_record install-skills --toolkit . --target /absolute/path/to/project
PYTHONPATH=src python3 -m project_record install-skills --toolkit . --target /absolute/path/to/project --apply
```

The first command previews. Applying preserves existing AGENTS text and refuses conflicts with owned files. Repeating the same installation produces no changes. For an upgrade, use the [ownership and recovery procedure](standards/UPGRADING.md).

Give the agent this request:

```text
Read AGENTS.md and .agents/skills/use-project-records/SKILL.md.
Start project tracking with the verified Project Record Standard v0.4.1.
Inspect the project and accessible GitHub sources before asking questions.
Choose establishment or adaptation from the existing source authority.
Keep branding, IDs and counts. Assess current/target L0–L5 readiness and
R0–R4 task limits separately from completion. Ask focused questions about
unresolved outcome, scope, priorities and acceptance decisions, then
prepare the overview, scoped plan, milestones, roadmap and branded views.
```

If the runner does not discover `.agents/skills/`, point it there or use its supported skill location. Installing guidance does not start a background agent, create credentials, schedule work, or authorize merges and deployment.

## Build the optional example site

Site generation additionally needs the hash-pinned Markdown dependency. JavaScript regression tests need Node 22 and the locked development dependencies:

```sh
python3 -m pip install --require-hashes -r requirements-site.txt
npm ci --ignore-scripts --no-audit --no-fund
PYTHONPATH=src python3 -m unittest discover -s tests -v
npm test
PYTHONPATH=src python3 tools/check_skills.py
python3 tools/check_palette.py
PYTHONPATH=src python3 tools/build_site.py --records ../record-smoke --output ../record-site
PYTHONPATH=src python3 tools/check_readme.py --records ../record-smoke
```

Serve `record-site` with a local HTTP server to inspect the example. Adapting a project connects reviewed output to its existing site and deployment process. The source kit does not replace that site.

## Development tree and future support

The instructions above describe the immutable v0.4.1 kit. Current main also contains unreleased planning/tooling changes. Its development checks use the pinned `.python-version` and `.node-version`; Python3.10 is now end-of-life, so choose a supported Python for new installations. A future minimum-version change belongs to the next declared release, with its compatibility notes. Do not replace the v0.4.1 checksum with a development archive. See [compatibility](standards/COMPATIBILITY.md).
