import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import simpy

from src.simulation.engine import SimulationEngine
from src.simulation.metrics import SimulationMetrics
from src.experiments.comparison import ComparisonChecker
from src.experiments.e4_burst_autoscaling import E4ExperimentRunner
from src.experiments.e7_security_classification import E7SecurityExperimentRunner
from src.security.data_classifier import DataClassifier

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
        architecture: str,  # "on_premise", "hybrid_fixed", "hybrid_autoscaling"
        workload_id: str = "W1",
        seed: int = 42,
        max_events: Optional[int] = 1000,
        autoscaling_enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        config_path = CONFIG_DIR / "simulation_config.json"
        
        # Match workload path
        workload_file = DATA_DIR / "workloads" / f"{workload_id}.jsonl"
        if not workload_file.exists():
            # Try looking for W1_normal, etc.
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
            return engine.run_on_premise()
        elif architecture in ("hybrid_cloud", "hybrid_fixed", "hybrid_autoscaling"):
            enable_as = autoscaling_enabled if autoscaling_enabled is not None else (architecture == "hybrid_autoscaling")
            return engine.run_hybrid_cloud(autoscaling_enabled=enable_as)
        else:
            raise ValueError(f"Unknown architecture type: {architecture}")

    @staticmethod
    def run_e4_experiment(seed: int = 42, max_events: Optional[int] = 3000) -> Dict[str, Any]:
        config_path = CONFIG_DIR / "simulation_config.json"
        workload_file = DATA_DIR / "workloads" / "W4.jsonl"
        if not workload_file.exists():
            matches = list((DATA_DIR / "workloads").glob("W4*.jsonl"))
            if matches:
                workload_file = matches[0]

        runner = E4ExperimentRunner(
            config_path=config_path,
            workload_path=workload_file,
            seed=seed,
            max_events=max_events
        )
        return runner.run()

    @staticmethod
    def run_e7_experiment(seed: int = 42, max_events: Optional[int] = 2000) -> Dict[str, Any]:
        config_path = CONFIG_DIR / "simulation_config.json"
        rules_path = CONFIG_DIR / "security_rules.json"
        workload_file = DATA_DIR / "workloads" / "W1.jsonl"
        if not workload_file.exists():
            matches = list((DATA_DIR / "workloads").glob("W1*.jsonl"))
            if matches:
                workload_file = matches[0]

        runner = E7SecurityExperimentRunner(
            config_path=config_path,
            rules_path=rules_path,
            workload_path=workload_file,
            seed=seed,
            max_events=max_events
        )
        return runner.run()
