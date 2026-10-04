"""
hybrid_cloud.py
Discrete-event model of the proposed Secure Hybrid Cloud banking environment.
Partitions traffic into a protected Private Cloud tier (core banking/sensitive data)
and an elastic Public Cloud tier (public/internal services) via deterministic compliance routing.
Supports deterministic load balancing (Round Robin) and dynamic public-cloud autoscaling.
"""

import copy
import hashlib
import random
from typing import Any, Dict, List, Optional, Tuple
import simpy

from src.simulation.metrics import SimulationMetrics


class PublicCloudInstance:
    """Represents an elastic virtual compute instance in the Public Cloud tier."""

    def __init__(self, env: simpy.Environment, instance_id: str, cores: int = 4):
        self.env = env
        self.instance_id = instance_id
        self.cores = cores
        self.server_pool = simpy.Resource(env, capacity=cores)
        self.state = "PROVISIONING"  # PROVISIONING, ACTIVE, DRAINING, REMOVED
        self.created_at = env.now
        self.activated_at: Optional[float] = None
        self.terminated_at: Optional[float] = None
        self.active_requests = 0

    @property
    def active_cores(self) -> int:
        return self.server_pool.count

    @property
    def queue_length(self) -> int:
        return len(self.server_pool.queue)

    @property
    def is_active(self) -> bool:
        return self.state == "ACTIVE"

    @property
    def is_draining(self) -> bool:
        return self.state == "DRAINING"

    def __repr__(self) -> str:
        return f"<Instance {self.instance_id} state={self.state} active_cores={self.active_cores}/{self.cores}>"


class PublicLoadBalancer:
    """
    Distributes incoming public requests across ACTIVE public-cloud instances.
    Excludes PROVISIONING, DRAINING, and REMOVED instances from receiving new requests.
    Supports deterministic Round Robin (default), Least Connections, and Least Loaded strategies.
    """

    def __init__(self, env: simpy.Environment, strategy: str = "round_robin"):
        self.env = env
        self.strategy = strategy.lower()
        self.instances: List[PublicCloudInstance] = []
        self._rr_index = 0

    def add_instance(self, instance: PublicCloudInstance):
        self.instances.append(instance)

    def get_active_instances(self) -> List[PublicCloudInstance]:
        return [inst for inst in self.instances if inst.state == "ACTIVE"]

    def select_instance(self) -> Optional[PublicCloudInstance]:
        active = self.get_active_instances()
        if not active:
            return None

        if self.strategy == "least_connections":
            return min(active, key=lambda inst: inst.active_requests)
        elif self.strategy == "least_loaded":
            return min(active, key=lambda inst: inst.active_cores)
        else:
            # Deterministic Round Robin
            inst = active[self._rr_index % len(active)]
            self._rr_index = (self._rr_index + 1) % len(active)
            return inst


