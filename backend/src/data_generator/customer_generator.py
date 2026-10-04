"""
customer_generator.py
Generates synthetic, privacy-safe banking customers and linked accounts with referential integrity.
"""

import random
from typing import Dict, List, Tuple


class CustomerGenerator:
    """Generates synthetic customers and accounts adhering to banking classification standards."""

    FIRST_NAMES = [
        "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Sam", 
        "Pat", "Quinn", "Cameron", "Dakota", "Reese", "Skyler", "Rowan", "Ellis"
    ]
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", 
        "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin"
    ]

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate(self, num_customers: int, num_accounts: int) -> Tuple[List[Dict], List[Dict]]:
        """
        Generates customers and accounts.
        Ensures num_accounts >= num_customers so every customer has at least one account.
        """
        self.rng.seed(self.seed)
        customers = []
        accounts = []

        if num_accounts < num_customers:
            num_accounts = num_customers

        # 1. Generate Customers
        for i in range(1, num_customers + 1):
            cust_id = f"CUST_{i:06d}"
            first_name = self.rng.choice(self.FIRST_NAMES)
            last_name = self.rng.choice(self.LAST_NAMES)
            full_name = f"{first_name} {last_name} (Synth-{i:04d})"
            age = self.rng.randint(18, 78)
            phone = f"+1-555-01{self.rng.randint(10, 99)}-{i % 10000:04d}"
            email = f"synth_user_{i:06d}@synth-bank.test"
            address = f"{100 + (i % 900)} Synthetic Way, Suite {i % 50 + 1}, Region-{i % 10 + 1}"
            
            kyc_status = self.rng.choices(
                ["VERIFIED", "PENDING", "FLAGGED"],
                weights=[0.85, 0.10, 0.05],
                k=1
            )[0]
            
            risk_score = round(self.rng.betavariate(2, 5), 3)  # Skewed towards lower risk
            risk_score = max(0.01, min(0.99, risk_score))

            customers.append({
                "customer_id": cust_id,
                "name": full_name,
                "age": age,
                "phone": phone,
                "email": email,
                "address": address,
                "kyc_status": kyc_status,
                "customer_risk_score": risk_score,
                "classification_tier": "RESTRICTED"
            })

        # 2. Generate Accounts (Referential integrity guaranteed)
        # First assign one primary account per customer
        acc_idx = 1
        for cust in customers:
            acc_id = f"ACC_{acc_idx:06d}"
            acc_type = "SAVINGS"
            balance = round(self.rng.uniform(1000.0, 50000.0), 2)
            acc_status = "ACTIVE" if cust["kyc_status"] != "FLAGGED" else "FROZEN"
            acc_risk = cust["customer_risk_score"]

            accounts.append({
                "account_id": acc_id,
                "customer_id": cust["customer_id"],
                "account_type": acc_type,
                "balance": balance,
                "status": acc_status,
                "kyc_status": cust["kyc_status"],
                "risk_score": acc_risk,
                "classification_tier": "RESTRICTED"
            })
            acc_idx += 1

        # Distribute remaining accounts randomly among customers
        account_types = ["SAVINGS", "CURRENT", "SALARY", "FIXED_DEPOSIT"]
        account_type_weights = [0.40, 0.35, 0.15, 0.10]

        while acc_idx <= num_accounts:
            chosen_cust = self.rng.choice(customers)
            acc_id = f"ACC_{acc_idx:06d}"
            acc_type = self.rng.choices(account_types, weights=account_type_weights, k=1)[0]
            
            if acc_type == "FIXED_DEPOSIT":
                balance = round(self.rng.uniform(10000.0, 250000.0), 2)
            else:
                balance = round(self.rng.uniform(500.0, 35000.0), 2)
                
            acc_status = "ACTIVE" if chosen_cust["kyc_status"] != "FLAGGED" else "FROZEN"
            # small variation in account risk
            acc_risk = round(max(0.01, min(0.99, chosen_cust["customer_risk_score"] + self.rng.uniform(-0.05, 0.05))), 3)

            accounts.append({
                "account_id": acc_id,
                "customer_id": chosen_cust["customer_id"],
                "account_type": acc_type,
                "balance": balance,
                "status": acc_status,
                "kyc_status": chosen_cust["kyc_status"],
                "risk_score": acc_risk,
                "classification_tier": "RESTRICTED"
            })
            acc_idx += 1

        return customers, accounts
