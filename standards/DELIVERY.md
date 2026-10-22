# Repository and delivery evidence

The canonical repository is [interzettel/project-record-standard](https://github.com/interzettel/project-record-standard). This record distinguishes source installation, hosted checks, website deployment and owner acceptance.

| Work | Evidence status |
| --- | --- |
| Canonical repository | Public repository created by the owner; initial source installation in progress. |
| Composite action | Local entry-point tests passed. Hosted execution awaits the first run. |
| Reusable workflow | Hosted execution awaits the first run. |
| Example website | Public artifact prepared; deployment awaits a passing hosted run and Pages configuration. |
| Keyboard verification | Native browser interaction awaits the deployed site. |
| Screen-reader verification | Actual spoken output has not been verified. Accessibility names and landmarks have been inspected. |
| Owner acceptance | Pending. Repository creation does not imply approval of the standard. |

## Reproduce and deploy

The `Verify and publish the standard` workflow tests the Python runtime, compares browser calculations with the public records, exercises the root composite action and calls the reusable workflow. The Pages deployment depends on both verification jobs.

Only the deploy job receives `pages: write` and `id-token: write`. Source checks use `contents: read`. Pull requests build an artifact but do not deploy. No workflow commits generated status or edits another repository.

The website builder accepts only public, hash-matching files listed in the record build manifest. It renders the standard's guide and adds site navigation to the independently branded reference pages. It does not fetch fresh project data or infer publication from a plan.
