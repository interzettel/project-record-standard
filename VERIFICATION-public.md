# Public-source distribution verification

Version 0.2.0, 22 October 2026.

The source kit has an explicit file selection and per-file SHA-256 checksums. Its examples use public inputs. Owner-review output, private fixtures, browser screenshots and generated Python metadata are excluded.

The included tests cover scope/state accounting, observation order, evidence gates, release-channel distinctions, governance approvals and WBS ownership, private-input guards, marked README preservation, cold setup, non-destructive hot inspection, host-owned rendering, manifest hashes, action execution and deterministic packaging. The full owner review additionally exercises the repository-specific reference adapters and browser calculation parity.

The source archive is extracted and its included Python tests, pipeline and repackaging command are run in that extraction. A Python wheel is also built, installed in an isolated environment and used to build the standard reference with its installed browser assets. These are local observations, not hosted GitHub Actions or deployment observations.

The browser review checks real-data history/drill-down, candidate gates, changelog/coverage states, narrow layouts, appearance and doubled-text reflow. See `standards/ACCESSIBILITY.md` for exact scope and remaining keyboard/assistive-technology checks. Review evidence does not award owner acceptance.

No native project fields, issues, labels, target websites, remote repositories, releases, schedules or deployments are changed by these checks. The adaptation skill has not been authored or installed. PMI alignment is a documented tailoring map based on the cited public sources; it is not an endorsement or full-standard compliance assessment.
