"""
generate_data.py
Main orchestration script to generate synthetic banking datasets and workload traces (W1-W6),
validate referential integrity, and output comprehensive statistics reports.
"""

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Dict, List

# Local imports
from src.data_generator.customer_generator import CustomerGenerator
from src.data_generator.transaction_generator import TransactionGenerator
from src.data_generator.workload_generator import WorkloadGenerator
from src.data_generator.validator import DatasetValidator


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Synthetic Banking Data and Workload Traces.")
    parser.add_argument(
        "--profile",
        type=str,
        default="medium",
        choices=["small", "medium", "large"],
        help="Dataset volume profile (small: 1k cust / 10k tx, medium: 10k cust / 50k tx, large: 50k cust / 200k tx)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed (default: 42)")
    parser.add_argument("--customers", type=int, default=None, help="Override number of customers")
    parser.add_argument("--accounts", type=int, default=None, help="Override number of accounts")
    parser.add_argument("--transactions", type=int, default=None, help="Override number of transactions")
    parser.add_argument("--output-data-dir", type=str, default="data/synthetic", help="Output directory for CSV datasets")
    parser.add_argument("--output-workloads-dir", type=str, default="data/workloads", help="Output directory for workload JSONL files")
    parser.add_argument("--output-reports-dir", type=str, default="reports", help="Output directory for statistics reports")
    return parser.parse_args()


def load_dataset_config(config_path: Path) -> Dict:
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_csv(records: List[Dict], filepath: Path):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    args = parse_args()
    root_dir = Path(__file__).resolve().parent.parent.parent
    config_file = root_dir / "config" / "dataset_config.json"
    cfg = load_dataset_config(config_file)

    profiles = cfg.get("profiles", {})
    profile_cfg = profiles.get(args.profile, {
        "customers": 1000,
        "accounts": 1000,
        "transactions": 10000,
        "login_events": 3000,
        "payment_requests": 5000,
        "risk_requests": 1000,
        "notifications": 5000,
        "audit_logs": 6000
    })

    num_customers = args.customers or profile_cfg["customers"]
    num_accounts = args.accounts or profile_cfg["accounts"]
    num_transactions = args.transactions or profile_cfg["transactions"]
    
    # Scale supporting logs proportionally if overrides are supplied
    scale_factor = num_customers / profile_cfg.get("customers", 1000)
    num_logins = int(profile_cfg.get("login_events", 3000) * scale_factor)
    num_payments = int(profile_cfg.get("payment_requests", 5000) * scale_factor)
    num_risk = int(profile_cfg.get("risk_requests", 1000) * scale_factor)
    num_notifs = int(profile_cfg.get("notifications", 5000) * scale_factor)
    num_audits = int(profile_cfg.get("audit_logs", 6000) * scale_factor)

    seed = args.seed

    print("=" * 70)
    print("DIGITAL BANKING SYSTEM — SYNTHETIC DATASET & WORKLOAD GENERATION")
    print(f"Profile: {args.profile} | Random Seed: {seed}")
    print(f"Target Counts: Customers={num_customers:,}, Accounts={num_accounts:,}, Transactions={num_transactions:,}")
    print("=" * 70)

    # 1. Generate Customers & Accounts
    print("[1/4] Generating customers and accounts...")
    cust_gen = CustomerGenerator(seed=seed)
    customers, accounts = cust_gen.generate(num_customers, num_accounts)
    print(f"      -> Created {len(customers):,} customers, {len(accounts):,} accounts.")

    # 2. Generate Transactions and Operational Logs
    print("[2/4] Generating transactions and operational logs...")
    tx_gen = TransactionGenerator(seed=seed)
    operational_data = tx_gen.generate_all(
        customers=customers,
        accounts=accounts,
        num_transactions=num_transactions,
        num_logins=num_logins,
        num_payments=num_payments,
        num_risk=num_risk,
        num_notifications=num_notifs,
        num_audits=num_audits
    )

    all_datasets = {
        "customers": customers,
        "accounts": accounts,
        "transactions": operational_data["transactions"],
        "login_events": operational_data["login_events"],
        "payment_requests": operational_data["payment_requests"],
        "risk_requests": operational_data["risk_requests"],
        "notifications": operational_data["notifications"],
        "audit_logs": operational_data["audit_logs"]
    }

    # 3. Generate Workloads W1 to W6
    print("[3/4] Generating workload event streams (W1-W6)...")
    workload_gen = WorkloadGenerator(seed=seed, config_dir=root_dir / "config")
    cust_ids = [c["customer_id"] for c in customers]
    acc_ids = [a["account_id"] for a in accounts]

    workload_limits = cfg.get("workload_event_limits", {
        "W1": 5000, "W2": 10000, "W3": 15000, "W4": 12000, "W5": 8000, "W6": 10000
    })

    workloads = {}
    for wid in ["W1", "W2", "W3", "W4", "W5", "W6"]:
        evts = workload_gen.generate_workload(
            workload_id=wid,
            customer_ids=cust_ids,
            account_ids=acc_ids,
            max_events=workload_limits.get(wid, 5000)
        )
        workloads[wid] = evts
        print(f"      -> {wid}: Generated {len(evts):,} requests")

    # 4. Validate & Output
    print("[4/4] Validating referential integrity and saving files...")
    validator = DatasetValidator()
    is_valid, stats = validator.validate_all(all_datasets, workloads)

    if not is_valid:
        print(f"ERROR: Dataset validation failed with {stats['error_count']} errors!")
        for err in stats["errors"]:
            print(f"  - {err}")
        sys.exit(1)

    # Save CSV Datasets
    data_out_dir = root_dir / args.output_data_dir
    for name, records in all_datasets.items():
        save_csv(records, data_out_dir / f"{name}.csv")

    # Save Workload JSONL Files
    wl_out_dir = root_dir / args.output_workloads_dir
    wl_name_map = {
        "W1": "W1_normal",
        "W2": "W2_peak",
        "W3": "W3_extreme",
        "W4": "W4_burst",
        "W5": "W5_failure",
        "W6": "W6_recovery"
    }
    for wid, evts in workloads.items():
        workload_gen.save_workload(evts, wl_out_dir / f"{wl_name_map[wid]}.jsonl")
        # Also write short name alias e.g. W1.jsonl
        workload_gen.save_workload(evts, wl_out_dir / f"{wid}.jsonl")

    # Save Reports
    rep_out_dir = root_dir / args.output_reports_dir
    validator.export_reports(stats, rep_out_dir)

    print("\nGeneration & Validation Completed Successfully!")
    print(f"Datasets written to: {data_out_dir}")
    print(f"Workloads written to: {wl_out_dir}")
    print(f"Statistics report written to: {rep_out_dir / 'dataset_statistics.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
