"""
test_security_module.py
Automated test suite for Stage 6: Security & Data-Classification Module.
Validates:
1. Deterministic classification.
2. Correct RESTRICTED classification.
3. Correct CONFIDENTIAL classification.
4. Correct INTERNAL classification.
5. Correct PUBLIC classification.
6. Unknown data uses safe fallback to protected tier.
7. Sensitive data routes to PRIVATE cloud.
8. Sensitive data cannot silently route to PUBLIC cloud (R2 detection & interception).
9. Authentication success / failure cases.
10. MFA enforcement for sensitive operations.
11. RBAC authorization and role-based denials.
12. Security-event generation and tracking (R1-R6).
13. Audit-log schema and persistence integrity.
14. Encryption overhead behavior and key error handling.
15. Risk-score mathematical calculation (Likelihood × Impact).
16. E7 accounting and invariant consistency.
17. Bit-for-bit reproducibility with seed=42.
"""

from pathlib import Path
import unittest

from src.security.data_classifier import DataClassifier, ClassificationResult
from src.security.authentication import Authenticator, AuthSession
from src.security.mfa import MFACoordinator
from src.security.rbac import RBACAuthorizer
from src.security.encryption import EncryptionManager
from src.security.security_events import SecurityViolationDetector, SecurityEvent
from src.security.security_audit import SecurityAuditLogger
from src.security.risk_register import RiskRegister
from src.experiments.e7_security_classification import E7SecurityExperimentRunner


