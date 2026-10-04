"""
engine.py
Simulation execution harness that orchestrates workload playback, discrete-event scheduling,
and outputs verified raw/processed metrics.
"""

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import simpy

from src.simulation.metrics import SimulationMetrics
from src.simulation.on_premise import OnPremiseDatacenter
from src.simulation.hybrid_cloud import HybridCloudEnvironment


class SimulationEngine:
    """Orchestrates discrete-event simulation runs for given architectures and workload traces."""

    def __init__(
        self,
        config_path: Path,
        workload_path: Path,
        seed: int = 42,
        max_events: Optional[int] = None
    ):
        self.config_path = config_path
        self.workload_path = workload_path
        self.seed = seed
        self.max_events = max_events

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.workload_events = self._load_workload(workload_path, max_events)

    def _load_workload(self, path: Path, max_events: Optional[int]) -> List[Dict[str, Any]]:
        events = []
        if not path.exists():
            raise FileNotFoundError(f"Workload trace file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                if max_events and idx >= max_events:
                    break
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events

    def run_on_premise(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Executes the on-premise baseline simulation run."""
        env = simpy.Environment()
        workload_id = self.workload_path.stem.split("_")[0]  # e.g., W1, W2, W3
        on_prem = self.config.get("on_premise", {})
        total_cores = on_prem.get("server_count", 8) * on_prem.get("cores_per_server", 8)
        total_db = on_prem.get("database", {}).get("connection_pool_capacity", 64)

        metrics = SimulationMetrics(
            architecture_name="On-Premise-Baseline",
            workload_id=workload_id,
            seed=self.seed,
            total_cores=total_cores,
            total_db=total_db
        )

        datacenter = OnPremiseDatacenter(
            env=env,
            config=self.config,
            metrics=metrics,
            seed=self.seed
        )

        if not self.workload_events:
            datacenter.stop()
            return metrics.compile_summary(0.0)

        all_done_event = env.event()
        in_flight = len(self.workload_events)

        def request_wrapper(event):
            nonlocal in_flight
            req_process = env.process(datacenter.handle_request(event))
            yield req_process
            in_flight -= 1
            if in_flight == 0:
                datacenter.stop()
                metrics.record_time_series_sample(
                    timestamp=env.now,
                    queue_len=datacenter.current_queue_length,
                    active_cores=datacenter.server_pool.count,
                    total_cores=datacenter.total_cores,
                    active_db=datacenter.db_pool.count,
                    total_db=datacenter.db_pool_capacity
                )
                if not all_done_event.triggered:
                    all_done_event.succeed()

        # Workload injector process
        def workload_feeder():
            for event in self.workload_events:
                event_time = event.get("timestamp_sec", 0.0)
                if event_time > env.now:
                    yield env.timeout(event_time - env.now)
                env.process(request_wrapper(event))

        env.process(workload_feeder())

        # Execute until all queued events and handlers complete
        env.run(until=all_done_event)

        simulation_duration = env.now
        summary = metrics.compile_summary(simulation_duration)

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            metrics.export_results(output_dir, simulation_duration)
            # Save configuration snapshot for auditability
            with open(output_dir / "config_snapshot.json", "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)

        return summary

    def run_hybrid_cloud(
        self,
        output_dir: Optional[Path] = None,
        autoscaling_enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Executes the dual-tier hybrid cloud simulation run (fixed or autoscaling)."""
        env = simpy.Environment()
        workload_id = self.workload_path.stem.split("_")[0]

        run_config = copy.deepcopy(self.config)
        if autoscaling_enabled is not None:
            if "hybrid_cloud" not in run_config:
                run_config["hybrid_cloud"] = {}
            if "autoscaling" not in run_config["hybrid_cloud"]:
                run_config["hybrid_cloud"]["autoscaling"] = {}
            run_config["hybrid_cloud"]["autoscaling"]["enabled"] = autoscaling_enabled

        is_autoscaling = run_config.get("hybrid_cloud", {}).get("autoscaling", {}).get("enabled", False)
        arch_name = "Hybrid-Cloud-Autoscaling" if is_autoscaling else "Hybrid-Cloud-Fixed"

        hybrid_cfg = run_config.get("hybrid_cloud", {})
        priv_cfg = hybrid_cfg.get("private_tier", {})
        pub_cfg = hybrid_cfg.get("public_tier", {})
        auto_cfg = hybrid_cfg.get("autoscaling", {})

        total_private_cores = priv_cfg.get("server_count", 6) * priv_cfg.get("cores_per_server", 8)  # 48
        cores_per_pub_inst = auto_cfg.get("cores_per_instance", pub_cfg.get("cores_per_instance", 4))
        initial_pub_inst = auto_cfg.get("min_instances", pub_cfg.get("initial_instances", 2))
        total_public_cores = initial_pub_inst * cores_per_pub_inst  # 8 cores initially
        total_cores = total_private_cores + total_public_cores  # 56 cores initial
        total_db = priv_cfg.get("database", {}).get("connection_pool_capacity", 64)

        metrics = SimulationMetrics(
            architecture_name=arch_name,
            workload_id=workload_id,
            seed=self.seed,
            total_cores=total_cores,
            total_db=total_db,
            total_private_cores=total_private_cores,
            total_public_cores=total_public_cores
        )

        hybrid_env = HybridCloudEnvironment(
            env=env,
            config=run_config,
            metrics=metrics,
            seed=self.seed
        )

        if not self.workload_events:
            hybrid_env.stop()
            return metrics.compile_summary(0.0)

        all_done_event = env.event()
        in_flight = len(self.workload_events)

        def request_wrapper(event):
            nonlocal in_flight
            req_process = env.process(hybrid_env.handle_request(event))
            yield req_process
            in_flight -= 1
            if in_flight == 0:
                if is_autoscaling:
                    # Allow idle observation window for scale-in hysteresis evaluation
                    monitor_int = auto_cfg.get("monitoring_interval_seconds", 0.5)
                    scale_in_consec = auto_cfg.get("scale_in_consecutive_intervals", 2)
                    cooldown = auto_cfg.get("cooldown_seconds", 1.5)
                    idle_window = max(2.5, (scale_in_consec * monitor_int) + cooldown + 0.5)
                    yield env.timeout(idle_window)

                hybrid_env.stop()
                active_pub = len(hybrid_env.load_balancer.get_active_instances())
                current_total_cores = total_private_cores + (active_pub * cores_per_pub_inst)
                metrics.record_time_series_sample(
                    timestamp=env.now,
                    queue_len=hybrid_env.current_private_queue_length + hybrid_env.current_public_queue_length,
                    active_cores=hybrid_env.private_server_pool.count + hybrid_env.public_active_cores,
                    total_cores=current_total_cores,
                    active_db=hybrid_env.private_db_pool.count,
                    total_db=hybrid_env.private_db_capacity,
                    private_queue_len=hybrid_env.current_private_queue_length,
                    public_queue_len=hybrid_env.current_public_queue_length,
                    private_active_cores=hybrid_env.private_server_pool.count,
                    public_active_cores=hybrid_env.public_active_cores,
                    public_instances=active_pub,
                    public_provisioning_instances=sum(1 for inst in hybrid_env.load_balancer.instances if inst.state == "PROVISIONING"),
                    public_draining_instances=sum(1 for inst in hybrid_env.load_balancer.instances if inst.state == "DRAINING")
                )
                if not all_done_event.triggered:
                    all_done_event.succeed()

        def workload_feeder():
            for event in self.workload_events:
                event_time = event.get("timestamp_sec", 0.0)
                if event_time > env.now:
                    yield env.timeout(event_time - env.now)
                env.process(request_wrapper(event))

        env.process(workload_feeder())
        env.run(until=all_done_event)

        last_comp = max((r.completion_time_sec for r in metrics.requests if r.completion_time_sec is not None), default=env.now)
        simulation_duration = max(0.001, last_comp)
        summary = metrics.compile_summary(simulation_duration)

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            metrics.export_results(output_dir, simulation_duration)
            with open(output_dir / "config_snapshot.json", "w", encoding="utf-8") as f:
                json.dump(run_config, f, indent=2)

        return summary
