# Pinned offline handoff

This boundary is demonstrated by `tests/fixtures/handoff/` through the existing `load_config`, `validate`, `summarize` and `policy_satisfied` functions. It is an offline synthetic example for contract **0.2.0**, not a new runtime adapter, installed service or consumer protocol implementation.

## Identities and writers

| Field or identity | Writer and meaning |
| --- | --- |
| `project.id` + `items[].id` | Canonical project manifest and ledger identify the accounting leaf together. Count the leaf once. |
| `items[].state`, `required`, `dependsOn`, `criterion`, `completionBasis` | Canonical ledger author records scoped work and its evidence-based completion decision. A worker's status does not automatically write these fields. |
| `groups`, `milestones`, `gateItemIds` | Canonical ledger author owns grouping and outcome gates; these add no accounting leaves. |
| `milestones[].acceptanceRule`, `sourceAccepted` | Project's declared acceptance writer records outcome acceptance. The example uses `source-state` and explicit false. |
| `items[].evidence` | Canonical author retains attributed worker/check observations: kind, exact subject, result, implementation revision, source, producer and observation. Structural validation cannot authenticate their producers. |
| `source.path`, `kind`, `commit`, `observedOn`, `authority` | Manifest declares the source observation; loader derives `source.sha256` from the actual input bytes. A build date does not refresh that observation. |
| `contractVersion` | Source declares the supported record contract; the fixture pins 0.2.0 and the schema bytes. It does not introduce a new required contract field. |
| Consumer task ID/status/implementation revision | Synthetic consumer task record owns execution facts, linked to the PRS project and leaf. No consumer task is appended to `items`. |
| Optional A2A task ID | Transport correlation only, explicitly null in this example. Neither another accounting leaf nor an authority token. |
| `metrics`, group/milestone progress and `accepted` | Existing calculator derives read-only views under the declared acceptance rule. |

The adjacent `handoff.json` is a **test envelope**, not an input understood or validated by the core loader. Its consumer task is a local example named for the planned Qurultai mapping. No real Qurultai schema, endpoint, credentials, message exchange or A2A wire-format conformance was inspected or implemented here. Host integration must validate its actual mapping under its own authorized package.

## Reproduce the example

