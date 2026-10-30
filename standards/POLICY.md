# Policy catalogue and enforcement boundaries

PRS records what a check proves and what still needs judgment. This catalogue specifies the selected rules for the planned automatic workflow; it does not activate hooks, protected branches, schedulers, MCP or a universal permission engine.

The versioned [catalogue revision 1](https://github.com/interzettel/project-record-standard/blob/main/audit/policy/2026-10-30/catalogue.json) names each rule's source revision, applicability, writer, check point, failure/unknown behavior, trust boundary, bypass, evidence and override authority. It is a research artifact, not an extension to record contract 0.2.0. [Records](RECORDS.md) supplies the information/writer map; [compatibility](COMPATIBILITY.md) supplies adoption and update decisions.

## Rule-to-mechanism matrix

| Stable rule ID | Rule | Available check or guidance | Remaining boundary |
| --- | --- | --- | --- |
| `PRS-ACCOUNT-01` | Count each stable leaf once; containers earn no second credit | core.progress/validate; governance WBS mapping | Distinct IDs describing the same work need judgment; bypass by not calling core |
| `PRS-EVIDENCE-01` | Match evidence kind, subject, result and exact artifact revision | core.policy_satisfied; delivery.release_readiness | Legacy source Done labels are not recertified; revision=None does not pin; source strings do not authenticate observations |
| `PRS-ACCEPT-01` | Attribute acceptance to the designated authority | governance metadata checks plus attributed-source review | Plausible approvedBy/source strings can pass; this core has no identity authentication |
| `PRS-SOURCE-01` | Compare expected source identity with current bytes before writing | policy-check compares selected source bytes with before/current expected SHA-256; #32 owns atomic write preconditions | Digest shape or new computed hash is not compare-and-swap; current core does not prevent stale writes |
| `PRS-SCOPE-01` | Admit required scope only under declared authority or bounded grant | policy-check detects changed scope fields and missing explanations; real admission authority remains external | Valid JSON and complete WBS can include an unapproved new leaf; no authorization proof in core |
| `PRS-PRIVACY-01` | Keep private memory, locators and revealing totals out of public output | core.export_record plus reviewed public selection | Visibility flag can lie; content review and process isolation are separate controls |
| `PRS-OWNED-01` | Write only selected owned outputs; preserve authored inputs | installer ownership plus shared build/export/action/policy destination guard | Does not stop another program or credential holder writing directly |
| `PRS-HISTORY-01` | Preserve prior observation and explain scope/state changes | comparison plus policy-check before/after scope explanations | compare reports selected differences, not every criterion edit or scope permission |
| `PRS-PINS-01` | Separate verified expected pin, observed installation and newer release discovery | pins.verify_installation API; not invoked by this policy request format | Current catalogue does not implement general pin checks or support every runtime |
| `PRS-ELIGIBLE-01` | Select authorized unfinished work with satisfied execution prerequisites | execution.select_work API and installed protocol; not invoked by this policy request format | A reference/cycle check does not verify permission or distinguish all dependency meanings |
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
| CLI / library | Deterministic validation over explicit inputs | Named predicate, input identity, command/result and exact tested revision | A pass covers only supplied facts; direct writes outside the call bypass it. policy-check supplies scoped rule-ID results; required unknown exits3. |
| Local Git or agent hook | Early invocation and after-work capture | Installed hook, runtime/version, event coverage, failure/timeout behavior and actual test | Local configuration can be disabled or skipped. Post-action checks cannot prevent the action already performed. Future #34 owns runtime pilots. |
| Required CI / host rules | Gate the specified merge/release boundary | Actual required-check settings, trusted check producer, exact revision and positive/negative merge tests including bypass actors | Missing/inaccessible settings stay unknown. Other branches, privileged actors and changed workflows can bypass a narrower gate. #33 owns activation proof. |
| Scheduler | Detect missed events, stale collection and release drift | Actual last successful observation, partial coverage, missed-run and retry evidence | Delays/failures retain last success; no silent refresh or zero substitution. #39 owns the observer. |
| Optional MCP | Carry calls to the same core under host permissions | Real client/protocol/version and scoped tool execution | Discovery is not invocation; transport does not authenticate record truth or enlarge authority. #40 owns evaluation. |

## Results, exceptions and ordinary work

The shared read-only interface reports `pass`, `fail`, `unknown` or `not-applicable` per rule and subject. A pass needs the actual predicate and input/artifact revision; it cannot mean every rule passed. Unknown means needed evidence or coverage is unavailable. Not-applicable needs a specific applicability reason; a missing receipt is not an exemption. The implemented policyVersion1 request and policyResultVersion1 report are independent of completion record contract0.2.0; neither adds execution states or authority.

For a claimed completion, acceptance, public export or source write, fail/unknown holds that affected operation. Preserve the proposed work result and actual error for recovery. Continue independent authorized work. A scheduler failure need not stop unrelated coding, but it cannot certify fresh status. Report actionable changes or exceptions instead of emitting a new ticket or owner prompt after each unchanged scan.

Ordinary updates within an existing grant need no repeated approval. An exception records rule ID, subject/revision, bounded scope, reason, designated authority, evidence, disposition and expiry/review trigger when relevant. A bypass attempt is evidence, not approval. Correct invalid structure rather than waiving duplicate accounting. Never manufacture human approval from an agent-written exception or lower a failed check to unknown to hide its result.

## Executed probes and honest gaps

`tests/fixtures/policy/cases.json` contains five paired cases and three limit probes. Run:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_policy.py' -v
```

The probes call existing core functions. They test duplicate accounting, exact evidence matching, attribution structure, source revision mismatch and out-of-scope references. Negative authorization cases deliberately show the current core accepting plausible but unauthenticated approval and scope metadata. An unpinned evidence call also accepts a different revision. Passing these limit probes means the limitation was reproduced, not that unauthorized operations are prevented.

The proposed operational outcome for unauthenticated approval, unapproved scope or a stale write is hold/unknown until the designated source authority resolves it. No compare-and-swap writer, identity verifier or admission engine is supplied here. Pin/selection APIs are available from #30/#3; #32 owns writes and #33 actual host enforcement. The shared evidence/dependency meaning is in STANDARD.

## Primary references and support limits

Inspected on 30 October 2026: [Git hooks](https://git-scm.com/docs/githooks) documents the pre-commit bypass; [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) documents required checks and configurable bypass; [GitHub schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) documents possible delay/drop; [Claude hooks](https://code.claude.com/docs/en/hooks-guide) distinguishes pre/post events and event matching. These rolling documents establish mechanism distinctions, not exact-version PRS adapter support. No host ruleset or installed agent hook was activated/tested in this package. CI execution is recorded separately from enforcement.

No new credential, service, paid inference, consumer migration, distributed skill or release is authorized by this catalogue. Optional mechanisms stay optional. The original catalogue was authored before #29; current execution order remains in progress/execution-plan.md. CLI implementation does not activate host enforcement or publish a release.

## Shared offline API and CLI

Call `project_record.policy.evaluate(request)` with a reviewed JSON-compatible **policyVersion1** request. `evaluate_file(path)`, the CLI and the thin script call that same implementation:

```sh
PYTHONPATH=src python3 -m project_record policy-check --request templates/policy-request.example.json
python3 tools/check_policy.py --request templates/policy-request.example.json
```

The supplied example is synthetic, not a consumer observation. It deliberately checks only an explicit subset. Every report includes all seventeen catalogue rule IDs, required flags, status, scope, actionable reasons, canonical JSON input SHA-256 values, declared source revision/digest/observation and any actually probed source digest. Gate results retain their exact subject/revision. Canonical JSON hashes identify evaluated content, not original file formatting. Relative paths resolve from the caller's working directory. No model, server, extra runtime dependency, network fetch, repair or file write is required.

| Exit | Meaning |
| ---: | --- |
| 0 | Every required predicate passed or was specifically not applicable. This is not whole-catalogue conformance or permission to perform the operation. |
| 1 | At least one required predicate failed; failure takes precedence over unknown. |
| 3 | No required failure, but at least one required predicate is unknown. Hold the affected gate; do not treat this as success. |
| 2 | Invalid request/JSON/file input. CLI argument syntax also uses argparse's exit2. |

`operationAuthorized` and `written` are always false. A caller must use the actual exit result and configured authority, not search stdout for a passing row. Non-required unknowns remain visible. Rules outside this interface's implemented scope are not silently skipped or relabelled not-applicable: requiring such a rule yields unknown/exit3 with its missing mechanism and responsible package.

### Request and actual predicates

The request contains `policyVersion`, `record` (a normalized source observation), a nonempty list of `requiredRules`, and optional `before`, `gates`, `source`, `audience`, `output`, `changes`. Unknown top-level fields and rule IDs are input errors. The policy request itself must come from reviewed host configuration; an untrusted worker cannot choose which quality checks or rules authorize its work. The command authenticates neither that configuration nor its receipts.

| Rule | Implemented predicate and inputs | Boundary |
| --- | --- | --- |
| ACCOUNT | Existing validator/summarizer on current and any prior record; always required | Includes unique IDs, references and structural governance/history checks; distinct IDs for duplicate meaning still need judgment. |
| EVIDENCE | `gates`: subject, exact immutable revision, allOf/anyOf policy and attributed receipts; calls existing policy_satisfied | Does not run tests or interpret prose criteria. Empty/missing policy or observations are unknown; wrong-revision, failed or malformed proof cannot certify the gate. |
| SOURCE | `source`: actual local file `path` and expectedSha256 matching the supplied before/current source identity | Actually hashes those bytes. Missing/inaccessible is unknown, mismatch fails. No lock, compare-and-swap, multi-file atomicity or write occurs. |
| HISTORY | `before` for the same project; existing comparison/timeline order plus changed-field explanations | Required on a supplied comparison. Detects removed/added/membership/cancelled IDs, criterion/dependency/placement, group/milestone scope, visibility and governance changes. Distinct source observations use the existing timeline guard; a comparison of the same identity is not a new history point. Supplied prior facts do not prove archival persistence. |
| SCOPE | The same changed-field comparison | Unexplained changes fail; explained changes remain unknown for admission authority. Unchanged scope needs no newly invented approval. Metadata cannot authenticate a scope decision. |
| PRIVACY | Explicit `audience`, calling existing export_record for public | Public is automatically required. Known private input is refused. Owner-local assessment is specifically not applicable; visibility flags do not classify hidden content. |
| OWNED | `output.path`, calling the same new/empty nonsymlink directory guard as action/public build/export | Automatically required when supplied. Observes current destination only; creates/reserves nothing and prevents no later race or direct-write bypass. Existing owner build/export reuse policy remains distinct. |
| ACCEPT | Compare newly accepted outcomes with the prior observation | An unchanged all-gate-items derivation can pass in that limited scope. New source-state acceptance remains unknown for identity/authority; historical acceptance is left unchanged. |

PINS, ELIGIBLE, DELIVERY and FRESH retain their existing specialized APIs; this request format does not invoke them. HOST, EVENT, TRANSPORT, FEEDBACK and OVERHEAD require their own actual boundary/effectiveness evidence. Their catalogue results remain unknown here, with actionable reasons. A successful schema check cannot stand in for them.

Accounting is always required. Supplied gates/source/output, a public audience and a before comparison automatically require their corresponding predicates. New Done transitions automatically require evidence coverage; if a leaf declares `implementationRevision`, its gate must target that identity. Missing coverage is unknown. The reviewed gate policy defines the applicable artifact when no such optional field exists; the checker does not infer it from prose. New acceptance and changed scope automatically require their relevant rules. This prevents omitting a rule name from silently certifying an explicitly supplied operation context.

Change explanations use `{kind, id, reason, source}` for each observed scope field. Kinds are `added`, `removed`, `membership`, `cancelled`, `restored`, `criterion`, `dependencies`, `placement`, `group-scope`, `milestone-scope`, `visibility`, `governance`. Retain these as sourced explanations, not another completion ledger. Supplying plausible approval text does not turn unknown admission into a pass. Ordinary state updates with unchanged scope use their existing grant; no new owner prompt is implied.

Reports are local diagnostics and may contain private identifiers. They are not an approved public projection. A caller owns safe report handling and the actual configured merge/write/export boundary. #32 must supply transactional writing/recovery, #33 must demonstrate required host invocation/bypass behavior, and later adapter/real-session packages must prove their own coverage. This command alone establishes none of them.
