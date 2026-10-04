import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import simpy

from src.simulation.engine import SimulationEngine
from src.simulation.metrics import SimulationMetrics
from src.experiments.comparison import ComparisonChecker
from src.experiments.e4_burst_autoscaling import E4ExperimentRunner
from src.experiments.e5_failure_resilience import E5ExperimentRunner
from src.experiments.e6_disaster_recovery import E6ExperimentRunner
from src.experiments.e7_security_classification import E7SecurityExperimentRunner
from src.experiments.e8_cost_pareto_analysis import E8CostExperimentRunner
from src.experiments.benchmark_suite import BenchmarkSuite

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BACKEND_DIR / "config"
DATA_DIR = BACKEND_DIR / "data"
RESULTS_DIR = BACKEND_DIR / "results"

class SimRunnerService:
    @staticmethod
    def get_workloads_list() -> List[Dict[str, Any]]:
        workloads_cfg_file = CONFIG_DIR / "workloads_config.json"
        if workloads_cfg_file.exists():
            with open(workloads_cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [
                    {"id": k, **v} for k, v in data.get("workloads", {}).items()
                ]
        return []

    @staticmethod
    def get_simulation_config() -> Dict[str, Any]:
        sim_cfg_file = CONFIG_DIR / "simulation_config.json"
        if sim_cfg_file.exists():
            with open(sim_cfg_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def run_simulation(
        architecture: str,
        workload_id: str = "W1",
        seed: int = 42,
        max_events: Optional[int] = 1000,
        autoscaling_enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        import numpy as np

        config_path = CONFIG_DIR / "simulation_config.json"
        workload_file = DATA_DIR / "workloads" / f"{workload_id}.jsonl"
        if not workload_file.exists():
            matches = list((DATA_DIR / "workloads").glob(f"{workload_id}*.jsonl"))
            if matches:
                workload_file = matches[0]
            else:
                raise FileNotFoundError(f"Workload trace {workload_id} not found in {DATA_DIR / 'workloads'}")

        engine = SimulationEngine(
            config_path=config_path,
            workload_path=workload_file,
            seed=seed,
            max_events=max_events
        )

        if architecture == "on_premise":
            raw_summary = engine.run_on_premise()
        elif architecture in ("hybrid_cloud", "hybrid_fixed", "hybrid_autoscaling"):
            enable_as = autoscaling_enabled if autoscaling_enabled is not None else (architecture == "hybrid_autoscaling")
            raw_summary = engine.run_hybrid_cloud(autoscaling_enabled=enable_as)
        else:
            raise ValueError(f"Unknown architecture type: {architecture}")

        # Construct UI-friendly summary KPI object
        req_acc = raw_summary.get("request_accounting", {})
        perf = raw_summary.get("performance_metrics", {})
        res_util = raw_summary.get("resource_utilization", {})
        meta = raw_summary.get("metadata", {})

        summary = {
            "total_requests": req_acc.get("total_requests", 0),
            "completed_requests": req_acc.get("completed_requests", 0),
            "dropped_requests": req_acc.get("dropped_requests", 0),
            "avg_latency_ms": perf.get("avg_response_time_ms", 0.0),
            "p95_latency_ms": perf.get("p95_response_time_ms", 0.0),
            "p99_latency_ms": perf.get("p99_response_time_ms", 0.0),
            "avg_queue_length": res_util.get("avg_queue_length", 0.0),
            "max_queue_length": res_util.get("max_queue_length", 0),
            "avg_utilization": (res_util.get("avg_server_utilization_pct", 0.0) / 100.0),
            "peak_utilization": (res_util.get("peak_server_utilization_pct", 0.0) / 100.0),
        }

        # Build high-resolution time-series data points for charts
        time_series = []
        metrics = getattr(engine, "metrics", None)
        if metrics and metrics.requests:
            sim_dur = meta.get("simulation_duration_sec", 1.0)
            if sim_dur <= 0:
                sim_dur = max(0.01, max((r.completion_time_sec or 0) for r in metrics.requests))

            num_bins = min(40, max(12, len(metrics.requests) // 25))
            bin_width = sim_dur / num_bins

            for b in range(num_bins):
                t_start = b * bin_width
                t_end = (b + 1) * bin_width
                t_mid = round(t_start + bin_width / 2.0, 3)

                bin_reqs = [r for r in metrics.requests if t_start <= r.arrival_time_sec < t_end]
                bin_completed = [r for r in bin_reqs if r.status == "COMPLETED"]

                avg_lat = float(np.mean([r.total_response_time_ms for r in bin_completed])) if bin_completed else perf.get("avg_response_time_ms", 0.0)
                arr_rate = round(len(bin_reqs) / bin_width, 1) if bin_width > 0 else 0.0
                comp_rate = round(len(bin_completed) / bin_width, 1) if bin_width > 0 else 0.0

                # Nearest time series sample point if available
                nearest_ts = None
                if metrics.time_series:
                    nearest_ts = min(metrics.time_series, key=lambda p: abs(p.timestamp_sec - t_mid))

                q_len = nearest_ts.queue_length if nearest_ts else res_util.get("avg_queue_length", 0)
                util = nearest_ts.server_utilization_pct if nearest_ts else res_util.get("avg_server_utilization_pct", 0.0)
                pub_inst = nearest_ts.public_instances if nearest_ts else (2 if "hybrid" in architecture else 0)

                time_series.append({
                    "time_sec": t_mid,
                    "arrival_rate": arr_rate,
                    "completed_rate": comp_rate,
                    "queue_length": q_len,
                    "utilization": round(util, 1),
                    "latency_ms": round(avg_lat, 2),
                    "active_instances": pub_inst
                })

        # Scaling events
        scaling_events = []
        if metrics and metrics.scaling_events:
            for evt in metrics.scaling_events:
                scaling_events.append({
                    "timestamp": evt.timestamp_sec,
                    "event_type": evt.event_type,
                    "prev_instances": evt.old_instance_count,
                    "new_instances": evt.new_instance_count,
                    "reason": evt.reason
                })

        return {
            "summary": summary,
            "time_series": time_series,
            "scaling_events": scaling_events,
            "raw_summary": raw_summary
        }

    @staticmethod
    def run_e4_experiment(seed: int = 42, max_events: Optional[int] = 3000) -> Dict[str, Any]:
        config_path = CONFIG_DIR / "simulation_config.json"
        matches = list((DATA_DIR / "workloads").glob("W4*.jsonl"))
        workload_file = matches[0] if matches else DATA_DIR / "workloads" / "W4.jsonl"
        runner = E4ExperimentRunner(config_path, workload_file, seed, max_events)
        return runner.run(RESULTS_DIR / "processed" / "E4")

    @staticmethod
    def run_e5_experiment(seed: int = 42, max_events: Optional[int] = 2500) -> Dict[str, Any]:
        config_path = CONFIG_DIR / "simulation_config.json"
        matches = list((DATA_DIR / "workloads").glob("W5*.jsonl"))
        workload_file = matches[0] if matches else DATA_DIR / "workloads" / "W5.jsonl"
        runner = E5ExperimentRunner(config_path, workload_file, seed, max_events)
        return runner.run(RESULTS_DIR / "processed" / "E5")

    @staticmethod
    def run_e6_experiment(seed: int = 42, max_events: Optional[int] = 2500) -> Dict[str, Any]:
        config_path = CONFIG_DIR / "simulation_config.json"
        matches = list((DATA_DIR / "workloads").glob("W6*.jsonl"))
        workload_file = matches[0] if matches else DATA_DIR / "workloads" / "W6.jsonl"
        runner = E6ExperimentRunner(config_path, workload_file, seed, max_events)
        return runner.run(RESULTS_DIR / "processed" / "E6")

    @staticmethod
    def run_e7_experiment(seed: int = 42, max_events: Optional[int] = 2000) -> Dict[str, Any]:
        config_path = CONFIG_DIR / "simulation_config.json"
        rules_path = CONFIG_DIR / "security_rules.json"
        matches = list((DATA_DIR / "workloads").glob("W1*.jsonl"))
        workload_file = matches[0] if matches else DATA_DIR / "workloads" / "W1.jsonl"
        runner = E7SecurityExperimentRunner(config_path, rules_path, workload_file, seed, max_events)
        return runner.run(RESULTS_DIR / "processed" / "E7")

    @staticmethod
    def run_e8_experiment() -> Dict[str, Any]:
        config_path = CONFIG_DIR / "simulation_config.json"
        runner = E8CostExperimentRunner(config_path)
        return runner.run(RESULTS_DIR / "processed" / "E8")

    @staticmethod
    def run_all_benchmarks(seed: int = 42, event_limit: int = 1500) -> Dict[str, Any]:
        suite = BenchmarkSuite(BACKEND_DIR, seed, event_limit)
        return suite.run_all()
