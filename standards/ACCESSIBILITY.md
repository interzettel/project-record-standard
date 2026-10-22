# Reference-view accessibility review

Review scope: the three local reference presentations and their shared explorers, 22 October 2026. This is a scoped engineering review against selected WCAG 2.2 concerns, not a conformance certification for the reference pages or the existing project websites.

| Concern | Result and evidence |
| --- | --- |
| Text alternatives and structure | History SVGs have names/titles and an adjacent exact-count table. Inspected controls had accessible names. Work maps have readable lists, item IDs and state words/symbols. |
| Colour and contrast | The palette check evaluates the normal-text role pairs used by the references, including signal-button text. In the owner review, 32 role/mode pairs passed 4.5:1, with minimum 4.98:1. This is a role-level check, not a scan of every rendered pixel or hover state. |
| Narrow reflow | All three references fit the 390 px frame check, with 375 px content after the scrollbar and no horizontal page overflow. |
| Text enlargement | Doubling every existing element's authored computed font size initially exposed headline/header overflow. Grid minimums, narrow layouts and wrapping were corrected. Repeating the check produced 375 px content/scroll widths in all three views. This is an instrumented text-resize stress check, not a native browser-zoom result. |
| Focus and selection | Clicking a work item transfers focus to its inspector control. Changing a milestone retains control focus. History drill-down opens the correct milestone/item and focuses the inspector. Tab traversal and assistive-technology announcements were not independently verified in this browser. |
| Navigation | Milestone/item deep links, restored selection and browser history were checked. A main landmark and skip link are supplied. Native keyboard activation of the skip link remains part of the consuming-site verification. |
| Motion | Reduced-motion CSS disables transitions/transforms and smooth scrolling. The reference code has no autoplaying content or timed status mutation. An OS-level reduced-motion toggle was not independently exercised. |
| Target and status behavior | Work tiles and delivery controls use minimum 44 px targets. Status words/icons accompany colour. Work-result announcements are limited to the short result count rather than the entire ledger. |

The adapting agent must test the integrated site with real keyboard navigation, the host's screen-reader/browser combinations, text/viewport zoom, high-contrast settings, long project text, light/dark variants and reduced motion. It must inspect computed host styles; inheriting a brand does not automatically preserve contrast.

References: [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [W3C's explanation of text resizing](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html). The role checker is `tools/check_palette.py`; the internal text-resize fixture is `tests/qa.html` in the owner-review source. Browser screenshots are not included.
