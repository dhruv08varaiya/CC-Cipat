"""
workload_generator.py
Generates deterministic, reproducible JSONL workload event traces (W1-W6)
for on-premise vs hybrid-cloud comparative simulations.
"""

import json
from pathlib import Path
import random
from typing import Dict, List, Optional


class WorkloadGenerator:
    """Generates Poisson and bursty request streams with deterministic random seeds."""

    SERVICES = [
        {"type": "account_balance_inquiry", "priority": 1, "tier": "CONFIDENTIAL", "size": 384},
        {"type": "fund_transfer", "priority": 1, "tier": "RESTRICTED", "size": 1024},
        {"type": "kyc_verification", "priority": 2, "tier": "RESTRICTED", "size": 4096},
        {"type": "loan_application", "priority": 2, "tier": "CONFIDENTIAL", "size": 2048},
        {"type": "credit_risk_evaluation", "priority": 2, "tier": "CONFIDENTIAL", "size": 1536},
        {"type": "transaction_history", "priority": 2, "tier": "CONFIDENTIAL", "size": 1280},
        {"type": "exchange_rate_lookup", "priority": 3, "tier": "PUBLIC", "size": 256},
        {"type": "branch_atm_locator", "priority": 3, "tier": "PUBLIC", "size": 320},
        {"type": "interest_rate_calculator", "priority": 3, "tier": "PUBLIC", "size": 512},
        {"type": "batch_analytics_report", "priority": 3, "tier": "INTERNAL", "size": 8192},
        {"type": "customer_support_faq", "priority": 3, "tier": "PUBLIC", "size": 450}
    ]

    SERVICE_WEIGHTS = [0.25, 0.20, 0.05, 0.03, 0.04, 0.15, 0.10, 0.06, 0.04, 0.02, 0.06]

    def __init__(self, seed: int = 42, config_dir: Optional[Path] = None):
        self.seed = seed
        self.rng = random.Random(seed)
        self.config_dir = config_dir or Path(__file__).resolve().parent.parent.parent / "config"
        self._load_security_mapping()

    def _load_security_mapping(self):
        sec_path = self.config_dir / "security_rules.json"
        if sec_path.exists():
            with open(sec_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                mapping = data.get("service_classification_mapping", {})
                for svc in self.SERVICES:
                    if svc["type"] in mapping:
                        svc["tier"] = mapping[svc["type"]]

    def generate_workload(
        self,
        workload_id: str,
        customer_ids: List[str],
        account_ids: List[str],
        max_events: int = 5000,
        duration_sec: float = 120.0
    ) -> List[Dict]:
        """
        Generates a sequence of request events for a given workload profile (W1-W6).
        Ensures burst, failure, and recovery events occur within the event window.
        """
        seed_offset = int(workload_id[1]) if len(workload_id) > 1 and workload_id[1].isdigit() else 1
        self.rng.seed(self.seed + seed_offset * 100)

        events = []
        current_time = 0.0
        event_num = 1

        # Profile parameters
        if workload_id == "W1":
            base_rate = 600.0
        elif workload_id == "W2":
            base_rate = 1400.0
        elif workload_id == "W3":
            base_rate = 2600.0
        elif workload_id == "W4":
            base_rate = 600.0
        elif workload_id == "W5":
            base_rate = 1200.0
        elif workload_id == "W6":
            base_rate = 1200.0
        else:
            base_rate = 800.0

        # Timeline estimation based on max_events and rate
        estimated_duration = max_events / base_rate
        actual_span = min(duration_sec, estimated_duration)

        # Proportional milestone windows guaranteeing presence of phase transitions
        burst_start = actual_span * 0.30
        burst_end = actual_span * 0.65
        failure_start = actual_span * 0.35
        recovery_start = actual_span * 0.65

        while current_time < duration_sec and event_num <= max_events:
            rate = base_rate
            failure_meta = None

            if workload_id == "W4":
                # Burst phase
                if burst_start <= current_time <= burst_end:
                    rate = 2800.0
            elif workload_id == "W5":
                # Permanent failure injection phase
                if current_time >= failure_start:
                    failure_meta = {
                        "failure_injected": True,
                        "failed_node_ratio": 0.50,
                        "recovery_active": False,
                        "failure_trigger_sec": round(failure_start, 3)
                    }
            elif workload_id == "W6":
                # Failure injection followed by recovery
                if failure_start <= current_time < recovery_start:
                    failure_meta = {
                        "failure_injected": True,
                        "failed_node_ratio": 0.50,
                        "recovery_active": False,
                        "failure_trigger_sec": round(failure_start, 3)
                    }
                elif current_time >= recovery_start:
                    failure_meta = {
                        "failure_injected": False,
                        "failed_node_ratio": 0.0,
                        "recovery_active": True,
                        "recovered_time_sec": round(recovery_start, 3)
                    }

            inter_arrival = self.rng.expovariate(rate)
            current_time += inter_arrival
            if current_time > duration_sec:
                break

            svc = self.rng.choices(self.SERVICES, weights=self.SERVICE_WEIGHTS, k=1)[0]
            cust_id = self.rng.choice(customer_ids) if customer_ids else f"CUST_{self.rng.randint(1, 1000):06d}"
            acc_id = self.rng.choice(account_ids) if account_ids else f"ACC_{self.rng.randint(1, 1000):06d}"

            size_variation = int(svc["size"] * self.rng.uniform(0.85, 1.15))

            event = {
                "event_id": f"{workload_id}_EVT_{event_num:07d}",
                "timestamp_sec": round(current_time, 4),
                "request_type": svc["type"],
                "customer_id": cust_id,
                "account_id": acc_id,
                "payload_size_bytes": size_variation,
                "priority": svc["priority"],
                "classification_tier": svc["tier"],
                "expected_service": svc["type"],
                "arrival_rate_rps": round(rate, 1),
                "failure_metadata": failure_meta
            }
            events.append(event)
            event_num += 1

        return events

    def save_workload(self, events: List[Dict], output_path: Path):
        """Saves events as JSON Lines (.jsonl)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for evt in events:
                f.write(json.dumps(evt) + "\n")
