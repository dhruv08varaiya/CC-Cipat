from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
from typing import Dict, Any, List
from src.security.data_classifier import DataClassifier

router = APIRouter()
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BACKEND_DIR / "config"

class ClassifyPayloadRequest(BaseModel):
    service_type: str
    payload: Dict[str, Any]

@router.get("/rules")
def get_security_rules():
    """Fetch 4-tier classification rules, RBAC matrix, and security policies."""
    rules_file = CONFIG_DIR / "security_rules.json"
    if rules_file.exists():
        with open(rules_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.get("/risk-register")
def get_risk_register():
    """Fetch security risk register definitions and scoring parameters."""
    risk_file = CONFIG_DIR / "security_risk_register.json"
    if risk_file.exists():
        with open(risk_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.post("/classify")
def classify_payload(req: ClassifyPayloadRequest):
    """Test the two-stage zero-trust data classifier on an arbitrary service payload."""
    rules_file = CONFIG_DIR / "security_rules.json"
    classifier = DataClassifier(rules_file)
    result = classifier.classify(req.service_type, req.payload)
    return {
        "service_type": req.service_type,
        "classification": result.classification.value,
        "decision_reason": result.decision_reason,
        "tainted_fields": result.tainted_fields,
        "confidence": result.confidence,
        "processing_time_ms": result.processing_time_ms,
        "target_datacenter": "PRIVATE" if result.classification.value in ("RESTRICTED", "CONFIDENTIAL") else "PUBLIC"
    }
