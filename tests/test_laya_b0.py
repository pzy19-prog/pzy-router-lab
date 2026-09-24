import json
import hashlib
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from jsonschema import Draft202012Validator

from router_lab.laya_adapter import (
    ADAPTER_VERSION,
    CANDIDATE_SOURCE_COMMIT,
    CHECKPOINT_ARTIFACT_HASH,
    CHECKPOINT_REPO,
    CHECKPOINT_REVISION,
)
from router_lab.runner import (
    ArtifactState,
    Authorization,
    ExecutionNotAuthorized,
    LayaFeasibilityRunner,
    PolicyViolation,
    RUNNER_VERSION,
    enforce_policy,
    validate_candidate,
    verify_local_artifact,
    _artifact_hash,
)


ROOT = Path(__file__).parents[1]
REQUEST = {
    "task_id": "B0-001",
    "complexity": "low",
    "sensitivity": "public",
    "risk": "low",
    "available_targets": ["local_small", "local_strong"],
}


class LayaB0Tests(unittest.TestCase):
    def setUp(self):
        self.runner = LayaFeasibilityRunner(environment_id="test-env-b0")

    def test_exact_revision_accepted(self):
        validate_candidate(CHECKPOINT_REPO, CHECKPOINT_REVISION)

    def test_floating_revision_rejected(self):
        for value in ("latest", "main", "master", "floating", "a" * 39):
            with self.subTest(value=value), self.assertRaises(PolicyViolation):
                validate_candidate(CHECKPOINT_REPO, value)

    def test_wrong_checkpoint_and_multiple_checkpoints_rejected(self):
        with self.assertRaises(PolicyViolation):
            validate_candidate(CHECKPOINT_REPO, "0" * 40)
        with self.assertRaises(PolicyViolation):
            validate_candidate("some-other/model", CHECKPOINT_REVISION)
        with self.assertRaises(PolicyViolation):
            validate_candidate(CHECKPOINT_REPO, CHECKPOINT_REVISION, checkpoint_count=2)

    def test_no_artifact_returns_not_ready_without_load(self):
        receipt = self.runner.qualify(REQUEST)
        self.assertEqual(receipt.status, "NOT_READY")
        self.assertEqual(receipt.decision, "NOT_READY")
        self.assertEqual(receipt.failure_class, "ARTIFACT_MISSING")
        with self.assertRaises(ExecutionNotAuthorized):
            self.runner.load()

    def test_infer_without_authorization_is_rejected(self):
        with self.assertRaisesRegex(ExecutionNotAuthorized, "not authorized in B0"):
            self.runner.infer()

    def test_acquisition_before_authorization_is_rejected(self):
        with self.assertRaisesRegex(ExecutionNotAuthorized, "LOAD denied"):
            enforce_policy(stage="LOAD")

    def test_paid_api_heldout_acquisition_and_budget_expansion_rejected(self):
        for kwargs in (
            {"paid_api": True},
            {"heldout_access": True},
            {"stage": "LOAD", "requested_download_bytes": 1, "authorization": Authorization()},
            {"requested_disk_bytes": 8 * 1024**3 + 1},
            {"requested_wall_clock_seconds": 7201},
            {"requested_dev_cases": 7},
            {"requested_full_benchmark_reruns": 1},
        ):
            kwargs.setdefault("stage", "PREPARE")
            with self.subTest(kwargs=kwargs), self.assertRaises(PolicyViolation):
                enforce_policy(**kwargs)

    def test_receipt_preserves_frozen_identities_and_unknown_artifact(self):
        receipt = self.runner.prepare(REQUEST).to_dict()
        self.assertEqual(receipt["candidate_source_commit"], CANDIDATE_SOURCE_COMMIT)
        self.assertEqual(receipt["checkpoint_repo"], CHECKPOINT_REPO)
        self.assertEqual(receipt["checkpoint_revision"], CHECKPOINT_REVISION)
        self.assertEqual(receipt["checkpoint_artifact_hash"], CHECKPOINT_ARTIFACT_HASH)
        self.assertEqual(receipt["adapter_version"], ADAPTER_VERSION)
        self.assertEqual(receipt["runner_version"], RUNNER_VERSION)
        self.assertEqual(len(receipt["adapter_source_sha256"]), 64)
        self.assertEqual(len(receipt["runner_source_sha256"]), 64)
        self.assertEqual(len(receipt["config_digest"]), 64)
        self.assertEqual(receipt["routing_contract_version"], "routing-v0")
        self.assertEqual(receipt["execution_mode"], "CPU_FIRST_LOCAL")
        self.assertIsNone(receipt["started_at"])
        self.assertIsNone(receipt["completed_at"])
        self.assertEqual(receipt["status"], "PREPARED")

    def test_unknown_or_not_acquired_artifact_cannot_be_pass(self):
        for artifact in (
            ArtifactState(acquisition_status="NOT_ACQUIRED", sha256="NOT_ACQUIRED"),
            ArtifactState(acquisition_status="ACQUIRED", sha256="UNKNOWN"),
        ):
            receipt = self.runner.qualify(REQUEST, artifact)
            self.assertEqual(receipt.status, "NOT_READY")
            self.assertNotEqual(receipt.status, "PASS")
        prepared = self.runner.prepare(REQUEST)
        with self.assertRaisesRegex(ValueError, "verified checkpoint SHA-256"):
            replace(prepared, decision="PASS", status="PASS").to_dict()

    def test_forged_caller_state_cannot_qualify_against_not_acquired_manifest(self):
        forged = ArtifactState(acquisition_status="ACQUIRED", sha256="not-a-hash")
        receipt = self.runner.qualify(REQUEST, forged)
        self.assertEqual(receipt.status, "NOT_READY")
        self.assertEqual(receipt.failure_class, "ARTIFACT_MISSING")

    def test_malformed_artifact_hashes_are_rejected(self):
        for malformed in ("not-a-hash", "UNKNOWN", ""):
            with self.subTest(malformed=malformed):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    artifacts = root / "artifacts"
                    artifacts.mkdir()
                    content = b"synthetic identity/integrity fixture"
                    (artifacts / "model.bin").write_bytes(content)
                    manifest = {
                        "repo": CHECKPOINT_REPO,
                        "revision": CHECKPOINT_REVISION,
                        "expected_files": [{"path": "model.bin", "bytes": len(content)}],
                        "expected_total_bytes": len(content),
                        "actual_files": 1,
                        "actual_total_bytes": len(content),
                        "sha256": {"status": "VERIFIED_LOCAL", "value": malformed},
                        "acquisition_status": "ACQUIRED",
                    }
                    manifest_path = root / "manifest.json"
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    verification = verify_local_artifact(manifest_path=manifest_path, artifact_root=artifacts)
                    self.assertFalse(verification.verified)

    def test_synthetic_verified_artifact_plumbing_accepts_complete_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifacts = root / "artifacts"
            artifacts.mkdir()
            content = b"synthetic test fixture; not a model artifact"
            (artifacts / "weights.fixture").write_bytes(content)
            digest = hashlib.sha256(content).hexdigest()
            rows = [("weights.fixture", len(content), digest)]
            manifest = {
                "repo": CHECKPOINT_REPO,
                "revision": CHECKPOINT_REVISION,
                "expected_files": [{"path": "weights.fixture", "bytes": len(content)}],
                "expected_total_bytes": len(content),
                "actual_files": 1,
                "actual_total_bytes": len(content),
                "sha256": {"status": "VERIFIED_LOCAL", "value": _artifact_hash(rows)},
                "acquisition_status": "ACQUIRED",
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            verification = verify_local_artifact(manifest_path=manifest_path, artifact_root=artifacts)
            self.assertTrue(verification.verified)
            self.assertEqual(verification.sha256, manifest["sha256"]["value"])
            qualified = replace(
                self.runner.prepare(REQUEST),
                checkpoint_artifact_hash=verification.sha256,
                decision="QUALIFIED_FOR_REVIEW",
                status="QUALIFIED_FOR_REVIEW",
            )
            self.runner.receipt(qualified)
            schema = json.loads((ROOT / "schemas/decision-receipt.schema.json").read_text())
            self.assertEqual(
                list(Draft202012Validator(schema).iter_errors(qualified.to_dict())),
                [],
            )
            # This only exercises synthetic identity/integrity plumbing, not Laya model execution.

    def test_receipt_schema_requires_complete_success_identity_and_real_hash(self):
        schema = json.loads((ROOT / "schemas/decision-receipt.schema.json").read_text())
        validator = Draft202012Validator(schema)
        receipt = self.runner.prepare(REQUEST).to_dict()
        receipt.update(status="PASS", decision="PASS", checkpoint_artifact_hash="a" * 64)
        self.assertEqual(list(validator.iter_errors(receipt)), [])
        # Synthetic verified identity exercises receipt plumbing only.
        self.runner.receipt(replace(
            self.runner.prepare(REQUEST),
            status="PASS",
            decision="PASS",
            checkpoint_artifact_hash="a" * 64,
        ))
        for field in ("config_digest", "adapter_source_sha256", "runner_source_sha256"):
            with self.subTest(field=field):
                incomplete = receipt.copy()
                incomplete.pop(field)
                self.assertNotEqual(list(validator.iter_errors(incomplete)), [])
        for malformed in ("UNKNOWN", "NOT_ACQUIRED", "", "not-a-hash"):
            with self.subTest(malformed=malformed):
                incomplete = receipt.copy()
                incomplete["checkpoint_artifact_hash"] = malformed
                self.assertNotEqual(list(validator.iter_errors(incomplete)), [])

    def test_receipt_decision_status_matrix_and_success_requirements_fail_closed(self):
        schema = json.loads((ROOT / "schemas/decision-receipt.schema.json").read_text())
        validator = Draft202012Validator(schema)
        prepared = self.runner.prepare(REQUEST)

        # Fresh-read matrix: only these decision/status pairs are valid.
        valid_pairs = (
            ("NOT_EVALUATED", "PREPARED", None),
            ("NOT_READY", "NOT_READY", "ARTIFACT_MISSING"),
            ("QUALIFIED_FOR_REVIEW", "QUALIFIED_FOR_REVIEW", None),
            ("PASS", "PASS", None),
        )
        for decision, status, failure_class in valid_pairs:
            candidate = replace(prepared, decision=decision, status=status, failure_class=failure_class)
            if decision in {"QUALIFIED_FOR_REVIEW", "PASS"}:
                candidate = replace(candidate, checkpoint_artifact_hash="a" * 64)
            self.runner.receipt(candidate)
            self.assertEqual(list(validator.iter_errors(candidate.to_dict())), [])

        # Sol counterexamples: success-like decisions cannot sit on PREPARED with
        # UNKNOWN artifact identity; schema and serializer both reject them.
        for decision in ("PASS", "QUALIFIED_FOR_REVIEW"):
            with self.subTest(decision=decision):
                forged = replace(prepared, decision=decision, status="PREPARED")
                forged_dict = prepared.to_dict()
                forged_dict.update(decision=decision, status="PREPARED")
                self.assertNotEqual(list(validator.iter_errors(forged_dict)), [])
                with self.assertRaises(ValueError):
                    forged.to_dict()

        complete = replace(
            prepared,
            decision="QUALIFIED_FOR_REVIEW",
            status="QUALIFIED_FOR_REVIEW",
            checkpoint_artifact_hash="a" * 64,
        )
        for field in ("adapter_version", "runner_version", "environment_id", "execution_mode"):
            with self.subTest(empty_field=field):
                forged = replace(complete, **{field: ""})
                forged_dict = complete.to_dict()
                forged_dict[field] = ""
                self.assertNotEqual(list(validator.iter_errors(forged_dict)), [])
                with self.assertRaises(ValueError):
                    forged.to_dict()

        for malformed in ("UNKNOWN", "NOT_ACQUIRED", "", "not-a-hash"):
            with self.subTest(invalid_success_hash=malformed):
                forged = replace(complete, checkpoint_artifact_hash=malformed)
                forged_dict = complete.to_dict()
                forged_dict["checkpoint_artifact_hash"] = malformed
                self.assertNotEqual(list(validator.iter_errors(forged_dict)), [])
                with self.assertRaises(ValueError):
                    forged.to_dict()

    def test_receipt_serializer_fails_closed_for_missing_success_identity(self):
        prepared = self.runner.prepare(REQUEST)
        for field in ("config_digest", "adapter_source_sha256", "runner_source_sha256"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                replace(
                    prepared,
                    decision="PASS",
                    status="PASS",
                    checkpoint_artifact_hash="a" * 64,
                    **{field: ""},
                ).to_dict()
        with self.assertRaisesRegex(ValueError, "verified checkpoint SHA-256"):
            replace(prepared, decision="PASS", status="PASS", checkpoint_artifact_hash="UNKNOWN").to_dict()

    def test_canonical_not_acquired_manifest_prevents_real_b0_qualification(self):
        manifest = json.loads((ROOT / "data/laya-artifact-manifest.json").read_text())
        self.assertEqual(manifest["acquisition_status"], "NOT_ACQUIRED")
        receipt = self.runner.qualify(REQUEST, ArtifactState("ACQUIRED", 7, 100, "a" * 64))
        self.assertEqual(receipt.status, "NOT_READY")
        self.assertNotEqual(receipt.status, "QUALIFIED_FOR_REVIEW")

    def test_manifest_states_no_local_artifact_and_binds_exact_revision(self):
        manifest = json.loads((ROOT / "data/laya-artifact-manifest.json").read_text())
        self.assertEqual(manifest["repo"], CHECKPOINT_REPO)
        self.assertEqual(manifest["revision"], CHECKPOINT_REVISION)
        self.assertEqual(manifest["acquisition_status"], "NOT_ACQUIRED")
        self.assertEqual(manifest["sha256"], {"status": "UNKNOWN", "value": "NOT_ACQUIRED"})
        self.assertIsNone(manifest["actual_files"])
        self.assertIsNone(manifest["actual_total_bytes"])
        self.assertEqual(manifest["expected_total_bytes"], sum(row["bytes"] for row in manifest["expected_files"]))


if __name__ == "__main__":
    unittest.main()
