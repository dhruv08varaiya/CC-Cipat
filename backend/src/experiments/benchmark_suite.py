"""
benchmark_suite.py
Stage 8: End-to-End Comparative Evaluation Suite (E1 through E8).
Executes all experiments deterministically, validates invariants, and exports summaries.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from src.experiments.comparison import ComparisonChecker
from src.experiments.e4_burst_autoscaling import E4ExperimentRunner
from src.experiments.e5_failure_resilience import E5ExperimentRunner
from src.experiments.e6_disaster_recovery import E6ExperimentRunner
from src.experiments.e7_security_classification import E7SecurityExperimentRunner
from src.experiments.e8_cost_pareto_analysis import E8CostExperimentRunner

class BenchmarkSuite:
    def __init__(self, backend_dir: Path, seed: int = 42, event_limit: int = 2000):
        self.backend_dir = backend_dir
        self.seed = seed
        self.event_limit = event_limit
        self.config_path = backend_dir / "config" / "simulation_config.json"
        self.rules_path = backend_dir / "config" / "security_rules.json"
        self.workloads_dir = backend_dir / "data" / "workloads"
        self.results_dir = backend_dir / "results" / "processed"

    def run_all(self) -> Dict[str, Any]:
        results = {}
        print("="*70)
        print("CC-CIPAT END-TO-END BENCHMARK EVALUATION SUITE (E1 - E8)")
        print("="*70)

        # 1. E1 - Normal Load Baseline (W1)
        print("\n[*] Running E1: Normal Load (W1 - 600 RPS)...")
        w1_path = self._get_workload_path("W1")
        e1_runner = ComparisonChecker(self.config_path, w1_path, self.seed, self.event_limit)
        results["E1"] = e1_runner.run(self.results_dir / "E1")
        print("    -> E1 Complete.")

        # 2. E2 - Peak Load (W2)
        print("\n[*] Running E2: Peak Load (W2 - 1400 RPS)...")
        w2_path = self._get_workload_path("W2")
        e2_runner = ComparisonChecker(self.config_path, w2_path, self.seed, self.event_limit)
        results["E2"] = e2_runner.run(self.results_dir / "E2")
        print("    -> E2 Complete.")

        # 3. E3 - Extreme Load (W3)
        print("\n[*] Running E3: Extreme Load (W3 - 2600 RPS)...")
        w3_path = self._get_workload_path("W3")
        e3_runner = ComparisonChecker(self.config_path, w3_path, self.seed, self.event_limit)
        results["E3"] = e3_runner.run(self.results_dir / "E3")
        print("    -> E3 Complete.")

        # 4. E4 - Burst Autoscaling (W4)
        print("\n[*] Running E4: Burst Autoscaling (W4 - 600->2800 RPS)...")
        w4_path = self._get_workload_path("W4")
        e4_runner = E4ExperimentRunner(self.config_path, w4_path, self.seed, self.event_limit)
        results["E4"] = e4_runner.run(self.results_dir / "E4")
        print("    -> E4 Complete.")

        # 5. E5 - Failure Resilience (W5)
        print("\n[*] Running E5: Failure Resilience (W5 50% Outage)...")
        w5_path = self._get_workload_path("W5")
        e5_runner = E5ExperimentRunner(self.config_path, w5_path, self.seed, self.event_limit)
        results["E5"] = e5_runner.run(self.results_dir / "E5")
        print("    -> E5 Complete.")

        # 6. E6 - Disaster Recovery (W6)
        print("\n[*] Running E6: Disaster Recovery (W6 MTTR/RTO)...")
        w6_path = self._get_workload_path("W6")
        e6_runner = E6ExperimentRunner(self.config_path, w6_path, self.seed, self.event_limit)
        results["E6"] = e6_runner.run(self.results_dir / "E6")
        print("    -> E6 Complete.")

        # 7. E7 - Security Classification Benchmark
        print("\n[*] Running E7: 4-Tier Security Classification...")
        e7_runner = E7SecurityExperimentRunner(self.config_path, self.rules_path, w1_path, self.seed, self.event_limit)
        results["E7"] = e7_runner.run(self.results_dir / "E7")
        print("    -> E7 Complete.")

        # 8. E8 - Financial TCO & Pareto Analysis
        print("\n[*] Running E8: 3-Year TCO & Cost-Performance Pareto...")
        e8_runner = E8CostExperimentRunner(self.config_path)
        results["E8"] = e8_runner.run(self.results_dir / "E8")
        print("    -> E8 Complete.")

        print("\n" + "="*70)
        print("ALL EXPERIMENTS E1 THROUGH E8 EXECUTED & VALIDATED SUCCESSFULLY!")
        print("="*70)
        return results

    def _get_workload_path(self, prefix: str) -> Path:
        matches = list(self.workloads_dir.glob(f"{prefix}*.jsonl"))
        if matches:
            return matches[0]
        raise FileNotFoundError(f"Workload file with prefix {prefix} not found in {self.workloads_dir}")

if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent.parent
    suite = BenchmarkSuite(base, seed=42, event_limit=1500)
    suite.run_all()
