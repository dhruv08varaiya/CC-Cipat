"""
rbac.py
Role-Based Access Control (RBAC) authorization module for the Digital Banking System.
Validates session permissions against a hierarchical banking role matrix.
Synthetic Roles:
- CUSTOMER: Standard consumer banking operations.
- BANK_OPERATOR: Back-office underwriting, KYC compliance, and loan reviews.
- SECURITY_AUDITOR: Inspection of security events, audit logs, and compliance telemetry.
- ADMIN: Infrastructure administration and configuration controls.

Academic simulation abstraction: Models enterprise access control principles without real banking authorization backends.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src.security.authentication import AuthSession


@dataclass(frozen=True)
class AuthorizationResult:
    authorized: bool
    user_id: str
    role: str
    operation: str
    reason: str
    authz_latency_ms: float


class RBACAuthorizer:
    """Enforces role-based permissions across simulated banking operations."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            root_dir = Path(__file__).resolve().parent.parent.parent
            config_path = root_dir / "config" / "security_rules.json"

        self.config_path = Path(config_path)
        self.role_permissions: Dict[str, Set[str]] = {}
        self._load_config()

    def _load_config(self):
        """Loads the RBAC role-permission matrix."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        rbac_cfg = cfg.get("rbac_matrix", {}).get("roles", {})
        for role, data in rbac_cfg.items():
            self.role_permissions[role.upper()] = set(data.get("allowed_operations", []))

        # Default fallback permissions if config missing
        if not self.role_permissions:
            self.role_permissions = {
                "CUSTOMER": {
                    "account_balance_inquiry", "transaction_history", "fund_transfer",
                    "exchange_rate_lookup", "branch_atm_locator", "interest_rate_calculator",
                    "customer_support_faq"
                },
                "BANK_OPERATOR": {
                    "account_balance_inquiry", "transaction_history", "kyc_verification",
                    "loan_application", "credit_risk_evaluation", "customer_support_faq",
                    "branch_atm_locator"
                },
                "SECURITY_AUDITOR": {
                    "audit_logs", "security_events", "monitoring_query",
                    "batch_analytics_report", "exchange_rate_lookup"
                },
                "ADMIN": {
                    "account_balance_inquiry", "fund_transfer", "kyc_verification",
                    "loan_application", "credit_risk_evaluation", "transaction_history",
                    "exchange_rate_lookup", "branch_atm_locator", "interest_rate_calculator",
                    "batch_analytics_report", "customer_support_faq", "audit_logs",
                    "security_events", "system_configuration", "key_rotation"
                }
            }

    def get_allowed_operations(self, role: str) -> List[str]:
        """Returns allowed operations for a role."""
        return sorted(list(self.role_permissions.get(role.upper(), set())))

    def authorize(self, session: AuthSession, operation: str) -> AuthorizationResult:
        """
        Evaluates whether an authenticated session is authorized to execute the operation.
        """
        role = session.role.upper()
        op = operation.lower()
        authz_latency_ms = 0.15  # Fast in-memory policy lookup overhead

        if not session.is_authenticated:
            return AuthorizationResult(
                authorized=False,
                user_id=session.user_id,
                role=role,
                operation=op,
                reason="Unauthenticated session cannot execute operations",
                authz_latency_ms=authz_latency_ms
            )

        allowed_ops = self.role_permissions.get(role, set())

        # ADMIN role has superuser override
        if role == "ADMIN" or op in allowed_ops:
            return AuthorizationResult(
                authorized=True,
                user_id=session.user_id,
                role=role,
                operation=op,
                reason=f"Operation '{op}' permitted for role '{role}'",
                authz_latency_ms=authz_latency_ms
            )

        return AuthorizationResult(
            authorized=False,
            user_id=session.user_id,
            role=role,
            operation=op,
            reason=f"Role '{role}' is not granted permission for operation '{op}'",
            authz_latency_ms=authz_latency_ms
        )
