import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure backend root and src directory are in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "src"))

from app.routes import simulation, experiments, datasets, security

app = FastAPI(
    title="CC-CIPAT Simulation API",
    description="Backend API for Secure Hybrid Cloud Migration Discrete-Event Simulation",
    version="2.0.0",
)

# Configure CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["Experiments"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])

# Serve generated results figures if directory exists
figures_dir = BACKEND_DIR / "results" / "figures"
if figures_dir.exists():
    app.mount("/static/figures", StaticFiles(directory=str(figures_dir)), name="figures")

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "CC-CIPAT Simulation Engine API",
        "version": "2.0.0",
        "docs_url": "/docs",
    }

@app.get("/api/health")
def health():
    return {"status": "healthy", "engine": "SimPy 4.1.2"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
