from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
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
    """List completed experiments E1 through E8."""
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
            "id": "E5",
            "name": "Failure Resilience & Chaos Injection (W5)",
            "status": "COMPLETED",
            "description": "Evaluates fault tolerance under sudden 50% node outage, comparing On-Prem vs Hybrid."
        },
        {
            "id": "E6",
            "name": "Disaster Recovery & Node Restoration (W6)",
            "status": "COMPLETED",
            "description": "Measures quantitative MTTR and RTO recovery times during automated node restoration."
        },
        {
            "id": "E7",
            "name": "Security Classification & Compliance Benchmark",
            "status": "COMPLETED",
            "description": "Zero-trust 4-tier data classification, zero data leakage routing, MFA/RBAC evaluation."
        },
        {
            "id": "E8",
            "name": "Financial TCO Modeling & Cost-Performance Pareto",
            "status": "COMPLETED",
            "description": "3-Year TCO breakdown ($814K On-Prem vs $662K Hybrid, -18.7% savings) and Pareto frontier."
        }
    ]

@router.get("/summary/{exp_id}")
def get_experiment_summary(exp_id: str):
    """Fetch pre-computed or live summary JSON for experiment E1-E8."""
    exp_id = exp_id.upper()
    if exp_id in ("E1", "E2", "E3"):
        summary_file = COMPARISON_DIR / exp_id / "comparison_summary.json"
    elif exp_id in ("E4", "E5", "E6", "E7", "E8"):
        # Check either eX_summary.json or comparison_summary.json
        p_dir = PROCESSED_DIR / exp_id
        summary_file = p_dir / f"{exp_id.lower()}_summary.json"
        if not summary_file.exists():
            summary_file = p_dir / "comparison_summary.json"
    else:
        raise HTTPException(status_code=404, detail=f"Summary for experiment {exp_id} not found.")

    if not summary_file.exists():
        # Generate on the fly if not cached
        if exp_id == "E5":
            return SimRunnerService.run_e5_experiment()
        elif exp_id == "E6":
            return SimRunnerService.run_e6_experiment()
        elif exp_id == "E8":
            return SimRunnerService.run_e8_experiment()
        else:
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

@router.post("/e5/run")
def run_e5(req: ExperimentRequest):
    """Execute live E5 failure resilience experiment."""
    try:
        results = SimRunnerService.run_e5_experiment(seed=req.seed, max_events=req.max_events)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/e6/run")
def run_e6(req: ExperimentRequest):
    """Execute live E6 disaster recovery experiment."""
    try:
        results = SimRunnerService.run_e6_experiment(seed=req.seed, max_events=req.max_events)
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

@router.post("/e8/run")
def run_e8():
    """Execute E8 financial TCO and Pareto analysis."""
    try:
        results = SimRunnerService.run_e8_experiment()
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-all")
def run_all_benchmarks(req: ExperimentRequest):
    """Run all benchmarks E1 through E8 in unified pass."""
    try:
        results = SimRunnerService.run_all_benchmarks(seed=req.seed, event_limit=req.max_events)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
