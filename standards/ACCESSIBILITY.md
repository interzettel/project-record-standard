# Reference-view accessibility review

Review scope: the three local reference presentations and their shared explorers, 22 October 2026. This is a scoped engineering review against selected WCAG 2.2 concerns, not a conformance certification for the reference pages or the existing project websites.

| Concern | Result and evidence |
| --- | --- |
| Text alternatives and structure | History SVGs have names/titles and an adjacent exact-count table. Inspected controls had accessible names. Work maps have readable lists, item IDs and state words/symbols. |
| Colour and contrast | The palette check evaluates the normal-text role pairs used by the references, including signal-button text. In the owner review, 32 role/mode pairs passed 4.5:1, with minimum 4.98:1. This is a role-level check, not a scan of every rendered pixel or hover state. |
| Narrow reflow | All three references fit the 390 px frame check, with 375 px content after the scrollbar and no horizontal page overflow. |
| Text enlargement | Doubling every existing element's authored computed font size initially exposed headline/header overflow. Grid minimums, narrow layouts and wrapping were corrected. Repeating the check produced 375 px content/scroll widths in all three views. This is an instrumented text-resize stress check, not a native browser-zoom result. |
| Focus and selection | Clicking a work item transfers focus to its inspector control. Changing a milestone retains control focus. History drill-down opens the correct milestone/item and focuses the inspector. Native Tab traversal and keyboard activation were later checked in Edge on the canonical Pages site; actual assistive-technology announcements remain unverified. |
| Navigation | Milestone/item deep links, restored selection and browser history were checked. A main landmark and skip link are supplied. Native skip-link activation passed on the canonical tracker and guide; consuming-site integrations still require their own check. |
| Motion | Reduced-motion CSS disables transitions/transforms and smooth scrolling. The reference code has no autoplaying content or timed status mutation. An OS-level reduced-motion toggle was not independently exercised. |
| Target and status behavior | Work tiles and delivery controls use minimum 44 px targets. Status words/icons accompany colour. Work-result announcements are limited to the short result count rather than the entire ledger. |

The adapting agent must test the integrated site with real keyboard navigation, the host's screen-reader/browser combinations, text/viewport zoom, high-contrast settings, long project text, light/dark variants and reduced motion. It must inspect computed host styles; inheriting a brand does not automatically preserve contrast.

References: [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [W3C's explanation of text resizing](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html). The role checker is `tools/check_palette.py`; the internal text-resize fixture is `tests/qa.html` in the owner-review source. Browser screenshots are not included.


## Native Edge verification of the canonical Pages site

On 22 October 2026, the deployed tracker and guide were tested in the connected Edge browser. A native Tab press reached the skip link; Enter moved focus to the main landmark. Tab reached Appearance, and Enter changed its mode while retaining focus. Tab traversal and Space activated Release readiness. A native End key on the milestone selector chose the final milestone, updated the URL and retained selector focus.

Enter on a work tile opened its inspector and moved focus to Close. Space closed it and restored focus to the original tile. Enter switched to the readable list while retaining its view-control focus. The guide skip link also moved focus to its main content. The guide and Prehnite reference had 375 px content/scroll widths in a 390 px viewport.

A native Enter on a Prehnite milestone card exposed an off-screen focus defect: the page scrolled to the workbench while focus stayed on the original card. The deployed fix at `8ca75f2fdcf8da51d554fd9c3a0ca1ef551cd976` focuses the selected milestone heading. Retesting both the standard and Prehnite cards kept that heading in view; in the 390 px Prehnite check, it occupied y=423–446 within the 844 px viewport. The next Tab reached the selected milestone’s remaining criterion.

These checks exercise real browser keyboard behavior. They do not verify a screen reader's spoken output. Browser controls expose the page's semantic structure, but do not provide audio or control of a native assistive-technology application. STD-13 remains open for that verification.

## Complete the screen-reader check

Use the deployed revision with a named browser and screen reader, and record both versions. Confirm that the skip link reaches the main landmark, headings describe the selected milestone, filters announce names and values, item buttons announce IDs and states, and result changes announce only the short count. Open and close an item to confirm reading order and focus restoration. Inspect the history chart through its adjacent exact-count table and expand candidate evidence. Record failures and the source revision tested before marking STD-13 complete.
