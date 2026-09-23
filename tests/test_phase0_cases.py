import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
CASE_FILE = ROOT / "data" / "phase0-cases.jsonl"
PROMPT_FILE = ROOT / "data" / "phase0-prompts.jsonl"
FREEZE_FILE = ROOT / "data" / "phase0-freeze.json"
TARGET_CLASSES = {"local_small", "local_strong", "cloud_strong", "manual_review"}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def language_from_task_instruction(text):
    """Classify the natural-language instruction, ignoring code and data tokens."""
    text = re.sub(r"(?s)```.*?```", " ", text)
    text = re.sub(r"(?m)^\s*(?:def|class|if|return|for|import)\b.*$", " ", text)
    text = re.sub(r"[：:]\s*def\b.*", " ", text)
    text = re.sub(r"\b(?:Python|JSON|API|ID)\b", " ", text)
    has_cjk = re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text) is not None
    has_latin_words = re.search(r"[A-Za-z]{2,}", text) is not None
    if has_cjk and has_latin_words:
        return "mixed"
    if has_cjk:
        return "zh"
    if has_latin_words:
        return "en"
    return "mixed"


class Phase0CasesTests(unittest.TestCase):
    def test_cases_link_to_synthetic_task_inputs_and_provisional_hypotheses(self):
        rows = read_jsonl(CASE_FILE)
        prompts = read_jsonl(PROMPT_FILE)
        case_ids = [row["case_id"] for row in rows]
        prompt_ids = {row["fixture_id"] for row in prompts}

        self.assertEqual(len(rows), 12)
        self.assertEqual(len(prompts), len(rows))
        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertEqual(prompt_ids, set(case_ids))
        self.assertEqual(len(prompt_ids), len(prompts))
        for prompt in prompts:
            self.assertTrue(prompt["task_input"].strip())
            self.assertTrue(prompt["acceptance_criteria"])
            self.assertIn(prompt["execution_mode"], {"execute_and_grade", "policy_only"})
        for row in rows:
            self.assertEqual(row["split"], "dev")
            self.assertEqual(row["prompt_fixture_id"], row["case_id"])
            self.assertEqual(row["provisional_gold"]["status"], "unreviewed_hypothesis")
            self.assertIn(row["provisional_gold"]["target_class"], TARGET_CLASSES)
            self.assertIsInstance(row["requires_executor_outcome"], bool)
            fixture = next(item for item in prompts if item["fixture_id"] == row["prompt_fixture_id"])
            self.assertEqual(row["requires_executor_outcome"], fixture["execution_mode"] == "execute_and_grade")

    def test_language_labels_match_task_instructions(self):
        rows = {row["case_id"]: row for row in read_jsonl(CASE_FILE)}
        prompts = {row["fixture_id"]: row for row in read_jsonl(PROMPT_FILE)}
        expected = {
            "p0-001": "en", "p0-002": "zh", "p0-003": "en", "p0-004": "zh",
            "p0-005": "zh", "p0-006": "zh", "p0-007": "zh", "p0-008": "zh",
            "p0-009": "zh", "p0-010": "zh", "p0-011": "zh", "p0-012": "zh",
        }
        self.assertEqual(set(rows), set(expected))
        for case_id, language in expected.items():
            self.assertEqual(rows[case_id]["language"], language)
            self.assertEqual(language_from_task_instruction(prompts[case_id]["task_input"]), language)

    def test_p0_001_rules_receipt_is_generated_from_its_case_input(self):
        evidence = json.loads((ROOT / "examples" / "phase0-evidence-design.json").read_text(encoding="utf-8"))
        # Resolve artifact paths relative to the repository while keeping the evidence file human-readable.
        rules_input = json.loads((ROOT / evidence["rules_input_file"]).read_text(encoding="utf-8"))
        receipt_path = ROOT / "examples" / evidence["receipt_file"]
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        case = next(row for row in read_jsonl(CASE_FILE) if row["case_id"] == evidence["case_id"])
        prompt = next(row for row in read_jsonl(PROMPT_FILE) if row["fixture_id"] == evidence["prompt_fixture_id"])

        self.assertEqual(evidence["design_status"], "design_only_not_cli_output")
        self.assertEqual(evidence["receipt_kind"], "actual_rules_cli_execution")
        self.assertEqual(evidence["case_id"], evidence["task_id"])
        self.assertEqual(evidence["task_id"], rules_input["task_id"])
        self.assertEqual(rules_input["task_id"], receipt["task_id"])
        self.assertEqual(evidence["case_id"], case["case_id"])
        self.assertEqual(evidence["prompt_fixture_id"], case["prompt_fixture_id"])
        self.assertEqual(prompt["fixture_id"], evidence["prompt_fixture_id"])
        self.assertEqual(rules_input["complexity"], case["complexity"])
        self.assertEqual(rules_input["sensitivity"], case["sensitivity"])
        self.assertEqual(rules_input["risk"], case["risk"])
        self.assertEqual(rules_input["available_targets"], case["available_targets"])
        self.assertEqual(rules_input["allow_cloud"], case["allow_cloud"])
        canonical_input = json.dumps(rules_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(receipt["input_digest"], hashlib.sha256(canonical_input.encode("utf-8")).hexdigest())

        cli_result = subprocess.run(
            [sys.executable, "-m", "router_lab.cli", "route", "--input", str(ROOT / evidence["rules_input_file"])],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(cli_result.stdout), receipt)

        design_fields = evidence["benchmark_evidence"]
        self.assertEqual(design_fields["router_run_status"], "NOT_RUN")
        self.assertEqual(receipt["task_id"], "p0-001")
        example_receipt = json.loads((ROOT / "examples" / "example-rules-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(example_receipt["task_id"], "EXAMPLE-LOW-001")
        self.assertNotEqual(receipt["input_digest"], example_receipt["input_digest"])
        example_input = json.loads((ROOT / "examples" / "low-risk.json").read_text(encoding="utf-8"))
        example_canonical = json.dumps(example_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(example_receipt["input_digest"], hashlib.sha256(example_canonical.encode("utf-8")).hexdigest())

    def test_freeze_hashes_and_formal_preregistration_gates(self):
        manifest = json.loads(FREEZE_FILE.read_text(encoding="utf-8"))
        self.assertEqual(manifest["data_version"], "phase0-synthetic-v1")
        self.assertEqual(manifest["freeze_scope"], "development_and_protocol_validation_only")
        self.assertFalse(manifest["independent_test_eligible"])
        for path, expected_hash in manifest["files_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected_hash)
        for key in (
            "candidate_checkpoints", "adapter_versions",
            "execution_environment_and_hardware", "budget_and_stop_conditions",
            "primary_metrics_and_acceptance_conditions", "sample_size_and_independent_test_split",
        ):
            self.assertIn("PRE-REGISTRATION REQUIRED", manifest[key])
        coverage = manifest["checkpoint_language_coverage"]
        self.assertEqual(coverage["required_case_languages"], ["en", "zh"])
        self.assertIn("PRE-REGISTRATION REQUIRED", coverage["status"])
        self.assertIn("every language label", coverage["rule"])
        self.assertIn("independent_test", manifest["split_boundaries"])
        self.assertIn("PRE-REGISTRATION REQUIRED", manifest["split_boundaries"]["independent_test"])

    def test_protocol_separates_input_tracks_and_freeze_requirements(self):
        protocol = (ROOT / "docs" / "benchmark-plan.md").read_text(encoding="utf-8")
        controlled = protocol.split("**A. Controlled Routing Comparison**", 1)[1].split("**B. End-to-End System Comparison**", 1)[0]
        end_to_end = protocol.split("**B. End-to-End System Comparison**", 1)[1].split("\n\n两个轨道", 1)[0]
        self.assertIn("不得提供 task prompt", controlled)
        self.assertIn("完全相同的序列化能力", controlled)
        self.assertIn("每个 Router 使用其正式 adapter 实际支持的输入", end_to_end)
        self.assertIn("Rules 继续只收元数据", end_to_end)
        self.assertIn("两个轨道分表报告、分开计算与解释", protocol)
        self.assertIn("PRE-REGISTRATION REQUIRED", protocol)
        self.assertIn("独立测试集", protocol)
        self.assertIn("预算上限与停止条件", protocol)
        self.assertIn("主要指标和验收条件", protocol)


if __name__ == "__main__":
    unittest.main()
