"""
security_events.py
Simulated security violation detection and security event tracking.
Captures governance risks R1 through R6:
- R1: Unauthorized internal access (RBAC / Auth / MFA rejections)
- R2: Sensitive data leakage to public cloud tier
- R3: Provider dependency / cloud control deviation
- R4: Cryptographic key management failure
- R5: Service availability / security subsystem disruption
- R6: Cross-border data residency governance violation

Disclaimer: These are simulation-level governance and policy violation representations.
They do not represent real-world network intrusions or live exploit payloads.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SecurityEvent:
    event_id: str
    timestamp: float
    event_type: str         # "R1", "R2", "R3", "R4", "R5", "R6"
    severity: str           # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    request_id: Optional[str]
    source_component: str
    description: str
    detected: bool
    action_taken: str       # "BLOCKED", "REDIRECTED_TO_PRIVATE", "ALERT_LOGGED", "QUARANTINED"


class SecurityViolationDetector:
    """Monitors simulation traffic and triggers structured security events on governance violations."""

    def __init__(self):
        self.events: List[SecurityEvent] = []
        self._counter = 0

    def _next_event_id(self) -> str:
        self._counter += 1
        return f"SEC_EVT_{self._counter:05d}"

    def check_routing_violation(
        self,
        request_id: str,
        classification_tier: str,
        target_tier: str,
        timestamp: float
    ) -> Optional[SecurityEvent]:
        """
        Detects Risk R2: Sensitive data (RESTRICTED or CONFIDENTIAL) routed to PUBLIC tier.
        """
        tier = classification_tier.upper()
        target = target_tier.upper()

        if tier in ("RESTRICTED", "CONFIDENTIAL") and target == "PUBLIC":
            severity = "CRITICAL" if tier == "RESTRICTED" else "HIGH"
            event = SecurityEvent(
                event_id=self._next_event_id(),
                timestamp=timestamp,
                event_type="R2",
                severity=severity,
                request_id=request_id,
                source_component="REQUEST_ROUTER",
                description=f"Regulatory violation: {tier} data attempted route to PUBLIC elastic zone",
                detected=True,
                action_taken="REDIRECTED_TO_PRIVATE"
            )
            self.events.append(event)
            return event
        return None

    def check_access_violation(
        self,
        request_id: str,
        user_id: str,
        role: str,
        operation: str,
        auth_success: bool,
        authz_success: bool,
        mfa_success: bool,
        timestamp: float
    ) -> Optional[SecurityEvent]:
        """
        Detects Risk R1: Unauthorized internal access, credential failure, or MFA bypass attempt.
        """
        if not auth_success:
            event = SecurityEvent(
                event_id=self._next_event_id(),
                timestamp=timestamp,
                event_type="R1",
                severity="MEDIUM",
                request_id=request_id,
                source_component="AUTHENTICATOR",
                description=f"Authentication rejected for user '{user_id}' attempting operation '{operation}'",
                detected=True,
                action_taken="BLOCKED"
            )
            self.events.append(event)
            return event

        if not authz_success:
            event = SecurityEvent(
                event_id=self._next_event_id(),
                timestamp=timestamp,
                event_type="R1",
                severity="HIGH",
                request_id=request_id,
                source_component="RBAC_AUTHORIZER",
                description=f"Access denied: Role '{role}' lacks permission for banking operation '{operation}'",
                detected=True,
                action_taken="BLOCKED"
            )
            self.events.append(event)
            return event

        if not mfa_success:
            event = SecurityEvent(
                event_id=self._next_event_id(),
                timestamp=timestamp,
                event_type="R1",
                severity="HIGH",
                request_id=request_id,
                source_component="MFA_COORDINATOR",
                description=f"Multi-factor challenge failed for sensitive operation '{operation}' by user '{user_id}'",
                detected=True,
                action_taken="BLOCKED"
            )
            self.events.append(event)
            return event

        return None

    def check_crypto_violation(
        self,
        request_id: str,
        crypto_status: str,
        timestamp: float
    ) -> Optional[SecurityEvent]:
        """
        Detects Risk R4: Cryptographic key management or decryption failure.
        """
        if crypto_status == "FAILURE_KEY_ERROR":
            event = SecurityEvent(
                event_id=self._next_event_id(),
                timestamp=timestamp,
                event_type="R4",
                severity="HIGH",
                request_id=request_id,
                source_component="ENCRYPTION_MANAGER",
                description=f"Cryptographic key failure: unable to decrypt/encrypt payload for request '{request_id}'",
                detected=True,
                action_taken="QUARANTINED"
            )
            self.events.append(event)
            return event
        return None

    def check_data_residency_violation(
        self,
        request_id: str,
        classification_tier: str,
        residency_zone: str,
        timestamp: float
    ) -> Optional[SecurityEvent]:
        """
        Detects Risk R6: Cross-border transfer of sovereign RESTRICTED banking data.
        """
        if classification_tier.upper() == "RESTRICTED" and residency_zone.upper() != "DOMESTIC_ZONE":
            event = SecurityEvent(
                event_id=self._next_event_id(),
                timestamp=timestamp,
                event_type="R6",
                severity="CRITICAL",
                request_id=request_id,
                source_component="DATA_RESIDENCY_FILTER",
                description=f"Cross-border governance breach: RESTRICTED sovereign record destined for external zone '{residency_zone}'",
                detected=True,
                action_taken="BLOCKED"
            )
            self.events.append(event)
            return event
        return None

    def get_events(self) -> List[SecurityEvent]:
        return list(self.events)

    def get_events_by_type(self, event_type: str) -> List[SecurityEvent]:
        return [e for e in self.events if e.event_type == event_type.upper()]

    def get_events_by_severity(self, severity: str) -> List[SecurityEvent]:
        return [e for e in self.events if e.severity == severity.upper()]
