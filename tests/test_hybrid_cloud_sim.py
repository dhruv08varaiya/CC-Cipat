"""
test_hybrid_cloud_sim.py
Comprehensive unit tests for the Secure Hybrid Cloud simulation engine.
Validates deterministic compliance routing, tier isolation, queue bounds, reproducibility,
accounting invariants, and error resilience.
"""

import copy
import json
from pathlib import Path
import tempfile
import unittest
import simpy

from src.simulation.engine import SimulationEngine
from src.simulation.hybrid_cloud import HybridCloudEnvironment
from src.simulation.metrics import SimulationMetrics


class TestHybridCloudSimulation(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.config_path = self.root_dir / "config" / "simulation_config.json"
        self.workload_w1_path = self.root_dir / "data" / "workloads" / "W1.jsonl"
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.base_config = json.load(f)

    def test_routing_policy_deterministic_compliance(self):
        """Validates that classification tier strictly governs private vs public tier routing."""
        env = simpy.Environment()
        metrics = SimulationMetrics("Test", "W1", 42, 56, 64, 48, 8)
        hybrid = HybridCloudEnvironment(env, self.base_config, metrics, seed=42)

        # 1. RESTRICTED -> PRIVATE
        tier, reason = hybrid.route_request({
            "request_type": "fund_transfer",
            "classification_tier": "RESTRICTED"
        })
        self.assertEqual(tier, "PRIVATE")
        self.assertEqual(reason, "classification_policy")

        # 2. CONFIDENTIAL -> PRIVATE
        tier, reason = hybrid.route_request({
            "request_type": "transaction_history",
            "classification_tier": "CONFIDENTIAL"
        })
        self.assertEqual(tier, "PRIVATE")
        self.assertEqual(reason, "classification_policy")

        # 3. PUBLIC -> PUBLIC
        tier, reason = hybrid.route_request({
            "request_type": "exchange_rate_lookup",
            "classification_tier": "PUBLIC"
        })
        self.assertEqual(tier, "PUBLIC")
        self.assertEqual(reason, "classification_policy")

        # 4. INTERNAL -> PUBLIC
        tier, reason = hybrid.route_request({
            "request_type": "batch_analytics_report",
            "classification_tier": "INTERNAL"
        })
        self.assertEqual(tier, "PUBLIC")
        self.assertEqual(reason, "classification_policy")

        # 5. Missing tier fallback to service mapping
        tier, reason = hybrid.route_request({
            "request_type": "branch_atm_locator",
            "classification_tier": "UNKNOWN_CUSTOM"
        })
        self.assertEqual(tier, "PUBLIC")
        self.assertEqual(reason, "service_policy")

        # 6. Completely unknown event safe fallback
        tier, reason = hybrid.route_request({
            "request_type": "undefined_custom_op",
            "classification_tier": "UNDEFINED"
        })
        self.assertEqual(tier, "PRIVATE")
        self.assertEqual(reason, "default_safe_fallback")

    def test_accounting_invariants(self):
        """Verifies total_requests == completed + dropped + failed across dual tiers."""
        engine = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w1_path,
            seed=42,
            max_events=120
        )
        summary = engine.run_hybrid_cloud()
        acct = summary["request_accounting"]
        self.assertEqual(
            acct["total_requests"],
            acct["completed_requests"] + acct["dropped_requests"] + acct["failed_requests"]
        )
        self.assertGreaterEqual(acct["completed_requests"], 1)

    def test_tier_breakdown_metrics(self):
        """Verifies that tier-specific request counts sum up to total requests."""
        engine = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w1_path,
            seed=42,
            max_events=100
        )
        summary = engine.run_hybrid_cloud()
        self.assertIn("tier_breakdown", summary)
        tb = summary["tier_breakdown"]

        priv_reqs = tb["private_tier"]["total_requests"]
        pub_reqs = tb["public_tier"]["total_requests"]
        total_reqs = summary["request_accounting"]["total_requests"]

        self.assertEqual(priv_reqs + pub_reqs, total_reqs)
        self.assertGreater(priv_reqs, 0)
        self.assertGreater(pub_reqs, 0)

    def test_reproducibility(self):
        """Tests that running hybrid cloud twice with seed=42 produces bit-for-bit identical metrics."""
        engine1 = SimulationEngine(self.config_path, self.workload_w1_path, seed=42, max_events=150)
        s1 = engine1.run_hybrid_cloud()

        engine2 = SimulationEngine(self.config_path, self.workload_w1_path, seed=42, max_events=150)
        s2 = engine2.run_hybrid_cloud()

        self.assertEqual(s1["request_accounting"], s2["request_accounting"])
        self.assertEqual(
            s1["performance_metrics"]["avg_response_time_ms"],
            s2["performance_metrics"]["avg_response_time_ms"]
        )
        self.assertEqual(
            s1["tier_breakdown"]["private_tier"]["completed_requests"],
            s2["tier_breakdown"]["private_tier"]["completed_requests"]
        )

    def test_queue_overflow_tier_isolation(self):
        """Verifies that an overflow in the public tier drops public requests without crashing private tier."""
        constrained_config = copy.deepcopy(self.base_config)
        # Constrain public tier queue to 1
        constrained_config["hybrid_cloud"]["public_tier"]["initial_instances"] = 1
        constrained_config["hybrid_cloud"]["public_tier"]["cores_per_instance"] = 1
        constrained_config["hybrid_cloud"]["public_tier"]["max_queue_depth_per_instance"] = 1
        constrained_config["hybrid_cloud"]["public_tier"]["base_processing_latency_ms"] = 50.0

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tf_cfg:
            json.dump(constrained_config, tf_cfg)
            cfg_path = Path(tf_cfg.name)

        try:
            engine = SimulationEngine(cfg_path, self.workload_w1_path, seed=42, max_events=100)
            summary = engine.run_hybrid_cloud()
            tb = summary.get("tier_breakdown", {})
            self.assertGreater(tb["public_tier"]["dropped_requests"], 0, "Public tier should drop when saturated")
            # Private tier should still complete requests successfully
            self.assertGreater(tb["private_tier"]["completed_requests"], 0)
        finally:
            cfg_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
