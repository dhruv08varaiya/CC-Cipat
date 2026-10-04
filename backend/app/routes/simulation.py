from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.sim_runner import SimRunnerService

router = APIRouter()

class SimulationRunRequest(BaseModel):
    architecture: str  # "on_premise", "hybrid_fixed", "hybrid_autoscaling"
    workload_id: str = "W1"
    seed: int = 42
    max_events: Optional[int] = 1000
    autoscaling_enabled: Optional[bool] = None

@router.get("/workloads")
def get_workloads():
    """List available workload profiles (W1–W6)."""
    return SimRunnerService.get_workloads_list()

@router.get("/config")
def get_config():
    """Get active infrastructure simulation config."""
    return SimRunnerService.get_simulation_config()

@router.post("/run")
def run_simulation(req: SimulationRunRequest):
    """Execute a discrete-event simulation run synchronously and return telemetry & summary metrics."""
    try:
        results = SimRunnerService.run_simulation(
            architecture=req.architecture,
            workload_id=req.workload_id,
            seed=req.seed,
            max_events=req.max_events,
            autoscaling_enabled=req.autoscaling_enabled
        )
        return {
            "status": "success",
            "architecture": req.architecture,
            "workload_id": req.workload_id,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
