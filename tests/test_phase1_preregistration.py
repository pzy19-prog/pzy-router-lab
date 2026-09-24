import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MANIFEST_PATH = ROOT / "data" / "phase1-preregistration.json"
SCHEMA_PATH = ROOT / "schemas" / "phase1-preregistration.schema.json"


class Phase1PreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_manifest_has_required_stage_a_shape(self):
        required = self.schema["required"]
        self.assertTrue(set(required).issubset(self.manifest))
        self.assertEqual(self.manifest["schema_version"], "phase1-preregistration-v1")
        self.assertEqual(self.manifest["status"], "READY_FOR_SOL_REVIEW")
        self.assertFalse(self.manifest["execution_authorized"])
        self.assertEqual(self.manifest["scope"]["stage"], "A")
        self.assertEqual(self.manifest["base_commit"], "47a00d9135fd8c262e82d2a0a16f2ea25ca18372")

    def test_data_plan_does_not_create_or_authorize_a_heldout_set(self):
        data = self.manifest["data_plan"]
        self.assertFalse(data["formal_heldout_created"])
        self.assertEqual(data["phase0_disposition"], "dev_only_not_heldout")
        self.assertIn("PRE_REGISTRATION_REQUIRED", data["generation_method"]["sample_count"])
        self.assertIn("UNKNOWN", data["gold_and_blinding"]["unknown"])
        self.assertTrue(data["leakage_prevention"])

    def test_statistical_thresholds_are_not_fabricated(self):
        stats = self.manifest["sample_size_and_statistics"]
        for key in ("sample_size", "non_inferiority_margin", "acceptance_threshold", "statistical_test_and_alpha"):
            self.assertIn("PRE_REGISTRATION_REQUIRED / NOT YET JUSTIFIED", stats[key])

    def test_metrics_define_units_aggregation_unknowns_and_tracks(self):
        metrics = self.manifest["metrics"]["secondary"]
        names = {metric["name"] for metric in metrics}
        self.assertTrue({
            "decision_correctness", "task_outcome_success", "abstain_escalation_correctness",
            "over_escalation", "router_latency", "end_to_end_latency", "local_resource_usage",
            "api_token_cost", "fallback_behavior", "unknown_rate",
        }.issubset(names))
        for metric in metrics:
            for field in ("unit", "aggregation", "unknown", "tracks"):
                self.assertTrue(metric[field], (metric["name"], field))

    def test_candidate_source_and_model_identity_is_separated(self):
        candidates = {candidate["name"]: candidate for candidate in self.manifest["candidates"]}
        self.assertTrue({"Rules", "Laya", "RouteLLM", "vLLM Semantic Router"}.issubset(candidates))
        for candidate in candidates.values():
            self.assertTrue(candidate["repo"])
            self.assertTrue(candidate["code_license"])
            self.assertTrue(candidate["adapter_status"])
            if "code_commit_candidate" in candidate:
                self.assertRegex(candidate["code_commit_candidate"], r"^[0-9a-f]{40}$")
        self.assertIn("UNKNOWN", candidates["RouteLLM"]["checkpoint_license"])
        self.assertIn("UNKNOWN", candidates["Laya"]["cpu_local_feasibility"])
        self.assertIn("NOT_IMPLEMENTED", candidates["Laya"]["adapter_status"])

    def test_budget_prohibits_costs_and_blocks_unapproved_run_limits(self):
        budget = self.manifest["budget_and_stops"]
        self.assertEqual(budget["paid_api_budget"], "0; fixed")
        self.assertEqual(budget["stage_a_model_downloads"], 0)
        self.assertEqual(budget["stage_a_model_inference_calls"], 0)
        for key in ("future_max_model_downloads", "future_max_disk_use", "future_max_wall_clock", "future_max_benchmark_reruns"):
            self.assertIn("PRE_REGISTRATION_REQUIRED", budget[key])
        self.assertIn("same root", budget["same_root_repair_stop"])

    def test_playbook_status_does_not_promote_candidate_rules(self):
        pb = self.manifest["playbook_preflight"]
        self.assertEqual(pb["authority_state"], "NO_ADOPTED_CURRENT_RULES")
        self.assertEqual(set(pb["topics"].values()), {"NOT_APPLICABLE"})
        doc = (ROOT / pb["record"]).read_text(encoding="utf-8")
        for status in ("APPLICABLE", "NOT_APPLICABLE", "DEFER", "UNKNOWN"):
            self.assertIn(status, doc)
        self.assertIn("No experiment design/verification rule was changed", pb["material_design_change"])

    def test_schema_and_candidate_commit_formats_are_well_formed(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("phase1-preregistration.schema.json", self.schema["$id"])
        for candidate in self.manifest["candidates"]:
            sha = candidate.get("code_commit_candidate")
            if sha:
                self.assertTrue(re.fullmatch(r"[0-9a-f]{40}", sha))


if __name__ == "__main__":
    unittest.main()
