# Phase 1 Stage A — Playbook applicability preflight

**Checked:** 2026-09-24 (Asia/Shanghai)  
**Playbook source:** `pzy19-prog/ai-native-project-playbook`, `main` at `1ad5d2c76b1cdec97032e6c71d553770512c7555` when read.  
**Scope:** accepted / Current rules only. This is a bounded applicability check, not a request to promote candidate rules.

## Authority snapshot

The Playbook's current execution profile says `NO_ADOPTED_CURRENT_RULES` and has an empty `current_rules` array. It names only the accepted Rebaseline 01 control baseline, scoped to authority separation, evidence before generalization, and no automatic promotion. `STATUS.md` says that baseline is not Playbook V1 and does not make every draft governance document a universal mandatory rule. The profile is still bound to its stated exact base `main@2ef9aea5de5362b7312877c283a47f1adc871024`; this preflight does not claim it was regenerated at the `1ad5d2c...` read head.

The cited evidence and governance documents for load-bearing evidence integrity, review independence, runtime identity, acceptance-threshold freeze, and repair-loop classification are drafts, evidence packs, or candidates. They are not Current rules. The accepted Rebaseline control is the only accepted control found; no rule-level Current authority was found for any requested topic.

## Applicability results

| Topic | Result | Authority finding | Effect on this Stage A design |
|---|---|---|---|
| Exact evidence / subject binding | `NOT_APPLICABLE` | No adopted Current rule. Similar language in draft review/evidence guidance and backfill evidence is non-authoritative. | No rule-driven change. The preregistration nevertheless defines per-case IDs, input digests, exact code/checkpoint/environment identity because Issue #3 and Phase 0 require reproducible identity. |
| `PASS` != proof target | `NOT_APPLICABLE` | No adopted Current rule. The related load-bearing-evidence candidate/backfill is not Current. | No rule-driven change. Tests are described only as deterministic artifact/contract checks; they do not prove model quality, held-out validity, or acceptance. |
| Acceptance-threshold freeze / anti-ratcheting | `NOT_APPLICABLE` | No adopted Current rule found. The threshold-freeze backfill is not Current authority. | No rule-driven change. Statistical margins, sample size, and pass thresholds remain `PRE_REGISTRATION_REQUIRED / NOT YET JUSTIFIED`; they are not invented from the exposed dev set. |
| Repair-loop stop conditions | `NOT_APPLICABLE` | No adopted Current rule found. Repair-loop classification/anti-loop material remains candidate/evidence-layer material. | No rule-driven change. This preregistration independently sets a local stop after one bounded repair if the same root cause recurs; this is an experiment-specific scope limit, not imported Playbook policy. |
| Source / runtime / environment / receipt identity separation | `NOT_APPLICABLE` | No adopted Current rule found for this topic in the profile. | No rule-driven change. Identity fields are included because Issue #3 and the Phase 0 benchmark protocol explicitly require them. |
| Accepted Rebaseline 01 control baseline | `APPLICABLE` | Accepted control baseline: preserve authority boundaries, evidence before generalization, and no automatic promotion. It does not establish any of the candidate topics above as rules. | It changes the record's authority framing: candidate/draft material is explicitly not treated as a project hard constraint, and a clean test result is not represented as evidence of model or study validity. It does not change the experiment design or add an experiment gate. |

`UNKNOWN` was not assigned to authority status because the current profile and Playbook status were readable and explicit. Applicability is bounded to the named source and checked revision; this is not a claim about unlisted external playbooks.

Status count for this bounded check: `APPLICABLE` — 1 accepted control baseline; `NOT_APPLICABLE` — 5 requested rule topics; `DEFER` — recheck only if the Playbook's accepted/current profile changes before Stage B; `UNKNOWN` — 0 for the inspected source snapshot. The deferred recheck does not adopt or activate any candidate rule.

## Sources inspected

- `STATUS.md` at the checked source revision: accepted Rebaseline 01, no Playbook V1, no universal mandatory policy.
- `profiles/current_execution_profile_v0.json`: `NO_ADOPTED_CURRENT_RULES`; `current_rules: []`; one accepted control baseline; a candidate advisory source marked non-Current.
- `evidence/issue-88-current-control-reconciliation.md`: names relevant governance documents as drafts/supporting control guidance, not adopted Current rules.
- `docs/governance/RULE_LIFECYCLE_V2.md`: explicitly `DRAFT_FOR_REBASELINE_01_REVIEW`, supporting guidance only.
- Relevant backfill records were checked for status and authority, not applied as normative requirements.
