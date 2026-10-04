"""
transaction_generator.py
Generates synthetic banking transactions, payment requests, login events,
risk requests, notifications, and audit logs with strict referential integrity.
"""

from datetime import datetime, timedelta, timezone
import random
from typing import Dict, List, Tuple


class TransactionGenerator:
    """Generates synthetic operational and transactional logs linked to accounts and customers."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.base_time = datetime(2026, 10, 1, 8, 0, 0, tzinfo=timezone.utc)

    def generate_all(
        self,
        customers: List[Dict],
        accounts: List[Dict],
        num_transactions: int,
        num_logins: int,
        num_payments: int,
        num_risk: int,
        num_notifications: int,
        num_audits: int
    ) -> Dict[str, List[Dict]]:
        """
        Generates all operational datasets with strict foreign-key integrity against
        the provided customers and accounts lists.
        """
        self.rng.seed(self.seed)

        # Build lookup indices for fast, valid referential linking
        cust_ids = [c["customer_id"] for c in customers]
        acc_ids = [a["account_id"] for a in accounts]
        
        # Customer-to-Accounts mapping
        cust_to_accounts: Dict[str, List[str]] = {}
        for a in accounts:
            cust_to_accounts.setdefault(a["customer_id"], []).append(a["account_id"])

        results: Dict[str, List[Dict]] = {}

        # -------------------------------------------------------------
        # 1. Transactions (transactions.csv)
        # -------------------------------------------------------------
        transactions = []
        tx_types = ["TRANSFER", "PAYMENT", "WITHDRAWAL", "DEPOSIT"]
        tx_weights = [0.45, 0.35, 0.12, 0.08]
        channels = ["MOBILE_APP", "ONLINE_BANKING", "ATM", "BRANCH_PORTAL"]
        channel_weights = [0.55, 0.30, 0.10, 0.05]

        current_time = self.base_time
        for i in range(1, num_transactions + 1):
            tx_id = f"TX_{i:07d}"
            # Incremental timestamp with small jitter (0.05s to 2.5s)
            current_time += timedelta(milliseconds=self.rng.randint(50, 2500))
            
            src_acc = self.rng.choice(acc_ids)
            # Pick a target account distinct from source
            tgt_acc = self.rng.choice(acc_ids)
            while tgt_acc == src_acc and len(acc_ids) > 1:
                tgt_acc = self.rng.choice(acc_ids)

            tx_type = self.rng.choices(tx_types, weights=tx_weights, k=1)[0]
            channel = self.rng.choices(channels, weights=channel_weights, k=1)[0]
            
            # Amount distribution: log-normal shape
            amount = round(self.rng.expovariate(1 / 250.0) + 5.0, 2)
            amount = min(50000.0, max(1.0, amount))

            # Failure rate ~ 3.5%
            status = self.rng.choices(["SUCCESS", "PENDING", "FAILED"], weights=[0.94, 0.025, 0.035], k=1)[0]

            transactions.append({
                "tx_id": tx_id,
                "timestamp": current_time.isoformat(),
                "source_account_id": src_acc,
                "target_account_id": tgt_acc,
                "amount": amount,
                "transaction_type": tx_type,
                "channel": channel,
                "status": status,
                "classification_tier": "CONFIDENTIAL"
            })
        results["transactions"] = transactions

        # -------------------------------------------------------------
        # 2. Login Events (login_events.csv)
        # -------------------------------------------------------------
        login_events = []
        auth_methods = ["PASSWORD", "BIOMETRIC", "OAUTH2", "SMS_OTP"]
        devices = ["IOS", "ANDROID", "WEB_BROWSER", "ATM_KIOSK"]
        current_time = self.base_time

        for i in range(1, num_logins + 1):
            evt_id = f"LOG_{i:06d}"
            current_time += timedelta(milliseconds=self.rng.randint(100, 3000))
            cust_id = self.rng.choice(cust_ids)
            auth = self.rng.choice(auth_methods)
            mfa = (auth in ["OAUTH2", "SMS_OTP"]) or (self.rng.random() < 0.60)
            success = self.rng.random() < 0.96
            device = self.rng.choice(devices)

            login_events.append({
                "event_id": evt_id,
                "customer_id": cust_id,
                "timestamp": current_time.isoformat(),
                "authentication_method": auth,
                "mfa_used": mfa,
                "success": success,
                "device_type": device,
                "classification_tier": "RESTRICTED"
            })
        results["login_events"] = login_events

        # -------------------------------------------------------------
        # 3. Payment Requests (payment_requests.csv)
        # -------------------------------------------------------------
        payments = []
        pay_types = ["BILL_PAY", "PEER_TO_PEER", "MERCHANT_PAY", "SUBSCRIPTION"]
        pay_channels = ["MOBILE_APP", "ONLINE_BANKING", "API_GATEWAY"]
        current_time = self.base_time

        for i in range(1, num_payments + 1):
            pid = f"PAY_{i:06d}"
            current_time += timedelta(milliseconds=self.rng.randint(80, 2800))
            cust_id = self.rng.choice(cust_ids)
            acc_id = self.rng.choice(cust_to_accounts[cust_id])  # Must belong to customer
            amount = round(self.rng.uniform(10.0, 5000.0), 2)
            ptype = self.rng.choice(pay_types)
            pchan = self.rng.choice(pay_channels)
            pstatus = self.rng.choices(["COMPLETED", "PENDING", "REJECTED"], weights=[0.93, 0.03, 0.04], k=1)[0]

            payments.append({
                "payment_id": pid,
                "customer_id": cust_id,
                "account_id": acc_id,
                "amount": amount,
                "payment_type": ptype,
                "channel": pchan,
                "timestamp": current_time.isoformat(),
                "status": pstatus,
                "classification_tier": "CONFIDENTIAL"
            })
        results["payment_requests"] = payments

        # -------------------------------------------------------------
        # 4. Risk Requests (risk_requests.csv)
        # -------------------------------------------------------------
        risk_requests = []
        rsk_types = ["CREDIT_EVALUATION", "FRAUD_DETECTION", "AML_SCREENING", "LOAN_SCORING"]
        current_time = self.base_time

        for i in range(1, num_risk + 1):
            rid = f"RSK_{i:06d}"
            current_time += timedelta(milliseconds=self.rng.randint(200, 5000))
            cust_id = self.rng.choice(cust_ids)
            rtype = self.rng.choice(rsk_types)
            score = round(self.rng.betavariate(2, 5), 3)
            if score > 0.70:
                rstatus = "REJECTED"
            elif score > 0.45:
                rstatus = "FLAGGED_FOR_REVIEW"
            else:
                rstatus = "APPROVED"

            risk_requests.append({
                "request_id": rid,
                "customer_id": cust_id,
                "request_type": rtype,
                "timestamp": current_time.isoformat(),
                "risk_score": score,
                "status": rstatus,
                "classification_tier": "CONFIDENTIAL"
            })
        results["risk_requests"] = risk_requests

        # -------------------------------------------------------------
        # 5. Notifications (notifications.csv)
        # -------------------------------------------------------------
        notifications = []
        notif_types = ["TRANSACTION_ALERT", "SECURITY_OTP", "STATEMENT_READY", "MARKETING_PROMO"]
        current_time = self.base_time

        for i in range(1, num_notifications + 1):
            nid = f"NOTIF_{i:06d}"
            current_time += timedelta(milliseconds=self.rng.randint(60, 2000))
            cust_id = self.rng.choice(cust_ids)
            ntype = self.rng.choice(notif_types)
            nstatus = self.rng.choices(["DELIVERED", "SENT", "FAILED"], weights=[0.95, 0.03, 0.02], k=1)[0]

            notifications.append({
                "notification_id": nid,
                "customer_id": cust_id,
                "notification_type": ntype,
                "timestamp": current_time.isoformat(),
                "status": nstatus
            })
        results["notifications"] = notifications

        # -------------------------------------------------------------
        # 6. Audit Logs (audit_logs.csv)
        # -------------------------------------------------------------
        audit_logs = []
        actors = ["SYSTEM_WORKER", "ADMIN_USR_01", "API_GATEWAY", "TELLER_04", "SECURITY_DAEMON"]
        actions = ["READ_ACCOUNT", "UPDATE_BALANCE", "AUTH_VERIFY", "BATCH_SETTLEMENT", "KEY_ROTATION"]
        current_time = self.base_time

        for i in range(1, num_audits + 1):
            aid = f"AUD_{i:06d}"
            current_time += timedelta(milliseconds=self.rng.randint(40, 1500))
            actor = self.rng.choice(actors)
            act = self.rng.choice(actions)
            # Pick a realistic internal target
            if "ACCOUNT" in act or "BALANCE" in act:
                res = self.rng.choice(acc_ids)
            elif "AUTH" in act:
                res = self.rng.choice(cust_ids)
            else:
                res = "CORE_BANKING_ENGINE"
            
            astatus = self.rng.choices(["SUCCESS", "FAILURE", "DENIED"], weights=[0.97, 0.02, 0.01], k=1)[0]

            audit_logs.append({
                "log_id": aid,
                "actor_id": actor,
                "action": act,
                "resource": res,
                "timestamp": current_time.isoformat(),
                "status": astatus,
                "classification_tier": "INTERNAL"
            })
        results["audit_logs"] = audit_logs

        return results
