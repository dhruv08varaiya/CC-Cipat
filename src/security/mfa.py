"""
mfa.py
Multi-Factor Authentication (MFA) coordinator for high-sensitivity banking operations.
Simulates second-factor challenge-response verification for restricted operations (fund transfer, KYC, loans).
Academic simulation abstraction: Does NOT transmit or store real OTPs, SMS codes, or authenticator secrets.
"""

from dataclasses import dataclass
import hashlib
import random
from typing import Any, Dict, List, Optional, Set

from src.security.authentication import AuthSession


@dataclass(frozen=True)
class MFAResult:
    required: bool
    success: bool
    reason: str
    mfa_latency_ms: float
    factor_type: str


class MFACoordinator:
    """Evaluates MFA policy requirements and simulates multi-factor challenge verification."""

    def __init__(
        self,
        enforced_services: Optional[List[str]] = None,
        default_success_rate: float = 0.98,
        seed: int = 42
    ):
        if enforced_services is None:
            enforced_services = [
                "fund_transfer",
                "kyc_verification",
                "loan_application",
                "key_rotation",
                "system_configuration"
            ]
        self.enforced_services: Set[str] = set(enforced_services)
        self.default_success_rate = default_success_rate
        self.seed = seed
        self._counter = 0

    def _get_rng(self, identifier: str) -> random.Random:
        hash_val = int(hashlib.sha256(f"mfa_{identifier}_{self.seed}".encode()).hexdigest()[:8], 16)
        return random.Random(hash_val)

    def is_mfa_required(self, service_type: str) -> bool:
        """Checks if the invoked service mandates multi-factor authorization."""
        return service_type.lower() in self.enforced_services

    def verify_mfa(
        self,
        session: AuthSession,
        service_type: str,
        mfa_token_provided: bool = True
    ) -> MFAResult:
        """
        Simulates verifying second-factor proof.
        Returns MFAResult detailing requirement status, verification success, and latency.
        """
        if not self.is_mfa_required(service_type):
            return MFAResult(
                required=False,
                success=True,
                reason="MFA not required for non-sensitive service",
                mfa_latency_ms=0.0,
                factor_type="NONE"
            )

        self._counter += 1
        rng = self._get_rng(f"{session.user_id}_{service_type}_{self._counter}")
        mfa_latency_ms = round(0.60 + rng.uniform(0.10, 0.25), 3)

        # Test failure conditions
        if not mfa_token_provided or "MFA_FAIL" in session.user_id:
            return MFAResult(
                required=True,
                success=False,
                reason="MFA verification failed: missing or invalid second-factor proof",
                mfa_latency_ms=mfa_latency_ms,
                factor_type="SIMULATED_TOTP"
            )

        # Stochastic MFA timeout/drop simulation
        if rng.random() > self.default_success_rate:
            return MFAResult(
                required=True,
                success=False,
                reason="MFA challenge expired or verification timed out",
                mfa_latency_ms=mfa_latency_ms,
                factor_type="SIMULATED_TOTP"
            )

        return MFAResult(
            required=True,
            success=True,
            reason="MFA challenge successfully verified",
            mfa_latency_ms=mfa_latency_ms,
            factor_type="SIMULATED_TOTP"
        )
