# Policy catalogue and enforcement boundaries

PRS records what a check proves and what still needs judgment. This catalogue specifies the selected rules for the planned automatic workflow; it does not activate hooks, protected branches, schedulers, MCP or a universal permission engine.

The versioned [catalogue revision 1](https://github.com/interzettel/project-record-standard/blob/main/audit/policy/2026-10-30/catalogue.json) names each rule's source revision, applicability, writer, check point, failure/unknown behavior, trust boundary, bypass, evidence and override authority. It is a research artifact, not an extension to record contract 0.2.0. [Records](RECORDS.md) supplies the information/writer map; [compatibility](COMPATIBILITY.md) supplies adoption and update decisions.

## Rule-to-mechanism matrix

| Stable rule ID | Rule | Available check or guidance | Remaining boundary |
| --- | --- | --- | --- |
| `PRS-ACCOUNT-01` | Count each stable leaf once; containers earn no second credit | core.progress/validate; governance WBS mapping | Distinct IDs describing the same work need judgment; bypass by not calling core |
| `PRS-EVIDENCE-01` | Match evidence kind, subject, result and exact artifact revision | core.policy_satisfied; delivery.release_readiness | Legacy source Done labels are not recertified; revision=None does not pin; source strings do not authenticate observations |
| `PRS-ACCEPT-01` | Attribute acceptance to the designated authority | governance metadata checks plus attributed-source review | Plausible approvedBy/source strings can pass; this core has no identity authentication |
| `PRS-SOURCE-01` | Compare expected source identity with current bytes before writing | adapter digests available; future #30/#32 precondition check | Digest shape or new computed hash is not compare-and-swap; current core does not prevent stale writes |
| `PRS-SCOPE-01` | Admit required scope only under declared authority or bounded grant | governance reference checks; future admission policy; contributor judgment | Valid JSON and complete WBS can include an unapproved new leaf; no authorization proof in core |
| `PRS-PRIVACY-01` | Keep private memory, locators and revealing totals out of public output | core.export_record plus reviewed public selection | Visibility flag can lie; content review and process isolation are separate controls |
| `PRS-OWNED-01` | Write only selected owned outputs; preserve authored inputs | agents installer; build/run_action dedicated-output checks | Does not stop another program or credential holder writing directly |
| `PRS-HISTORY-01` | Preserve prior observation and explain scope/state changes | compare/timeline checks plus update-project-progress guidance | compare reports selected differences, not every criterion edit or scope permission |
| `PRS-PINS-01` | Separate verified expected pin, observed installation and newer release discovery | existing skill byte receipts; future #30 pin assessment | Current catalogue does not implement general pin checks or support every runtime |
| `PRS-ELIGIBLE-01` | Select authorized unfinished work with satisfied execution prerequisites | router/agent-workflows guidance; future #3 selection contract | A reference/cycle check does not verify permission or distinguish all dependency meanings |
| `PRS-DELIVERY-01` | Separate work, verification, acceptance, publication and deployment | delivery summaries, matching receipts and source review | Synthetic attributed receipts can be structurally valid; network publication is separately observed |
| `PRS-HOST-01` | Prove required checks and permitted bypass at the actual boundary | CI invokes core; #33 activation receipt remains future | Workflow success/YAML presence is not protected merge; admin/bypass and alternate branches matter |
| `PRS-EVENT-01` | Capture after-work results and replay without duplicate or stale writes | future #32/#34 journal and lifecycle adapters | Hooks may be absent/disabled, miss tool paths or run after a write; no adapter installed by this policy |
| `PRS-FRESH-01` | Observe drift without replacing the last successful facts | status collection receipts; future #39 observer | Schedule can be delayed/dropped; time elapsed is not a successful collection |
| `PRS-TRANSPORT-01` | Optional MCP delegates to the same core and authority | future #40 thin transport; no second policy engine | Tool discovery does not force use; process credentials and client coverage limit enforcement |
| `PRS-FEEDBACK-01` | Report only actual encountered shared gaps, safely and without duplicates | FEEDBACK guidance; future #36 route | No ticket quota or background idea generation; a tool cannot judge all relevance/privacy |
| `PRS-OVERHEAD-01` | Measure usefulness and correction burden before claiming unattended support | future #35/#37 actual sessions and multiple producer/runtime paths | Metadata/synthetic cases or one model in many lenses do not establish effectiveness |

## Choose the control surface

| Mechanism | Responsibility | Evidence before claiming enforcement | Failure and bypass |
| --- | --- | --- | --- |
| Skills / AGENTS | Work selection, relevance, criteria, judgments and exceptions | Actual runner discovery/application coverage | Guidance may be missed or ignored; it does not grant permissions. |
| CLI / library | Deterministic validation over explicit inputs | Named predicate, input identity, command/result and exact tested revision | A pass covers only supplied facts; direct writes outside the call bypass it. Future #31 supplies shared rule-ID results. |
| Local Git or agent hook | Early invocation and after-work capture | Installed hook, runtime/version, event coverage, failure/timeout behavior and actual test | Local configuration can be disabled or skipped. Post-action checks cannot prevent the action already performed. Future #34 owns runtime pilots. |
| Required CI / host rules | Gate the specified merge/release boundary | Actual required-check settings, trusted check producer, exact revision and positive/negative merge tests including bypass actors | Missing/inaccessible settings stay unknown. Other branches, privileged actors and changed workflows can bypass a narrower gate. #33 owns activation proof. |
| Scheduler | Detect missed events, stale collection and release drift | Actual last successful observation, partial coverage, missed-run and retry evidence | Delays/failures retain last success; no silent refresh or zero substitution. #39 owns the observer. |
| Optional MCP | Carry calls to the same core under host permissions | Real client/protocol/version and scoped tool execution | Discovery is not invocation; transport does not authenticate record truth or enlarge authority. #40 owns evaluation. |

## Results, exceptions and ordinary work

The future shared interface reports `pass`, `fail`, `unknown` or `not-applicable` per rule and subject. A pass needs the actual predicate and input/artifact revision; it cannot mean every rule passed. Unknown means needed evidence or coverage is unavailable. Not-applicable needs a specific applicability reason; a missing receipt is not an exemption. This vocabulary is a design requirement for #31, not a new command implemented here.

For a claimed completion, acceptance, public export or source write, fail/unknown holds that affected operation. Preserve the proposed work result and actual error for recovery. Continue independent authorized work. A scheduler failure need not stop unrelated coding, but it cannot certify fresh status. Report actionable changes or exceptions instead of emitting a new ticket or owner prompt after each unchanged scan.

Ordinary updates within an existing grant need no repeated approval. An exception records rule ID, subject/revision, bounded scope, reason, designated authority, evidence, disposition and expiry/review trigger when relevant. A bypass attempt is evidence, not approval. Correct invalid structure rather than waiving duplicate accounting. Never manufacture human approval from an agent-written exception or lower a failed check to unknown to hide its result.

## Executed probes and honest gaps

`tests/fixtures/policy/cases.json` contains five paired cases and three limit probes. Run:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_policy.py' -v
```

The probes call existing core functions. They test duplicate accounting, exact evidence matching, attribution structure, source revision mismatch and out-of-scope references. Negative authorization cases deliberately show the current core accepting plausible but unauthenticated approval and scope metadata. An unpinned evidence call also accepts a different revision. Passing these limit probes means the limitation was reproduced, not that unauthorized operations are prevented.

The proposed operational outcome for unauthenticated approval, unapproved scope or a stale write is hold/unknown until the designated source authority resolves it. No compare-and-swap writer, identity verifier or admission engine is supplied here. #30/#32 own source pins/write preconditions; #3/#31/#33 own selection/check/enforcement integration. Evidence-stage policy remains #6's work.

## Primary references and support limits

Inspected on 30 October 2026: [Git hooks](https://git-scm.com/docs/githooks) documents the pre-commit bypass; [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) documents required checks and configurable bypass; [GitHub schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) documents possible delay/drop; [Claude hooks](https://code.claude.com/docs/en/hooks-guide) distinguishes pre/post events and event matching. These rolling documents establish mechanism distinctions, not exact-version PRS adapter support. No host ruleset or installed agent hook was activated/tested in this package. CI execution is recorded separately from enforcement.

No new credential, service, paid inference, consumer migration, distributed skill or release is authorized by this catalogue. Optional mechanisms stay optional. The next package, #29, maps portable layouts/naming onto these writers and boundaries.
