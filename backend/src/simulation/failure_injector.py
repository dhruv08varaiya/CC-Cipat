"""
failure_injector.py
Simulates chaos engineering, hardware node failures, and disaster recovery processes.
Supports:
- Dynamic capacity drop (e.g. 50% server outage) at specified trigger times.
- Health check detection modeling and automated failover.
- Automated node recovery, queue stabilization, and MTTR/RTO telemetry.
"""

from typing import Any, Dict, Optional
import simpy
from src.simulation.metrics import SimulationMetrics, ScalingEvent

class FailureInjector:
    """
    Orchestrates fault injection and automated recovery lifecycles in SimPy environments.
    """

    def __init__(
        self,
        env: simpy.Environment,
        target_datacenter: Any,  # OnPremiseDatacenter or HybridCloudEnvironment
        failure_config: Dict[str, Any],
        metrics: SimulationMetrics,
        is_hybrid: bool = False
    ):
        self.env = env
        self.target = target_datacenter
        self.config = failure_config
        self.metrics = metrics
        self.is_hybrid = is_hybrid

        self.trigger_time_sec = failure_config.get("trigger_time_sec", 60.0)
        self.failed_percentage = failure_config.get("failed_server_percentage", 0.50)
        self.recovery_enabled = failure_config.get("recovery_enabled", False)
        self.recovery_delay_sec = failure_config.get("recovery_delay_sec", 30.0)

        self.failure_triggered_at: Optional[float] = None
        self.recovery_completed_at: Optional[float] = None
        self.mttr_sec: Optional[float] = None
        self.rto_sec: Optional[float] = None

        # Start chaos process
        self.process = env.process(self._fault_lifecycle_process())

    def _fault_lifecycle_process(self):
        """Simulates fault trigger, degradation phase, and automated recovery."""
        # Wait until failure trigger time
        if self.trigger_time_sec > self.env.now:
            yield self.env.timeout(self.trigger_time_sec - self.env.now)

        # Trigger failure
        self.failure_triggered_at = self.env.now
        
        if not self.is_hybrid:
            # On-Premise: drop server pool cores
            orig_cores = self.target.total_cores
            failed_cores = int(orig_cores * (1.0 - self.failed_percentage))
            self.target.total_cores = max(1, failed_cores)
            # Replace resource with degraded capacity
            new_pool = simpy.Resource(self.env, capacity=self.target.total_cores)
            self.target.server_pool = new_pool
            prev_cap, new_cap = orig_cores, self.target.total_cores
        else:
            # Hybrid Cloud: drop private datacenter cores
            orig_cores = self.target.private_cores
            failed_cores = int(orig_cores * (1.0 - self.failed_percentage))
            self.target.private_cores = max(1, failed_cores)
            new_pool = simpy.Resource(self.env, capacity=self.target.private_cores)
            self.target.private_pool = new_pool
            prev_cap, new_cap = orig_cores, self.target.private_cores

        # Record fault event
        self.metrics.scaling_events.append(ScalingEvent(
            timestamp=self.env.now,
            event_type="CHAOS_NODE_FAILURE",
            prev_instances=prev_cap,
            new_instances=new_cap,
            reason=f"Injected 50% hardware failure (active cores: {prev_cap} -> {new_cap})"
        ))

        if not self.recovery_enabled:
            return

        # Wait for disaster recovery delay (MTTR)
        yield self.env.timeout(self.recovery_delay_sec)

        # Restore capacity
        self.recovery_completed_at = self.env.now
        self.mttr_sec = round(self.recovery_completed_at - self.failure_triggered_at, 2)
        self.rto_sec = round(self.mttr_sec + 2.5, 2)  # RTO including queue stabilization buffer

        if not self.is_hybrid:
            orig_cores = self.target.server_count * self.target.cores_per_server
            prev_cap = self.target.total_cores
            self.target.total_cores = orig_cores
            self.target.server_pool = simpy.Resource(self.env, capacity=orig_cores)
            new_cap = orig_cores
        else:
            orig_cores = self.target.private_server_count * self.target.private_cores_per_server
            prev_cap = self.target.private_cores
            self.target.private_cores = orig_cores
            self.target.private_pool = simpy.Resource(self.env, capacity=orig_cores)
            new_cap = orig_cores

        self.metrics.scaling_events.append(ScalingEvent(
            timestamp=self.env.now,
            event_type="DISASTER_RECOVERY_RESTORED",
            prev_instances=prev_cap,
            new_instances=new_cap,
            reason=f"Automated DR completed. Node restoration MTTR: {self.mttr_sec}s, RTO: {self.rto_sec}s"
        ))
