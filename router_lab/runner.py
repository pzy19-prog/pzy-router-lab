"""Bounded B0 runner skeleton. Only PREPARE and QUALIFY are implemented."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .laya_adapter import (
    CHECKPOINT_REPO,
    CHECKPOINT_REVISION,
    DecisionReceipt,
    prepare_receipt,
)

RUNNER_VERSION = "laya-feasibility-runner-b0.1.0"
MAX_CHECKPOINT_COUNT = 1
MAX_MODEL_DOWNLOAD_BYTES = 750_000_000
MAX_DISK_USAGE_BYTES = 8 * 1024**3
MAX_WALL_CLOCK_SECONDS = 7_200
MAX_DEV_SMOKE_CASES = 6
MAX_FULL_BENCHMARK_RERUNS = 0
PAID_API_BUDGET = 0
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FLOATING_REVISIONS = {"latest", "main", "master", "head", "floating"}
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_MANIFEST = REPOSITORY_ROOT / "data" / "laya-artifact-manifest.json"
CANONICAL_ARTIFACT_ROOT = REPOSITORY_ROOT / "data" / "laya-artifacts"


class PolicyViolation(RuntimeError):
    """A requested action violates a frozen B0 policy guard."""


class ExecutionNotAuthorized(PolicyViolation):
    """LOAD or INFER was requested without explicit execution authorization."""


@dataclass(frozen=True)
class Authorization:
    acquisition_authorized: bool = False
    inference_authorized: bool = False


@dataclass(frozen=True)
class ArtifactState:
    acquisition_status: str = "NOT_ACQUIRED"
    actual_files: int | None = None
    actual_total_bytes: int | None = None
    sha256: str = "UNKNOWN"


@dataclass(frozen=True)
class ArtifactVerification:
    verified: bool
    sha256: str = "UNKNOWN"
    failure_class: str = "ARTIFACT_MISSING"


def _artifact_hash(rows: list[tuple[str, int, str]]) -> str:
    """Hash a stable manifest of relative paths, sizes, and actual file hashes."""
    payload = json.dumps(sorted(rows), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_local_artifact(
    *, manifest_path: Path = CANONICAL_MANIFEST, artifact_root: Path = CANONICAL_ARTIFACT_ROOT
) -> ArtifactVerification:
    """Verify exact manifest identity and all local files; caller state is never authoritative."""
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("repo") != CHECKPOINT_REPO or manifest.get("revision") != CHECKPOINT_REVISION:
            return ArtifactVerification(False, failure_class="ARTIFACT_IDENTITY_MISMATCH")
        if manifest.get("acquisition_status") != "ACQUIRED":
            return ArtifactVerification(False)
        expected = manifest["expected_files"]
        paths = [row["path"] for row in expected]
        if not paths or len(paths) != len(set(paths)):
            return ArtifactVerification(False, failure_class="ARTIFACT_MANIFEST_INVALID")
        rows: list[tuple[str, int, str]] = []
        total_bytes = 0
        for row in expected:
            rel = Path(row["path"])
            if rel.is_absolute() or ".." in rel.parts:
                return ArtifactVerification(False, failure_class="ARTIFACT_MANIFEST_INVALID")
            target = artifact_root / rel
            if artifact_root.is_symlink():
                return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
            # Reject symlinked parent directories and paths resolving outside the artifact root.
            cursor = artifact_root
            for component in rel.parts:
                cursor = cursor / component
                if cursor.is_symlink():
                    return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
            try:
                target.resolve(strict=True).relative_to(artifact_root.resolve(strict=True))
            except (OSError, ValueError):
                return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
            if not target.is_file():
                return ArtifactVerification(False)
            actual_size = target.stat().st_size
            if actual_size != row["bytes"]:
                return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
            file_hash = hashlib.sha256()
            with target.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    file_hash.update(chunk)
            digest = file_hash.hexdigest()
            upstream_digest = row.get("upstream_lfs_sha256")
            if upstream_digest is not None:
                if not isinstance(upstream_digest, str) or not SHA256.fullmatch(upstream_digest):
                    return ArtifactVerification(False, failure_class="ARTIFACT_MANIFEST_INVALID")
                if digest != upstream_digest:
                    return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
            rows.append((rel.as_posix(), actual_size, digest))
            total_bytes += actual_size
        actual_files = len(rows)
        if actual_files != len(expected) or total_bytes != manifest.get("expected_total_bytes"):
            return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
        all_paths = list(artifact_root.rglob("*")) if artifact_root.exists() else []
        if any(path.is_symlink() for path in all_paths):
            return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
        present_paths = {
            path.relative_to(artifact_root).as_posix()
            for path in all_paths
            if path.is_file()
        }
        if present_paths != set(paths):
            return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
        if manifest.get("actual_files") != actual_files or manifest.get("actual_total_bytes") != total_bytes:
            return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
        computed = _artifact_hash(rows)
        declared = manifest.get("sha256", {})
        declared_hash = declared.get("value")
        if declared.get("status") != "VERIFIED_LOCAL" or not isinstance(declared_hash, str) or not SHA256.fullmatch(declared_hash):
            return ArtifactVerification(False, failure_class="ARTIFACT_MANIFEST_INVALID")
        if computed != declared_hash:
            return ArtifactVerification(False, failure_class="ARTIFACT_INTEGRITY_MISMATCH")
        return ArtifactVerification(True, sha256=computed, failure_class="")
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return ArtifactVerification(False)


def validate_candidate(repo: str, revision: str, checkpoint_count: int = 1) -> None:
    if checkpoint_count > MAX_CHECKPOINT_COUNT:
        raise PolicyViolation("checkpoint count exceeds the single approved checkpoint")
    if revision.lower() in FLOATING_REVISIONS or not SHA40.fullmatch(revision):
        raise PolicyViolation("floating or non-exact checkpoint revision is forbidden")
    if repo != CHECKPOINT_REPO or revision != CHECKPOINT_REVISION:
        raise PolicyViolation("checkpoint identity is not the approved exact revision")


def enforce_policy(
    *,
    stage: str,
    authorization: Authorization = Authorization(),
    paid_api: bool = False,
    checkpoint_count: int = 1,
    repo: str = CHECKPOINT_REPO,
    revision: str = CHECKPOINT_REVISION,
    heldout_access: bool = False,
    requested_download_bytes: int = 0,
    requested_disk_bytes: int = 0,
    requested_wall_clock_seconds: int = 0,
    requested_dev_cases: int = 0,
    requested_full_benchmark_reruns: int = 0,
) -> None:
    if paid_api:
        raise PolicyViolation("paid API path is forbidden; budget is zero")
    if heldout_access:
        raise PolicyViolation("heldout access is forbidden")
    if requested_download_bytes > MAX_MODEL_DOWNLOAD_BYTES:
        raise PolicyViolation("model acquisition budget expansion is forbidden")
    if requested_disk_bytes > MAX_DISK_USAGE_BYTES:
        raise PolicyViolation("disk budget expansion is forbidden")
    if requested_wall_clock_seconds > MAX_WALL_CLOCK_SECONDS:
        raise PolicyViolation("wall-clock budget expansion is forbidden")
    if requested_dev_cases > MAX_DEV_SMOKE_CASES:
        raise PolicyViolation("dev case budget expansion is forbidden")
    if requested_full_benchmark_reruns > MAX_FULL_BENCHMARK_RERUNS:
        raise PolicyViolation("full benchmark reruns are forbidden")
    validate_candidate(repo, revision, checkpoint_count)
    if stage == "LOAD" and not authorization.acquisition_authorized:
        raise ExecutionNotAuthorized("LOAD denied: model acquisition/load is not authorized in B0")
    if stage == "INFER" and not authorization.inference_authorized:
        raise ExecutionNotAuthorized("INFER denied: model inference is not authorized in B0")
    if stage not in {"PREPARE", "QUALIFY", "LOAD", "INFER", "RECEIPT"}:
        raise PolicyViolation(f"unknown runner stage: {stage}")


class LayaFeasibilityRunner:
    def __init__(self, *, environment_id: str, authorization: Authorization = Authorization()):
        self.environment_id = environment_id
        self.authorization = authorization

    def prepare(self, request: dict[str, Any]) -> DecisionReceipt:
        enforce_policy(stage="PREPARE", authorization=self.authorization)
        return prepare_receipt(request, runner_version=RUNNER_VERSION, environment_id=self.environment_id)

    def qualify(self, request: dict[str, Any], artifact: ArtifactState = ArtifactState()) -> DecisionReceipt:
        enforce_policy(stage="QUALIFY", authorization=self.authorization)
        receipt = self.prepare(request)
        # Retain the legacy argument for API compatibility, but it is only a hint.
        # Qualification is based solely on the repository manifest and local files.
        verification = verify_local_artifact()
        if not verification.verified:
            return _replace_receipt(
                receipt,
                decision="NOT_READY",
                status="NOT_READY",
                failure_class=verification.failure_class,
            )
        return _replace_receipt(
            receipt,
            checkpoint_artifact_hash=verification.sha256,
            decision="QUALIFIED_FOR_REVIEW",
            status="QUALIFIED_FOR_REVIEW",
        )

    def load(self, *_: Any, **__: Any) -> None:
        enforce_policy(stage="LOAD", authorization=self.authorization)
        raise RuntimeError("LOAD backend is intentionally unimplemented in B0; B1 requires independent review")

    def infer(self, *_: Any, **__: Any) -> None:
        enforce_policy(stage="INFER", authorization=self.authorization)
        raise RuntimeError("INFER backend is intentionally unimplemented in B0; B2 requires separate authorization")

    @staticmethod
    def receipt(receipt: DecisionReceipt) -> dict[str, Any]:
        enforce_policy(stage="RECEIPT")
        return receipt.to_dict()


def _replace_receipt(receipt: DecisionReceipt, **changes: Any) -> DecisionReceipt:
    values = receipt.__dict__ | changes
    return DecisionReceipt(**values)