class PublicCloudAutoscaler:
    """
    Controls dynamic horizontal elasticity for the Public Cloud tier.
    Monitors aggregate public utilization and triggers SCALE_OUT / SCALE_IN events
    governed by sustained interval thresholds, hysteresis cooldowns, and provisioning delays.
    """

    def __init__(
        self,
        env: simpy.Environment,
        config: Dict[str, Any],
        load_balancer: PublicLoadBalancer,
        metrics: SimulationMetrics,
        cores_per_instance: int = 4
    ):
        self.env = env
        self.config = config
        self.load_balancer = load_balancer
        self.metrics = metrics
        self.cores_per_instance = cores_per_instance

        hybrid_cfg = config.get("hybrid_cloud", {})
        public_cfg = hybrid_cfg.get("public_tier", {})
        auto_cfg = hybrid_cfg.get("autoscaling", {})

        self.enabled = auto_cfg.get("enabled", False)
        if self.enabled:
            self.min_instances = auto_cfg.get("min_instances", 2)
            self.max_instances = auto_cfg.get("max_instances", 20)
        else:
            self.min_instances = public_cfg.get("initial_instances", 2)
            self.max_instances = self.min_instances

        self.scale_out_threshold = auto_cfg.get("scale_out_threshold", 0.70)
        self.scale_in_threshold = auto_cfg.get("scale_in_threshold", 0.35)
        self.monitoring_interval = auto_cfg.get("monitoring_interval_seconds", 1.0)
        self.scale_out_consecutive = auto_cfg.get("scale_out_consecutive_intervals", 2)
        self.scale_in_consecutive = auto_cfg.get("scale_in_consecutive_intervals", 3)
        self.cooldown_period = auto_cfg.get("cooldown_seconds", 5.0)
        self.provisioning_delay = auto_cfg.get("provisioning_delay_seconds", 2.0)
        self.scale_out_step = auto_cfg.get("scale_out_step", 2)
        self.scale_in_step = auto_cfg.get("scale_in_step", 1)

        self.consecutive_high_intervals = 0
        self.consecutive_low_intervals = 0
        self.last_scaling_time = -999.0
        self.event_counter = 0
        self.instance_counter = 0
        self.is_active = True

        # Initialize baseline minimum instances
        for _ in range(self.min_instances):
            self.instance_counter += 1
            inst = PublicCloudInstance(
                env=self.env,
                instance_id=f"pub-inst-{self.instance_counter:02d}",
                cores=self.cores_per_instance
            )
            inst.state = "ACTIVE"
            inst.activated_at = self.env.now
            self.load_balancer.add_instance(inst)

        if self.enabled:
            self.env.process(self._monitoring_loop())

    def stop(self):
        self.is_active = False

    def _monitoring_loop(self):
        while self.is_active:
            yield self.env.timeout(self.monitoring_interval)
            if not self.is_active:
                break

            active_instances = self.load_balancer.get_active_instances()
            if not active_instances:
                continue

            total_active_cores = sum(inst.active_cores for inst in active_instances)
            total_capacity_cores = len(active_instances) * self.cores_per_instance
            current_util = (total_active_cores / total_capacity_cores) if total_capacity_cores > 0 else 0.0

            # Scale-out evaluation
            if current_util >= self.scale_out_threshold:
                self.consecutive_high_intervals += 1
                self.consecutive_low_intervals = 0
                now = self.env.now

                # Count all instances that are currently ACTIVE or already PROVISIONING
                non_removed = [inst for inst in self.load_balancer.instances if inst.state in ("ACTIVE", "PROVISIONING")]
                can_scale_out = (
                    self.consecutive_high_intervals >= self.scale_out_consecutive
                    and (now - self.last_scaling_time) >= self.cooldown_period
                    and len(non_removed) < self.max_instances
                )

                if can_scale_out:
                    instances_to_add = min(self.scale_out_step, self.max_instances - len(non_removed))
                    if instances_to_add > 0:
                        old_count = len(active_instances)
                        new_count = old_count + instances_to_add
                        self.event_counter += 1
                        event_id = f"SCALE_EVT_{self.event_counter:03d}"
                        self.last_scaling_time = now
                        self.consecutive_high_intervals = 0

                        total_q = sum(inst.queue_length for inst in active_instances)
                        self.metrics.record_scaling_event(
                            event_id=event_id,
                            timestamp=now,
                            event_type="SCALE_OUT",
                            old_count=old_count,
                            new_count=new_count,
                            trigger="sustained_high_utilization",
                            utilization_pct=current_util * 100.0,
                            queue_length=total_q,
                            reason=f"Public utilization reached {current_util*100.0:.1f}% >= threshold {self.scale_out_threshold*100.0:.1f}% for {self.scale_out_consecutive} intervals",
                            provisioning_delay_sec=self.provisioning_delay
                        )

                        for _ in range(instances_to_add):
                            self.instance_counter += 1
                            new_inst = PublicCloudInstance(
                                env=self.env,
                                instance_id=f"pub-inst-{self.instance_counter:02d}",
                                cores=self.cores_per_instance
                            )
                            self.load_balancer.add_instance(new_inst)
                            self.env.process(self._provision_instance(new_inst))

            # Scale-in evaluation
            elif current_util <= self.scale_in_threshold:
                self.consecutive_low_intervals += 1
                self.consecutive_high_intervals = 0
                now = self.env.now

                active_only = [inst for inst in self.load_balancer.instances if inst.state == "ACTIVE"]
                can_scale_in = (
                    self.consecutive_low_intervals >= self.scale_in_consecutive
                    and (now - self.last_scaling_time) >= self.cooldown_period
                    and len(active_only) > self.min_instances
                )

                if can_scale_in:
                    instances_to_remove = min(self.scale_in_step, len(active_only) - self.min_instances)
                    if instances_to_remove > 0:
                        old_count = len(active_only)
                        new_count = old_count - instances_to_remove
                        self.event_counter += 1
                        event_id = f"SCALE_EVT_{self.event_counter:03d}"
                        self.last_scaling_time = now
                        self.consecutive_low_intervals = 0

                        total_q = sum(inst.queue_length for inst in active_only)
                        self.metrics.record_scaling_event(
                            event_id=event_id,
                            timestamp=now,
                            event_type="SCALE_IN",
                            old_count=old_count,
                            new_count=new_count,
                            trigger="sustained_low_utilization",
                            utilization_pct=current_util * 100.0,
                            queue_length=total_q,
                            reason=f"Public utilization dropped to {current_util*100.0:.1f}% <= threshold {self.scale_in_threshold*100.0:.1f}% for {self.scale_in_consecutive} intervals",
                            provisioning_delay_sec=0.0
                        )

                        # Gracefully drain newest active instances
                        for inst in reversed(active_only):
                            if instances_to_remove <= 0:
                                break
                            inst.state = "DRAINING"
                            instances_to_remove -= 1
                            self.env.process(self._drain_instance(inst))
            else:
                self.consecutive_high_intervals = 0
                self.consecutive_low_intervals = 0

    def _provision_instance(self, instance: PublicCloudInstance):
        yield self.env.timeout(self.provisioning_delay)
        instance.state = "ACTIVE"
        instance.activated_at = self.env.now

    def _drain_instance(self, instance: PublicCloudInstance):
        while instance.active_requests > 0 or instance.queue_length > 0:
            yield self.env.timeout(0.05)
        instance.state = "REMOVED"
        instance.terminated_at = self.env.now


