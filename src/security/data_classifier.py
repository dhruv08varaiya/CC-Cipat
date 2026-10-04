"""
data_classifier.py
Deterministic, transparent rule-based data classification engine for the Digital Banking System.
Inspects request metadata, field identifiers, payload attributes, and keyword patterns to
assign sensitive data into four regulatory tiers:
- RESTRICTED: Core credentials, KYC records, authentication tokens, cryptographic secrets.
- CONFIDENTIAL: Financial transactions, account balances, loan applications, credit scores.
- INTERNAL: Non-PII operational logs, batch telemetry, queue metrics, diagnostic traces.
- PUBLIC: General FAQs, branch/ATM locators, currency exchange rates, public announcements.

Note: Grounded in literature motivations (e.g. UP-SDCG, sensitive data governance).
This is an academic simulation classifier and does NOT claim to reproduce UP-SDCG or any paper's exact algorithm.
"""

from dataclasses import dataclass
import fnmatch
import json
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ClassificationResult:
    classification: str               # RESTRICTED, CONFIDENTIAL, INTERNAL, PUBLIC
    matched_rule: str                 # Unique rule identifier
    classification_reason: str        # Explanation of matched criteria
    classification_latency_ms: float  # Simulated computational inspection latency
    confidence: float                 # Confidence score (0.0 to 1.0)
    features_detected: Tuple[str, ...] # Tuple of detected features/keywords


