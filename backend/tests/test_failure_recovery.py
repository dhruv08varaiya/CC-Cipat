"""
test_failure_recovery.py
Unit tests verifying Stage 7 Failure Injection, Automated Recovery, and MTTR calculation.
"""

from pathlib import Path
import pytest
import simpy

from src.simulation.metrics import SimulationMetrics
from src.simulation.on_premise import OnPremiseDatacenter
from src.simulation.hybrid_cloud import HybridCloudEnvironment
from src.simulation.failure_injector import FailureInjector
from src.experiments.e8_cost_pareto_analysis import E8CostExperimentRunner

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "simulation_config.json"
import json
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

def test_on_premise_failure_capacity_drop():
    env = simpy.Environment()
    metrics = SimulationMetrics("On-Prem-Test", "W5", 42, 64, 64)
    dc = OnPremiseDatacenter(env, CONFIG, metrics, seed=42)

    failure_cfg = {
        "trigger_time_sec": 5.0,
        "failed_server_percentage": 0.50,
        "recovery_enabled": False
    }
    FailureInjector(env, dc, failure_cfg, metrics, is_hybrid=False)

    assert dc.total_cores == 64
    env.run(until=10.0)
    # After 5.0s, total_cores should drop by 50% (to 32)
    assert dc.total_cores == 32
    assert any(ev.event_type == "CHAOS_NODE_FAILURE" for ev in metrics.scaling_events)

def test_disaster_recovery_restoration():
    env = simpy.Environment()
    metrics = SimulationMetrics("DR-Test", "W6", 42, 56, 48)
    hybrid = HybridCloudEnvironment(env, CONFIG, metrics, seed=42, autoscaling_enabled=True)

    failure_cfg = {
        "trigger_time_sec": 5.0,
        "failed_server_percentage": 0.50,
        "recovery_enabled": True,
        "recovery_delay_sec": 10.0
    }
    injector = FailureInjector(env, hybrid, failure_cfg, metrics, is_hybrid=True)

    env.run(until=8.0)
    assert hybrid.private_cores == 24  # Degraded

    env.run(until=20.0)
    assert hybrid.private_cores == 48  # Restored
    assert injector.mttr_sec == 10.0
    assert any(ev.event_type == "DISASTER_RECOVERY_RESTORED" for ev in metrics.scaling_events)

def test_e8_cost_financial_model():
    runner = E8CostExperimentRunner(CONFIG_PATH)
    res = runner.run()
    assert res["experiment_id"] == "E8"
    assert res["financial_summary"]["three_year_savings_usd"] > 0
    assert res["financial_summary"]["three_year_savings_pct"] > 15.0
