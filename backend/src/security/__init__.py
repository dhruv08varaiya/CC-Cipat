"""
src/security
Security and Data Classification Package for the Digital Banking System simulation.
Provides:
- DataClassifier: Rule-based sensitive data classification (RESTRICTED, CONFIDENTIAL, INTERNAL, PUBLIC)
- Authenticator: Simulated session lifecycle and credential verification
- MFACoordinator: Multi-factor authentication enforcement for sensitive banking services
- RBACAuthorizer: Role-based access control matrix evaluation
- EncryptionManager: Data-at-rest and data-in-transit cryptographic overhead simulation
- SecurityViolationDetector: Detection and tracking of governance violations (R1-R6)
- SecurityAuditLogger: Structured, immutable audit trail in JSON Lines format
- RiskRegister: Project-level security risk register and scoring invariants
"""

from src.security.data_classifier import DataClassifier, ClassificationResult
from src.security.authentication import Authenticator, AuthSession, AuthResult
from src.security.mfa import MFACoordinator, MFAResult
from src.security.rbac import RBACAuthorizer, AuthorizationResult
from src.security.encryption import EncryptionManager, EncryptionResult
from src.security.security_events import SecurityViolationDetector, SecurityEvent
from src.security.security_audit import SecurityAuditLogger, AuditEntry
from src.security.risk_register import RiskRegister, SecurityRisk

__all__ = [
    "DataClassifier",
    "ClassificationResult",
    "Authenticator",
    "AuthSession",
    "AuthResult",
    "MFACoordinator",
    "MFAResult",
    "RBACAuthorizer",
    "AuthorizationResult",
    "EncryptionManager",
    "EncryptionResult",
    "SecurityViolationDetector",
    "SecurityEvent",
    "SecurityAuditLogger",
    "AuditEntry",
    "RiskRegister",
    "SecurityRisk",
]
