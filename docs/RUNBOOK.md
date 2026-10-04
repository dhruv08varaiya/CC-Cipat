# Practical Developer Runbook

A step-by-step operational guide for team members and evaluators to set up, configure, run, and inspect the banking simulation testbed.

---

## 1. Prerequisites
- **Operating System**: Windows, macOS, or Linux.
- **Python**: Version 3.10+ (Tested and verified on Python 3.14.6).
- **Git** (for version control).

---

## 2. Installation
Clone the repository and install the project dependencies in your environment:
```powershell
# Navigate to the workspace
cd "d:\Study\Sem 7\Cloud Computing (3170717)\Cipat"

# Install dependencies
python -m pip install -r requirements.txt
```

Verify installed packages:
```powershell
python -c "import simpy, matplotlib, pandas, numpy, cryptography; print('Environment verified!')"
```

---

## 3. Configuration Files
All environment parameters reside in `config/`:
- `config/simulation_config.json`: Infrastructure parameters (server counts, core capacities, latencies, queue limits).
- `config/workloads_config.json`: Formal definitions for workloads W1 to W6.
- `config/dataset_config.json`: Sizing presets (`small`, `medium`, `large`) and limits.
- `config/security_rules.json`: Classification tiers and service mappings.

---

## 4. Synthetic Dataset & Workload Generation
To generate the 8 synthetic banking datasets and W1–W6 workload event traces:
```powershell
# Standard profile: 10,000 customers, 10,000 accounts, 50,000 transactions, seed=42
python generate_data.py --profile medium

# Fast profile for quick test iterations:
python generate_data.py --profile small

# Custom sizing:
python generate_data.py --customers 5000 --transactions 25000 --seed 42
```
Outputs are written to:
- `data/synthetic/*.csv`
- `data/workloads/*.jsonl`
- `reports/dataset_statistics.md`

---

## 5. Running On-Premise Baseline Simulations
Execute the baseline simulation against pre-generated workload traces:
```powershell
# Normal Workload (W1, 5,000 requests)
python run_on_premise_sim.py --workload W1 --seed 42

# Peak Workload (W2, 10,000 requests)
python run_on_premise_sim.py --workload W2 --seed 42

# Extreme Workload (W3, 15,000 requests)
python run_on_premise_sim.py --workload W3 --seed 42

# Fast calibration run (e.g., 200 events)
python run_on_premise_sim.py --workload W1 --max-events 200
```

---

## 6. Running Hybrid Cloud Simulations (Stage 4)
Execute the hybrid-cloud dual-tier simulation (48 Private cores + 8 Public cores, deterministic routing):
```powershell
# Normal Workload (W1, 5,000 requests)
python run_hybrid_cloud_sim.py --workload W1 --seed 42

# Peak Workload (W2, 10,000 requests)
python run_hybrid_cloud_sim.py --workload W2 --seed 42

# Extreme Workload (W3, 15,000 requests)
python run_hybrid_cloud_sim.py --workload W3 --seed 42

# Fast calibration run (200 events)
python run_hybrid_cloud_sim.py --workload W1 --max-events 200
```

---

## 7. Running Comparative Validations (E1–E3)
Execute the automated fair comparison validator and report generator:
```powershell
# Normal Workload Comparison (E1)
python run_comparison.py --experiment E1

# Peak Workload Comparison (E2)
python run_comparison.py --experiment E2

# Extreme Workload Comparison (E3)
python run_comparison.py --experiment E3
```

---

## 8. Running Experiment E4 (Burst + Autoscaling)
Execute the complete end-to-end Experiment E4 comparing Fixed Hybrid against Autoscaling Hybrid under Workload W4:
```powershell
# Runs Fixed Hybrid vs Autoscaling Hybrid on W4 and generates 8 publication figures:
python run_e4_experiment.py --seed 42

# Running individual autoscaling simulation via hybrid runner:
python run_hybrid_cloud_sim.py --workload W4 --autoscaling --seed 42
```
Outputs are generated in:
- `results/raw/hybrid_fixed/W4/`
- `results/raw/hybrid_autoscaling/W4/`
- `results/processed/E4/comparison_summary.json` & `comparison_table.md`
- `results/figures/E4/*.png` (All 8 publication figures)

---

## 9. Running Experiment E7 (Security & Data Classification)
Execute the complete end-to-end Experiment E7 evaluating rule-based classification, secure compliance routing, access controls, cryptographic overhead, and audit logging:
```powershell
# Run Experiment E7 and generate all 8 publication figures:
python run_e7_experiment.py --seed 42
```
Outputs are generated in:
- `results/raw/security/audit_log.jsonl` (Comprehensive audit log)
- `results/raw/E7/e7_requests.jsonl` (Processed request telemetry)
- `results/raw/E7/security_events.jsonl` (Detected governance risk events)
- `results/processed/E7/e7_summary.json` & `e7_report.md`
- `results/figures/E7/*.png` (All 8 publication figures)

---

## 10. Running Tests
Run the entire automated test suite:
```powershell
python -m unittest discover tests
```
Individual test modules:
```powershell
# Project structure and config validation:
python -m unittest tests/test_project_structure.py

# Synthetic data referential integrity and reproducibility:
python -m unittest tests/test_synthetic_data.py

# On-premise discrete-event simulation engine & queue invariants:
python -m unittest tests/test_on_premise_sim.py

# Hybrid-cloud routing, queues, interconnect, and accounting invariants:
python -m unittest tests/test_hybrid_cloud_sim.py

# Public cloud horizontal autoscaling, load balancing & draining:
python -m unittest tests/test_autoscaling.py

# Security classification, Auth/MFA/RBAC, crypto overhead, and risk detection:
python -m unittest tests/test_security_module.py
```

---

## 11. Finding Results
Simulation outputs are structured in `results/`:
- `results/raw/on_premise/<workload>/`: On-premise baseline runs.
- `results/raw/hybrid_cloud/<workload>/`: Hybrid cloud baseline runs.
- `results/raw/hybrid_fixed/W4/`: Fixed hybrid run for Experiment E4.
- `results/raw/hybrid_autoscaling/W4/`: Elastic autoscaling run with `scaling_events.jsonl`.
- `results/raw/comparison/<experiment>/`: Comparative analyses for E1, E2, E3.
- `results/processed/E4/`: Processed summary statistics and Markdown table for E4.
- `results/figures/E4/`: 8 publication figures for Experiment E4.
- `results/raw/security/audit_log.jsonl`: Structured security audit trail.
- `results/raw/E7/`: E7 request-level telemetry and security events.
- `results/processed/E7/`: E7 executive summary and markdown report.
- `results/figures/E7/`: 8 publication figures for Experiment E7.

---

## 12. Troubleshooting
- **Error: `ModuleNotFoundError: No module named 'simpy'`**  
  *Fix*: Run `python -m pip install -r requirements.txt`.
- **Error: `Workload trace not found`**  
  *Fix*: Run `python generate_data.py --profile medium` to generate workload traces in `data/workloads/`.
- **Error: `Comparison validation failed`**  
  *Fix*: Ensure both On-Premise and Hybrid Cloud simulations have been executed on the same workload trace before running `run_comparison.py`.
- **Accounting Invariant Warning**  
  *Fix*: The simulation engine enforces $\text{Total} = \text{Completed} + \text{Dropped} + \text{Failed}$. If an error is thrown, check if a process terminated prematurely or an exception occurred in the discrete-event loop.

