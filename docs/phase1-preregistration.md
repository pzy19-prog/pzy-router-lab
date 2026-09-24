# Router Lab Phase 1 — Stage A preregistration

**Status:** `READY_FOR_SOL_REVIEW`  
**Execution authorization:** **NO**  
**Version:** `phase1-preregistration-v1`  
**Base:** `pzy19-prog/pzy-router-lab@47a00d9135fd8c262e82d2a0a16f2ea25ca18372`  
**Issue:** [#3 — Preregister and run local open-source router comparison](https://github.com/pzy19-prog/pzy-router-lab/issues/3), current body read 2026-09-24.  
**Machine record:** [`data/phase1-preregistration.json`](../data/phase1-preregistration.json)

This document freezes a Stage A protocol proposal for independent Sol High review. It authorizes no Laya or RouteLLM inference, model download, paid API use, Jev rerun, fine-tuning, formal held-out result, performance conclusion, push, or merge. It does not enter Stage B. `READY_FOR_SOL_REVIEW` means the proposal is reviewable; it does not mean the statistical design is justified or an experiment may start.

## Research question and comparison boundary

**PRIMARY_RESEARCH_QUESTION:** On a newly generated, independently sealed test set, does a frozen local-first semantic routing configuration improve task outcome success over the deterministic Rules baseline while preserving policy invariants and staying within an independently approved resource and cost budget? If no candidate meets feasibility or evidentiary requirements, the result remains insufficient evidence or candidate not feasible; no advantage is inferred.

### A. Controlled Routing Comparison

This track asks whether decision behavior differs under an identical router-visible information set. Each included method may receive only the same canonical metadata payload: case/task ID, complexity, sensitivity, risk, available targets, cloud opt-in, and a scenario/availability value only if every included method accepts it. The task prompt is not visible to any Controlled router. Rules stays on its native metadata-only contract.

Compare Rules only with candidate adapters proven to accept that exact payload without additional prompt-derived fields. If the shared serialized interface is unavailable, do not include that candidate in this track. Allowed conclusions are decision behavior against adjudicated routing gold, policy invariant behavior, and router-only latency. Decision correctness cannot establish answer quality or task success.

### B. End-to-End System Comparison

This track compares frozen router-adapter-executor configurations on the same task fixtures and outcome rubric. Each router receives only inputs supported by its pinned adapter. A component that supports task text may receive it; Rules receives metadata only and its executor receives task text after routing. Report the exact input mapping and identities for every configuration.

Compare blinded task outcomes, fallback/escalation, latency, resource use, and applicable cost. These are system-level results for the tested configurations. Do not interpret differences as the router's isolated causal effect when inputs, adapters, executors, or model pairs differ. Keep the two tracks separate.

## Independent held-out data

No formal held-out dataset is created in this stage. All 12 cases in `phase0-synthetic-v1` remain exposed `dev` / protocol-validation fixtures and cannot be renamed, paraphrased into, or sampled as held-out cases.

Before generation, a data owner and Sol reviewer must freeze the target population, task-family/language/risk strata, inclusion and exclusion criteria, sampling or authoring quotas, provenance/rights, and sample count. A custodian independent of router implementation/configuration work will produce fresh cases after candidate adapters/configurations and scoring rubrics are frozen. Cases must not be copied or paraphrased from Phase 0, authored or filtered using candidate outputs, or contain unauthorized real personal/confidential data. Record each case's provenance and rights.

The custodian assigns a random opaque UUID once per case; IDs are not content-derived and cannot be reused across splits. Store task text as exact UTF-8 under a fixed line-ending policy. `prompt_sha256` is the SHA-256 of those exact bytes. Each router input has a separate SHA-256 over canonical UTF-8 JSON (sorted keys, compact separators, `ensure_ascii=false`); Controlled input digests must not include task text. Do not publish per-case prompt digests before unsealing. Keep data and unsalted hashes in a private access-controlled store, with an append-only/signed manifest containing dataset version, IDs, provenance, file and per-case digests, rubric version, timestamps, and access events. Publish only a non-revealing commitment before evaluation.

Check exact and normalized overlap against Phase 0 and any declared source benchmark; manually review likely paraphrase overlap. Record known benchmark contamination and the limits of detecting pretraining exposure. Router implementers and configuration selectors receive no held-out contents, labels, or per-case digests before configuration lock. If anyone sees held-out outputs and changes cases, rubric, prompt template, adapter, threshold, or model configuration, retire that version for confirmatory use and create a newly sealed version.

At least two independent adjudicators label routing gold from the frozen policy and permitted metadata without seeing router decisions or task outcomes; a third resolves disagreement. For end-to-end scoring, use anonymized outputs and a frozen itemized rubric; reviewers are blind to router/system identity and route decision. Two reviewers score independently and a third resolves disagreement. Preserve each judgment, rationale, rubric version, and resolution.

Unresolvable or insufficient evidence remains `UNKNOWN`; never force a label or silently delete a case. Analyze assigned cases by intention to treat. Report eligible/scored/unknown counts. Unknown gold is excluded from a metric's scorable denominator but is reported. A valid output that fails any required rubric criterion is a task failure. A missing/corrupt output attributable to a system is failure; otherwise record outcome `UNKNOWN` and retain the case in flow accounting. Unknown risk/sensitivity follows the frozen fail-closed policy; missing policy data is never recoded as safe.

## Sample size and statistical method

Use paired case-level comparisons on the same sealed cases. Report raw numerators and denominators, paired differences, and predeclared strata. A defensible sample size needs a target effect or precision goal, expected paired discordance/variance, outcome prevalence, alpha, power, multiplicity plan, clustering/strata assumptions, and expected unscorable cases. There is no suitable independent pilot variance or target effect; the 12 exposed dev cases cannot justify a sample size.

For binary paired outcomes, exact McNemar is a candidate primary test. If Sol accepts it, determine n from a justified minimally meaningful paired difference and expected discordant-pair rate, with sensitivity analysis over plausible discordance rates. The test, effect/precision target, alpha/power, and source of the discordance assumptions remain unresolved; this proposal does not supply invented values.

**Sample size: `PRE_REGISTRATION_REQUIRED / NOT YET JUSTIFIED`.**  
**Non-inferiority margin: `PRE_REGISTRATION_REQUIRED / NOT YET JUSTIFIED`.**  
**Acceptance threshold: `PRE_REGISTRATION_REQUIRED / NOT YET JUSTIFIED`.**  
Inferential test, alpha/power or precision target, interval method, and multiplicity plan also remain `PRE_REGISTRATION_REQUIRED / NOT YET JUSTIFIED`. No superiority, non-inferiority, or statistical pass/fail claim may be made until Sol accepts those choices and they are frozen before unsealing.

## Frozen metrics

Primary metrics are track-specific: **Controlled** uses decision correctness against independently adjudicated routing gold, only if exact-input eligibility is met and gold is not `UNKNOWN`; **End-to-End** uses blinded task outcome success over executable assigned cases, with intention-to-treat accounting. No acceptance threshold is set in Stage A.

| Metric | Unit and aggregation | Missing / UNKNOWN | Track |
|---|---|---|---|
| Decision correctness | Correct / scorable decisions; raw counts, rate, paired case difference and declared strata | Unknown gold is unscorable; publish eligible, scored and unknown counts/rates | Controlled primary; End-to-End secondary |
| Task outcome success | Rubric-passing / executable assigned tasks; raw counts, rate and paired case difference | System-attributable missing/corrupt output is failure; otherwise unknown with reason and flow count | End-to-End primary |
| Abstain/escalation correctness | Correct abstain/escalate / cases whose verified gold requires or permits the action; counts, rate, paired difference | Unknown gold is unscorable and reported | Both |
| Over-escalation | Unnecessary escalation / cases where verified gold permits an available automated route; count/rate, paired difference | Unknown gold excluded from denominator and reported | Both |
| Router latency | Milliseconds per decision; raw calls and per-case median; separately record cold start, load and first call | Missing timing is `UNKNOWN`; no imputation | Both |
| End-to-end latency | Milliseconds per assigned task; raw values and per-case median, split router/executor where measurable | N/A for no execution; missing measurement is `UNKNOWN`; queue and human wait separate | End-to-End |
| Local resource use | Peak resident RAM MiB, peak VRAM MiB, CPU-seconds, process load time; raw samples/maxima with tool and sampling interval | Unmeasured resource is `UNKNOWN`; never infer from parameter count | Both |
| API/token cost | Provider-reported input/output tokens and currency per case/total, including router calls, with dated price source | N/A for fully local system; missing usage/cost is `UNKNOWN`, not zero | End-to-End |
| Fallback behavior | Fallback events / assigned decisions; counts/rates by failure class, ordered attempts retained | Unclassifiable cause is `UNKNOWN` and retained | Both |
| UNKNOWN rate | Unknown/unscorable / assigned cases, split by gold, output, runtime, cost, and identity source | Unknown is counted and reported, never silently dropped | Both |

Policy invariants are reported separately from averaged quality metrics: confidential input never goes to cloud; unavailable targets are never reported executable; unknown/high-risk policy input fails closed or escalates under the frozen policy. Any observed invariant violation stops the affected run and cannot be offset by quality gains.

## Candidate source and checkpoint state

All SHA values below identify candidate source revisions observed on 2026-09-24, not releases approved for use. No weights were downloaded. Repository license metadata and model-card metadata are leads; complete license and artifact review remains a pre-download gate.

| Candidate | Exact source candidate | Code license | Model/checkpoint status | Adapter / language / local status |
|---|---|---|---|---|
| Rules | `pzy19-prog/pzy-router-lab@47a00d9135fd8c262e82d2a0a16f2ea25ca18372` | MIT | No checkpoint | Native `routing-v0`; benchmark adapter version must be recorded before Stage B |
| Laya | [`NandhaKishorM/laya@1e28ac20c0896b1c37a744cd11f740eb98f8b178`](https://github.com/NandhaKishorM/laya/tree/1e28ac20c0896b1c37a744cd11f740eb98f8b178) | Apache-2.0 per GitHub metadata | Candidate [`convaiinnovations/laya-multilingual@82d57fc4f2d1be3d2caac494045f2ec51d0842f3`](https://huggingface.co/convaiinnovations/laya-multilingual/tree/82d57fc4f2d1be3d2caac494045f2ec51d0842f3); HF metadata declares Apache-2.0 and lists `zh`. No download, artifact hash, or load validation. | Not implemented; input mapping and Controlled eligibility unknown. Chinese task-specific routing quality unknown. CPU/local feasibility unknown. |
| RouteLLM | [`lm-sys/RouteLLM@0b64fdafe049e596a3f5657c219329f24af24198`](https://github.com/lm-sys/RouteLLM/tree/0b64fdafe049e596a3f5657c219329f24af24198) | Apache-2.0 per GitHub metadata | No router/model pair selected. Checkpoint revision/license unknown; no download/evaluation. | Not implemented. Prompt/model-pair semantics may not qualify for Controlled. Chinese support and complete CPU/offline feasibility unknown. |
| vLLM Semantic Router (optional) | [`vllm-project/semantic-router@3448de83f093f2108505cf2902a0602de8929d20`](https://github.com/vllm-project/semantic-router/tree/3448de83f093f2108505cf2902a0602de8929d20) | Apache-2.0 per GitHub metadata | No model/recipe selected. Checkpoint license and revision unknown; no download/evaluation. | Not implemented; full wire/gateway mapping and Controlled eligibility unknown. CPU paths are described upstream; exact recipe's local feasibility and Chinese behavior unknown. |

No candidate is yet admitted to formal evaluation. No adapter status, candidate name, or upstream performance statement is evidence of Router Lab task quality.

## Planned execution environment identity

Read-only deterministic commands on 2026-09-24 reported:

- OS: Linux x86_64 under WSL2; kernel `6.18.33.1-microsoft-standard-WSL2`.
- Python: `3.12.3`.
- CPU: Intel Core i7-10750H, 6 cores / 12 threads (`lscpu`).
- RAM: `16,284,284 kB` total (`/proc/meminfo`, approximately 15.5 GiB); available memory varies.
- GPU: NVIDIA GeForce RTX 2060, 6,144 MiB; driver `596.36` (`nvidia-smi`).

This identifies the reported session, not a unique host attestation. Before a run, record WSL distribution/version, OS build, driver/CUDA/runtime, effective CPU affinity and memory cap, device visibility, timestamp, dependency lock digest, relevant environment variables, and container/environment digest where used. Dependency lock, exact runner version/commit, and clean/dirty-tree state remain `PRE_REGISTRATION_REQUIRED`. No runner currently exists. Verify effective resource limits at run time; do not silently substitute hardware, dependency, or checkpoint.

## Budget and stop conditions

- Paid API budget is fixed at **0**.
- Stage A model downloads and inference calls are fixed at **0**.
- Before Stage B, Sol must approve the number of checkpoint artifacts, per-artifact and aggregate byte caps, disk cap, wall-clock cap, and maximum full benchmark reruns. These are `PRE_REGISTRATION_REQUIRED`; no unsupported high-cost budget is assumed.
- Per-case timing/inference replicates and full benchmark reruns are distinct. Their counts must be fixed before Stage B.
- Any safety invariant violation, paid call/charge, identity mismatch, pre-lock held-out exposure, unapproved network dependency, or approved budget overrun stops the affected run immediately.
- Unsupported language/input capability or missing license excludes that candidate; do not substitute a different checkpoint silently.
- Environment incompatibility stops that candidate. Any changed candidate/environment requires a reviewed preregistration version.
- Allow at most one bounded repair for an identified root cause. If the same root cause recurs after that repair, stop work on that candidate and return for review; new issue/test names do not reset this local limit.

## Playbook applicability preflight

See [`docs/playbook-preflight.md`](playbook-preflight.md). The current Playbook profile read at `ai-native-project-playbook@1ad5d2c76b1cdec97032e6c71d553770512c7555` states `NO_ADOPTED_CURRENT_RULES` and `current_rules: []`; only the accepted Rebaseline 01 control baseline is listed. Therefore each requested rule topic—exact evidence/subject binding, `PASS` vs proof target, threshold freeze/anti-ratcheting, repair-loop stop, and source/runtime/environment/receipt identity—is `NOT_APPLICABLE` as a Current rule. Related draft/candidate material was not elevated.

The accepted control baseline changed authority framing only: candidate/draft ideas are not project hard constraints, and green deterministic checks are not represented as study or model proof. **No accepted Current rule materially changed the experiment design or verification plan.** Identity and stop fields follow Issue #3, the Phase 0 protocol, and this task's explicit scope.

## Review blockers before Stage B

Sol High must independently judge this exact subject and resolve or explicitly waive, in a versioned review decision:

1. Sample size rationale and count; statistical test, alpha/power or precision target, interval and multiplicity plan.
2. Non-inferiority margin and acceptance threshold, or a frozen decision not to make a thresholded confirmatory claim.
3. Held-out population/frame, strata, sample count, custodian, access controls, and case generation rights/provenance.
4. Candidate inclusion; exact adapter/configuration/executor; complete checkpoint and license review.
5. Dependency lock, runner identity, effective environment limits and hardware feasibility.
6. Download count/byte caps, disk, wall-clock, benchmark rerun cap, and any per-case replicate counts.

Until that review and all required items are closed, `stage_b_eligibility=false`. A green unittest or schema check only checks the declared deterministic properties of these files; it does not prove the study design, data independence, candidate performance, or any result.