From a reviewed checkout or an extracted unpublished development source kit:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_handoff.py' -v
```

`projects.json` selects a one-leaf `ledger.json` file snapshot. `handoff.json` retains both files' SHA-256 values, the source observation, contract version and exact reader/schema identities anchored to toolkit commit `d1d609b5fbf72b33e7b030aab18fd265b7a18e91`. The input source is new synthetic data, so its commit is explicitly null; its content digest supplies its exact identity. The worker implementation's 40-hex identity is also synthetic and is not claimed to be a resolvable Git object. Changed pinned fixture/reader bytes require a deliberate fixture reassessment, not silently refreshed test values.

The worker reports completed execution with matching implementation and test receipts. The authored leaf is Done against the example's work policy. Its milestone remains unaccepted: no owner-review receipt exists, and `sourceAccepted` remains false. With this source-state rule, progress is **1/1**, accepted milestones **0/1**. Hosts selecting `all-gate-items` deliberately choose a different derived acceptance rule; do not apply that rule to an owner-acceptance outcome by accident.

The six tests check byte pins, one-to-one mapping, the missing acceptance gate, deterministic offline replay without changing input bytes, basic receipt subject/revision mismatches, duplicate leaf rejection and unsupported contract rejection. The envelope's false permission flags are illustrative declarations; they grant nothing and are not a security sandbox. No network calls, runtime permission changes or external writes are part of this path.

## Remaining gates

The first six tests alone establish the happy path. The adversarial reference below extends it under **PRS-HANDOFF-02 / #16**; neither fixture establishes production transaction safety or live consumer behavior. Existing `policy_satisfied` can accept unpinned calls when revision is null; this example always supplies an exact implementation revision. It matches metadata, not signatures or human authority.

M5 outcome acceptance remains Yiğit's decision and also depends on its other declared work gates. No release, consumer migration, Hermes launch, Qurultai launch or unattended operation follows from this fixture or a merged PR. Published v0.4.1 and the independent contract version remain unchanged.

## Adversarial reference and bounded exit

`tests/fixtures/handoff/consumer_stub.py` is a minimal, read-only consumer **test stub**, shipped beside the fixture so the tests can be reproduced. It calls the existing validator/calculator/status functions, checks correlation and source identities, deduplicates proposed evidence in memory, and returns diagnostics. Its `pass` means the supplied fixture observations are consistent; it never means permission to execute, apply or accept. It exposes no supported PRS API, persistent event journal or canonical writer. Any diagnostic conflict/unknown withholds all proposals; metrics remain the historical canonical source's metrics.

| Case | Expected boundary result | Demonstrated check |
| --- | --- | --- |
| Exact replay or retry with another delivery ID | Pass; one canonical leaf/credit, two distinct evidence proposals | Repeated assessments and replay batches are identical; source unchanged. |
| Same event ID with changed payload | Conflict; no proposals | In-memory collision is surfaced rather than replacing the earlier event. |
| Current source digest/observation differs, or implementation revision changes | Conflict; old observation retained, old receipts cannot certify the new implementation | Exact source comparison and existing pinned evidence policy. |
| Wrong project, leaf, task or source correlation | Conflict; no proposals or extra accounting row | Each supplied identity is compared with the pinned mapping. |
| Issue reopened while canonical leaf is Done | Conflict; canonical state retained for review | External discussion status cannot overwrite work completion. Issue closure also cannot grant outcome acceptance. |
| No source ever observed / current source unavailable | Unknown; metrics absent / last observed metrics retained | Missing is not an observed zero and no proposals are offered. |
| Failed/partial collection or success with incomplete page coverage | Unknown/degraded; original source/counts retained | Existing status reader retains coverage and timestamp. |
| Newer report/render of an old snapshot | Source remains old; stale assessment is unknown | Real public build preserves digest/date; explicit later reporting date yields stale, not refreshed. |
| Private project or private supplement flag in a public build | Refusal before any output | Existing public export preflight rejects the entire mixed input list, including a synthetic private task sentinel. |
| Worker delivery while source records blocked prerequisites | Work remains incomplete/blocked | Event evidence does not change dependencies, state, scope or grant execution eligibility. |
| Authored cancellation/deferral | Only the authored membership changes; stable leaf/history retained | Existing comparison reports source identities and keeps cancelled/deferred rows instead of removing history. |
| Implementation/test without owner approval | Work can be Done; source-state milestone unaccepted | Original fixture's negative acceptance policy remains unsatisfied. |

There are sixteen handoff tests in total, including the original six. The test harness adds no mandatory schema fields or accounting leaves. It does not validate arbitrary consumer JSON, authenticate an issue observation, verify signatures, implement durable exactly-once transactions, perform compare-and-swap writes, discover hidden private content, or infer live collection completeness. Privacy refusal relies on correctly declared input visibility; a public flag is not a content-classification service. Contradictory issue observations are supplied diagnostics, not fetched current facts.

The **specific offline PRS record-semantics gate** can pass after exact-revision review of these tests; that verdict is separate from M5 acceptance and from the other #3/#6/#1 work. The final assessed revision, checks and review producer are retained in the package audit and linked PR. No v0.4.1 tag or release is modified.

Consumer-owned gates remain **unknown/not tested here**:

- [Qurultai #102](https://github.com/interzettel/agent-council/issues/102): coordination/task mapping against its real schema, board delivery, persistent retry/race recovery, actual source observation and authorized reconciliation. Qurultai's maintainers own those runtime tests.
- [Hermes #13](https://github.com/interzettel/personal-agent-stack/issues/13): real-worker Gate C, peer participation and client/dispatch behavior under the host's authorization. Hermes' maintainers own those runtime tests.
- OS isolation, credentials, paid-model execution, cross-host transport and real-task efficacy need their own authorized consumer evidence. The stub's false permission flags do not establish any of them.

The future production writer/journal belongs to #32 and host adapters to #34. Evidence-stage terminology remains #6; within-repository selection/reconciliation remains #3; optional richer authority vocabulary remains #1. These are shared inputs or separate gates, not reasons to relabel this bounded synthetic proof as a live runtime pass.
