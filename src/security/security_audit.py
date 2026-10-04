"""
security_audit.py
Structured Security Audit Logging engine for the Digital Banking System simulation.
Captures an immutable, timestamped record of security events, authorization decisions,
classification assessments, and policy violations in JSON Lines format.

Audit Categories:
- AUTH: Authentication attempts and session creation.
- MFA: Second-factor challenge and verification.
- RBAC: Authorization evaluations against role matrix.
- CLASSIFICATION: Automated tier assignment and rule matches.
- ROUTING: Secure hybrid routing decisions and compliance enforcement.
- ENCRYPTION: Cryptographic lifecycle events and overhead logging.
- VIOLATION: Triggered security alerts and governance violations (R1-R6).

Disclaimer: Academic simulation logger. Does NOT record real customer PII or cryptographic secrets.
"""

from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AuditEntry:
    log_id: str
    timestamp: float
    category: str           # "AUTH", "MFA", "RBAC", "CLASSIFICATION", "ROUTING", "ENCRYPTION", "VIOLATION"
    request_id: Optional[str]
    user_id: Optional[str]
    role: Optional[str]
    action: str
    outcome: str            # "SUCCESS", "DENIED", "FLAGGED", "REDIRECTED"
    details: Dict[str, Any]


class SecurityAuditLogger:
    """Manages structured security audit logging in memory and persists to JSONL."""

    def __init__(self, output_path: Optional[Path] = None):
        self.output_path = Path(output_path) if output_path else None
        self.entries: List[AuditEntry] = []
        self._counter = 0

    def _next_log_id(self) -> str:
        self._counter += 1
        return f"AUDIT_{self._counter:07d}"

    def log(
        self,
        category: str,
        action: str,
        outcome: str,
        timestamp: float,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        role: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """Appends a new audit record to the log buffer."""
        entry = AuditEntry(
            log_id=self._next_log_id(),
            timestamp=round(timestamp, 4),
            category=category.upper(),
            request_id=request_id,
            user_id=user_id,
            role=role.upper() if role else None,
            action=action,
            outcome=outcome.upper(),
            details=details or {}
        )
        self.entries.append(entry)
        return entry

    def flush_to_disk(self, target_path: Optional[Path] = None):
        """Persists all buffered audit entries to a JSONL file."""
        dest = Path(target_path) if target_path else self.output_path
        if not dest:
            raise ValueError("No output path specified for security audit log.")

        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            for entry in self.entries:
                f.write(json.dumps(asdict(entry)) + "\n")

    def get_entries_by_category(self, category: str) -> List[AuditEntry]:
        cat = category.upper()
        return [e for e in self.entries if e.category == cat]

    def get_entries_by_outcome(self, outcome: str) -> List[AuditEntry]:
        out = outcome.upper()
        return [e for e in self.entries if e.outcome == out]

    def count(self) -> int:
        return len(self.entries)
