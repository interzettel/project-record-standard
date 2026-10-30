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

This happy path does not establish retry-safe reconciliation, race handling, stale-source detection, missing/inaccessible collection behavior or private-payload export safety. **PRS-HANDOFF-02 / #16** must exercise those adversarial cases and record a bounded exit verdict. Existing `policy_satisfied` can accept unpinned calls when revision is null; this example always supplies an exact implementation revision. It matches metadata, not signatures or human authority.

M5 outcome acceptance remains Yiğit's decision and also depends on its other declared work gates. No release, consumer migration, Hermes launch, Qurultai launch or unattended operation follows from this fixture or a merged PR. Published v0.4.1 and the independent contract version remain unchanged.
