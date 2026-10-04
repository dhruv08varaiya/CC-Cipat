"""
validator.py
Validates synthetic banking datasets for referential integrity, schema constraints,
missing values, duplicates, and generates statistical summary reports.
"""

from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Tuple
import numpy as np


class DatasetValidator:
    """Rigorous integrity validator and summary reporter for synthetic banking data."""

    VALID_CLASSIFICATIONS = {"RESTRICTED", "CONFIDENTIAL", "INTERNAL", "PUBLIC"}

    def __init__(self):
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []

    def validate_all(
        self,
        datasets: Dict[str, List[Dict]],
        workloads: Dict[str, List[Dict]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Runs complete validation pipeline across all 8 datasets and workload traces.
        Returns (is_valid, statistics_report).
        """
        self.validation_errors = []
        self.validation_warnings = []

        customers = datasets.get("customers", [])
        accounts = datasets.get("accounts", [])
        transactions = datasets.get("transactions", [])
        logins = datasets.get("login_events", [])
        payments = datasets.get("payment_requests", [])
        risks = datasets.get("risk_requests", [])
        notifs = datasets.get("notifications", [])
        audits = datasets.get("audit_logs", [])

        # 1. Primary Key Uniqueness & Missing Values
        cust_ids = self._check_pk_and_nulls(customers, "customer_id", "customers")
        acc_ids = self._check_pk_and_nulls(accounts, "account_id", "accounts")
        self._check_pk_and_nulls(transactions, "tx_id", "transactions")
        self._check_pk_and_nulls(logins, "event_id", "login_events")
        self._check_pk_and_nulls(payments, "payment_id", "payment_requests")
        self._check_pk_and_nulls(risks, "request_id", "risk_requests")
        self._check_pk_and_nulls(notifs, "notification_id", "notifications")
        self._check_pk_and_nulls(audits, "log_id", "audit_logs")

        # 2. Referential Integrity
        # Every account must point to a valid customer
        for acc in accounts:
            if acc["customer_id"] not in cust_ids:
                self.validation_errors.append(f"Account {acc['account_id']} references unknown customer {acc['customer_id']}")

        # Customer to accounts map for payment verification
        cust_acc_map = {}
        for acc in accounts:
            cust_acc_map.setdefault(acc["customer_id"], set()).add(acc["account_id"])

        # Every transaction source and target must exist in accounts
        for tx in transactions:
            if tx["source_account_id"] not in acc_ids:
                self.validation_errors.append(f"Transaction {tx['tx_id']} has unknown source account {tx['source_account_id']}")
            if tx["target_account_id"] not in acc_ids:
                self.validation_errors.append(f"Transaction {tx['tx_id']} has unknown target account {tx['target_account_id']}")

        # Payment requests: customer must exist and account must belong to customer
        for pay in payments:
            cid = pay["customer_id"]
            aid = pay["account_id"]
            if cid not in cust_ids:
                self.validation_errors.append(f"Payment {pay['payment_id']} references unknown customer {cid}")
            elif aid not in cust_acc_map.get(cid, set()):
                self.validation_errors.append(f"Payment {pay['payment_id']} references account {aid} not owned by {cid}")

        # Login, Risk, Notification customer checks
        for log in logins:
            if log["customer_id"] not in cust_ids:
                self.validation_errors.append(f"Login {log['event_id']} references unknown customer {log['customer_id']}")

        for rsk in risks:
            if rsk["customer_id"] not in cust_ids:
                self.validation_errors.append(f"Risk {rsk['request_id']} references unknown customer {rsk['customer_id']}")

        for notif in notifs:
            if notif["customer_id"] not in cust_ids:
                self.validation_errors.append(f"Notification {notif['notification_id']} references unknown customer {notif['customer_id']}")

        # 3. Value Constraints & Numeric Ranges
        for cust in customers:
            if not (18 <= cust["age"] <= 120):
                self.validation_errors.append(f"Customer {cust['customer_id']} invalid age: {cust['age']}")
            if not (0.0 <= cust["customer_risk_score"] <= 1.0):
                self.validation_errors.append(f"Customer {cust['customer_id']} invalid risk score: {cust['customer_risk_score']}")
            if cust["classification_tier"] not in self.VALID_CLASSIFICATIONS:
                self.validation_errors.append(f"Customer {cust['customer_id']} invalid classification: {cust['classification_tier']}")

        for acc in accounts:
            if acc["balance"] < 0:
                self.validation_errors.append(f"Account {acc['account_id']} negative balance: {acc['balance']}")
            if acc["classification_tier"] not in self.VALID_CLASSIFICATIONS:
                self.validation_errors.append(f"Account {acc['account_id']} invalid classification")

        for tx in transactions:
            if tx["amount"] <= 0:
                self.validation_errors.append(f"Transaction {tx['tx_id']} non-positive amount: {tx['amount']}")
            if tx["classification_tier"] not in self.VALID_CLASSIFICATIONS:
                self.validation_errors.append(f"Transaction {tx['tx_id']} invalid classification")

        # 4. Workload Events Validation
        workload_stats = {}
        for wid, evts in workloads.items():
            workload_stats[wid] = len(evts)
            evt_ids = set()
            for evt in evts:
                if evt["event_id"] in evt_ids:
                    self.validation_errors.append(f"Duplicate workload event ID {evt['event_id']} in {wid}")
                evt_ids.add(evt["event_id"])
                if evt["classification_tier"] not in self.VALID_CLASSIFICATIONS:
                    self.validation_errors.append(f"Workload {wid} event {evt['event_id']} invalid tier")

        is_valid = len(self.validation_errors) == 0

        # 5. Compile Comprehensive Statistics
        stats = self._compile_statistics(datasets, workload_stats)
        return is_valid, stats

    def _check_pk_and_nulls(self, records: List[Dict], pk_field: str, table_name: str) -> set:
        seen = set()
        for idx, r in enumerate(records):
            pk_val = r.get(pk_field)
            if not pk_val:
                self.validation_errors.append(f"{table_name} record index {idx} has missing {pk_field}")
                continue
            if pk_val in seen:
                self.validation_errors.append(f"Duplicate primary key {pk_val} in {table_name}")
            seen.add(pk_val)

            # Check for any null or empty string fields
            for k, v in r.items():
                if v is None or v == "":
                    self.validation_errors.append(f"{table_name} record {pk_val} has empty field '{k}'")
        return seen

    def _compile_statistics(self, datasets: Dict[str, List[Dict]], workload_stats: Dict[str, int]) -> Dict[str, Any]:
        customers = datasets.get("customers", [])
        accounts = datasets.get("accounts", [])
        transactions = datasets.get("transactions", [])

        balances = [a["balance"] for a in accounts] if accounts else [0.0]
        tx_amounts = [t["amount"] for t in transactions] if transactions else [0.0]
        risk_scores = [c["customer_risk_score"] for c in customers] if customers else [0.0]

        # Classification counts across core entities
        class_dist: Dict[str, int] = {}
        for ds_name, records in datasets.items():
            for r in records:
                tier = r.get("classification_tier")
                if tier:
                    class_dist[tier] = class_dist.get(tier, 0) + 1

        stats = {
            "validation_status": "PASSED" if len(self.validation_errors) == 0 else "FAILED",
            "error_count": len(self.validation_errors),
            "errors": self.validation_errors[:20],  # cap first 20 errors
            "row_counts": {name: len(records) for name, records in datasets.items()},
            "workload_event_counts": workload_stats,
            "financial_metrics": {
                "account_balance": {
                    "total": round(float(np.sum(balances)), 2),
                    "mean": round(float(np.mean(balances)), 2),
                    "median": round(float(np.median(balances)), 2),
                    "min": round(float(np.min(balances)), 2),
                    "max": round(float(np.max(balances)), 2),
                    "std": round(float(np.std(balances)), 2)
                },
                "transaction_amount": {
                    "total": round(float(np.sum(tx_amounts)), 2),
                    "mean": round(float(np.mean(tx_amounts)), 2),
                    "median": round(float(np.median(tx_amounts)), 2),
                    "min": round(float(np.min(tx_amounts)), 2),
                    "max": round(float(np.max(tx_amounts)), 2),
                    "std": round(float(np.std(tx_amounts)), 2)
                },
                "customer_risk_score": {
                    "mean": round(float(np.mean(risk_scores)), 3),
                    "median": round(float(np.median(risk_scores)), 3),
                    "min": round(float(np.min(risk_scores)), 3),
                    "max": round(float(np.max(risk_scores)), 3)
                }
            },
            "classification_distribution": class_dist
        }
        return stats

    def export_reports(self, stats: Dict[str, Any], output_dir: Path):
        """Saves reports in JSON and Markdown formats."""
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "dataset_statistics.json"
        md_path = output_dir / "dataset_statistics.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        # Markdown report
        lines = [
            "# Synthetic Banking Dataset & Workload Statistics Report",
            "",
            f"**Validation Status**: `{stats['validation_status']}` (Errors: {stats['error_count']})",
            "",
            "## 1. Dataset Row Counts",
            "| Dataset Name | Record Count | Primary Key | Description |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for ds, count in stats["row_counts"].items():
            lines.append(f"| `{ds}.csv` | {count:,} | Unique ID | Synthetic banking operational data |")

        lines.extend([
            "",
            "## 2. Workload Event Counts (JSONL)",
            "| Workload ID | Profile Name | Event Count | Description |",
            "| :--- | :--- | :--- | :--- |"
        ])
        workload_desc = {
            "W1": "Normal steady-state (600 RPS baseline)",
            "W2": "Peak business volume (1400 RPS)",
            "W3": "Extreme volume stress test (2600 RPS)",
            "W4": "Bursty spike traffic (2800 RPS)",
            "W5": "Node outage injected (50% dropped)",
            "W6": "Node outage with automated DR recovery"
        }
        for wid, count in stats["workload_event_counts"].items():
            lines.append(f"| `{wid}` | {workload_desc.get(wid, 'Custom')} | {count:,} | Trace stream |")

        lines.extend([
            "",
            "## 3. Financial & Risk Statistical Summary",
            f"- **Account Balances**: Mean = ${stats['financial_metrics']['account_balance']['mean']:,.2f}, Max = ${stats['financial_metrics']['account_balance']['max']:,.2f}, Total System Liquidity = ${stats['financial_metrics']['account_balance']['total']:,.2f}",
            f"- **Transaction Amounts**: Mean = ${stats['financial_metrics']['transaction_amount']['mean']:,.2f}, Median = ${stats['financial_metrics']['transaction_amount']['median']:,.2f}, Max = ${stats['financial_metrics']['transaction_amount']['max']:,.2f}",
            f"- **Customer Risk Score**: Mean = {stats['financial_metrics']['customer_risk_score']['mean']:.3f}, Min = {stats['financial_metrics']['customer_risk_score']['min']:.3f}, Max = {stats['financial_metrics']['customer_risk_score']['max']:.3f}",
            "",
            "## 4. Security Classification Distribution",
            "| Classification Tier | Total Records | Routing Policy |",
            "| :--- | :--- | :--- |"
        ])
        for tier, count in stats["classification_distribution"].items():
            lines.append(f"| `{tier}` | {count:,} | Governed by security_rules.json |")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
