# Project-owned presentation

## What is shared

Share vocabulary, percentage calculations, claim boundaries, information order, stable links and interaction outcomes. Projects retain their fonts, palette roles, logos, imagery, page geometry, navigation, voice and existing site technology. A host can use the normalized record with its own renderer, or mount the optional explorer inside its own shell.

There is no organization-wide visual skin and no required qurultai imitation. A colour switch on one generic dashboard is insufficient. Prehnite's cards and phases and the portfolio's studio typography, milestone rows and monochrome work map are separate reference compositions backed by the same calculation code.

The brand token file points to the project's accepted source. The component uses scoped styles and inherits host typography. It must not reset `html`, `body`, global headings or the site's navigation. Existing webfonts stay under the site's own loading and licence policy. The reference examples use the documented font stacks without inventing a replacement wordmark or bundling unreviewed fonts.

## Explanation order

Write in plain, concrete technical English. Prefer a specific verb and object to an abstract noun chain. Use the following order when it helps the reader:

1. What someone can do or what outcome is being pursued.
2. What works today and where it is available.
3. How the important parts connect, with only the detail needed here.
4. Current progress and its exact scope.
5. The remaining gate, limitation or next action.
6. How to try it, inspect evidence or contribute.

For a work package, use Outcome → Scope → Acceptance → Evidence → Dependencies → Next action. For a difficult algorithm, introduce the purpose and inputs before the sequence, then show the output and limits. Link deeper implementation detail instead of placing it ahead of the result.

## README

Lead with the product and a way to try or understand it. The progress module is a compact front door: one or two named percentages, completed/required counts, active outcome, next gate, observation and links. A generated SVG has meaningful alternative text and an equivalent Markdown table.

Use project-owned colours and type. Keep the dense work map behind a disclosure or link. A GitHub image cannot be the sole interface for hover details; tiny unlabeled rectangles must not carry information unavailable in text. At narrow widths, the table and direct scope links remain usable even when the graphic is scaled down. Provide a compact/mobile image variant when the project's artwork needs one.

The README and Pages use the same source record and metric names. A live CI badge links to its actual workflow. Dated test counts and deployment observations are labelled snapshots. A static green badge does not establish ongoing health.

## Interactive Pages

The site's own navigation can expose Overview, Roadmap, Work, Changes, Releases and Evidence. These are content roles, not compulsory route names or tabs. An adapting agent fits them to the site's existing architecture and preserves URLs and aliases.

Roadmap starts with milestones: outcome, horizon, work percentage, accepted gate count and next action. Exact dates are optional and marked target versus commitment. Work exploration shows the epic/group hierarchy and stable leaf IDs. A readable list is equivalent to the map. Search and status/owner/area filters preserve context.

Selection has an immediate visible response. Tapping a work tile reveals its title, criterion, state, owner, dependency links and proof. The next action stays close to the selected scope. Detail appears near the current work, rather than at the bottom of hundreds of cells. Links to scopes and work items survive reload; browser Back restores the previous selection. Editing opens the source issue or file.

The optional component implements local search, state and denominator filters, selectable IDs, a map/list switch, dependencies and a selected-item inspector. The example host owns milestone navigation and deep links. It remains possible to replace every visual component without changing the data meanings.

## Interaction and accessibility acceptance

- Use native links, buttons, selects, inputs and disclosure elements; all essential actions work without hover.
- State uses words or symbols as well as colour. Percentage bars have accessible names, values and exact count text.
- Preserve keyboard focus when selecting or closing detail and when switching views. Selectable maps have readable-list equivalents.
- Use clear hit targets, hover/selected/pressed states and short, nonessential motion; honour reduced motion.
- Check 390 px and desktop widths, keyboard-only operation, 200% text zoom and the project's existing light/dark themes. Reflow long titles; do not hide the main title behind repeated ellipses.
- Keep normal page scrolling. Avoid a default of multiple independently scrolling panes.
- Render errors, stale observations, missing evidence and empty denominators explicitly.
- Check the actual branded component contrast; a token table or screenshot alone does not establish accessibility compliance.

## Original tracker ideas retained

The visual review in `audit/VISUAL-REVIEW.md` documents the actual rendered source graphics. Borrow the portfolio's hierarchy and large percentages, Prehnite's phase cards, Wearhouse's readable IDs, Personal Agent Stack's next-proof section, and Writing Kitchen's research/build separation. On Pages, add selection and inspection to these ideas. Preserve their project-specific expression.
