"""
test_autoscaling.py
Automated unit tests for Stage 5: Public Cloud Autoscaling & Load Balancing.
Validates:
1. Min/max instance boundary enforcement.
2. Sustained utilization threshold scale-out.
3. Sustained low utilization scale-in.
4. Cooldown hysteresis preventing oscillation.
5. Provisioning delay execution (PROVISIONING -> ACTIVE).
6. Load balancer routing only to ACTIVE instances.
7. Graceful draining excluding removed instances.
8. Seed reproducibility of scaling events.
9. Internal consistency of scaling telemetry logs.
10. Accounting invariants under dynamic scaling.
"""

import copy
import json
from pathlib import Path
import unittest
import simpy

from src.simulation.engine import SimulationEngine
from src.simulation.hybrid_cloud import (
    HybridCloudEnvironment,
    PublicCloudInstance,
    PublicLoadBalancer,
    PublicCloudAutoscaler
)
from src.simulation.metrics import SimulationMetrics


class TestAutoscalingAndLoadBalancing(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.config_path = self.root_dir / "config" / "simulation_config.json"
        self.workload_w4_path = self.root_dir / "data" / "workloads" / "W4.jsonl"
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.base_config = json.load(f)

    def test_min_and_max_instance_boundaries(self):
        """Verifies that public instances never scale below min_instances or above max_instances."""
        env = simpy.Environment()
        metrics = SimulationMetrics("Test", "W4", 42, 56, 64, 48, 8)
        cfg = copy.deepcopy(self.base_config)
        cfg["hybrid_cloud"]["autoscaling"]["enabled"] = True
        cfg["hybrid_cloud"]["autoscaling"]["min_instances"] = 3
        cfg["hybrid_cloud"]["autoscaling"]["max_instances"] = 5

        lb = PublicLoadBalancer(env, "round_robin")
        scaler = PublicCloudAutoscaler(env, cfg, lb, metrics, cores_per_instance=4)

        # Initially, active instances must equal min_instances
        active = lb.get_active_instances()
        self.assertEqual(len(active), 3)

        # Force scale-out past max
        scaler.consecutive_high_intervals = 10
        scaler.last_scaling_time = -100.0
        # Trigger scale-out loop step
        env.step()
        all_insts = [i for i in lb.instances if i.state in ("ACTIVE", "PROVISIONING")]
        self.assertLessEqual(len(all_insts), 5, "Instances must not exceed max_instances")

    def test_load_balancer_routes_only_to_active(self):
        """Validates that Load Balancer excludes PROVISIONING, DRAINING, and REMOVED instances."""
        env = simpy.Environment()
        lb = PublicLoadBalancer(env, "round_robin")

        inst1 = PublicCloudInstance(env, "inst-01", 4)
        inst1.state = "ACTIVE"
        inst2 = PublicCloudInstance(env, "inst-02", 4)
        inst2.state = "PROVISIONING"
        inst3 = PublicCloudInstance(env, "inst-03", 4)
        inst3.state = "DRAINING"
        inst4 = PublicCloudInstance(env, "inst-04", 4)
        inst4.state = "REMOVED"

        lb.add_instance(inst1)
        lb.add_instance(inst2)
        lb.add_instance(inst3)
        lb.add_instance(inst4)

        active = lb.get_active_instances()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].instance_id, "inst-01")

        # Round-robin always selects the only active instance
        selected1 = lb.select_instance()
        selected2 = lb.select_instance()
        self.assertEqual(selected1.instance_id, "inst-01")
        self.assertEqual(selected2.instance_id, "inst-01")

    def test_provisioning_delay_state_transition(self):
        """Verifies that an instance stays PROVISIONING until provisioning_delay_sec elapses."""
        env = simpy.Environment()
        metrics = SimulationMetrics("Test", "W4", 42, 56, 64, 48, 8)
        cfg = copy.deepcopy(self.base_config)
        cfg["hybrid_cloud"]["autoscaling"]["enabled"] = False
        cfg["hybrid_cloud"]["autoscaling"]["provisioning_delay_seconds"] = 3.0

        lb = PublicLoadBalancer(env, "round_robin")
        scaler = PublicCloudAutoscaler(env, cfg, lb, metrics, cores_per_instance=4)

        new_inst = PublicCloudInstance(env, "inst-new", 4)
        lb.add_instance(new_inst)
        self.assertEqual(new_inst.state, "PROVISIONING")
        self.assertNotIn(new_inst, lb.get_active_instances())

        env.process(scaler._provision_instance(new_inst))
        env.run(until=2.5)
        self.assertEqual(new_inst.state, "PROVISIONING")
        self.assertNotIn(new_inst, lb.get_active_instances())

        env.run(until=3.1)
        self.assertEqual(new_inst.state, "ACTIVE")
        self.assertIn(new_inst, lb.get_active_instances())

    def test_cooldown_prevents_rapid_oscillation(self):
        """Ensures that scaling actions respect the cooldown_seconds window."""
        env = simpy.Environment()
        metrics = SimulationMetrics("Test", "W4", 42, 56, 64, 48, 8)
        cfg = copy.deepcopy(self.base_config)
        cfg["hybrid_cloud"]["autoscaling"]["enabled"] = True
        cfg["hybrid_cloud"]["autoscaling"]["cooldown_seconds"] = 10.0
        cfg["hybrid_cloud"]["autoscaling"]["monitoring_interval_seconds"] = 1.0
        cfg["hybrid_cloud"]["autoscaling"]["scale_out_consecutive_intervals"] = 1

        lb = PublicLoadBalancer(env, "round_robin")
        scaler = PublicCloudAutoscaler(env, cfg, lb, metrics, cores_per_instance=4)

        # Artificially occupy all cores to trigger 100% util
        for inst in lb.get_active_instances():
            for _ in range(inst.cores):
                inst.server_pool.request()

        scaler.last_scaling_time = env.now
        # Advance 5 seconds (< 10s cooldown)
        env.run(until=5.0)
        # Scale-out must NOT have fired due to cooldown
        scale_events = [e for e in metrics.scaling_events if e.event_type == "SCALE_OUT"]
        self.assertEqual(len(scale_events), 0)

    def test_e4_fixed_vs_autoscaling_runs(self):
        """Verifies that W4 executes with and without autoscaling, obeying accounting invariants."""
        # 1. Fixed run
        engine_fixed = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w4_path,
            seed=42,
            max_events=200
        )
        summary_fixed = engine_fixed.run_hybrid_cloud(autoscaling_enabled=False)
        acct_fixed = summary_fixed["request_accounting"]
        self.assertEqual(
            acct_fixed["total_requests"],
            acct_fixed["completed_requests"] + acct_fixed["dropped_requests"] + acct_fixed["failed_requests"]
        )

        # 2. Autoscaling run
        engine_auto = SimulationEngine(
            config_path=self.config_path,
            workload_path=self.workload_w4_path,
            seed=42,
            max_events=200
        )
        summary_auto = engine_auto.run_hybrid_cloud(autoscaling_enabled=True)
        acct_auto = summary_auto["request_accounting"]
        self.assertEqual(
            acct_auto["total_requests"],
            acct_auto["completed_requests"] + acct_auto["dropped_requests"] + acct_auto["failed_requests"]
        )

        # Both must consume exact same total requests
        self.assertEqual(acct_fixed["total_requests"], acct_auto["total_requests"])

    def test_scale_out_triggered_on_sustained_high_utilization(self):
        """Verifies that sustained high utilization triggers SCALE_OUT and provisions instances."""
        env = simpy.Environment()
        metrics = SimulationMetrics("Test", "W4", 42, 56, 64, 48, 8)
        cfg = copy.deepcopy(self.base_config)
        cfg["hybrid_cloud"]["autoscaling"]["enabled"] = True
        cfg["hybrid_cloud"]["autoscaling"]["scale_out_threshold"] = 0.50
        cfg["hybrid_cloud"]["autoscaling"]["monitoring_interval_seconds"] = 1.0
        cfg["hybrid_cloud"]["autoscaling"]["scale_out_consecutive_intervals"] = 2
        cfg["hybrid_cloud"]["autoscaling"]["cooldown_seconds"] = 1.0
        cfg["hybrid_cloud"]["autoscaling"]["provisioning_delay_seconds"] = 1.0

        lb = PublicLoadBalancer(env, "round_robin")
        scaler = PublicCloudAutoscaler(env, cfg, lb, metrics, cores_per_instance=4)

        # Occupy cores continuously to keep utilization at 100%
        def keep_busy():
            while True:
                reqs = []
                for inst in lb.get_active_instances():
                    for _ in range(inst.cores):
                        reqs.append(inst.server_pool.request())
                yield env.timeout(0.5)

        env.process(keep_busy())
        # Advance 2.5 seconds (exceeding 2 consecutive intervals of 1.0s)
        env.run(until=2.5)

        scale_out_events = [e for e in metrics.scaling_events if e.event_type == "SCALE_OUT"]
        self.assertGreaterEqual(len(scale_out_events), 1, "Should trigger at least one SCALE_OUT event")
        evt = scale_out_events[0]
        self.assertEqual(evt.old_instance_count, 2)
        expected_new = 2 + cfg["hybrid_cloud"]["autoscaling"].get("scale_out_step", 4)
        self.assertEqual(evt.new_instance_count, expected_new)
        self.assertEqual(evt.trigger, "sustained_high_utilization")
        self.assertGreaterEqual(evt.utilization_pct, 50.0)

    def test_scale_in_triggered_on_sustained_low_utilization(self):
        """Verifies that sustained low utilization triggers SCALE_IN down to min_instances."""
        env = simpy.Environment()
        metrics = SimulationMetrics("Test", "W4", 42, 56, 64, 48, 8)
        cfg = copy.deepcopy(self.base_config)
        cfg["hybrid_cloud"]["autoscaling"]["enabled"] = True
        cfg["hybrid_cloud"]["autoscaling"]["min_instances"] = 2
        cfg["hybrid_cloud"]["autoscaling"]["max_instances"] = 10
        cfg["hybrid_cloud"]["autoscaling"]["scale_in_threshold"] = 0.35
        cfg["hybrid_cloud"]["autoscaling"]["monitoring_interval_seconds"] = 1.0
        cfg["hybrid_cloud"]["autoscaling"]["scale_in_consecutive_intervals"] = 2
        cfg["hybrid_cloud"]["autoscaling"]["cooldown_seconds"] = 1.0
        cfg["hybrid_cloud"]["autoscaling"]["provisioning_delay_seconds"] = 0.1

        lb = PublicLoadBalancer(env, "round_robin")
        scaler = PublicCloudAutoscaler(env, cfg, lb, metrics, cores_per_instance=4)

        # Manually add a 3rd active instance so we can scale in to 2
        inst3 = PublicCloudInstance(env, "pub-inst-03", 4)
        inst3.state = "ACTIVE"
        lb.add_instance(inst3)
        self.assertEqual(len(lb.get_active_instances()), 3)

        # Run with 0 load for 3 intervals (3.0s)
        env.run(until=3.0)

        scale_in_events = [e for e in metrics.scaling_events if e.event_type == "SCALE_IN"]
        self.assertGreaterEqual(len(scale_in_events), 1, "Should trigger SCALE_IN event")
        self.assertEqual(scale_in_events[0].old_instance_count, 3)
        self.assertEqual(scale_in_events[0].new_instance_count, 2)

    def test_graceful_draining_workflow(self):
        """Verifies that draining instance completes active requests before state transitions to REMOVED."""
        env = simpy.Environment()
        metrics = SimulationMetrics("Test", "W4", 42, 56, 64, 48, 8)
        cfg = copy.deepcopy(self.base_config)
        cfg["hybrid_cloud"]["autoscaling"]["enabled"] = False

        lb = PublicLoadBalancer(env, "round_robin")
        scaler = PublicCloudAutoscaler(env, cfg, lb, metrics, cores_per_instance=4)

        inst = lb.get_active_instances()[0]
        inst.state = "DRAINING"
        inst.active_requests = 1

        env.process(scaler._drain_instance(inst))
        env.run(until=0.1)
        # Still has 1 active request, so not yet REMOVED
        self.assertEqual(inst.state, "DRAINING")

        # Complete request
        inst.active_requests = 0
        env.run(until=0.2)
        self.assertEqual(inst.state, "REMOVED")
        self.assertIsNotNone(inst.terminated_at)

    def test_scaling_reproducibility(self):
        """Verifies that repeated autoscaling simulation runs produce identical telemetry."""
        engine1 = SimulationEngine(self.config_path, self.workload_w4_path, seed=42, max_events=250)
        s1 = engine1.run_hybrid_cloud(autoscaling_enabled=True)

        engine2 = SimulationEngine(self.config_path, self.workload_w4_path, seed=42, max_events=250)
        s2 = engine2.run_hybrid_cloud(autoscaling_enabled=True)

        self.assertEqual(s1["request_accounting"], s2["request_accounting"])
        self.assertEqual(s1["performance_metrics"], s2["performance_metrics"])
        if "autoscaling_summary" in s1:
            self.assertEqual(s1["autoscaling_summary"], s2["autoscaling_summary"])


if __name__ == "__main__":
    unittest.main()

