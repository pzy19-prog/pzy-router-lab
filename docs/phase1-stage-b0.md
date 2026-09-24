# Phase 1 Stage B0 — Laya implementation and identity freeze

**Status:** `B0_IMPLEMENTATION_READY_FOR_REVIEW`  
**Execution authorization in this packet:** `NO`  
**Version:** `phase1-stage-b0-v1`  
**Checkpoint:** `convaiinnovations/laya-multilingual@82d57fc4f2d1be3d2caac494045f2ec51d0842f3`  
**Scope:** B0 only. No acquisition, LOAD, INFER, heldout, paid API, or B1/B2 work is authorized here.

Issue #7 and Issue #3 were read on 2026-09-24, including Issue #3's two comments. The accepted pre-execution gate is recorded in `data/phase1-pre-execution-gate.json`; Issue #3's latest comment says the merged gate is `af51011a0c279b117ef9d87f6e5b2ad4d1cb7af1` and B0 review must precede any checkpoint download or inference. The Phase 1 preregistration, Routing Contract/schema, existing Phase 0 and Phase 1 tests, and `docs/playbook-preflight.md` were reread. The accepted Playbook authority state remains `NO_ADOPTED_CURRENT_RULES`, with only the Rebaseline 01 authority-boundary control applicable; candidate guidance is not promoted to Rules.

## Adapter seam

`router_lab.laya_adapter` sits after `routing-v0` and leaves Nexus, Relay, Forge, and PCT untouched. Input is exactly the existing metadata-only Routing Contract: `task_id`, `complexity`, `sensitivity`, `risk`, `available_targets`, and optional `allow_cloud`. The existing Rules `route()` validates the request and provides the canonical input digest. No task prompt or task text is accepted.

The B0 output is a `DecisionReceipt` identity record with the fields in `schemas/decision-receipt.schema.json`. In addition to version strings it records adapter and runner source file SHA-256 digests and a canonical config digest, binding the uncommitted review subject. During PREPARE, `decision=NOT_EVALUATED`, `status=PREPARED`, and execution timestamps are null. QUALIFY without a locally acquired, hash-verified artifact emits `decision=NOT_READY`, `status=NOT_READY`, `failure_class=ARTIFACT_MISSING`. Laya's output-to-`routing-v0` decision mapping remains `NOT_TESTED`; this seam does not invent a model decision or mock inference.

| Identity | Frozen value |
|---|---|
| Routing Contract | `routing-v0` |
| Rules/config identity | `rules-baseline-v0` / `laya-b0-default-v1` |
| Laya source candidate | `NandhaKishorM/laya@1e28ac20c0896b1c37a744cd11f740eb98f8b178` |
| Checkpoint | `convaiinnovations/laya-multilingual@82d57fc4f2d1be3d2caac494045f2ec51d0842f3` |
| Artifact hash | `UNKNOWN / NOT_ACQUIRED` |
| Adapter | `laya-adapter-b0.1.0` |
| Runner | `laya-feasibility-runner-b0.1.0` |
| Environment | `b0-wsl2-probe-2026-09-24` |
| Execution mode | `CPU_FIRST_LOCAL` |

The implementation versions identify this B0 interface. At a real execution, source commit/tree digest and dirty-tree state must additionally bind the exact implementation subject in its receipt.

## Runner stages and authorization

The bounded runner exposes PREPARE, QUALIFY, LOAD, INFER, and RECEIPT stages. Only PREPARE and QUALIFY are implemented. QUALIFY reads the canonical repository manifest and verifies the complete local artifact file set, exact repo/revision, byte counts, and SHA-256 values. Caller-supplied artifact state is not authoritative. With the committed `NOT_ACQUIRED` manifest it returns `NOT_READY / ARTIFACT_MISSING`; synthetic fixtures exercise verification plumbing only and do not represent model artifacts.

LOAD and INFER fail closed without their explicit authorization flags and explain that execution is not authorized in B0. Even if a caller supplies those flags, B0 has no loader or inference backend and fails with a clear out-of-scope error. This prevents accidental execution while preserving a bounded extension point for separately reviewed B1/B2 work.

The guard rejects paid APIs, more than one checkpoint, any floating or non-approved revision, heldout access, acquisition/load before authorization, inference before authorization, and requests beyond the approved download, disk, wall-clock, dev-case, or rerun budgets. The approved cap is one checkpoint, 750,000,000 download bytes, 8 GiB disk, 7,200 seconds, six public dev smoke cases, zero full benchmark reruns, and zero paid API spend. B0 does not consume these acquisition or inference budgets.

## Checkpoint and qualification evidence

