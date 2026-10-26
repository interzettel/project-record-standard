# Source license and attribution decision — proposed

**Status: UNAPPROVED PROPOSAL.** This document and the root `LICENSE` are staged on a **draft PR only**. Do **not** use this branch/PR as evidence that any owner has granted MIT rights. The source owner must first approve [licensing issue #4](https://github.com/interzettel/project-record-standard/issues/4) and the exact grant.

## Why this needs an explicit decision

The published [Project Record Standard v0.4.1](https://github.com/interzettel/project-record-standard/releases/tag/v0.4.1) source tree at `ebc6afb0b977ff3d7605893c73ac63021775c4d3` and current `main` were inspected on **2026-10-26**. Neither exposed a root `LICENSE`, `COPYING` or `NOTICE`; GitHub metadata reported no license; Python and Node package metadata do not specify one. That is an absence of explicit terms, **not** evidence that the project is MIT already. [GitHub licensing docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) explain the default restrictions.

## Proposed grant

- **Candidate for owner review:** MIT (simple and compatible with a reusable, permissively licensed shared standard; not the only possible choice).
- **Proposed notice:** `Copyright (c) 2026 Gökalp Yigit Denktas and Project Record Standard contributors`. The name appears as author of representative source commits. Verify the actual rights-holder(s), contribution agreements and desired copyright notice before merge.
- **Proposed scope after authorized merge:** original code, prose, schemas, original skills and assets for which those rights-holders have authority. External dependencies, separately licensed source, copied templates and third-party brand/assets retain their own terms; list any exceptions when identified. This proposal has **not** completed a full third-party provenance inspection.
- **Alternative choices:** choose an explicitly authorized different license (for example Apache-2.0) and update this proposal, or document that the project will remain proprietary/no-license. The absence of owner choice is **not** consent.

## Historical v0.4.1 coverage is an independent decision

A license newly committed to `main` does **not alter the old v0.4.1 Git tree, release ZIP, or asset digests**. The owner must explicitly state whether they are authorized to grant these terms to original source present in `v0.4.1`. If yes, record an attributable, date-stamped statement naming that exact revision and the exceptions, or ship a new license-bearing release through normal release governance. Do not edit historical SHA256 receipts or announce that v0.4.1 was always MIT.

## Owner acceptance checklist

- [ ] Confirm permission to license all original contributions within declared scope.
- [ ] Choose MIT (or select a different specified license).
- [ ] Confirm the legal copyright notice.
- [ ] Review assets, embedded notices and third-party exceptions.
- [ ] Declare whether and how the grant applies to **v0.4.1** source revision `ebc6afb0b977ff3d7605893c73ac63021775c4d3`.
- [ ] Merge license and update root README + pyproject/license metadata **only after** authorized decisions.
- [ ] Reconcile [Diakrisis DIA-002](https://github.com/interzettel/diakrisis/issues/2) evidence; this is separate from later local runtime/archive verification.

## Compatibility with Diakrisis

Diakrisis currently treats Project Record Standard as a *separate pinned Git submodule*. It has **not** imported its original source into the seven Diakrisis review skills, and this proposal grants no new automated installation or testing permissions.
