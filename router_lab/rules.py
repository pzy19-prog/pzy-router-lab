"""Deterministic, offline rule baseline (no model/API calls)."""

import hashlib
import json

CONTRACT_VERSION = "routing-v0"
POLICY_ID = "rules-baseline-v0"
VALID_TARGETS = {"local_small", "local_strong", "cloud_strong"}
VALID_COMPLEXITY = {"low", "medium", "high", "unknown"}
VALID_SENSITIVITY = {"public", "confidential"}
VALID_RISK = {"low", "high"}


def route(request: dict) -> dict:
    """Return an auditable routing *decision*, never execute a task.

    Requires explicit metadata and list of actually available targets. Unknown
    or missing risk/sensitivity fail closed rather than silently using a cloud.
    """
    required = {"task_id", "complexity", "sensitivity", "risk", "available_targets"}
    missing = required - request.keys()
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")
    unknown = request.keys() - (required | {"allow_cloud"})
    if unknown:
        raise ValueError(f"Unrecognized fields are forbidden: {sorted(unknown)}")
    if not isinstance(request["task_id"], str) or not request["task_id"].strip():
        raise ValueError("task_id must be a nonempty string")
    if request["complexity"] not in VALID_COMPLEXITY:
        raise ValueError("Invalid complexity")
    if request["sensitivity"] not in VALID_SENSITIVITY:
        raise ValueError("Invalid sensitivity; fail closed")
    if request["risk"] not in VALID_RISK:
        raise ValueError("Invalid risk; fail closed")
    available = request["available_targets"]
    if not isinstance(available, list) or len(available) != len(set(available)) or not set(available) <= VALID_TARGETS:
        raise ValueError("available_targets must be a unique list of known target names")
    if type(request.get("allow_cloud", False)) is not bool:
        raise ValueError("allow_cloud must be boolean")

    # Hash only metadata, not full prompts, secrets, or untrusted task content.
    canonical = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    input_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    selected, reasons = "manual_review", []

    if request["risk"] == "high":
        reasons.append("HIGH_RISK_REQUIRES_HUMAN_REVIEW")
    elif request["complexity"] == "unknown":
        reasons.append("UNKNOWN_COMPLEXITY_FAIL_CLOSED")
    else:
        preference = ["local_small", "local_strong"] if request["complexity"] == "low" else ["local_strong", "local_small"]
        for target in preference:
            if target in available:
                selected = target
                reasons.append("PREFERRED_LOCAL_TARGET" if target == preference[0] else "LOCAL_FALLBACK")
                break
        if selected == "manual_review" and "cloud_strong" in available:
            if request["sensitivity"] == "confidential":
                reasons.append("CONFIDENTIAL_CLOUD_BLOCKED")
            elif not request.get("allow_cloud", False):
                reasons.append("CLOUD_OPT_IN_REQUIRED")
            else:
                selected = "cloud_strong"
                reasons.append("EXPLICIT_CLOUD_OPT_IN")
        if selected == "manual_review" and not reasons:
            reasons.append("NO_PERMITTED_TARGET")

    return {
        "contract_version": CONTRACT_VERSION,
        "policy_id": POLICY_ID,
        "task_id": request["task_id"],
        "input_digest": input_digest,
        "selected_target": selected,
        "reason_codes": reasons,
        "fallback_target": "manual_review",
        "requires_human_review": selected == "manual_review",
        "execution_performed": False,
    }