The only accepted checkpoint is the exact immutable revision above. `latest`, branch names, abbreviated SHAs and any other repository/revision pair are rejected. The adapter and runner make no network request and never invoke a download helper. The manifest is `data/laya-artifact-manifest.json`, governed by `schemas/laya-artifact-manifest.schema.json`.

At the exact Hub revision, upstream metadata listed these seven files, totaling 678,211,536 bytes. The two LFS object SHA-256 values are recorded as upstream metadata only. Actual file count, bytes and local SHA-256 are null/`UNKNOWN`; acquisition is `NOT_ACQUIRED`. No upstream value is represented as local artifact verification.

| Qualification item | Status | Evidence / limit |
|---|---|---|
| Source identity | `VERIFIED_METADATA` | GitHub exact commit API returned the pinned SHA. |
| Source code license | `VERIFIED_METADATA` | Exact source commit `LICENSE` returned Apache-2.0 text. |
| Checkpoint identity | `VERIFIED_METADATA` | Hub revision endpoint returned the requested exact SHA. |
| Model card license | `VERIFIED_METADATA` | Exact revision metadata declares `apache-2.0`; this is not a legal conclusion. |
| Expected file list/bytes | `VERIFIED_METADATA` | Hub tree API response at exact revision; values are upstream metadata. |
| Actual checkpoint bytes/hash | `UNKNOWN` | No artifact acquired; no local verification. |
| Declared runtime dependencies | `UPSTREAM_CLAIM` | Pinned source `pyproject.toml` declares torch, transformers, safetensors, huggingface_hub, and numpy with lower bounds rather than exact versions. |
| External API/runtime path | `VERIFIED_METADATA` / `NOT_TESTED` | Static inspection of the pinned loader found `huggingface_hub.snapshot_download` in its model load path. The inspected loader files did not show a paid provider call, but whole-package runtime behavior is `NOT_TESTED`. B0 code is stdlib-only and offline. Before B1, the exact load path must be shown to work with network disabled and the approved pre-acquired artifact. |
| Task-specific routing quality / Chinese quality | `NOT_TESTED` | No inference or evaluation performed. |

RouteLLM remains `NOT_ELIGIBLE_FOR_CURRENT_PHASE_ZERO_PAID_API_BUDGET`. vLLM Semantic Router remains an optional reference only. Neither is implemented or executed.

## Dependency and environment identity

B0 uses Python 3.12.3 and the Python standard library only; this change installs no package. `data/laya-environment.json` is the lightweight environment/dependency manifest. Before B1, an isolated Python 3.12 dependency lock must pin transitive versions and hashes, platform markers, wheel provenance, and the execution environment. The upstream's permissive minimum versions are not a reproducible lock and have not been installed. No model or package cache is used by B0. A later approved run must use an explicit experiment-local cache and a network-denied execution path, not ambient Hugging Face cache state.

The saved probe summary records the WSL2 kernel, CPU, RAM/swap, GPU and driver, disk, and cgroup probes. `/sys/fs/cgroup/{cpu.max,memory.max,memory.current,pids.max}` were unavailable; effective host/WSL resource caps remain `UNKNOWN`. GPU utilization was nonzero and Xwayland used 533 MiB at probe time; this is an observed environment state, not Laya activity.

## Receipt and stop conditions

The receipt records task ID and canonical metadata digest; contract/rules/config identity and config digest; candidate engine and exact source commit; adapter/runner version and source digests; exact checkpoint repo/revision and artifact hash state; environment identity; execution mode; nullable actual-execution timestamps; decision/status/failure class; and evidence references. The B0 path cannot produce `PASS` while the checkpoint hash is unknown or not acquired.

Stop and return to review on any identity mismatch, paid API or undeclared network dependency, license discrepancy, resource/budget expansion, heldout access, or policy invariant failure. There is no model-quality, performance, feasibility, or benchmark conclusion in B0.

## Network and artifact accounting

Metadata-only GitHub and Hugging Face API reads were made to verify the exact source LICENSE, pinned source metadata/dependency declaration, checkpoint revision/card metadata, and upstream file list/size metadata. **No checkpoint file, model weight, Python package, or other runtime artifact was downloaded.** No inference or paid API call occurred; no heldout material was generated, read, or unsealed.

## Review required before B1

Sol High should review the exact checkpoint/source binding and distinction between upstream metadata and local artifact identity; adapter input/output semantics and the still-untested model-output mapping; runner stage guards and budget enforcement; receipt schema and B0 identity/version binding; dependency lock and offline policy plan, especially the upstream `snapshot_download` path; static license/dependency evidence labels; the effective-resource limitations (`cgroup` unavailable); deterministic guard tests; and whether the B0 implementation is sufficiently bounded to accept. No checkpoint acquisition or inference follows automatically from B0 acceptance; B1/B2 require their separately authorized steps.
