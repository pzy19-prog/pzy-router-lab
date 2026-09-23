# Phase 0 baseline protocol (pre-registration draft)

**Status:** Protocol only. No independent Laya/RouteLLM/Jev benchmark has been run in this repository.

## Question
When compared on the **same** task set, under pinned configs and defined cost accounting, does any open-source decision engine plus explicit local fallback improve task outcomes/cost/latency compared with deterministic rules alone?

## Candidates (validate before adopting)
- Rules baseline in this repository, no model call.
- Laya: verify current repo, model cards, licenses, weights, Chinese-task behavior and supported deployment platform.
- RouteLLM: verify current maintained repo, license, threshold calibration and route coverage.
- Historical Jev EXP-0001: reuse only exact comparable existing results; do not implicitly rerun.

Do not include an adapter in outcome tables until it has passed contract, license and runtime checks.

## Dataset and protocol
1. Pre-register representative task families, success criteria, severity, privacy flags, local/cloud availability and budget.
2. Split cases into development and held-out tests; never tune policies using held-out outcomes.
3. Run every eligible engine on identical case versions and availability scenarios; report exclusions and mismatches.
4. Store anonymized request metadata, pinned policy/adapter/model versions, decision receipt, downstream executor outcome and exact accounting method; redact prompts, keys and PII.
5. Compare: task success, false weak-route rate, unnecessary escalation, abstention, router latency, end-to-end latency and total metered cost. Include confidence intervals when sample size permits.
6. Add provider outage and confidential-task tests: local rules must work with no network; unavailable target must never be represented as available.

## Stop conditions
- If open-source baseline or rules suffice, **do not fine-tune** merely to have a custom model.
- If no robust benefit emerges, retain Router as an internal capability; do not claim independent product value.
- Escalation/retry tests require a separate authorized runtime harness; decision outputs alone are not evidence of end-to-end recovery.

## Scope gates
- V0: rules-only offline baseline (implemented here).
- V1: upstream baseline reproduction with evidence, licenses, and pinned adapters (not started).
- V2: failure-aware escalation on real execution traces, only if evidence supports it (not started).
- V3: custom fine-tuning only after measurable, persistent gaps are documented (not authorized).