class HybridCloudEnvironment:
    """
    Simulates a dual-tier hybrid cloud architecture:
    - Private Cloud Tier: Protected zone, multi-core cluster + dedicated core banking DB.
    - Public Cloud Tier: Elastic zone managed by a Load Balancer and optional Autoscaler.
    - Security Gateway & Request Router: Enforces deterministic data-classification routing.
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

        hybrid_cfg = config.get("hybrid_cloud", {})
        private_cfg = hybrid_cfg.get("private_tier", {})
        public_cfg = hybrid_cfg.get("public_tier", {})
        auto_cfg = hybrid_cfg.get("autoscaling", {})
        gateway_cfg = hybrid_cfg.get("gateway", {})
        routing_cfg = hybrid_cfg.get("routing", {})

        # Gateway parameters
        self.gateway_latency_sec = gateway_cfg.get("latency_ms", 1.5) / 1000.0

        # Routing rules
        self.classification_mapping = routing_cfg.get("classification_mapping", {
            "RESTRICTED": "PRIVATE",
            "CONFIDENTIAL": "PRIVATE",
            "INTERNAL": "PUBLIC",
            "PUBLIC": "PUBLIC"
        })
        self.service_fallback = routing_cfg.get("service_type_fallback", {})

        # Private Cloud Tier (Protected Zone)
        self.private_servers = private_cfg.get("server_count", 6)
        self.private_cores_per_server = private_cfg.get("cores_per_server", 8)
        self.total_private_cores = self.private_servers * self.private_cores_per_server  # 48 cores
        self.private_base_cpu_sec = private_cfg.get("base_processing_latency_ms", 10.0) / 1000.0
        self.private_net_sec = private_cfg.get("network_latency_ms", 3.0) / 1000.0
        self.private_queue_depth = private_cfg.get("max_queue_depth", 6000)

        # Private Database
        db_cfg = private_cfg.get("database", {})
        self.private_db_capacity = db_cfg.get("connection_pool_capacity", 64)
        self.private_db_latency_sec = db_cfg.get("base_query_latency_ms", 10.0) / 1000.0
        self.private_db_services = set(db_cfg.get("db_required_services", [
            "account_balance_inquiry",
            "fund_transfer",
            "kyc_verification",
            "loan_application",
            "credit_risk_evaluation",
            "transaction_history"
        ]))

        # Public Cloud Tier Setup
        if auto_cfg.get("enabled", False):
            self.public_cores_per_instance = auto_cfg.get("cores_per_instance", 4)
            self.initial_public_instances = auto_cfg.get("min_instances", 2)
            self.public_queue_depth = 10000
        else:
            self.public_cores_per_instance = public_cfg.get("cores_per_instance", 4)
            self.initial_public_instances = public_cfg.get("initial_instances", 2)
            self.public_queue_depth = self.initial_public_instances * public_cfg.get("max_queue_depth_per_instance", 1000)

        self.total_public_cores = self.initial_public_instances * self.public_cores_per_instance
        self.public_base_cpu_sec = public_cfg.get("base_processing_latency_ms", 12.0) / 1000.0
        self.public_net_sec = public_cfg.get("network_latency_ms", 18.0) / 1000.0  # WAN latency

        # Shared Private Resources
        self.private_server_pool = simpy.Resource(self.env, capacity=self.total_private_cores)
        self.private_db_pool = simpy.Resource(self.env, capacity=self.private_db_capacity)

        # Load Balancer & Autoscaler
        lb_strategy = auto_cfg.get("load_balancing_strategy", "round_robin")
        self.load_balancer = PublicLoadBalancer(self.env, strategy=lb_strategy)
        self.autoscaler = PublicCloudAutoscaler(
            env=self.env,
            config=self.config,
            load_balancer=self.load_balancer,
            metrics=self.metrics,
            cores_per_instance=self.public_cores_per_instance
        )

        # Queue tracking
        self.current_private_queue_length = 0
        self.current_public_queue_length = 0
        self.is_active = True

        # Periodic telemetry sampler
        sampling_interval = config.get("simulation", {}).get("metrics_sampling_interval_sec", 1.0)
        self.env.process(self._periodic_metrics_sampler(sampling_interval))

    @property
    def public_active_cores(self) -> int:
        return sum(inst.active_cores for inst in self.load_balancer.instances if inst.state in ("ACTIVE", "DRAINING"))

    @property
    def public_server_pool(self):
        """Compatibility property allowing .count access matching Stage 4 expectations."""
        class _PoolCompat:
            def __init__(self, parent):
                self.parent = parent
            @property
            def count(self):
                return self.parent.public_active_cores
        return _PoolCompat(self)

    def stop(self):
        """Signals background processes to cease execution."""
        self.is_active = False
        self.autoscaler.stop()

    def route_request(self, event: Dict[str, Any]) -> Tuple[str, str]:
        """
        Deterministic compliance routing decision based on explicit precedence:
        1. Classification tier takes precedence (RESTRICTED/CONFIDENTIAL -> PRIVATE, PUBLIC/INTERNAL -> PUBLIC)
        2. Fallback to service type mapping if classification tier is missing or undefined
        """
        tier = event.get("classification_tier")
        svc = event.get("request_type")

        if tier in self.classification_mapping:
            return self.classification_mapping[tier], "classification_policy"

        if svc in self.service_fallback:
            return self.service_fallback[svc], "service_policy"

        # Safe default: route to protected private tier
        return "PRIVATE", "default_safe_fallback"

    def _get_request_rng(self, request_id: str) -> random.Random:
        hash_val = int(hashlib.sha256(f"{request_id}_{self.seed}".encode()).hexdigest()[:8], 16)
        return random.Random(hash_val)

    def handle_request(self, request_event: Dict[str, Any]):
        """SimPy process orchestrating gateway routing, load balancing, and tier execution."""
        req_id = request_event["event_id"]
        arrival_time = self.env.now
        svc_type = request_event.get("request_type", "unknown")
        class_tier = request_event.get("classification_tier", "INTERNAL")
        payload_bytes = request_event.get("payload_size_bytes", 1024)

        # 1. Security Gateway Ingress Hop
        yield self.env.timeout(self.gateway_latency_sec)

        # 2. Routing Decision
        target_tier, routing_reason = self.route_request(request_event)
        rng = self._get_request_rng(req_id)

        # =============================================================
        # PRIVATE CLOUD TIER EXECUTION
        # =============================================================
        if target_tier == "PRIVATE":
            # Queue admission check
            if self.current_private_queue_length >= self.private_queue_depth:
                self.metrics.record_dropped(
                    request_id=req_id,
                    arrival_time=arrival_time,
                    drop_time=self.env.now,
                    reason="QUEUE_OVERFLOW_PRIVATE",
                    service_type=svc_type,
                    classification_tier=class_tier,
                    target_tier="PRIVATE",
                    routing_reason=routing_reason
                )
                return

            self.current_private_queue_length += 1

            # Inbound network hop to Private Cloud
            yield self.env.timeout(self.private_net_sec / 2.0)

            db_accessed = False
            db_time_ms = 0.0

            with self.private_server_pool.request() as server_req:
                yield server_req
                self.current_private_queue_length = max(0, self.current_private_queue_length - 1)
                start_service_time = self.env.now

                # Compute service time
                payload_factor = (payload_bytes / 1024.0) * 0.001
                mean_cpu = self.private_base_cpu_sec + payload_factor
                cpu_time = max(0.002, rng.gauss(mean_cpu, mean_cpu * 0.20))
                yield self.env.timeout(cpu_time)

                # Core Database Contention (if service accesses DB)
                if svc_type in self.private_db_services:
                    db_accessed = True
                    with self.private_db_pool.request() as db_req:
                        yield db_req
                        db_query_time = max(0.003, rng.gauss(self.private_db_latency_sec, self.private_db_latency_sec * 0.25))
                        yield self.env.timeout(db_query_time)
                        db_time_ms = db_query_time * 1000.0

            # Outbound network hop
            yield self.env.timeout(self.private_net_sec / 2.0)

            self.metrics.record_completed(
                request_id=req_id,
                arrival_time=arrival_time,
                start_service_time=start_service_time,
                completion_time=self.env.now,
                service_type=svc_type,
                classification_tier=class_tier,
                db_accessed=db_accessed,
                db_time_ms=db_time_ms,
                target_tier="PRIVATE",
                routing_reason=routing_reason
            )

        # =============================================================
        # PUBLIC CLOUD TIER EXECUTION (LOAD BALANCED)
        # =============================================================
        else:
            # Queue admission check across public instances
            if self.current_public_queue_length >= self.public_queue_depth:
                self.metrics.record_dropped(
                    request_id=req_id,
                    arrival_time=arrival_time,
                    drop_time=self.env.now,
                    reason="QUEUE_OVERFLOW_PUBLIC",
                    service_type=svc_type,
                    classification_tier=class_tier,
                    target_tier="PUBLIC",
                    routing_reason=routing_reason
                )
                return

            self.current_public_queue_length += 1

            # Inbound network hop to Public Cloud (WAN latency)
            yield self.env.timeout(self.public_net_sec / 2.0)

            # Load Balancer selects next ACTIVE instance
            instance = self.load_balancer.select_instance()
            if instance is None:
                # If no instance is active (transient), wait briefly for activation
                while instance is None:
                    yield self.env.timeout(0.01)
                    instance = self.load_balancer.select_instance()

            instance.active_requests += 1

            with instance.server_pool.request() as server_req:
                yield server_req
                self.current_public_queue_length = max(0, self.current_public_queue_length - 1)
                start_service_time = self.env.now

                # Public compute execution
                payload_factor = (payload_bytes / 1024.0) * 0.001
                mean_cpu = self.public_base_cpu_sec + payload_factor
                cpu_time = max(0.002, rng.gauss(mean_cpu, mean_cpu * 0.20))
                yield self.env.timeout(cpu_time)

            instance.active_requests = max(0, instance.active_requests - 1)

            # Outbound network hop
            yield self.env.timeout(self.public_net_sec / 2.0)

            self.metrics.record_completed(
                request_id=req_id,
                arrival_time=arrival_time,
                start_service_time=start_service_time,
                completion_time=self.env.now,
                service_type=svc_type,
                classification_tier=class_tier,
                db_accessed=False,
                db_time_ms=0.0,
                target_tier="PUBLIC",
                routing_reason=routing_reason
            )

    def _periodic_metrics_sampler(self, interval_sec: float):
        """Samples private, public, and total queue and compute resource utilizations."""
        while self.is_active:
            priv_active = self.private_server_pool.count
            pub_active = self.public_active_cores
            total_active = priv_active + pub_active
            priv_q = self.current_private_queue_length
            pub_q = self.current_public_queue_length
            total_q = priv_q + pub_q

            active_instances = len(self.load_balancer.get_active_instances())
            prov_instances = sum(1 for inst in self.load_balancer.instances if inst.state == "PROVISIONING")
            drain_instances = sum(1 for inst in self.load_balancer.instances if inst.state == "DRAINING")

            total_cores = self.total_private_cores + (active_instances * self.public_cores_per_instance)

            self.metrics.record_time_series_sample(
                timestamp=self.env.now,
                queue_len=total_q,
                active_cores=total_active,
                total_cores=total_cores,
                active_db=self.private_db_pool.count,
                total_db=self.private_db_capacity,
                private_queue_len=priv_q,
                public_queue_len=pub_q,
                private_active_cores=priv_active,
                public_active_cores=pub_active,
                public_instances=active_instances,
                public_provisioning_instances=prov_instances,
                public_draining_instances=drain_instances
            )
            yield self.env.timeout(interval_sec)
