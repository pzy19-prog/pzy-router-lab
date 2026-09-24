"""Fail-closed seam for the pinned Laya candidate.

This module validates the existing metadata-only Routing Contract. It does not
load a checkpoint, make a prediction, or access the network.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .rules import CONTRACT_VERSION, route

ADAPTER_VERSION = "laya-adapter-b0.1.0"
CANDIDATE_ENGINE = "laya"
CANDIDATE_SOURCE_COMMIT = "1e28ac20c0896b1c37a744cd11f740eb98f8b178"
CHECKPOINT_REPO = "convaiinnovations/laya-multilingual"
CHECKPOINT_REVISION = "82d57fc4f2d1be3d2caac494045f2ec51d0842f3"
CHECKPOINT_ARTIFACT_HASH = "UNKNOWN"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DECISION_STATUS = {
    "NOT_EVALUATED": "PREPARED",
    "NOT_READY": "NOT_READY",
    "QUALIFIED_FOR_REVIEW": "QUALIFIED_FOR_REVIEW",
    "PASS": "PASS",
}
FAILURE_CLASSES = {
    None,
    "ARTIFACT_MISSING",
    "ARTIFACT_IDENTITY_MISMATCH",
    "ARTIFACT_MANIFEST_INVALID",
    "ARTIFACT_INTEGRITY_MISMATCH",
}
SUCCESS_LIKE_DECISIONS = {"QUALIFIED_FOR_REVIEW", "PASS"}
CONFIG_IDENTITY = "laya-b0-default-v1"
RULES_CONFIG_IDENTITY = "rules-baseline-v0"


@dataclass(frozen=True)
class DecisionReceipt:
    task_id: str
    input_digest: str
    routing_contract_version: str
    rules_config_identity: str
    config_identity: str
    config_digest: str
    candidate_engine: str
    candidate_source_commit: str
    adapter_source_sha256: str
    runner_source_sha256: str
    checkpoint_repo: str
    checkpoint_revision: str
    checkpoint_artifact_hash: str
    adapter_version: str
    runner_version: str
    environment_id: str
    execution_mode: str
    started_at: str | None
    completed_at: str | None
    decision: str
    status: str
    failure_class: str | None
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["evidence_refs"] = list(self.evidence_refs)
        required_identity = (
            "task_id", "input_digest", "routing_contract_version", "config_digest",
            "candidate_engine", "candidate_source_commit", "checkpoint_repo",
            "checkpoint_revision", "checkpoint_artifact_hash", "adapter_version",
            "adapter_source_sha256", "runner_version", "runner_source_sha256",
            "environment_id", "execution_mode", "status", "failure_class", "evidence_refs",
        )
        nullable = {"failure_class"}
        missing = [
            name for name in required_identity
            if name not in result or (name not in nullable and (result[name] is None or result[name] == ""))
        ]
        if missing:
            raise ValueError(f"DecisionReceipt missing required identity fields: {', '.join(missing)}")
        expected_status = DECISION_STATUS.get(self.decision)
        if expected_status is None:
            raise ValueError(f"unsupported DecisionReceipt decision: {self.decision}")
        if self.status != expected_status:
            raise ValueError(
                f"DecisionReceipt decision/status mismatch: {self.decision} requires {expected_status}"
            )
        if self.failure_class not in FAILURE_CLASSES:
            raise ValueError(f"unsupported DecisionReceipt failure_class: {self.failure_class}")
        if (self.decision == "NOT_READY") != (self.failure_class is not None):
            raise ValueError("DecisionReceipt failure_class must be set exactly for NOT_READY decisions")
        for name in ("input_digest", "config_digest", "adapter_source_sha256", "runner_source_sha256"):
            if not SHA256_RE.fullmatch(result[name]):
                raise ValueError(f"DecisionReceipt {name} must be a valid SHA-256")
        if self.decision in SUCCESS_LIKE_DECISIONS:
            for name in ("adapter_version", "runner_version", "environment_id", "execution_mode"):
                if not isinstance(result[name], str) or not result[name]:
                    raise ValueError(f"success receipt requires non-empty {name}")
            if not SHA256_RE.fullmatch(self.checkpoint_artifact_hash):
                raise ValueError("success receipt requires a verified checkpoint SHA-256; unverified identity cannot produce PASS or QUALIFIED_FOR_REVIEW")
        elif self.status == "NOT_READY" and self.failure_class == "ARTIFACT_MISSING":
            if self.checkpoint_artifact_hash not in {"UNKNOWN", "NOT_ACQUIRED"}:
                raise ValueError("ARTIFACT_MISSING receipt must use an unavailable artifact hash marker")
        elif self.checkpoint_artifact_hash not in {"UNKNOWN", "NOT_ACQUIRED"} and (
            not isinstance(self.checkpoint_artifact_hash, str)
            or not SHA256_RE.fullmatch(self.checkpoint_artifact_hash)
        ):
            raise ValueError("checkpoint artifact identity must be a SHA-256 or an allowed unavailable marker")
        return result


def prepare_receipt(request: dict[str, Any], *, runner_version: str, environment_id: str) -> DecisionReceipt:
    """Validate a routing-v0 request and freeze identities without execution."""
    baseline_decision = route(request)  # Existing contract validation + canonical digest.
    return DecisionReceipt(
        task_id=baseline_decision["task_id"],
        input_digest=baseline_decision["input_digest"],
        routing_contract_version=CONTRACT_VERSION,
        rules_config_identity=RULES_CONFIG_IDENTITY,
        config_identity=CONFIG_IDENTITY,
        config_digest=canonical_config_digest(),
        candidate_engine=CANDIDATE_ENGINE,
        candidate_source_commit=CANDIDATE_SOURCE_COMMIT,
        adapter_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        runner_source_sha256=hashlib.sha256(Path(__file__).with_name("runner.py").read_bytes()).hexdigest(),
        checkpoint_repo=CHECKPOINT_REPO,
        checkpoint_revision=CHECKPOINT_REVISION,
        checkpoint_artifact_hash=CHECKPOINT_ARTIFACT_HASH,
        adapter_version=ADAPTER_VERSION,
        runner_version=runner_version,
        environment_id=environment_id,
        execution_mode="CPU_FIRST_LOCAL",
        started_at=None,
        completed_at=None,
        decision="NOT_EVALUATED",
        status="PREPARED",
        failure_class=None,
        evidence_refs=("data/laya-artifact-manifest.json", "data/laya-environment.json"),
    )


def canonical_config_digest() -> str:
    """Digest the frozen B0 config identity; contains no model or task data."""
    payload = json.dumps({"config_identity": CONFIG_IDENTITY}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
