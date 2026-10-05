# Practical Developer Runbook

An operational guide for developers, researchers, and evaluators to configure, execute, inspect, and benchmark the CC-CIPAT simulation testbed and web telemetry terminal.

---

## 1. Environment Setup & Prerequisites

- **Python**: Version 3.10+ (with virtual environment support)
- **Node.js**: Version 18+ (with npm)
- **Operating System**: Windows, macOS, or Linux

### Step 1: Backend Setup
```powershell
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Frontend Setup
```powershell
cd ../frontend
npm install
```

---

## 2. Launching Services

### Backend REST API Server (FastAPI + Uvicorn)
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/api/health`

### Frontend Web Dashboard (React 18 + Vite)
```powershell
cd frontend
npm run dev
```
- Web Application: `http://localhost:5173`
- Production Build Check: `npm run build`

---

## 3. Dataset & Workload Generation

To re-generate the 8 synthetic banking datasets (170k rows) and W1–W6 workload traces:
```powershell
cd backend

# Medium profile: 10k customers, 10k accounts, 50k transactions, seed=42
python -m src.data_generator.generate_data --profile medium

# Fast profile for quick test iterations:
python -m src.data_generator.generate_data --profile small
```
Generated artifacts:
- `data/synthetic/*.csv` (8 relational tables)
- `data/workloads/*.jsonl` (W1 through W6 traces)
- `reports/dataset_statistics.md` (Dataset statistics)

---

## 4. Running Experiments from CLI

### Run On-Premise Baseline
```powershell
python -m src.experiments.comparison --architecture on_premise --workload W1
```

### Run Hybrid Cloud Autoscaling (E4 Burst Benchmark)
```powershell
python -m src.experiments.e4_burst_autoscaling --seed 42
```

### Run Zero-Trust Security Classifier (E7 Benchmark)
```powershell
python -m src.experiments.e7_security_classification --seed 42
```

### Run All Benchmarks (E1–E8 Suite)
```powershell
python -m src.experiments.comparison --run-all
```

---

## 5. Automated Test Suite

Run the full backend test suite:
```powershell
cd backend
pytest tests/ -v
```

Execute specific test modules:
```powershell
# Project structure & config validation
pytest tests/test_project_structure.py -v

# Synthetic dataset referential integrity
pytest tests/test_synthetic_data.py -v

# On-premise discrete simulation invariants
pytest tests/test_on_premise_sim.py -v

# Hybrid cloud compliance routing & interconnect
pytest tests/test_hybrid_cloud_sim.py -v

# Autoscaling controller & load balancer
pytest tests/test_autoscaling.py -v

# Zero-trust classifier, RBAC, and crypto models
pytest tests/test_security_module.py -v
```

---

## 6. Telemetry & Results Artifacts

Simulation results and verification reports are stored in `results/`:
- `results/raw/on_premise/`: On-premise baseline runs.
- `results/raw/hybrid_cloud/`: Hybrid cloud baseline runs.
- `results/raw/hybrid_autoscaling/W4/`: Elastic autoscaling telemetry and scaling events.
- `results/raw/security/audit_log.jsonl`: Structured JSON Lines security audit trail.
- `results/processed/E4/`: E4 autoscaling comparison summary and table.
- `results/processed/E7/`: E7 classification metrics and risk events.
- `results/figures/E4/`: 8 publication figures for autoscaling burst dynamics.
- `results/figures/E7/`: 8 publication figures for zero-trust security validation.

---

## 7. Troubleshooting

- **Error: `ModuleNotFoundError: No module named 'simpy'`**  
  *Fix*: Ensure virtual environment is activated, then run `pip install -r requirements.txt`.
- **Error: `Port 8000 already in use`**  
  *Fix*: Kill existing uvicorn process or specify another port (`--port 8001`).
- **Error: `Vite proxy ECONNREFUSED`**  
  *Fix*: Ensure FastAPI backend is running on `http://localhost:8000` before accessing API-connected frontend tabs.
- **Accounting Invariant Warning**  
  *Fix*: SimPy simulation enforces $\text{Total} = \text{Completed} + \text{Dropped} + \text{Failed}$. If an error is thrown, inspect `raw_requests.jsonl` to ensure all event lifecycles terminated cleanly.
