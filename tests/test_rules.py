import copy
import unittest

from router_lab.rules import route


BASE = {
    "task_id": "T1", "complexity": "low", "sensitivity": "public", "risk": "low",
    "available_targets": ["local_small", "local_strong", "cloud_strong"],
}


class RouterRulesTests(unittest.TestCase):
    def decide(self, **changes):
        request = copy.deepcopy(BASE)
        request.update(changes)
        return route(request)

    def test_low_risk_prefers_local(self):
        result = self.decide()
        self.assertEqual(result["selected_target"], "local_small")
        self.assertFalse(result["execution_performed"])

    def test_high_complexity_prefers_local_strong(self):
        self.assertEqual(self.decide(complexity="high")["selected_target"], "local_strong")

    def test_local_fallback(self):
        result = self.decide(complexity="high", available_targets=["local_small"])
        self.assertEqual(result["selected_target"], "local_small")
        self.assertIn("LOCAL_FALLBACK", result["reason_codes"])

    def test_confidential_cloud_blocked_even_opted_in(self):
        result = self.decide(sensitivity="confidential", available_targets=["cloud_strong"], allow_cloud=True)
        self.assertEqual(result["selected_target"], "manual_review")
        self.assertIn("CONFIDENTIAL_CLOUD_BLOCKED", result["reason_codes"])

    def test_cloud_opt_in(self):
        self.assertEqual(self.decide(available_targets=["cloud_strong"])["selected_target"], "manual_review")
        self.assertEqual(self.decide(available_targets=["cloud_strong"], allow_cloud=True)["selected_target"], "cloud_strong")

    def test_cloud_unavailable_fails_closed(self):
        self.assertEqual(self.decide(available_targets=[])["selected_target"], "manual_review")

    def test_high_risk_human_review(self):
        self.assertEqual(self.decide(risk="high", allow_cloud=True)["selected_target"], "manual_review")

    def test_unknown_complexity_human_review(self):
        self.assertEqual(self.decide(complexity="unknown")["selected_target"], "manual_review")

    def test_repeatable_decision(self):
        self.assertEqual(self.decide(), self.decide())

    def test_invalid_sensitivity_fails_closed(self):
        with self.assertRaises(ValueError):
            self.decide(sensitivity="unknown")

    def test_no_unrecognized_task_content_accepted(self):
        with self.assertRaises(ValueError):
            self.decide(prompt="this should never enter a metadata-only decision receipt")

    def test_duplicate_targets_rejected(self):
        with self.assertRaises(ValueError):
            self.decide(available_targets=["local_small", "local_small"])


if __name__ == "__main__":
    unittest.main()
