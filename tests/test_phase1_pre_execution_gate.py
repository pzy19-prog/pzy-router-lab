import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKET_PATH = ROOT / "data" / "phase1-pre-execution-gate.json"
SCHEMA_PATH = ROOT / "schemas" / "phase1-pre-execution-gate.schema.json"
DOC_PATH = ROOT / "docs" / "phase1-pre-execution-gate.md"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class Phase1PreExecutionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_packet_is_review_only_and_bound_to_requested_base(self):
        packet = self.packet
        self.assertEqual(packet["schema_version"], "phase1-pre-execution-gate-v1")
        self.assertEqual(packet["status"], "PRE_EXECUTION_GATE_READY_FOR_REVIEW")
        self.assertFalse(packet["execution_authorized"])
        self.assertEqual(packet["branch"], "phase1/pre-execution-gate")
        self.assertEqual(packet["base_commit"], "6e10cb1b2d5332180e748f8ddfa141bdecc69abc")
        self.assertEqual(packet["fresh_read"]["main_commit"], packet["base_commit"])
        self.assertEqual(packet["fresh_read"]["current_branch_commit"], packet["base_commit"])
        self.assertTrue(packet["fresh_read"]["worktree_initially_clean"])

    def test_schema_defines_closed_gate_contract(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("phase1-pre-execution-gate.schema.json", self.schema["$id"])
        self.assertTrue(set(self.schema["required"]).issubset(self.packet))
        self.assertEqual(self.schema["properties"]["execution_authorized"]["const"], False)
        self.assertEqual(self.schema["properties"]["status"]["const"], self.packet["status"])

    def test_claim_hierarchy_freezes_both_tracks_without_fabricated_inference(self):
        claims = self.packet["claim_hierarchy"]
        self.assertEqual(claims["formal_inferential_benchmark"], "NOT_YET_JUSTIFIED")
        self.assertEqual(claims["pilot_type"], "NON-INFERENTIAL PILOT")
        self.assertEqual(set(claims["tracks"]), {
            "A_controlled_routing_comparison", "B_end_to_end_system_comparison"
        })
        for track in claims["tracks"].values():
            for key in ("primary_claim", "primary_metric", "secondary_metrics", "paired_case_semantics", "inferential_method_boundary"):
                self.assertTrue(track[key], key)
        self.assertIn("no alpha", claims["alpha_power_and_thresholds"])
        self.assertIn("multiplicity", claims)
        self.assertTrue(claims["descriptive_only"])

    def test_unknown_denominators_and_multiplicity_are_explicit(self):
        claims = self.packet["claim_hierarchy"]
        denominator = claims["unknown_denominator_rule"]
        for required in ("assigned", "unknown", "failure", "never"):
            self.assertIn(required, denominator.lower())
        self.assertIn("descriptive", claims["multiplicity"])
        self.assertIn("UNKNOWN", self.packet["heldout_governance"]["unknown_handling"])

    def test_heldout_is_absent_and_roles_sealing_and_unseal_are_defined(self):
        heldout = self.packet["heldout_governance"]
        self.assertFalse(heldout["formal_heldout_created"])
        self.assertFalse(heldout["formal_heldout_content_present"])
        self.assertIn("HELDOUT_CUSTODIAN", heldout["custodian_role"])
        for key in ("population", "strata", "sample_frame", "generation_protocol", "sealing", "manifest_fields", "case_id", "digests", "overlap_contamination", "blind_route_gold", "blind_task_outcome", "unseal_authorization"):
            self.assertTrue(heldout[key], key)
        self.assertIn("No unseal", heldout["unseal_authorization"])

    def test_candidate_identities_are_pinned_or_explicitly_unknown(self):
        candidates = {candidate["name"]: candidate for candidate in self.packet["candidate_registry"]}
        self.assertEqual(set(candidates), {"Laya", "RouteLLM", "vLLM Semantic Router"})
        for candidate in candidates.values():
            commit = candidate["source_commit"]["value"]
            self.assertRegex(commit, SHA_RE)
            revision = candidate["checkpoint_revision"]["value"]
            status = candidate["checkpoint_revision"]["status"]
            self.assertTrue(SHA_RE.fullmatch(revision) or revision == "UNKNOWN", candidate["name"])
            if revision == "UNKNOWN":
                self.assertEqual(status, "UNKNOWN")
            self.assertNotRegex(candidate["candidate_checkpoint"], r"(?i)(latest|main|master|floating)")
        laya = candidates["Laya"]
        self.assertRegex(laya["checkpoint_revision"]["value"], SHA_RE)
        self.assertIn("exact checkpoint_revision", laya["adapter_status"])
        self.assertEqual(candidates["RouteLLM"]["eligibility"], "NOT_ELIGIBLE_FOR_CURRENT_PHASE_ZERO_PAID_API_BUDGET")
        self.assertEqual(candidates["RouteLLM"]["model_license"]["status"], "UNKNOWN")

    def test_zero_paid_api_and_proposed_budgets_require_approval(self):
        budget = self.packet["resource_budget"]
        self.assertEqual(budget["paid_api_budget"], 0)
        self.assertIn("USER_APPROVAL_REQUIRED", budget)
        for key in ("MAX_MODEL_DOWNLOAD_COUNT", "MAX_MODEL_DOWNLOAD_BYTES", "MAX_DISK_USAGE", "MAX_WALL_CLOCK", "MAX_FULL_BENCHMARK_RERUNS", "MAX_FEASIBILITY_CASES"):
            self.assertFalse(budget[key]["approved"], key)
        self.assertIn("USER_APPROVAL_REQUIRED", self.doc)

    def test_receipt_identity_plan_and_stop_conditions_are_complete(self):
        identity = self.packet["adapter_runner_executor_identity"]
        self.assertIn("RoutingContract", identity["architecture"])
        self.assertIn("DecisionReceipt", identity["architecture"])
        self.assertEqual(identity["end_to_end_architecture"], ["Router", "Adapter", "Executor", "OutcomeReceipt"])
        for field in ("input_digest", "source_commit", "checkpoint_revision", "adapter_version", "config_digest", "environment_digest"):
            self.assertIn(field, identity["receipt_required_fields"])
        self.assertIn("executor_identity_or_NONE", identity["receipt_required_fields"])
        stops = " ".join(item["condition"] for item in self.packet["stop_conditions"])
        for term in ("heldout leakage", "license mismatch", "identity mismatch", "paid API", "policy invariant", "environment incompatibility", "resource", "same root", "receipt identity"):
            self.assertIn(term, stops)

    def test_environment_and_resource_probes_are_recorded_without_model_download(self):
        env = self.packet["environment_plan"]
        for key in ("python", "wsl", "cpu", "ram", "gpu", "disk", "network_policy", "offline_cache_policy"):
            self.assertTrue(env[key], key)
        self.assertIn("Python 3.12.3", env["python"])
        self.assertIn("RTX 2060", env["gpu"])
        self.assertIn("891 GiB", env["disk"])


if __name__ == "__main__":
    unittest.main()
