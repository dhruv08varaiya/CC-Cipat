"""
authentication.py
Lightweight simulated authentication mechanism for the Digital Banking System simulation.
Represents user session lifecycle, credential verification latency, and authentication outcomes.
Academic simulation abstraction: Does NOT use real credentials, passwords, or tokens.
"""

from dataclasses import dataclass
import hashlib
import random
import time
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AuthSession:
    session_id: str
    user_id: str
    role: str
    is_authenticated: bool
    auth_method: str
    created_at: float
    expires_at: float


@dataclass(frozen=True)
class AuthResult:
    success: bool
    session: Optional[AuthSession]
    reason: str
    auth_latency_ms: float


class Authenticator:
    """Simulates authentication verification, session generation, and credential checking."""

    def __init__(
        self,
        default_success_rate: float = 0.99,
        session_timeout_seconds: float = 900.0,
        seed: int = 42
    ):
        self.default_success_rate = default_success_rate
        self.session_timeout_seconds = session_timeout_seconds
        self.seed = seed
        self._counter = 0

    def _get_rng(self, identifier: str) -> random.Random:
        hash_val = int(hashlib.sha256(f"{identifier}_{self.seed}".encode()).hexdigest()[:8], 16)
        return random.Random(hash_val)

    def authenticate(
        self,
        user_id: str,
        role: str = "CUSTOMER",
        credentials_valid: bool = True,
        current_time: float = 0.0
    ) -> AuthResult:
        """
        Simulates authenticating a user.
        Evaluates credentials validity, simulated network/crypto latency, and stochastic failure.
        """
        self._counter += 1
        rng = self._get_rng(f"{user_id}_{self._counter}")
        auth_latency_ms = round(0.40 + rng.uniform(0.05, 0.15), 3)

        # Explicit failure cases for security testing
        if not credentials_valid or user_id.startswith("BAD_ACTOR") or user_id.startswith("INVALID"):
            return AuthResult(
                success=False,
                session=None,
                reason="Invalid credentials or blacklisted user identifier",
                auth_latency_ms=auth_latency_ms
            )

        # Stochastic authentication drop / failure representation
        if rng.random() > self.default_success_rate:
            return AuthResult(
                success=False,
                session=None,
                reason="Transient identity verification / credential handshake failure",
                auth_latency_ms=auth_latency_ms
            )

        session_id = f"SESS_{hashlib.sha256(f'{user_id}_{self._counter}_{self.seed}'.encode()).hexdigest()[:12]}"
        session = AuthSession(
            session_id=session_id,
            user_id=user_id,
            role=role.upper(),
            is_authenticated=True,
            auth_method="SIMULATED_MUTUAL_TLS_TOKEN",
            created_at=current_time,
            expires_at=current_time + self.session_timeout_seconds
        )

        return AuthResult(
            success=True,
            session=session,
            reason="Authentication successful; valid simulated session token generated",
            auth_latency_ms=auth_latency_ms
        )
