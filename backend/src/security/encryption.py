"""
encryption.py
Cryptographic simulation abstraction for the Digital Banking System.
Models latency overhead and state tracking for:
- Data-at-Rest Encryption (AES-256-GCM)
- Data-in-Transit Encryption (TLS 1.3)

Disclaimer: This is strictly an academic simulation abstraction modeling cryptographic
timing overhead and failure modes. It does NOT implement production KMS/HSM key management.
"""

from dataclasses import dataclass
import hashlib
import random
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class EncryptionResult:
    at_rest_applied: bool
    in_transit_applied: bool
    at_rest_latency_ms: float
    in_transit_latency_ms: float
    total_crypto_overhead_ms: float
    algorithm_at_rest: str
    algorithm_in_transit: str
    status: str  # "SUCCESS", "FAILURE_KEY_ERROR", "BYPASSED"


class EncryptionManager:
    """Manages simulated cryptographic overhead, algorithms, and simulated failure injection."""

    def __init__(
        self,
        at_rest_enabled: bool = True,
        in_transit_enabled: bool = True,
        at_rest_overhead_ms: float = 0.80,
        in_transit_overhead_ms: float = 0.40,
        simulated_failure_rate: float = 0.001,
        seed: int = 42
    ):
        self.at_rest_enabled = at_rest_enabled
        self.in_transit_enabled = in_transit_enabled
        self.at_rest_overhead_ms = at_rest_overhead_ms
        self.in_transit_overhead_ms = in_transit_overhead_ms
        self.simulated_failure_rate = simulated_failure_rate
        self.seed = seed
        self._counter = 0

    def _get_rng(self, identifier: str) -> random.Random:
        hash_val = int(hashlib.sha256(f"crypto_{identifier}_{self.seed}".encode()).hexdigest()[:8], 16)
        return random.Random(hash_val)

    def apply_encryption(
        self,
        request_id: str,
        classification_tier: str,
        force_failure: bool = False
    ) -> EncryptionResult:
        """
        Simulates cryptographic operations based on data classification tier.
        RESTRICTED and CONFIDENTIAL enforce both At-Rest and In-Transit encryption.
        INTERNAL and PUBLIC enforce In-Transit encryption.
        """
        self._counter += 1
        rng = self._get_rng(f"{request_id}_{self._counter}")

        if force_failure or (self.simulated_failure_rate > 0 and rng.random() < self.simulated_failure_rate):
            return EncryptionResult(
                at_rest_applied=False,
                in_transit_applied=False,
                at_rest_latency_ms=0.0,
                in_transit_latency_ms=0.0,
                total_crypto_overhead_ms=0.0,
                algorithm_at_rest="AES-256-GCM",
                algorithm_in_transit="TLS-1.3",
                status="FAILURE_KEY_ERROR"
            )

        tier = classification_tier.upper()
        apply_rest = self.at_rest_enabled and tier in ("RESTRICTED", "CONFIDENTIAL")
        apply_transit = self.in_transit_enabled

        rest_latency = round(self.at_rest_overhead_ms * (1.0 + rng.uniform(-0.10, 0.10)), 3) if apply_rest else 0.0
        transit_latency = round(self.in_transit_overhead_ms * (1.0 + rng.uniform(-0.10, 0.10)), 3) if apply_transit else 0.0
        total_overhead = round(rest_latency + transit_latency, 3)

        return EncryptionResult(
            at_rest_applied=apply_rest,
            in_transit_applied=apply_transit,
            at_rest_latency_ms=rest_latency,
            in_transit_latency_ms=transit_latency,
            total_crypto_overhead_ms=total_overhead,
            algorithm_at_rest="AES-256-GCM" if apply_rest else "NONE",
            algorithm_in_transit="TLS-1.3" if apply_transit else "NONE",
            status="SUCCESS"
        )
