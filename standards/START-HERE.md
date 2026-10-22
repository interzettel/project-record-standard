# Use the project record standard

A project record explains what a project plans to deliver, what work supports it, and what evidence makes the result acceptable. The standard gives those facts shared meanings. Each project keeps its website, typography, colours and visual composition.

## Read the tracker

1. Start with the named percentage and its fraction. Required work, retained work and accepted milestones have different denominators.
2. Open a milestone to read its outcome, exit criteria and next action.
3. Filter the work map or use its list. Open an item to inspect scope, dependencies and available evidence.
4. Read History to distinguish work completed from changes in scope.
5. Read Release readiness for candidate checks. Changelog and deployments show observed delivery; a ready plan is not a publication.

An empty scope displays **Not measured**. Active work earns no partial completion credit. A new scope item can lower a percentage while the completed count stays the same.

## Use it in a new project

Use `establish-project-tracking` to write the project overview, scout repository evidence and propose scoped work. Run `project-record init` with the project name, owner and observation date in an empty staging directory when the project already has files. It creates an empty private local scaffold. The cold profile in [New and existing projects](ADAPTATION-PROFILES.md) defines the inventory, decisions and acceptance needed before public integration.

Define purpose, deliverables, owners and acceptance criteria before filling a roadmap. Choose source authorities and the project brand. Do not add arbitrary tasks to produce an impressive percentage.

## Use it in an existing project

Use `adapt-project-tracking` and the hot profile. Run `project-record adoption-plan` after the manifest maps the actual sources. Inventory the existing tracker, issues, milestone criteria, labels, website routes and generated files. Preserve IDs and prove before/after count parity.

Use the host renderer to add data to the existing website. Replace a source only after review and a recoverable cutover. The [agent workflow guide](AGENT-WORKFLOWS.md) covers setup, adaptation, scope growth, skills installation, status questions and recovery. Individual repository migrations are separate work.

## Connect GitHub

Use stable work IDs in issue titles, for example `[PRINT-014] Export separated plates as a ZIP`. Labels describe work type, priority and area. A milestone represents an accepted checkpoint. A GitHub Project provides planning views.

Declare which system owns each fact. Issues, JSON files and Projects must not compete as writers of the same status. [Issues and GitHub Projects](GITHUB.md) defines the mapping, and [Automation](AUTOMATION.md) explains the action and reusable workflow.

## Build this example

```sh
python3 -m pip install --require-hashes -r requirements-site.txt
PYTHONPATH=src python3 -m project_record pipeline --config examples/projects.json --output .record-build --audience public
PYTHONPATH=src python3 tools/build_site.py --records .record-build --output .site
```

The tracking runtime has no third-party dependencies. The documentation website uses the pinned Markdown package only at build time. Serve `.site/` with a local static server to preview it. Public build destinations must be new or empty.

## Know the evidence limits

The public Prehnite example is pinned to its stated source revision. It does not claim to show the latest repository state or replace the real Prehnite site. The standard's own tracker records the canonical delivery work and pending owner review.

Read [Repository and delivery evidence](DELIVERY.md) for actual hosted runs and deployment observations. [Accessibility evidence](ACCESSIBILITY.md) records tested interactions and remaining manual checks. [PMI alignment](PMI-ALIGNMENT.md) explains the tailored mapping to public PMI guidance; it does not claim certification.
