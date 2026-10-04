"""
test_synthetic_data.py
Unit and regression tests for synthetic data generation, referential integrity,
and seed-based reproducibility.
"""

import copy
import hashlib
import json
from pathlib import Path
import unittest

from src.data_generator.customer_generator import CustomerGenerator
from src.data_generator.transaction_generator import TransactionGenerator
from src.data_generator.workload_generator import WorkloadGenerator
from src.data_generator.validator import DatasetValidator


class TestSyntheticData(unittest.TestCase):
    def setUp(self):
        self.seed = 42
        self.cust_gen = CustomerGenerator(seed=self.seed)
        self.tx_gen = TransactionGenerator(seed=self.seed)
        self.workload_gen = WorkloadGenerator(seed=self.seed)
        self.validator = DatasetValidator()

    def test_customer_account_integrity(self):
        customers, accounts = self.cust_gen.generate(num_customers=50, num_accounts=75)
        self.assertEqual(len(customers), 50)
        self.assertEqual(len(accounts), 75)

        cust_ids = {c["customer_id"] for c in customers}
        self.assertEqual(len(cust_ids), 50, "Customer IDs must be unique")

        # Referential integrity: each account must link to an existing customer
        for acc in accounts:
            self.assertIn(acc["customer_id"], cust_ids)
            self.assertGreaterEqual(acc["balance"], 0.0)

    def test_reproducibility_identical_runs(self):
        """Verify that running generation with seed=42 yields bit-for-bit identical outputs."""
        gen1 = CustomerGenerator(seed=42)
        c1, a1 = gen1.generate(num_customers=100, num_accounts=120)

        gen2 = CustomerGenerator(seed=42)
        c2, a2 = gen2.generate(num_customers=100, num_accounts=120)

        self.assertEqual(c1, c2, "Customer outputs must be identical for identical seeds")
        self.assertEqual(a1, a2, "Account outputs must be identical for identical seeds")

        # Now test with differing seeds
        gen3 = CustomerGenerator(seed=99)
        c3, a3 = gen3.generate(num_customers=100, num_accounts=120)
        self.assertNotEqual(c1, c3, "Differing seeds must produce distinct outputs")

    def test_transaction_foreign_keys(self):
        customers, accounts = self.cust_gen.generate(num_customers=50, num_accounts=60)
        operational = self.tx_gen.generate_all(
            customers=customers,
            accounts=accounts,
            num_transactions=100,
            num_logins=40,
            num_payments=50,
            num_risk=20,
            num_notifications=50,
            num_audits=50
        )

        acc_ids = {a["account_id"] for a in accounts}
        cust_ids = {c["customer_id"] for c in customers}
        cust_acc_map = {}
        for a in accounts:
            cust_acc_map.setdefault(a["customer_id"], set()).add(a["account_id"])

        for tx in operational["transactions"]:
            self.assertIn(tx["source_account_id"], acc_ids)
            self.assertIn(tx["target_account_id"], acc_ids)
            self.assertNotEqual(tx["source_account_id"], tx["target_account_id"])

        for pay in operational["payment_requests"]:
            self.assertIn(pay["customer_id"], cust_ids)
            self.assertIn(pay["account_id"], cust_acc_map[pay["customer_id"]])

    def test_workload_generator_phases(self):
        customers, accounts = self.cust_gen.generate(num_customers=20, num_accounts=25)
        c_ids = [c["customer_id"] for c in customers]
        a_ids = [a["account_id"] for a in accounts]

        # W4: Burst
        w4 = self.workload_gen.generate_workload("W4", c_ids, a_ids, max_events=1000)
        rates = [e["arrival_rate_rps"] for e in w4]
        self.assertTrue(any(r >= 2000.0 for r in rates), "W4 must contain burst arrival rates")

        # W5: Failure
        w5 = self.workload_gen.generate_workload("W5", c_ids, a_ids, max_events=1000)
        has_failure = any(e.get("failure_metadata") and e["failure_metadata"].get("failure_injected") for e in w5)
        self.assertTrue(has_failure, "W5 must contain failure-injected events")

        # W6: Recovery
        w6 = self.workload_gen.generate_workload("W6", c_ids, a_ids, max_events=1000)
        has_recovery = any(e.get("failure_metadata") and e["failure_metadata"].get("recovery_active") for e in w6)
        self.assertTrue(has_recovery, "W6 must contain recovery-active events")

    def test_validator_detects_tampered_records(self):
        customers, accounts = self.cust_gen.generate(num_customers=20, num_accounts=20)
        datasets = {
            "customers": customers,
            "accounts": accounts,
            "transactions": [],
            "login_events": [],
            "payment_requests": [],
            "risk_requests": [],
            "notifications": [],
            "audit_logs": []
        }
        is_valid, _ = self.validator.validate_all(datasets, {})
        self.assertTrue(is_valid)

        # Inject foreign key corruption
        tampered_datasets = copy.deepcopy(datasets)
        tampered_datasets["accounts"][0]["customer_id"] = "CUST_NON_EXISTENT_999999"
        is_invalid, stats = self.validator.validate_all(tampered_datasets, {})
        self.assertFalse(is_invalid)
        self.assertGreaterEqual(stats["error_count"], 1)


if __name__ == "__main__":
    unittest.main()