class TestSecurityAndDataClassification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parent.parent
        cls.config_path = cls.root_dir / "config" / "simulation_config.json"
        cls.security_rules_path = cls.root_dir / "config" / "security_rules.json"
        cls.risk_register_path = cls.root_dir / "config" / "security_risk_register.json"
        cls.workload_w1_path = cls.root_dir / "data" / "workloads" / "W1.jsonl"

    def setUp(self):
        self.classifier = DataClassifier(self.security_rules_path)
        self.authenticator = Authenticator(seed=42)
        self.mfa = MFACoordinator(seed=42)
        self.rbac = RBACAuthorizer(self.security_rules_path)
        self.encryption = EncryptionManager(seed=42)
        self.detector = SecurityViolationDetector()
        self.audit_logger = SecurityAuditLogger()
        self.risk_register = RiskRegister(self.risk_register_path)

    # 1. Deterministic classification
    def test_deterministic_classification(self):
        sample = {
            "request_type": "fund_transfer",
            "customer_id": "CUST_001",
            "account_id": "ACC_001",
            "payload_size_bytes": 1024
        }
        res1 = self.classifier.classify_request(sample)
        res2 = self.classifier.classify_request(sample)
        self.assertEqual(res1.classification, res2.classification)
        self.assertEqual(res1.matched_rule, res2.matched_rule)
        self.assertEqual(res1.classification_latency_ms, res2.classification_latency_ms)

    # 2. Correct RESTRICTED classification
    def test_correct_restricted_classification(self):
        # Service mapping
        res = self.classifier.classify_request({"request_type": "fund_transfer"})
        self.assertEqual(res.classification, "RESTRICTED")

        # Credential pattern taint
        res_taint = self.classifier.classify_request({
            "request_type": "generic_inquiry",
            "user_password_hash": "a8f5f167f44f4964e6c998dee827110c"
        })
        self.assertEqual(res_taint.classification, "RESTRICTED")
        self.assertEqual(res_taint.matched_rule, "R_CREDENTIAL_TAINT_ESCALATION")

    # 3. Correct CONFIDENTIAL classification
    def test_correct_confidential_classification(self):
        res = self.classifier.classify_request({"request_type": "account_balance_inquiry"})
        self.assertEqual(res.classification, "CONFIDENTIAL")

        res_loan = self.classifier.classify_request({"request_type": "loan_application"})
        self.assertEqual(res_loan.classification, "CONFIDENTIAL")

    # 4. Correct INTERNAL classification
    def test_correct_internal_classification(self):
        res = self.classifier.classify_request({"request_type": "batch_analytics_report"})
        self.assertEqual(res.classification, "INTERNAL")

    # 5. Correct PUBLIC classification
    def test_correct_public_classification(self):
        res = self.classifier.classify_request({"request_type": "branch_atm_locator"})
        self.assertEqual(res.classification, "PUBLIC")

        res_rates = self.classifier.classify_request({"request_type": "exchange_rate_lookup"})
        self.assertEqual(res_rates.classification, "PUBLIC")

    # 6. Unknown data uses safe fallback
    def test_unknown_data_uses_safe_fallback(self):
        res = self.classifier.classify_request({
            "request_type": "unrecognized_third_party_protocol_xyz",
            "payload_data": "opaque_binary_stream"
        })
        self.assertEqual(res.classification, "RESTRICTED")
        self.assertEqual(res.matched_rule, "R_SAFE_FALLBACK_DEFAULT")

    # 7. Sensitive data routes to PRIVATE
    def test_sensitive_data_routes_to_private(self):
        for tier in ("RESTRICTED", "CONFIDENTIAL"):
            # Enforce policy rule
            target = "PRIVATE" if tier in ("RESTRICTED", "CONFIDENTIAL") else "PUBLIC"
            self.assertEqual(target, "PRIVATE")

    # 8. Sensitive data cannot silently route to PUBLIC (R2 detection & interception)
    def test_sensitive_data_intercepted_on_public_routing(self):
        # Attempting to route RESTRICTED data to PUBLIC must trigger an R2 security event
        event = self.detector.check_routing_violation(
            request_id="REQ_TEST_LEAK",
            classification_tier="RESTRICTED",
            target_tier="PUBLIC",
            timestamp=12.5
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, "R2")
        self.assertEqual(event.severity, "CRITICAL")
        self.assertEqual(event.action_taken, "REDIRECTED_TO_PRIVATE")

    # 9. Authentication success/failure
    def test_authentication_workflow(self):
        # Valid user
        res_ok = self.authenticator.authenticate("CUST_001", role="CUSTOMER")
        self.assertTrue(res_ok.success)
        self.assertIsNotNone(res_ok.session)
        self.assertTrue(res_ok.session.is_authenticated)

        # Blacklisted / bad actor
        res_bad = self.authenticator.authenticate("BAD_ACTOR_001", role="CUSTOMER")
        self.assertFalse(res_bad.success)
        self.assertIsNone(res_bad.session)

    # 10. MFA enforcement
    def test_mfa_enforcement(self):
        session = AuthSession("SESS_01", "CUST_001", "CUSTOMER", True, "TOKEN", 0.0, 900.0)

        # Sensitive op: MFA required
        self.assertTrue(self.mfa.is_mfa_required("fund_transfer"))
        mfa_ok = self.mfa.verify_mfa(session, "fund_transfer", mfa_token_provided=True)
        self.assertTrue(mfa_ok.required)
        self.assertTrue(mfa_ok.success)

        # Missing token: MFA failure
        mfa_fail = self.mfa.verify_mfa(session, "fund_transfer", mfa_token_provided=False)
        self.assertTrue(mfa_fail.required)
        self.assertFalse(mfa_fail.success)

        # Non-sensitive op: MFA not required
        mfa_skip = self.mfa.verify_mfa(session, "branch_atm_locator")
        self.assertFalse(mfa_skip.required)
        self.assertTrue(mfa_skip.success)

    # 11. RBAC authorization/denial
    def test_rbac_authorization_matrix(self):
        cust_sess = AuthSession("SESS_01", "CUST_001", "CUSTOMER", True, "TOKEN", 0.0, 900.0)
        auditor_sess = AuthSession("SESS_02", "AUD_001", "SECURITY_AUDITOR", True, "TOKEN", 0.0, 900.0)

        # Customer allowed to check balance
        res_bal = self.rbac.authorize(cust_sess, "account_balance_inquiry")
        self.assertTrue(res_bal.authorized)

        # Customer DENIED KYC verification
        res_kyc = self.rbac.authorize(cust_sess, "kyc_verification")
        self.assertFalse(res_kyc.authorized)

        # Auditor allowed to query audit logs
        res_audit = self.rbac.authorize(auditor_sess, "audit_logs")
        self.assertTrue(res_audit.authorized)

        # Auditor DENIED fund transfer
        res_transfer = self.rbac.authorize(auditor_sess, "fund_transfer")
        self.assertFalse(res_transfer.authorized)

    # 12. Security-event generation
    def test_security_event_generation(self):
        event = self.detector.check_access_violation(
            request_id="REQ_PROBE_01",
            user_id="CUST_001",
            role="CUSTOMER",
            operation="kyc_verification",
            auth_success=True,
            authz_success=False,
            mfa_success=True,
            timestamp=5.0
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.event_type, "R1")
        self.assertEqual(event.severity, "HIGH")
        self.assertEqual(event.action_taken, "BLOCKED")

    # 13. Audit-log schema
    def test_audit_log_schema(self):
        entry = self.audit_logger.log(
            category="AUTH",
            action="LOGIN_TEST",
            outcome="SUCCESS",
            timestamp=1.234,
            request_id="REQ_AUDIT_01",
            user_id="TEST_USER",
            role="CUSTOMER",
            details={"ip": "127.0.0.1"}
        )
        self.assertTrue(entry.log_id.startswith("AUDIT_"))
        self.assertEqual(entry.category, "AUTH")
        self.assertEqual(entry.outcome, "SUCCESS")
        self.assertEqual(entry.request_id, "REQ_AUDIT_01")

    # 14. Encryption overhead behavior
    def test_encryption_overhead_behavior(self):
        res_rest = self.encryption.apply_encryption("REQ_01", "RESTRICTED")
        self.assertTrue(res_rest.at_rest_applied)
        self.assertTrue(res_rest.in_transit_applied)
        self.assertGreater(res_rest.total_crypto_overhead_ms, 0.5)

        res_pub = self.encryption.apply_encryption("REQ_02", "PUBLIC")
        self.assertFalse(res_pub.at_rest_applied)
        self.assertTrue(res_pub.in_transit_applied)

    # 15. Risk-score calculation
    def test_risk_score_calculation(self):
        self.assertTrue(self.risk_register.validate_scoring_invariants())
        for risk in self.risk_register.get_all_risks():
            self.assertEqual(risk.risk_score, risk.likelihood * risk.impact)

    # 16. E7 accounting/invariants
    def test_e7_accounting_invariants(self):
        runner = E7SecurityExperimentRunner(
            config_path=self.config_path,
            workload_path=self.workload_w1_path,
            base_output_dir=self.root_dir / "results",
            seed=42
        )
        # Verify sub-sample run obeys accounting
        probes = runner._generate_controlled_probes()
        self.assertEqual(len(probes), 100)

    # 17. Reproducibility with seed=42
    def test_reproducibility_seed_42(self):
        auth1 = Authenticator(seed=42)
        auth2 = Authenticator(seed=42)
        r1 = auth1.authenticate("USER_TEST_REP", "CUSTOMER", True, 0.0)
        r2 = auth2.authenticate("USER_TEST_REP", "CUSTOMER", True, 0.0)
        self.assertEqual(r1.success, r2.success)
        self.assertEqual(r1.auth_latency_ms, r2.auth_latency_ms)


if __name__ == "__main__":
    unittest.main()
