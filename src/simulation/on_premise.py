"""
on_premise.py
Discrete-event model of the fixed-capacity legacy On-Premise banking datacenter.
Simulates application server queueing, multi-core contention, database pooling, and network latency.
"""

import hashlib
import random
from typing import Any, Dict, List, Optional
import simpy

from src.simulation.metrics import SimulationMetrics


class OnPremiseDatacenter:
    """
    Fixed-capacity on-premise datacenter with finite request queuing and database connection pooling.
    """

    def __init__(
        self,
        env: simpy.Environment,
        config: Dict[str, Any],
        metrics: SimulationMetrics,
        seed: int = 42
    ):
        self.env = env
        self.config = config
        self.metrics = metrics
        self.seed = seed

        # Extract infrastructure configuration
        on_prem = config.get("on_premise", {})
        self.server_count = on_prem.get("server_count", 8)
        self.cores_per_server = on_prem.get("cores_per_server", 8)
        self.total_cores = self.server_count * self.cores_per_server  # 64 cores
        self.capacity_rps_per_core = on_prem.get("capacity_rps_per_core", 25.0)

        # Latency parameters (converted to seconds)
        self.base_processing_latency_sec = on_prem.get("base_processing_latency_ms", 15.0) / 1000.0
        self.network_latency_sec = on_prem.get("network_latency_ms", 5.0) / 1000.0
        self.max_queue_depth = on_prem.get("max_queue_depth", 5000)

        # Database configuration
        db_cfg = on_prem.get("database", {})
        self.db_pool_capacity = db_cfg.get("connection_pool_capacity", 64)
        self.db_latency_sec = db_cfg.get("base_query_latency_ms", 12.0) / 1000.0
        self.db_required_services = set(db_cfg.get("db_required_services", [
            "account_balance_inquiry",
            "fund_transfer",
            "kyc_verification",
            "loan_application",
            "credit_risk_evaluation",
            "transaction_history"
        ]))

        # SimPy shared resources
        self.server_pool = simpy.Resource(self.env, capacity=self.total_cores)
        self.db_pool = simpy.Resource(self.env, capacity=self.db_pool_capacity)

        # Dynamic state tracking
        self.current_queue_length = 0
        self.is_active = True

        # Start background metrics sampler
        sampling_interval = config.get("simulation", {}).get("metrics_sampling_interval_sec", 1.0)
        self.env.process(self._periodic_metrics_sampler(sampling_interval))

    def stop(self):
        """Signals background processes to stop."""
        self.is_active = False

    def _get_request_rng(self, request_id: str) -> random.Random:
        """Derives a deterministic PRNG instance per request for repeatable service times."""
        hash_val = int(hashlib.sha256(f"{request_id}_{self.seed}".encode()).hexdigest()[:8], 16)
        return random.Random(hash_val)

    def handle_request(self, request_event: Dict[str, Any]):
        """SimPy process modeling the end-to-end request lifecycle."""
        req_id = request_event["event_id"]
        arrival_time = self.env.now
        svc_type = request_event.get("request_type", "unknown")
        tier = request_event.get("classification_tier", "INTERNAL")
        payload_bytes = request_event.get("payload_size_bytes", 1024)

        # 1. Finite Queue Capacity Check
        if self.current_queue_length >= self.max_queue_depth:
            self.metrics.record_dropped(
                request_id=req_id,
                arrival_time=arrival_time,
                drop_time=self.env.now,
                reason="QUEUE_OVERFLOW",
                service_type=svc_type,
                classification_tier=tier
            )
            return

        # 2. Enter Queue
        self.current_queue_length += 1
        rng = self._get_request_rng(req_id)

        # Inbound network hop
        yield self.env.timeout(self.network_latency_sec / 2.0)

        # 3. Application Server Processing
        start_service_time = None
        db_accessed = False

        with self.server_pool.request() as server_req:
            yield server_req
            # Core allocated: leave waiting queue
            self.current_queue_length = max(0, self.current_queue_length - 1)
            start_service_time = self.env.now

            # Computational service time (M/G/c model: log-normal distribution around base processing time)
            payload_factor = (payload_bytes / 1024.0) * 0.001
            mean_cpu = self.base_processing_latency_sec + payload_factor
            # Gaussian variation bounded between 2ms and 200ms
            cpu_service_time = max(0.002, rng.gauss(mean_cpu, mean_cpu * 0.20))
            yield self.env.timeout(cpu_service_time)

            # 4. Core Database Contention (if required by service)
            db_time_ms = 0.0
            if svc_type in self.db_required_services:
                db_accessed = True
                with self.db_pool.request() as db_req:
                    yield db_req
                    db_query_time = max(0.003, rng.gauss(self.db_latency_sec, self.db_latency_sec * 0.25))
                    yield self.env.timeout(db_query_time)
                    db_time_ms = db_query_time * 1000.0

        # 5. Outbound network hop
        yield self.env.timeout(self.network_latency_sec / 2.0)

        # 6. Complete
        self.metrics.record_completed(
            request_id=req_id,
            arrival_time=arrival_time,
            start_service_time=start_service_time or arrival_time,
            completion_time=self.env.now,
            service_type=svc_type,
            classification_tier=tier,
            db_accessed=db_accessed,
            db_time_ms=db_time_ms
        )

    def _periodic_metrics_sampler(self, interval_sec: float):
        """Periodically samples queue depth and resource utilization for time-series analysis."""
        while self.is_active:
            self.metrics.record_time_series_sample(
                timestamp=self.env.now,
                queue_len=self.current_queue_length,
                active_cores=self.server_pool.count,
                total_cores=self.total_cores,
                active_db=self.db_pool.count,
                total_db=self.db_pool_capacity
            )
            yield self.env.timeout(interval_sec)
