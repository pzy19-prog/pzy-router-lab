# PZY Router Lab (experimental)

A small, local-first benchmark scaffold for replaceable task-routing strategies. This repository is an experiment, **not** a production Router or a trained model.

## What works now

- An implementation-neutral routing request/decision contract (v0), with a deterministic rules-only baseline.
- An offline CLI, fixtures and standard-library tests. No API key, network, paid model or external dependency is required.
- Explicit human-review fallback when no permitted target is available. Confidential tasks cannot be routed to cloud targets.

## What is NOT implemented

- Laya, RouteLLM, Jev, vLLM Semantic Router or other model adapters: **candidates for independent validation, not dependencies or installed features**.
- Runtime task execution, automatic retries, failure detection, feedback learning, custom model fine-tuning or full web UI.
- Any empirical evidence that this baseline improves success, cost or latency.

## Quick start (Python 3.10+)

```sh
python -m unittest discover -s tests -v
python -m router_lab.cli route --input examples/low-risk.json
python -m router_lab.cli route --input examples/confidential.json
```

The CLI emits a structured decision receipt only; it never calls or runs a target model.

## Design boundaries

1. **Local-first and provider-neutral:** paid decisions are optional; local deterministic rules always work.
2. **Routing is not execution:** offline decision-making does not mean the downstream task runs offline.
3. **Human-auditable:** every output includes policy ID, input digest, reason codes and fallback.
4. **Least authority:** no writes to external repositories; no cross-project permission transfer.
5. **Evidence before training:** reuse and compare established open-source baselines before considering fine-tuning.

See the [Phase 0 benchmark protocol](docs/benchmark-plan.md), [open-source selection report](docs/phase0-selection.md), [synthetic cases](data/phase0-cases.jsonl), and [routing schema](schemas/routing-v0.schema.json).

## Scope and status

Status: **Candidate / experiment only; not an active P0 project**. Nexus may incubate Router via a stable contract; Relay transports task state and evidence; Forge performs separately authorized engineering execution. No runtime dependency on these systems is introduced here.

## Licensing

Original scaffold: MIT, see LICENSE. No third-party code, weights or datasets are vendored. Upstream licenses must be checked before importing or distributing any third-party materials. `pzy-router-lab` is a provisional experimental repository name, not a final product brand.
