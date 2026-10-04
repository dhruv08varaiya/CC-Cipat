from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pathlib import Path
import json
from app.services.sim_runner import SimRunnerService

router = APIRouter()
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BACKEND_DIR / "results" / "processed"
COMPARISON_DIR = BACKEND_DIR / "results" / "raw" / "comparison"

class ExperimentRequest(BaseModel):
    seed: int = 42
    max_events: Optional[int] = 2000

@router.get("/list")
def list_experiments():
    """List completed and planned experiments with summaries."""
    return [
        {
            "id": "E1",
            "name": "Normal Load Baseline (W1 - 600 RPS)",
            "status": "COMPLETED",
            "description": "Baseline comparison of On-Premise vs Fixed Hybrid Cloud at 600 RPS steady state."
        },
        {
            "id": "E2",
            "name": "Peak Load Behavior (W2 - 1400 RPS)",
            "status": "COMPLETED",
            "description": "Stress testing under peak business conditions where public tier reaches 100% utilization."
        },
        {
            "id": "E3",
            "name": "Extreme Load / Saturation (W3 - 2600 RPS)",
            "status": "COMPLETED",
            "description": "Extreme stress testing proving necessity of autoscaling mechanism."
        },
        {
            "id": "E4",
            "name": "Promotional Burst & Autoscaling (W4 - 600→2800 RPS)",
            "status": "COMPLETED",
            "description": "Evaluates horizontal autoscaler elastic response, latency recovery, and queue dampening."
        },
        {
            "id": "E7",
            "name": "Security Classification & Compliance Benchmark",
            "status": "COMPLETED",
            "description": "Zero-trust 4-tier data classification, zero data leakage routing, MFA/RBAC evaluation."
        },
        {
            "id": "E5",
            "name": "Failure Resilience & Chaos Injection (W5)",
            "status": "PLANNED",
            "description": "Stage 7: 50% node drop failure tolerance and queue stability."
        },
        {
            "id": "E6",
            "name": "Disaster Recovery & Node Restoration (W6)",
            "status": "PLANNED",
            "description": "Stage 7: MTTR and automated replica failover."
        }
    ]

@router.get("/summary/{exp_id}")
def get_experiment_summary(exp_id: str):
    """Fetch pre-computed summary JSON for experiment E1-E4, E7."""
    exp_id = exp_id.upper()
    if exp_id in ("E1", "E2", "E3"):
        summary_file = COMPARISON_DIR / exp_id / "comparison_summary.json"
    elif exp_id == "E4":
        summary_file = PROCESSED_DIR / "E4" / "comparison_summary.json"
    elif exp_id == "E7":
        summary_file = PROCESSED_DIR / "E7" / "e7_summary.json"
    else:
        raise HTTPException(status_code=404, detail=f"Summary for experiment {exp_id} not found.")

    if not summary_file.exists():
        raise HTTPException(status_code=404, detail=f"Summary file not found: {summary_file}")

    with open(summary_file, "r", encoding="utf-8") as f:
        return json.load(f)

@router.post("/e4/run")
def run_e4(req: ExperimentRequest):
    """Execute live E4 burst autoscaling experiment."""
    try:
        results = SimRunnerService.run_e4_experiment(seed=req.seed, max_events=req.max_events)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/e7/run")
def run_e7(req: ExperimentRequest):
    """Execute live E7 security classification benchmark."""
    try:
        results = SimRunnerService.run_e7_experiment(seed=req.seed, max_events=req.max_events)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