class DataClassifier:
    """
    Deterministic rule-based data classification engine.
    Applies hierarchical inspection of field names, request types, keyword patterns,
    and data sensitivity indicators.
    """

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            root_dir = Path(__file__).resolve().parent.parent.parent
            config_path = root_dir / "config" / "security_rules.json"

        self.config_path = Path(config_path)
        self.rules: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Loads security rules, pattern definitions, and service mappings."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Security rules file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)

        self.service_mapping: Dict[str, str] = self.rules.get("service_classification_mapping", {})
        self.feature_rules: Dict[str, Any] = self.rules.get("feature_rules", {})
        self.field_patterns: Dict[str, List[str]] = self.feature_rules.get("field_name_patterns", {})
        self.keywords: Dict[str, List[str]] = self.feature_rules.get("keywords", {})

    def _compute_inspection_latency(self, num_fields: int, payload_bytes: int) -> float:
        """
        Simulates parsing and deterministic regex inspection latency.
        Nominal latency is ~0.25 ms to 0.45 ms based on payload size and field count.
        """
        base_latency = 0.20
        field_overhead = min(0.15, num_fields * 0.015)
        payload_overhead = min(0.20, (payload_bytes / 2048.0) * 0.05)
        return round(base_latency + field_overhead + payload_overhead, 3)

    def classify_request(self, request_event: Dict[str, Any]) -> ClassificationResult:
        """
        Classifies an incoming workload request event using deterministic rule evaluation.
        Two-stage inspection:
        1. Deep-payload scan for high-severity credential taint (passwords, keys, secrets).
           If detected, escalates immediately to RESTRICTED.
        2. Service-contract catalog evaluation mapping operational services to sensitivity tiers.
        3. Field pattern and keyword analysis for arbitrary or unmapped schemas.
        4. Safe-fallback to protected tier (RESTRICTED) for unknown payloads.
        """
        req_type = request_event.get("request_type", "").lower()
        payload_bytes = int(request_event.get("payload_size_bytes", 1024))
        detected_features: List[str] = []

        keys_to_inspect = list(request_event.keys())
        text_to_inspect = f"{req_type} {' '.join(str(v) for v in request_event.values())}".lower()
        num_fields = len(keys_to_inspect)
        latency = self._compute_inspection_latency(num_fields, payload_bytes)

        # -----------------------------------------------------------------
        # STAGE 1: Deep Credential / Secret Taint Scan -> Immediate Escalation
        # -----------------------------------------------------------------
        for pattern in self.field_patterns.get("RESTRICTED", []):
            for k in keys_to_inspect:
                if fnmatch.fnmatch(k.lower(), pattern):
                    detected_features.append(f"field_pattern:{pattern}")
                    return ClassificationResult(
                        classification="RESTRICTED",
                        matched_rule="R_CREDENTIAL_TAINT_ESCALATION",
                        classification_reason=f"Detected high-sensitivity credential/secret pattern '{pattern}' in field '{k}'",
                        classification_latency_ms=latency,
                        confidence=1.0,
                        features_detected=tuple(detected_features)
                    )

        # -----------------------------------------------------------------
        # STAGE 2: Service Contract Catalog Evaluation
        # -----------------------------------------------------------------
        if req_type in self.service_mapping:
            tier = self.service_mapping[req_type]
            detected_features.append(f"service_catalog:{req_type}")
            return ClassificationResult(
                classification=tier,
                matched_rule="R_SERVICE_CATALOG_MAPPING",
                classification_reason=f"Direct lookup for service '{req_type}' in banking service catalog",
                classification_latency_ms=latency,
                confidence=1.0,
                features_detected=tuple(detected_features)
            )

        # -----------------------------------------------------------------
        # STAGE 3: Field Pattern Heuristics for Unmapped Schemas
        # -----------------------------------------------------------------
        for pattern in self.field_patterns.get("CONFIDENTIAL", []):
            for k in keys_to_inspect:
                if fnmatch.fnmatch(k.lower(), pattern):
                    detected_features.append(f"field_pattern:{pattern}")
                    return ClassificationResult(
                        classification="CONFIDENTIAL",
                        matched_rule="R_FINANCIAL_ACCOUNT_PATTERN",
                        classification_reason=f"Matched financial account pattern '{pattern}' in field '{k}'",
                        classification_latency_ms=latency,
                        confidence=0.98,
                        features_detected=tuple(detected_features)
                    )

        for pattern in self.field_patterns.get("INTERNAL", []):
            for k in keys_to_inspect:
                if fnmatch.fnmatch(k.lower(), pattern):
                    detected_features.append(f"field_pattern:{pattern}")
                    return ClassificationResult(
                        classification="INTERNAL",
                        matched_rule="R_OPERATIONAL_PATTERN",
                        classification_reason=f"Matched operational metadata pattern '{pattern}' in field '{k}'",
                        classification_latency_ms=latency,
                        confidence=0.95,
                        features_detected=tuple(detected_features)
                    )

        for pattern in self.field_patterns.get("PUBLIC", []):
            for k in keys_to_inspect:
                if fnmatch.fnmatch(k.lower(), pattern):
                    detected_features.append(f"field_pattern:{pattern}")
                    return ClassificationResult(
                        classification="PUBLIC",
                        matched_rule="R_PUBLIC_INFO_PATTERN",
                        classification_reason=f"Matched public inquiry pattern '{pattern}' in field '{k}'",
                        classification_latency_ms=latency,
                        confidence=0.95,
                        features_detected=tuple(detected_features)
                    )

        # Keyword heuristics
        for kw in self.keywords.get("RESTRICTED", []):
            if re.search(r"\b" + re.escape(kw) + r"\b", text_to_inspect):
                detected_features.append(f"keyword:{kw}")
                return ClassificationResult(
                    classification="RESTRICTED",
                    matched_rule="R_RESTRICTED_KEYWORD_MATCH",
                    classification_reason=f"Detected restricted keyword '{kw}'",
                    classification_latency_ms=latency,
                    confidence=0.95,
                    features_detected=tuple(detected_features)
                )

        for kw in self.keywords.get("CONFIDENTIAL", []):
            if re.search(r"\b" + re.escape(kw) + r"\b", text_to_inspect):
                detected_features.append(f"keyword:{kw}")
                return ClassificationResult(
                    classification="CONFIDENTIAL",
                    matched_rule="R_CONFIDENTIAL_KEYWORD_MATCH",
                    classification_reason=f"Detected confidential keyword '{kw}'",
                    classification_latency_ms=latency,
                    confidence=0.90,
                    features_detected=tuple(detected_features)
                )

        for kw in self.keywords.get("INTERNAL", []):
            if re.search(r"\b" + re.escape(kw) + r"\b", text_to_inspect):
                detected_features.append(f"keyword:{kw}")
                return ClassificationResult(
                    classification="INTERNAL",
                    matched_rule="R_INTERNAL_KEYWORD_MATCH",
                    classification_reason=f"Detected internal keyword '{kw}'",
                    classification_latency_ms=latency,
                    confidence=0.90,
                    features_detected=tuple(detected_features)
                )

        for kw in self.keywords.get("PUBLIC", []):
            if re.search(r"\b" + re.escape(kw) + r"\b", text_to_inspect):
                detected_features.append(f"keyword:{kw}")
                return ClassificationResult(
                    classification="PUBLIC",
                    matched_rule="R_PUBLIC_KEYWORD_MATCH",
                    classification_reason=f"Detected public keyword '{kw}'",
                    classification_latency_ms=latency,
                    confidence=0.90,
                    features_detected=tuple(detected_features)
                )

        # -----------------------------------------------------------------
        # STAGE 4: Zero-Trust Safe Fallback
        # -----------------------------------------------------------------
        return ClassificationResult(
            classification="RESTRICTED",
            matched_rule="R_SAFE_FALLBACK_DEFAULT",
            classification_reason="Unrecognized payload schema; applied zero-trust safe fallback to protected private tier",
            classification_latency_ms=latency,
            confidence=0.50,
            features_detected=("fallback:unrecognized",)
        )

    def classify_fields(self, field_dict: Dict[str, Any]) -> ClassificationResult:
        """Classifies an arbitrary dictionary of data fields."""
        pseudo_event = {
            "request_type": field_dict.get("service", field_dict.get("table", "generic")),
            "payload_size_bytes": len(json.dumps(field_dict)),
            **field_dict
        }
        return self.classify_request(pseudo_event)

    def get_ground_truth(self, request_event: Dict[str, Any]) -> str:
        """
        Determines the explicit deterministic ground-truth classification tier.
        In order of authority:
        1. Explicit 'classification_tier' in workload trace
        2. Configured 'service_classification_mapping'
        3. 'RESTRICTED' fallback
        """
        tier = request_event.get("classification_tier")
        if tier in ("RESTRICTED", "CONFIDENTIAL", "INTERNAL", "PUBLIC"):
            return tier

        svc = request_event.get("request_type")
        if svc in self.service_mapping:
            return self.service_mapping[svc]

        return "RESTRICTED"
