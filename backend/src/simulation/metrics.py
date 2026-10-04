"""
metrics.py
Telemetry collector and statistical aggregator for discrete-event banking simulation.
Tracks request-level latencies, queue dynamics, resource utilization, and invariant accounting.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class RequestRecord:
    request_id: str
    arrival_time_sec: float
    start_service_time_sec: Optional[float]
    completion_time_sec: Optional[float]
    waiting_time_ms: float
    service_time_ms: float
    total_response_time_ms: float
    status: str  # "COMPLETED", "DROPPED", "FAILED"
    drop_reason: Optional[str] = None
    service_type: str = ""
    classification_tier: str = ""
    target_tier: str = "DEFAULT"
    routing_reason: str = ""
    db_accessed: bool = False


@dataclass
class ScalingEvent:
    event_id: str
    timestamp_sec: float
    event_type: str  # "SCALE_OUT", "SCALE_IN", "INSTANCE_ACTIVATED", "INSTANCE_TERMINATED"
    old_instance_count: int
    new_instance_count: int
    trigger: str
    utilization_pct: float
    queue_length: int
    reason: str
    provisioning_delay_sec: float = 0.0


@dataclass
class TimeSeriesPoint:
    timestamp_sec: float
    queue_length: int
    active_cores: int
    server_utilization_pct: float
    active_db_connections: int
    db_utilization_pct: float
    cumulative_completed: int
    cumulative_dropped: int
    cumulative_failed: int
    private_queue_length: int = 0
    public_queue_length: int = 0
    private_active_cores: int = 0
    public_active_cores: int = 0
    private_utilization_pct: float = 0.0
    public_utilization_pct: float = 0.0
    public_instances: int = 0
    public_provisioning_instances: int = 0
    public_draining_instances: int = 0


class SimulationMetrics:
    """Collects and compiles experimental metrics adhering to formal accounting invariants."""

    def __init__(
        self,
        architecture_name: str,
        workload_id: str,
        seed: int,
        total_cores: int = 64,
        total_db: int = 64,
        total_private_cores: int = 0,
        total_public_cores: int = 0
    ):
        self.architecture_name = architecture_name
        self.workload_id = workload_id
        self.seed = seed
        self.total_cores = total_cores
        self.total_db = total_db
        self.total_private_cores = total_private_cores
        self.total_public_cores = total_public_cores

        self.requests: List[RequestRecord] = []
        self.time_series: List[TimeSeriesPoint] = []
        self.scaling_events: List[ScalingEvent] = []

        # Busy time accumulators (in seconds) for continuous time-integrated utilization
        self.total_cpu_busy_sec: float = 0.0
        self.total_db_busy_sec: float = 0.0
        self.private_cpu_busy_sec: float = 0.0
        self.public_cpu_busy_sec: float = 0.0

        # Tier-specific accounting
        self.private_requests: int = 0
        self.public_requests: int = 0
        self.private_completed: int = 0
        self.public_completed: int = 0
        self.private_dropped: int = 0
        self.public_dropped: int = 0

        # Invariant counters
        self.total_requests: int = 0
        self.completed_requests: int = 0
        self.dropped_requests: int = 0
        self.failed_requests: int = 0

    def record_scaling_event(
        self,
        event_id: str,
        timestamp: float,
        event_type: str,
        old_count: int,
        new_count: int,
        trigger: str,
        utilization_pct: float,
        queue_length: int,
        reason: str,
        provisioning_delay_sec: float = 0.0
    ):
        """Records an autoscaling action (SCALE_OUT, SCALE_IN, etc.)."""
        event = ScalingEvent(
            event_id=event_id,
            timestamp_sec=round(timestamp, 4),
            event_type=event_type,
            old_instance_count=old_count,
            new_instance_count=new_count,
            trigger=trigger,
            utilization_pct=round(utilization_pct, 2),
            queue_length=queue_length,
            reason=reason,
            provisioning_delay_sec=provisioning_delay_sec
        )
        self.scaling_events.append(event)

    def record_completed(
        self,
        request_id: str,
        arrival_time: float,
        start_service_time: float,
        completion_time: float,
        service_type: str,
        classification_tier: str,
        db_accessed: bool,
        db_time_ms: float = 0.0,
        target_tier: str = "DEFAULT",
        routing_reason: str = ""
    ):
        waiting_ms = max(0.0, (start_service_time - arrival_time) * 1000.0)
        service_ms = max(0.0, (completion_time - start_service_time) * 1000.0)
        total_ms = max(0.0, (completion_time - arrival_time) * 1000.0)

        # Accumulate busy core and DB seconds
        self.total_cpu_busy_sec += (service_ms / 1000.0)
        if db_accessed:
            self.total_db_busy_sec += (db_time_ms / 1000.0)

        if target_tier == "PRIVATE":
            self.private_requests += 1
            self.private_completed += 1
            self.private_cpu_busy_sec += (service_ms / 1000.0)
        elif target_tier == "PUBLIC":
            self.public_requests += 1
            self.public_completed += 1
            self.public_cpu_busy_sec += (service_ms / 1000.0)

        record = RequestRecord(
            request_id=request_id,
            arrival_time_sec=arrival_time,
            start_service_time_sec=start_service_time,
            completion_time_sec=completion_time,
            waiting_time_ms=waiting_ms,
            service_time_ms=service_ms,
            total_response_time_ms=total_ms,
            status="COMPLETED",
            service_type=service_type,
            classification_tier=classification_tier,
            target_tier=target_tier,
            routing_reason=routing_reason,
            db_accessed=db_accessed
        )
        self.requests.append(record)
        self.completed_requests += 1

    def record_dropped(
        self,
        request_id: str,
        arrival_time: float,
        drop_time: float,
        reason: str,
        service_type: str,
        classification_tier: str,
        target_tier: str = "DEFAULT",
        routing_reason: str = ""
    ):
        if target_tier == "PRIVATE":
            self.private_requests += 1
            self.private_dropped += 1
        elif target_tier == "PUBLIC":
            self.public_requests += 1
            self.public_dropped += 1

        record = RequestRecord(
            request_id=request_id,
            arrival_time_sec=arrival_time,
            start_service_time_sec=None,
            completion_time_sec=drop_time,
            waiting_time_ms=0.0,
            service_time_ms=0.0,
            total_response_time_ms=0.0,
            status="DROPPED",
            drop_reason=reason,
            service_type=service_type,
            classification_tier=classification_tier,
            target_tier=target_tier,
            routing_reason=routing_reason,
            db_accessed=False
        )
        self.requests.append(record)
        self.dropped_requests += 1

    def record_failed(
        self,
        request_id: str,
        arrival_time: float,
        failure_time: float,
        reason: str,
        service_type: str,
        classification_tier: str,
        target_tier: str = "DEFAULT",
        routing_reason: str = ""
    ):
        record = RequestRecord(
            request_id=request_id,
            arrival_time_sec=arrival_time,
            start_service_time_sec=None,
            completion_time_sec=failure_time,
            waiting_time_ms=0.0,
            service_time_ms=0.0,
            total_response_time_ms=max(0.0, (failure_time - arrival_time) * 1000.0),
            status="FAILED",
            drop_reason=reason,
            service_type=service_type,
            classification_tier=classification_tier,
            target_tier=target_tier,
            routing_reason=routing_reason,
            db_accessed=False
        )
        self.requests.append(record)
        self.failed_requests += 1

    def record_time_series_sample(
        self,
        timestamp: float,
        queue_len: int,
        active_cores: int,
        total_cores: int,
        active_db: int,
        total_db: int,
        private_queue_len: int = 0,
        public_queue_len: int = 0,
        private_active_cores: int = 0,
        public_active_cores: int = 0,
        public_instances: int = 0,
        public_provisioning_instances: int = 0,
        public_draining_instances: int = 0
    ):
        server_util = (active_cores / total_cores * 100.0) if total_cores > 0 else 0.0
        db_util = (active_db / total_db * 100.0) if total_db > 0 else 0.0

        priv_util = (private_active_cores / self.total_private_cores * 100.0) if self.total_private_cores > 0 else 0.0
        current_pub_cores = (public_instances * 4) if public_instances > 0 else self.total_public_cores
        pub_util = (public_active_cores / current_pub_cores * 100.0) if current_pub_cores > 0 else 0.0

        point = TimeSeriesPoint(
            timestamp_sec=round(timestamp, 3),
            queue_length=queue_len,
            active_cores=active_cores,
            server_utilization_pct=round(server_util, 2),
            active_db_connections=active_db,
            db_utilization_pct=round(db_util, 2),
            cumulative_completed=self.completed_requests,
            cumulative_dropped=self.dropped_requests,
            cumulative_failed=self.failed_requests,
            private_queue_length=private_queue_len,
            public_queue_length=public_queue_len,
            private_active_cores=private_active_cores,
            public_active_cores=public_active_cores,
            private_utilization_pct=round(priv_util, 2),
            public_utilization_pct=round(pub_util, 2),
            public_instances=public_instances,
            public_provisioning_instances=public_provisioning_instances,
            public_draining_instances=public_draining_instances
        )
        self.time_series.append(point)

    def verify_accounting_invariants(self) -> Dict[str, Any]:
        """
        Validates the fundamental accounting invariants:
        1. total_requests == completed + dropped + failed
        2. completed <= total
        3. All response times and queue lengths >= 0
        """
        self.total_requests = len(self.requests)
        sum_components = self.completed_requests + self.dropped_requests + self.failed_requests

        invariants_passed = (self.total_requests == sum_components) and (self.completed_requests <= self.total_requests)

        return {
            "invariants_passed": invariants_passed,
            "total_requests": self.total_requests,
            "sum_components": sum_components,
            "completed": self.completed_requests,
            "dropped": self.dropped_requests,
            "failed": self.failed_requests
        }

    def compile_summary(self, simulation_duration_sec: float) -> Dict[str, Any]:
        invariant_check = self.verify_accounting_invariants()
        if not invariant_check["invariants_passed"]:
            raise ValueError(f"Accounting invariant violation: {invariant_check}")

        # Latency statistics on completed requests
        completed_latencies = [r.total_response_time_ms for r in self.requests if r.status == "COMPLETED"]
        waiting_times = [r.waiting_time_ms for r in self.requests if r.status == "COMPLETED"]
        service_times = [r.service_time_ms for r in self.requests if r.status == "COMPLETED"]

        if completed_latencies:
            mean_rt = float(np.mean(completed_latencies))
            median_rt = float(np.median(completed_latencies))
            p95_rt = float(np.percentile(completed_latencies, 95))
            p99_rt = float(np.percentile(completed_latencies, 99))
            min_rt = float(np.min(completed_latencies))
            max_rt = float(np.max(completed_latencies))
            std_rt = float(np.std(completed_latencies))
            mean_wait = float(np.mean(waiting_times))
            mean_serv = float(np.mean(service_times))
        else:
            mean_rt = median_rt = p95_rt = p99_rt = min_rt = max_rt = std_rt = mean_wait = mean_serv = 0.0

        # Throughput
        effective_duration = max(0.001, simulation_duration_sec)
        throughput_rps = self.completed_requests / effective_duration

        # Simulated availability formula: completed / total
        availability_pct = (self.completed_requests / self.total_requests * 100.0) if self.total_requests > 0 else 100.0

        # Queue dynamics from time series
        # Exact continuous time-weighted utilization (queueing theory)
        total_core_seconds = self.total_cores * effective_duration
        integrated_server_util = (
            (self.total_cpu_busy_sec / total_core_seconds * 100.0)
            if total_core_seconds > 0
            else 0.0
        )
        avg_server_util = min(100.0, max(0.0, integrated_server_util))

        total_db_seconds = self.total_db * effective_duration
        integrated_db_util = (
            (self.total_db_busy_sec / total_db_seconds * 100.0)
            if total_db_seconds > 0
            else 0.0
        )
        avg_db_util = min(100.0, max(0.0, integrated_db_util))

        # Queue dynamics and peak utilization from time series
        if self.time_series:
            queue_lengths = [p.queue_length for p in self.time_series]
            server_utils = [p.server_utilization_pct for p in self.time_series]
            avg_queue_len = float(np.mean(queue_lengths))
            max_queue_len = int(np.max(queue_lengths))
            peak_server_util = max(avg_server_util, float(np.max(server_utils)))
        else:
            avg_queue_len = 0.0
            max_queue_len = 0
            peak_server_util = avg_server_util

        # Tier-specific metrics calculation (for Hybrid Cloud)
        tier_breakdown = None
        if self.total_private_cores > 0 or self.total_public_cores > 0:
            priv_core_sec = self.total_private_cores * effective_duration
            priv_util = min(100.0, max(0.0, self.private_cpu_busy_sec / priv_core_sec * 100.0)) if priv_core_sec > 0 else 0.0

            pub_core_sec = self.total_public_cores * effective_duration
            pub_util = min(100.0, max(0.0, self.public_cpu_busy_sec / pub_core_sec * 100.0)) if pub_core_sec > 0 else 0.0

            priv_lats = [r.total_response_time_ms for r in self.requests if r.status == "COMPLETED" and r.target_tier == "PRIVATE"]
            pub_lats = [r.total_response_time_ms for r in self.requests if r.status == "COMPLETED" and r.target_tier == "PUBLIC"]

            tier_breakdown = {
                "private_tier": {
                    "total_cores": self.total_private_cores,
                    "total_requests": self.private_requests,
                    "completed_requests": self.private_completed,
                    "dropped_requests": self.private_dropped,
                    "avg_utilization_pct": round(priv_util, 2),
                    "avg_response_time_ms": round(float(np.mean(priv_lats)), 2) if priv_lats else 0.0,
                    "p95_response_time_ms": round(float(np.percentile(priv_lats, 95)), 2) if priv_lats else 0.0
                },
                "public_tier": {
                    "total_cores": self.total_public_cores,
                    "total_requests": self.public_requests,
                    "completed_requests": self.public_completed,
                    "dropped_requests": self.public_dropped,
                    "avg_utilization_pct": round(pub_util, 2),
                    "avg_response_time_ms": round(float(np.mean(pub_lats)), 2) if pub_lats else 0.0,
                    "p95_response_time_ms": round(float(np.percentile(pub_lats, 95)), 2) if pub_lats else 0.0
                },
                "routing_summary": {
                    "private_ratio_pct": round((self.private_requests / self.total_requests * 100.0), 2) if self.total_requests > 0 else 0.0,
                    "public_ratio_pct": round((self.public_requests / self.total_requests * 100.0), 2) if self.total_requests > 0 else 0.0
                }
            }

        summary = {
            "metadata": {
                "architecture": self.architecture_name,
                "workload_id": self.workload_id,
                "random_seed": self.seed,
                "simulation_duration_sec": round(simulation_duration_sec, 3)
            },
            "request_accounting": {
                "total_requests": self.total_requests,
                "completed_requests": self.completed_requests,
                "dropped_requests": self.dropped_requests,
                "failed_requests": self.failed_requests,
                "availability_pct": round(availability_pct, 4)
            },
            "performance_metrics": {
                "throughput_rps": round(throughput_rps, 2),
                "avg_response_time_ms": round(mean_rt, 2),
                "median_response_time_ms": round(median_rt, 2),
                "p95_response_time_ms": round(p95_rt, 2),
                "p99_response_time_ms": round(p99_rt, 2),
                "min_response_time_ms": round(min_rt, 2),
                "max_response_time_ms": round(max_rt, 2),
                "std_response_time_ms": round(std_rt, 2),
                "mean_waiting_time_ms": round(mean_wait, 2),
                "mean_service_time_ms": round(mean_serv, 2)
            },
            "resource_utilization": {
                "avg_server_utilization_pct": round(avg_server_util, 2),
                "peak_server_utilization_pct": round(peak_server_util, 2),
                "avg_database_utilization_pct": round(avg_db_util, 2),
                "avg_queue_length": round(avg_queue_len, 2),
                "max_queue_length": max_queue_len
            }
        }
        if tier_breakdown:
            summary["tier_breakdown"] = tier_breakdown

        # Autoscaling telemetry and statistics
        inst_counts = [p.public_instances for p in self.time_series if p.public_instances > 0]
        if self.scaling_events or inst_counts:
            min_inst = int(np.min(inst_counts)) if inst_counts else 2
            max_inst = int(np.max(inst_counts)) if inst_counts else 2
            avg_inst = float(np.mean(inst_counts)) if inst_counts else 2.0
            scale_out_count = sum(1 for e in self.scaling_events if e.event_type == "SCALE_OUT")
            scale_in_count = sum(1 for e in self.scaling_events if e.event_type == "SCALE_IN")
            summary["autoscaling_summary"] = {
                "scaling_events_total": len(self.scaling_events),
                "scale_out_count": scale_out_count,
                "scale_in_count": scale_in_count,
                "min_public_instances": min_inst,
                "max_public_instances": max_inst,
                "avg_public_instances": round(avg_inst, 2),
                "events": [e.__dict__ for e in self.scaling_events]
            }

        return summary

    def export_results(self, output_dir: Path, simulation_duration_sec: float):
        """Exports raw JSONL requests, time-series CSV, scaling events, and summary JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)

        summary = self.compile_summary(simulation_duration_sec)
        with open(output_dir / "summary_metrics.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Export time series as CSV
        if self.time_series:
            ts_data = [p.__dict__ for p in self.time_series]
            df_ts = pd.DataFrame(ts_data)
            df_ts.to_csv(output_dir / "time_series.csv", index=False)

        # Export raw request-level traces as JSONL
        with open(output_dir / "raw_requests.jsonl", "w", encoding="utf-8") as f:
            for r in self.requests:
                f.write(json.dumps(r.__dict__) + "\n")

        # Export scaling events as JSONL
        with open(output_dir / "scaling_events.jsonl", "w", encoding="utf-8") as f:
            for e in self.scaling_events:
                f.write(json.dumps(e.__dict__) + "\n")
