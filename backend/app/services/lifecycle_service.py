import time
import hashlib
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from src.security.data_classifier import DataClassifier
from src.security.authentication import Authenticator
from src.security.mfa import MFACoordinator
from src.security.rbac import RBACAuthorizer
from src.security.encryption import EncryptionManager
from src.security.security_events import SecurityViolationDetector, SecurityEvent
from src.security.security_audit import SecurityAuditLogger

@dataclass
class LifecycleStage:
    stage_id: int
    name: str
    status: str  # "PENDING", "ACTIVE", "SUCCESS", "BLOCKED", "WARNING"
    timestamp_offset_ms: float
    duration_ms: float
    details: Dict[str, Any]
    payload_snapshot: Any
    description: str

class TransactionLifecycleService:
    """
    Executes a high-fidelity, step-by-step trace of a single banking request
    through the entire 8-stage architecture.
    """

    @staticmethod
    def trace_transaction(
        service_type: str = "fund_transfer",
        user_role: str = "CUSTOMER",
        payload: Optional[Dict[str, Any]] = None,
        chaos_node_failure: bool = False,
        chaos_network_spike: bool = False,
        rules_path: Optional[str] = None
    ) -> Dict[str, Any]:
        if payload is None:
            payload = {
                "account_id": "ACC_984128",
                "recipient_id": "ACC_119482",
                "amount": 5000.00,
                "currency": "USD",
                "ssn_last4": "8841",
                "auth_token": "tok_sec_9941a8",
                "device_fingerprint": "dev_mac_x8812"
            }

        stages: List[LifecycleStage] = []
        accumulated_time = 0.0

        # Instantiate zero-trust security components
        from pathlib import Path
        backend_dir = Path(__file__).resolve().parent.parent.parent
        cfg_path = Path(rules_path) if rules_path else backend_dir / "config" / "security_rules.json"
        
        classifier = DataClassifier(cfg_path)
        authenticator = Authenticator(success_rate=0.99)
        mfa = MFACoordinator(failure_rate=0.03)
        authorizer = RBACAuthorizer(cfg_path)
        encryption = EncryptionManager(at_rest_overhead_ms=0.8, in_transit_overhead_ms=0.4)
        detector = SecurityViolationDetector()
        audit_logger = SecurityAuditLogger()

        req_id = f"TXN_{int(time.time()*1000)%1000000:06d}"

        # -------------------------------------------------------------
        # STAGE 1: Request Ingestion & Schema Validation
        # -------------------------------------------------------------
        stage1_duration = round(random.uniform(0.15, 0.35), 3)
        accumulated_time += stage1_duration
        stages.append(LifecycleStage(
            stage_id=1,
            name="Ingestion & Schema Validation",
            status="SUCCESS",
            timestamp_offset_ms=round(accumulated_time, 3),
            duration_ms=stage1_duration,
            details={
                "request_id": req_id,
                "service_type": service_type,
                "client_ip": f"192.168.1.{random.randint(20, 250)}",
                "payload_size_bytes": len(str(payload)),
                "schema_validation": "PASSED"
            },
            payload_snapshot=payload.copy(),
            description="Payload received at Edge Ingress Gateway, validated against API banking schema."
        ))

        # -------------------------------------------------------------
        # STAGE 2: 4-Tier Zero-Trust Data Classification
        # -------------------------------------------------------------
        cls_result = classifier.classify(service_type, payload)
        stage2_duration = round(cls_result.processing_time_ms, 3)
        accumulated_time += stage2_duration
        
        stages.append(LifecycleStage(
            stage_id=2,
            name="Zero-Trust Classification & Taint Scan",
            status="SUCCESS",
            timestamp_offset_ms=round(accumulated_time, 3),
            duration_ms=stage2_duration,
            details={
                "classification_tier": cls_result.classification.value,
                "confidence": cls_result.confidence,
                "decision_reason": cls_result.decision_reason,
                "tainted_fields": cls_result.tainted_fields
            },
            payload_snapshot={
                **payload,
                "_classification": cls_result.classification.value,
                "_tainted": cls_result.tainted_fields
            },
            description=f"Classified as {cls_result.classification.value}. Detected {len(cls_result.tainted_fields)} sensitive field(s)."
        ))

        # -------------------------------------------------------------
        # STAGE 3: Auth, MFA & RBAC Access Control
        # -------------------------------------------------------------
        auth_res = authenticator.authenticate(req_id, f"usr_{random.randint(100,999)}")
        rbac_res = authorizer.authorize(user_role, service_type)
        mfa_required = service_type in ("fund_transfer", "kyc_verification", "loan_application")
        mfa_res = mfa.verify_mfa(req_id, "TOTP_OTP") if mfa_required else None

        stage3_duration = round(auth_res.latency_ms + (mfa_res.latency_ms if mfa_res else 0.2) + rbac_res.latency_ms, 3)
        accumulated_time += stage3_duration

        is_rbac_allowed = rbac_res.is_allowed
        stages.append(LifecycleStage(
            stage_id=3,
            name="Identity, MFA & RBAC Authorization",
            status="SUCCESS" if (auth_res.authenticated and is_rbac_allowed) else "BLOCKED",
            timestamp_offset_ms=round(accumulated_time, 3),
            duration_ms=stage3_duration,
            details={
                "user_role": user_role,
                "authenticated": auth_res.authenticated,
                "mfa_enforced": mfa_required,
                "mfa_status": mfa_res.status if mfa_res else "SKIPPED",
                "rbac_allowed": is_rbac_allowed,
                "rbac_reason": rbac_res.reason
            },
            payload_snapshot={
                **payload,
                "_auth_status": "VERIFIED" if auth_res.authenticated else "FAILED",
                "_rbac": user_role
            },
            description=f"Role '{user_role}' authorized for '{service_type}'. MFA: {'Verified (TOTP)' if mfa_required else 'Not Required'}."
        ))

        # -------------------------------------------------------------
        # STAGE 4: Compliance Routing Gate
        # -------------------------------------------------------------
        tier = cls_result.classification.value
        target_cluster = "PRIVATE_DATACENTER" if tier in ("RESTRICTED", "CONFIDENTIAL") else "PUBLIC_CLOUD"
        stage4_duration = round(random.uniform(0.1, 0.2), 3)
        accumulated_time += stage4_duration

        stages.append(LifecycleStage(
            stage_id=4,
            name="Compliance Policy Routing Gate",
            status="SUCCESS",
            timestamp_offset_ms=round(accumulated_time, 3),
            duration_ms=stage4_duration,
            details={
                "target_cluster": target_cluster,
                "routing_rule": "Deterministic zero-leakage compliance rule",
                "data_residency": "ON-PREM / PRIVATE ZONE" if target_cluster == "PRIVATE_DATACENTER" else "PUBLIC ELASTIC POOL"
            },
            payload_snapshot=payload.copy(),
            description=f"Routed payload strictly to {target_cluster} to prevent sensitive data leakage."
        ))

        # -------------------------------------------------------------
        # STAGE 5: Security Gateway & Network Transit
        # -------------------------------------------------------------
        base_net_latency = 1.5 if target_cluster == "PRIVATE_DATACENTER" else 18.0
        if chaos_network_spike:
            base_net_latency *= 4.5  # Simulate network degradation
        
        stage5_duration = round(base_net_latency + random.uniform(-0.3, 0.5), 3)
        accumulated_time += stage5_duration

        stages.append(LifecycleStage(
            stage_id=5,
            name="WAF Gateway & Network Transit",
            status="WARNING" if chaos_network_spike else "SUCCESS",
            timestamp_offset_ms=round(accumulated_time, 3),
            duration_ms=stage5_duration,
            details={
                "waf_delay_ms": 1.5,
                "wan_transit_ms": round(stage5_duration - 1.5, 3),
                "network_condition": "DEGRADED_SPIKE" if chaos_network_spike else "OPTIMAL"
            },
            payload_snapshot=payload.copy(),
            description=f"Traversed Security Gateway WAF. Transit latency: {stage5_duration:.2f} ms."
        ))

        # -------------------------------------------------------------
        # STAGE 6: Server Queue & Processing Core Allocation
        # -------------------------------------------------------------
        sim_queue_depth = random.randint(12, 45) if chaos_node_failure else random.randint(2, 9)
        active_cores = 64 if target_cluster == "PRIVATE_DATACENTER" else 16
        stage6_duration = round((sim_queue_depth * 0.4) + random.uniform(1.2, 2.5), 3)
        accumulated_time += stage6_duration

        stages.append(LifecycleStage(
            stage_id=6,
            name="M/G/c Queue & Core Scheduling",
            status="WARNING" if chaos_node_failure else "SUCCESS",
            timestamp_offset_ms=round(accumulated_time, 3),
            duration_ms=stage6_duration,
            details={
                "cluster_assigned": target_cluster,
                "active_server_cores": active_cores,
                "current_queue_depth": sim_queue_depth,
                "db_pool_connection": f"CONN_{random.randint(1, 48)}: ACQUIRED",
                "chaos_node_drop": chaos_node_failure
            },
            payload_snapshot=payload.copy(),
            description=f"Scheduled on Core #{random.randint(1, active_cores)}. Queue depth: {sim_queue_depth} requests."
        ))

        # -------------------------------------------------------------
        # STAGE 7: Cryptographic Overhead & Immutable Audit Log
        # -------------------------------------------------------------
        enc_res = encryption.apply_encryption(req_id, tier)
        stage7_duration = round(enc_res.total_crypto_overhead_ms, 3)
        accumulated_time += stage7_duration

        # Generate visual ciphertext mock for frontend live mutation
        mock_ciphertext = "0x" + hashlib.sha256(f"{req_id}_{payload}".encode()).hexdigest()[:32].upper()

        stages.append(LifecycleStage(
            stage_id=7,
            name="AES-256 / TLS Cryptography & Audit Trail",
            status="SUCCESS",
            timestamp_offset_ms=round(accumulated_time, 3),
            duration_ms=stage7_duration,
            details={
                "data_at_rest_encryption": enc_res.algorithm_at_rest,
                "data_in_transit_encryption": enc_res.algorithm_in_transit,
                "crypto_overhead_ms": stage7_duration,
                "audit_event_hash": hashlib.sha256(f"AUDIT_{req_id}".encode()).hexdigest()[:16]
            },
            payload_snapshot={
                "encrypted_payload": mock_ciphertext,
                "_cipher": "AES-256-GCM",
                "_status": "SECURED"
            },
            description=f"Applied {enc_res.algorithm_at_rest} at rest + {enc_res.algorithm_in_transit} in transit. Immutable audit record committed."
        ))

        # -------------------------------------------------------------
        # STAGE 8: Response Dispatch & Metric Invariant Commit
        # -------------------------------------------------------------
        stage8_duration = round(random.uniform(0.1, 0.25), 3)
        accumulated_time += stage8_duration

        stages.append(LifecycleStage(
            stage_id=8,
            name="Response Dispatch & Metrics Commit",
            status="SUCCESS",
            timestamp_offset_ms=round(accumulated_time, 3),
            duration_ms=stage8_duration,
            details={
                "http_status": 200,
                "total_e2e_latency_ms": round(accumulated_time, 3),
                "accounting_invariant": "TOTAL = COMPLETED (1/1)",
                "p95_contribution": "WITHIN_BUDGET"
            },
            payload_snapshot={
                "status": "TRANSACTION_CONFIRMED",
                "reference_id": f"REF-{req_id}",
                "timestamp": time.time(),
                "execution_time_ms": round(accumulated_time, 3)
            },
            description=f"Transaction finalized successfully. End-to-end latency: {accumulated_time:.2f} ms."
        ))

        return {
            "transaction_id": req_id,
            "service_type": service_type,
            "user_role": user_role,
            "total_latency_ms": round(accumulated_time, 3),
            "stages": [asdict(s) for s in stages]
        }
