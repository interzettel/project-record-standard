# Repository and delivery evidence

The canonical repository is [interzettel/project-record-standard](https://github.com/interzettel/project-record-standard). This record distinguishes source installation, hosted checks, website deployment and owner acceptance.

| Work | Evidence status |
| --- | --- |
| Canonical repository | [Public source installed](https://github.com/interzettel/project-record-standard/tree/10a9e6501a9ed64f57ad139a56e3fc9fdd8b99ef). Private owner fixtures are excluded. |
| Composite action | Passed in [hosted verification](https://github.com/interzettel/project-record-standard/actions/runs/39800961253/job/119901169586): 18 Python tests and six browser-calculation tests. |
| Reusable workflow | Passed in the [reusable record job](https://github.com/interzettel/project-record-standard/actions/runs/39800961253/job/119901170257), including artifact upload. |
| Example website | [Pages deployment succeeded](https://github.com/interzettel/project-record-standard/actions/runs/39800961253/job/119901281252) at 2026-10-22T15:02:47Z. Tracker, guide and Prehnite routes were opened in Edge. |
| Keyboard verification | Native Edge keyboard checks exercised skip links, filters, item inspection, focus restoration and view controls. A milestone card left focus off screen; its fix awaits deployed retest. |
| Screen-reader verification | Actual spoken output has not been verified. Accessibility names and landmarks have been inspected. |
| Owner acceptance | Pending. Repository creation does not imply approval of the standard. |

## Reproduce and deploy

The `Verify and publish the standard` workflow tests the Python runtime, compares browser calculations with the public records, exercises the root composite action and calls the reusable workflow. The Pages deployment depends on both verification jobs.

Only the deploy job receives `pages: write` and `id-token: write`. Source checks use `contents: read`. Pull requests build an artifact but do not deploy. No workflow commits generated status or edits another repository.

The website builder accepts only public, hash-matching files listed in the record build manifest. It renders the standard's guide and adds site navigation to the independently branded reference pages. It does not fetch fresh project data or infer publication from a plan.

The first run exposed an artifact-upload failure because the output directory begins with a dot. The corrected run explicitly includes generated hidden-directory contents. This was a hosted integration finding; it was not covered by the local entry-point test.
