"""
test_on_premise_sim.py
Comprehensive unit tests for the On-Premise baseline discrete-event simulation engine.
Validates queue overflow, accounting invariants, metrics calculations, reproducibility, and error handling.
"""

import copy
import json
from pathlib import Path
import tempfile
import unittest
import simpy

from src.simulation.engine import SimulationEngine
from src.simulation.metrics import SimulationMetrics
from src.simulation.on_premise import OnPremiseDatacenter


class TestOnPremiseSimulation(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.config_path = self.root_dir / "config" / "simulation_config.json"
        self.workload_w1_path = self.root_dir / "data" / "workloads" / "W1.jsonl"
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.base_config = json.load(f)

    def test_workload_file_loading(self):
        engine = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w1_path,
            seed=42,
            max_events=50
        )
        self.assertEqual(len(engine.workload_events), 50)
        self.assertIn("event_id", engine.workload_events[0])

    def test_empty_workload_handled_safely(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf_path = Path(tf.name)
        try:
            engine = SimulationEngine(
                config_path=self.config_path,
                workload_path=tf_path,
                seed=42
            )
            summary = engine.run_on_premise()
            self.assertEqual(summary["request_accounting"]["total_requests"], 0)
            self.assertEqual(summary["request_accounting"]["completed_requests"], 0)
            self.assertEqual(summary["request_accounting"]["availability_pct"], 100.0)
        finally:
            tf_path.unlink(missing_ok=True)

    def test_accounting_invariants(self):
        """Verify that total_requests == completed + dropped + failed."""
        engine = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w1_path,
            seed=42,
            max_events=100
        )
        summary = engine.run_on_premise()
        acct = summary["request_accounting"]
        self.assertEqual(
            acct["total_requests"],
            acct["completed_requests"] + acct["dropped_requests"] + acct["failed_requests"]
        )
        self.assertGreaterEqual(acct["completed_requests"], 1)

    def test_queue_overflow_drop(self):
        """Tests that when queue depth is constrained, requests over capacity are dropped with QUEUE_OVERFLOW."""
        constrained_config = copy.deepcopy(self.base_config)
        # 1 server, 1 core, queue depth = 2 (severe constraint)
        constrained_config["on_premise"]["server_count"] = 1
        constrained_config["on_premise"]["cores_per_server"] = 1
        constrained_config["on_premise"]["max_queue_depth"] = 2
        constrained_config["on_premise"]["base_processing_latency_ms"] = 50.0

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tf_cfg:
            json.dump(constrained_config, tf_cfg)
            cfg_path = Path(tf_cfg.name)

        try:
            engine = SimulationEngine(
                config_path=cfg_path,
                workload_path=self.workload_w1_path,
                seed=42,
                max_events=50
            )
            summary = engine.run_on_premise()
            acct = summary["request_accounting"]
            self.assertGreater(acct["dropped_requests"], 0, "Constrained queue must drop overflowing requests")
            self.assertEqual(acct["total_requests"], acct["completed_requests"] + acct["dropped_requests"])
        finally:
            cfg_path.unlink(missing_ok=True)

    def test_simulation_reproducibility(self):
        """Tests that two runs with identical seed=42 yield identical summary results."""
        engine1 = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w1_path,
            seed=42,
            max_events=150
        )
        s1 = engine1.run_on_premise()

        engine2 = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w1_path,
            seed=42,
            max_events=150
        )
        s2 = engine2.run_on_premise()

        self.assertEqual(s1["request_accounting"], s2["request_accounting"])
        self.assertEqual(
            s1["performance_metrics"]["avg_response_time_ms"],
            s2["performance_metrics"]["avg_response_time_ms"]
        )
        self.assertEqual(
            s1["performance_metrics"]["throughput_rps"],
            s2["performance_metrics"]["throughput_rps"]
        )

    def test_metrics_ranges(self):
        engine = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w1_path,
            seed=42,
            max_events=80
        )
        summary = engine.run_on_premise()
        perf = summary["performance_metrics"]
        res = summary["resource_utilization"]

        self.assertGreaterEqual(perf["avg_response_time_ms"], 0.0)
        self.assertGreaterEqual(perf["p95_response_time_ms"], perf["median_response_time_ms"])
        self.assertTrue(0.0 <= res["avg_server_utilization_pct"] <= 100.0)
        self.assertTrue(0.0 <= res["peak_server_utilization_pct"] <= 100.0)
        self.assertGreaterEqual(res["max_queue_length"], 0)


if __name__ == "__main__":
    unittest.main()
