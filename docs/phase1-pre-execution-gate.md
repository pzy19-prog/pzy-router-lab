# Phase 1 Pre-Execution Gate Packet

- **Status:** `PRE_EXECUTION_GATE_READY_FOR_REVIEW`
- **Execution authorization:** `NO`
- **Version:** `phase1-pre-execution-gate-v1`
- **Branch / base:** `phase1/pre-execution-gate` at `6e10cb1b2d5332180e748f8ddfa141bdecc69abc`
- **Issues:** [#5](https://github.com/pzy19-prog/pzy-router-lab/issues/5) and [#3](https://github.com/pzy19-prog/pzy-router-lab/issues/3), both read on 2026-09-24.
- **Machine record:** [`data/phase1-pre-execution-gate.json`](../data/phase1-pre-execution-gate.json)
- **Schema:** [`schemas/phase1-pre-execution-gate.schema.json`](../schemas/phase1-pre-execution-gate.schema.json)

This packet only specifies the gate. No model weights were downloaded, no model was run, no heldout content was generated or unsealed, no paid API was called, and no real evaluation was started. Stage B remains unauthorized until independent Sol High review accepts the exact packet and separately grants execution authorization.

## 1. Fresh read and scope

The current branch and `main` both point to `6e10cb1b2d5332180e748f8ddfa141bdecc69abc`; the worktree was clean at the start of this task. Issue #5 requires a versioned gate packet and expressly keeps authorization at `NO`. Issue #3 makes the two comparison tracks distinct and Phase 0 synthetic fixtures development-only. The reread sources are `docs/phase1-preregistration.md`, `data/phase1-preregistration.json`, `schemas/phase1-preregistration.schema.json`, `docs/playbook-preflight.md`, `docs/phase0-selection.md`, `docs/benchmark-plan.md`, `data/phase0-freeze.json`, and the related preregistration/Phase 0 tests.

No changes were made to Nexus, Relay, Forge, PCT, or Playbook. No push or merge was performed.

## 2. Statistical claim hierarchy

The formal inferential benchmark is **`NOT_YET_JUSTIFIED`**. There is no independent pilot variance, supported target effect or precision objective, expected discordance, outcome prevalence, justified alpha/power, multiplicity family, strata/clustering assumption, or missing-case rate. The 12 Phase 0 fixtures are public development data and cannot justify formal sample size. No effect size, non-inferiority margin, threshold, alpha, power, or acceptance rule is invented here.

The primary claim and metric are frozen separately for each track:

| Track | Primary claim and metric | Secondary metrics | Interpretation |
|---|---|---|---|
| **A. Controlled Routing Comparison** | On identical canonical router metadata, report decision correctness against verified routing gold: exact correct decisions divided by assigned cases with scorable gold; report counts and paired case differences versus Rules. | Abstain/escalation correctness, over-escalation, router latency, fallback/failure classes, invariants, UNKNOWN rate, measured resources. | A candidate is eligible only if it accepts the exact same serialized fields and availability state. Decision correctness says nothing about answer quality or task success. |
| **B. End-to-End System Comparison** | Under a frozen itemized rubric, report blinded task success: rubric-passing outputs divided by executable cases assigned to the system; report paired case differences versus the frozen Rules-plus-executor configuration. | Escalation/fallback, router and end-to-end latency, measured resources, applicable token/currency cost, UNKNOWN rate, invariants. | This compares complete systems. When inputs, adapters, executors, or models differ, it cannot support a router-only causal claim. |

The approved next step proposed here is a **NON-INFERENTIAL PILOT** limited to adapter/load/runtime feasibility, at most six existing public Phase 0 development cases, only after a separate review and explicit authorization. It is not a performance pilot and cannot report advantage, superiority, non-inferiority, acceptance, or confirmatory task-quality claims. All pilot outputs and metrics are descriptive. No such pilot is run in this task.

### Statistical method boundary

- **Binary paired outcomes:** exact McNemar is a candidate method for a later formal design, but no test is currently approved. Sol must freeze the claim, sample-size rationale, alpha/power or precision objective, interval method, missingness assumptions, and multiplicity plan before heldout unseal.
- **Multiclass decisions/failure labels:** report confusion tables and per-class counts descriptively. No unapproved class-wise significance tests.
- **Continuous latency, resource, or cost measures:** preserve raw paired values and descriptive per-case differences/medians. No unapproved t-test, rank test, interval, tail-percentile claim, or pass threshold.
- **Secondary metrics and strata:** descriptive only. A future inferential secondary claim requires a predeclared test family and correction method; otherwise it remains exploratory/descriptive.
- **Paired-case semantics:** same case ID and same canonical payload in Track A; any input mismatch makes the candidate ineligible for that track. Track B pairs systems by case ID but treats the difference as whole-system evidence.

### UNKNOWN denominator rule

Keep every assigned case in flow accounting. For each metric, count a case in its scorable denominator only when the required gold/measurement is known. Publish assigned, eligible, scored, UNKNOWN, and failure counts and rates. System-attributable missing/corrupt outputs count as failure. Missing evidence not attributable to the system remains `UNKNOWN` and stays in flow counts. UNKNOWN is never converted to success or safe; missing risk/sensitivity follows the frozen fail-closed policy.

## 3. Heldout governance

No formal heldout exists in this packet. The public 12-case Phase 0 set remains `dev` and cannot be renamed, paraphrased, or sampled into a heldout set.

- **Custodian role:** `HELDOUT_CUSTODIAN`, appointed by the data owner, independent of router/adapter/executor implementation, tuning, and candidate selection. If a person cannot maintain this separation, the data owner appoints and audits a separate custodian.
- **Access:** before unseal, only the custodian and authorized case authors may see prompts; blind adjudicators receive only the content needed for their assigned task. Implementers, candidate/config selectors, benchmark operators, and public readers cannot see prompts, labels, or per-case digests. After any authorized release, implementers still receive no interactive case/result access until systems/configs are locked. Exposure followed by change retires that heldout version from confirmatory use.
- **Population:** new, rights-cleared English and Chinese requests representative of explicitly declared Router Lab local-first routing use cases. The data owner must approve the target population before generation. Private/confidential source text is excluded unless separately authorized and protected.
- **Strata:** language (`zh`, `en`, or `mixed` only where both are supported); task family (structured transformation, information extraction/classification, short-form reasoning/response); policy/risk (ordinary, elevated, high-risk/manual review); and execution mode (policy-only or executor-required). Exact quotas need approval.
- **Sample frame:** purpose-authored cases or an approved rights-cleared source frame, frozen before generation. No Phase 0 fixture, paraphrase, benchmark item, or candidate-output-derived item. Source, quota, sample count, inclusion/exclusion rules, and rights remain `NOT_YET_JUSTIFIED` until approved.
- **Generation:** freeze the population, strata, quotas, language policy, rubrics, executor/model identities, and authoring recipe first. Generate/sample only after configuration lock. Record provenance and rights. Assign random content-independent UUIDv4 case IDs once. Store prompts as exact UTF-8 with LF policy; hash exact prompt bytes and each actual canonical router payload separately.
- **Overlap/contamination:** check exact bytes, normalized text, and character/token n-gram fingerprints against Phase 0 and each declared source benchmark; manually review likely paraphrases. Record known benchmark overlap and pretraining uncertainty. This cannot prove no pretraining exposure.
- **Seal/manifest:** keep prompt, labels, per-case digests, and access log in a private, access-controlled store. Sign or append-only seal a manifest containing dataset/protocol versions, UUIDs, provenance/rights, prompt and input digests, rubric, timestamps, and access events. Publish only a non-revealing commitment. Never commit formal prompts or per-case prompt hashes here.
- **Blind route gold:** two independent adjudicators see policy version and permitted metadata, not router decisions or outcomes. A third adjudicator resolves disagreements. Preserve labels, rationale, and resolution. Unresolved gold stays `UNKNOWN`.
- **Blind task outcome:** two independent reviewers score anonymized output against a frozen itemized rubric without system identity or route decision; a third resolves disagreement. Preserve raw scores and resolution. Missing/corrupt output attributable to the system is failure; otherwise it is `UNKNOWN` with reason.
- **Unseal:** none is authorized now. Later unseal requires written independent Sol approval of the exact packet plus a separate explicit execution authorization, all hard gates passing, and a custodian-recorded authorizer, scope, manifest commitment/digest, time, and recipients.

## 4. Candidate qualification

Evidence labels are kept separate: `VERIFIED` means directly checked for the stated exact artifact; `UPSTREAM_CLAIM` means an upstream claim not validated locally; `UNKNOWN` means identity/evidence unresolved; `NOT_TESTED` means no local runtime test; `NOT_ELIGIBLE` means the current path violates a gate. Code and model licenses are assessed separately.

| Candidate | Exact code / checkpoint identity | License and size | External/offline and language evidence | Adapter / eligibility |
|---|---|---|---|---|
| **Laya** | Code: `NandhaKishorM/laya@1e28ac20c0896b1c37a744cd11f740eb98f8b178`. Candidate checkpoint: `convaiinnovations/laya-multilingual@82d57fc4f2d1be3d2caac494045f2ec51d0842f3`. Both are immutable SHAs; `latest`, branch names, and floating bundles are forbidden. | Exact source LICENSE is Apache-2.0 (`VERIFIED`). Hub card metadata for this exact checkpoint revision declares Apache-2.0 (`VERIFIED`); legal terms still require review. Hub reports 647 MB (`UPSTREAM_CLAIM`); exact bytes and artifact digest not tested. | PyTorch/Transformers and tokenizer/runtime dependencies (`UPSTREAM_CLAIM`); exact dependency lock absent. Chinese and 100+ language support are Hub claims, not task-quality evidence. CPU and offline feasibility are `NOT_TESTED`; 12 vCPU, 15 GiB RAM, 6 GiB GPU visible. | Adapter `NOT_TESTED` and unimplemented. Any future adapter must require the exact repository and revision, verify runtime identity, and abort on mismatch. Conditional feasibility candidate; not eligible to execute until approval and tests. |
| **RouteLLM** | Code: `lm-sys/RouteLLM@0b64fdafe049e596a3f5657c219329f24af24198`; no checkpoint/model pair selected (`UNKNOWN`). | Exact source LICENSE is Apache-2.0 (`VERIFIED`). Model licenses/revisions are `UNKNOWN` and must be checked per router and strong/weak executor. | Current intended `mf`/similarity path calls OpenAI `text-embedding-3-small`. No API-free local embedding path has been qualified. Chinese and full local/offline feasibility `UNKNOWN`. Paid API budget is zero. | Adapter `NOT_TESTED`; **NOT_ELIGIBLE_FOR_CURRENT_PHASE_ZERO_PAID_API_BUDGET**. Reconsider only after a local path and all model identities/licenses are independently qualified. No API was called. |
| **vLLM Semantic Router** | Code: `vllm-project/semantic-router@3448de83f093f2108505cf2902a0602de8929d20`; no recipe/checkpoint selected (`UNKNOWN`). | Exact source LICENSE is Apache-2.0 (`VERIFIED`). Model licenses and sizes `UNKNOWN`. | Upstream documents CPU paths, but full exact-recipe offline feasibility and resource need are `NOT_TESTED`; Chinese support depends on an unselected recipe. | Adapter `NOT_TESTED`; optional and not selected for this phase due to scope/integration overhead. |

The Laya exact checkpoint revision was checked through Hugging Face model metadata; its SHA and Apache-2.0 card metadata match. The Hub currently reports the multilingual model as 322M parameters and 647 MB, and describes 100+ language coverage. This is upstream evidence, not a local installation, inference, or Chinese routing result. RouteLLM's checked upstream router implementation invokes OpenAI embeddings for its similarity-weighted path, so that path is ineligible under the fixed zero paid API cap. Primary references: [Laya model card](https://huggingface.co/convaiinnovations/laya-multilingual), [Laya source](https://github.com/NandhaKishorM/laya), [RouteLLM router implementation](https://github.com/lm-sys/RouteLLM/blob/0b64fdafe049e596a3f5657c219329f24af24198/routellm/routers/routers.py), [RouteLLM models](https://huggingface.co/routellm/models), [vLLM Semantic Router](https://github.com/vllm-project/semantic-router).

## 5. Adapter, runner, executor, and receipt identity

The minimum planned flow is:

```text
RoutingContract -> Adapter -> Candidate engine -> DecisionReceipt
Router -> Adapter -> Executor -> OutcomeReceipt   (End-to-End only)
```

The planned adapter boundary is `predict(request: RoutingRequest, *, candidate_ref: ExactCandidateRef, config_ref: ConfigRef) -> DecisionReceipt`. It declares accepted fields and rejects unsupported/missing required fields. Controlled inputs never contain task text. A deterministic policy guard checks each target against risk, sensitivity, cloud opt-in, confidentiality, and `available_targets`.

Before a future run, record adapter semantic version, adapter source commit and tree SHA-256, interface version, runner version/source commit/tree digest, executor implementation and exact model revision/license, canonical config digest, dependency lock digest, case-order digest, actual input digest, and environment digest. Laya's adapter requires the exact checkpoint revision in constructor/config and compares it with runtime-reported identity before inference. No floating reference is allowed.

Each `DecisionReceipt`/`OutcomeReceipt` includes schema version, track, case ID, exact input digest, source commit, checkpoint repository/revision, adapter identity, runner identity, executor identity or `NONE`, config digest, environment digest, timestamps, decision/outcome, status/failure class, ordered fallback attempts, and network mode. The environment digest binds WSL/OS, Python, lockfile and installed package inventory, CPU/RAM/GPU/driver, execution-affecting environment, and cache identity; it excludes secrets. No complex framework is proposed.

## 6. Environment probes and plan

Deterministic probes were run on 2026-09-24: `python --version`, `uname -a`, `nvidia-smi`, `free -h`, `df -h .`, and `lscpu`.

| Item | Observed state |
|---|---|
| Python | 3.12.3; no isolated experiment env or dependency lock exists yet |
| WSL | Linux `PZY` 6.18.33.1-microsoft-standard-WSL2, x86_64; visible 12 vCPU, 15 GiB RAM and 4 GiB swap. cgroup v2 `memory.max`/`cpu.max` paths absent; host/WSL caps remain unknown. |
| CPU | Intel Core i7-10750H, 6 cores / 12 threads |
| RAM | 15 GiB total, about 12 GiB available at probe time |
| GPU | NVIDIA GeForce RTX 2060, 6144 MiB VRAM; 549 MiB in use. `nvidia-smi`: driver 596.36, CUDA 13.2; utility 595.71.01. |
| Disk | `/dev/sdd`, 1007 GiB total, 66 GiB used, 891 GiB available at probe time |

Use a dedicated Python 3.12 CPU-first environment only after approval. Lock transitive dependencies with `uv.lock` (or a hash-pinned requirements lock), preserve a wheelhouse/cache manifest and SHA-256, and record platform markers. No dependency is installed in this task. Stage any approved exact-revision artifacts first, then run with outbound network disabled. Runtime telemetry, provider calls, or undeclared networking stop the candidate. The only cache permitted is the approved immutable checkpoint and lockfile-pinned dependencies; no cache was populated here.

## 7. Proposed resource budget

Paid API budget is fixed at **0**. All other caps below are recommendations for Sol High to approve or revise; none is currently approved.

| Cap | Proposed maximum | Basis | State |
|---|---:|---|---|
| `MAX_MODEL_DOWNLOAD_COUNT` | 1 checkpoint revision | Laya only; excludes RouteLLM and vLLM assets. | `USER_APPROVAL_REQUIRED` |
| `MAX_MODEL_DOWNLOAD_BYTES` | 750,000,000 bytes | Hub-reported Laya size is 647 MB; modest bounded headroom, with exact revision bytes to be checked before approval. | `USER_APPROVAL_REQUIRED` |
| `MAX_DISK_USAGE` | 8 GiB total experiment footprint | Covers one checkpoint, CPU dependencies, cache, logs, temporary files; small relative to current 891 GiB free. | `USER_APPROVAL_REQUIRED` |
| `MAX_WALL_CLOCK` | 7,200 seconds (2 hours) | One bounded install/load/adapter feasibility session only. | `USER_APPROVAL_REQUIRED` |
| `MAX_FULL_BENCHMARK_RERUNS` | 0 | A formal full benchmark is outside this feasibility gate and needs a new review. | `USER_APPROVAL_REQUIRED` |
| `MAX_FEASIBILITY_CASES` | 6 public Phase 0 dev cases | Adapter plumbing only; no sample-size or performance claim. | `USER_APPROVAL_REQUIRED` |

Sol High must decide whether to approve these limits, approve a six-case dev-only feasibility smoke, set CPU-only versus optional GPU use, appoint a named data owner and `HELDOUT_CUSTODIAN`, approve the heldout population/strata/quotas/source frame/rights/sample count, and either define a justified formal inference design or keep future results descriptive. No positive cap authorizes work on its own.

## 8. Stop conditions

Stop immediately for heldout leakage/unauthorized access; candidate, source, checkpoint, or license mismatch; a floating or unexpected checkpoint identity; receipt identity inconsistency; unexpected paid API/network/telemetry or non-zero charge; any policy invariant break; environment incompatibility or unpinned dependency; any budget cap breach; or unauthorized heldout unseal. Preserve partial receipts/logs. At most one bounded repair is allowed for a root cause. If the same root cause recurs after that repair, stop that candidate and return for review; renaming the issue does not reset the limit. Any environment, candidate, model, or config change requires review before retry.

## 9. Status and remaining decisions

This packet is `PRE_EXECUTION_GATE_READY_FOR_REVIEW`, not execution-ready. Formal sample size and inferential claims remain `NOT_YET_JUSTIFIED`; the heldout set does not exist; Laya's adapter/runtime/license terms and local performance remain untested; RouteLLM is ineligible on its current API path; and each proposed positive cap needs Sol High approval. The machine record preserves these gaps and fixes `execution_authorized` to `false`. No Stage B work may start from this packet alone.
