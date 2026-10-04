# Digital Banking System — Secure Hybrid Cloud Migration Simulation

Final-Year Computer Engineering CIPAT Project (Academic Prototype & Simulation).

---

## 1. Project Overview

This project simulates the transition of a commercial banking infrastructure from a legacy **On-Premise Datacenter** to a **Secure Hybrid Cloud Architecture**. It provides quantitative, reproducible experimental results comparing latency, throughput, resource utilization, failure recovery, data classification compliance, and autoscaling elasticity under varied banking workloads.

> **CRITICAL ACADEMIC NOTE**:
> This is strictly an **ACADEMIC SIMULATION / PROTOTYPE**. It does **NOT** interface with real banking systems, real customer accounts, financial payment gateways, or live banking APIs. All financial transactions, account profiles, and request traces are 100% synthetically generated.

---

## 2. New Developer Quick Start

| Question | Answer |
| :--- | :--- |
| **1. What is this project?** | An academic discrete-event simulation evaluating a bank's migration from static on-premise infrastructure to a secure hybrid cloud. |
| **2. What problem does it solve?** | Quantifies performance, security, and cost trade-offs when migrating sensitive core banking vs elastic burstable workloads. |
| **3. What technology does it use?** | Python 3, SimPy 4.1.2 (discrete-event queueing engine), Pandas, NumPy, Matplotlib, PyCryptodome. |
| **4. Where is the main code?** | [`src/simulation/`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/src/simulation/) (simulation engine) and [`src/data_generator/`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/src/data_generator/) (synthetic data generator). |
| **5. Where is the configuration?** | [`config/simulation_config.json`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/config/simulation_config.json) and [`config/workloads_config.json`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/config/workloads_config.json). |
| **6. Where is the synthetic data?** | [`data/synthetic/`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/data/synthetic/) (8 CSV tables) and [`data/workloads/`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/data/workloads/) (W1–W6 JSONL streams). |
| **7. How do I run the tests?** | Run `python -m unittest discover tests`. |
| **8. How do I generate data?** | Run `python generate_data.py --profile medium`. |
| **9. How do I run the simulation?** | Run `python run_on_premise_sim.py --workload W1 --seed 42`. |
| **10. Where are the results?** | [`results/raw/on_premise/`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/results/raw/on_premise/), [`results/raw/hybrid_cloud/`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/results/raw/hybrid_cloud/), [`results/raw/comparison/`](file:///d:/Study/Sem%207/Cloud%20Computing%20%283170717%29/Cipat/results/raw/comparison/). |
| **11. What stage are we currently on?** | **Stage 6: Security & Data-Classification Module (COMPLETE)**. |
| **12. What should I work on next?** | **Stage 7: Failure, Chaos Injection & Disaster Recovery (E5/E6)** (NOT STARTED). |

---

## 3. Conceptual Architecture

```
                    USERS / CLIENT APPS
                            │
                    [ Security / WAF ]
                            │
                   [ Load Balancer ]
                            │
                [ Banking Applications ]
                            │
             [ Data Classification Engine ]
                     /             \
                    /               \
       PRIVATE CLOUD                 PUBLIC CLOUD
       (Protected Zone)              (Elastic Zone)
       ────────────────              ──────────────
       • Core Banking Data           • Elastic Microservices
       • Accounts & Ledgers          • Public FAQs & Locators
       • KYC Verification            • Non-PII Batch Analytics
       • Restricted Services         • Burst Workloads
              │                             │
              └──────────────┬──────────────┘
                             │
              [ Encrypted Interconnect ]
```

Surrounding controls:
- **IAM & Access Controls**: Role-based access control (RBAC).
- **Data Classification**: Automated routing based on 4 data tiers (`RESTRICTED`, `CONFIDENTIAL`, `INTERNAL`, `PUBLIC`).
- **Cryptographic Protection**: AES-256 for protected storage and TLS 1.3 in-transit simulation overhead.
- **Resilience & Governance**: Automated failure detection, health checks, failover, and audit trail logging.

---

## 3. Workload Profiles

- **W1 (Normal)**: 600 RPS steady-state transaction volume.
- **W2 (Peak)**: 1,400 RPS daily peak traffic.
- **W3 (Extreme)**: 2,600 RPS volume exceeding static on-premise capacity.
- **W4 (Burst)**: Sudden traffic spike (2,800 RPS) simulating promotional/payroll events.
- **W5 (Failure)**: Unexpected server failure (50% node drop) mid-run.
- **W6 (Recovery)**: Server fault followed by automated health checks and replica failover.

---

## 4. Planned Experiments

- **E1**: Normal Workload (On-Premise vs Hybrid Cloud)
- **E2**: Peak Workload (On-Premise vs Hybrid Cloud)
- **E3**: Extreme Workload (On-Premise Bottlenecks vs Elastic Scaling)
- **E4**: Burst Workload + Autoscaling Dynamics
- **E5**: Application Server Failure Resilience
- **E6**: Backup, Failover & Disaster Recovery (RTO/RPO)
- **E7**: Sensitive Data Classification & Compliant Routing
- **E8**: (Optional) Privacy-Preserving Analytics Overhead

---

## 5. Directory Structure

```
Cipat/
├── README.md                           # Project documentation
├── CHANGELOG.md                        # Version history & stage milestones
├── requirements.txt                    # Python dependencies
├── config/                             # Simulation, workload, and security configurations
│   ├── simulation_config.json
│   ├── workloads_config.json
│   ├── security_rules.json
│   └── security_risk_register.json
├── data/
│   ├── synthetic/                      # Synthetic accounts and transactions
│   └── workloads/                      # Generated workload traces (W1-W6)
├── src/
│   ├── data_generator/                 # Synthetic banking data & workload generator
│   ├── simulation/                     # Discrete-event simulation engines
│   ├── security/                       # Security & data-classification modules
│   ├── experiments/                    # Experiment runner harness (E1-E8)
│   └── visualization/                  # Graph plotting & table generator
├── results/
│   ├── raw/                            # Raw simulation telemetry
│   ├── processed/                      # Summary metrics (mean, p95, utilization)
│   └── figures/                        # Generated figures for CIPAT report & PPT
├── reports/                            # Comparison tables & text summaries
└── tests/                              # Unit & integration test suite
```

---

## 6. Setup & Verification

### Prerequisites
- Python 3.10+ (Tested on Python 3.14.6)
- Dependencies installed via `pip`:
  ```powershell
  python -m pip install -r requirements.txt
  ```

### Verify Project Structure
```powershell
python -m unittest tests/test_project_structure.py
```

### 7. Synthetic Data & Workload Generation (Stage 2)
Generate privacy-safe banking datasets and W1-W6 workload traces:
```powershell
# Default generation (10,000 customers, 10,000 accounts, 50,000 transactions, seed=42)
python generate_data.py --profile medium

# Fast testing profile (1,000 customers, 1,000 accounts, 10,000 transactions)
python generate_data.py --profile small

# Custom sizing
python generate_data.py --customers 5000 --transactions 25000 --seed 42
```

### 8. Run On-Premise Baseline Simulations (Stage 3)
Run baseline simulations against generated workload traces:
```powershell
# Normal Workload (W1, 5,000 requests)
python run_on_premise_sim.py --workload W1 --seed 42

# Peak Workload (W2, 10,000 requests)
python run_on_premise_sim.py --workload W2 --seed 42

# Extreme Workload (W3, 15,000 requests)
python run_on_premise_sim.py --workload W3 --seed 42

# Calibration test (200 requests)
python run_on_premise_sim.py --workload W1 --max-events 200
```

### 9. Run Hybrid Cloud Simulations (Stage 4)
Run hybrid cloud simulations (48 Private cores + 8 Public cores, deterministic routing):
```powershell
# Normal Workload (W1, 5,000 requests)
python run_hybrid_cloud_sim.py --workload W1 --seed 42

# Peak Workload (W2, 10,000 requests)
python run_hybrid_cloud_sim.py --workload W2 --seed 42

# Extreme Workload (W3, 15,000 requests)
python run_hybrid_cloud_sim.py --workload W3 --seed 42
```

### 10. Run Fair Comparative Validations (E1–E3)
Compare On-Premise baseline against Hybrid Cloud:
```powershell
# Normal Workload Comparison (E1)
python run_comparison.py --experiment E1

# Peak Workload Comparison (E2)
python run_comparison.py --experiment E2

# Extreme Workload Comparison (E3)
python run_comparison.py --experiment E3
```

### 11. Run Experiment E4 (Burst Workload + Autoscaling Dynamics)
Execute the comparative benchmark between Fixed Hybrid and Autoscaling Hybrid under Workload W4:
```powershell
# Run both Fixed and Autoscaling architectures and generate all 8 publication figures:
python run_e4_experiment.py --seed 42

# Run standalone autoscaling simulation on W4:
python run_hybrid_cloud_sim.py --workload W4 --autoscaling --seed 42
```

### 12. Run Experiment E7 (Sensitive Data Classification & Secure Routing)
Execute the Stage 6 security governance benchmark evaluating automated classification, RBAC, MFA, cryptographic overhead, and policy violation detection:
```powershell
# Run Experiment E7 and generate all 8 publication figures:
python run_e7_experiment.py --seed 42
```

### 13. Run All Automated Tests
```powershell
python -m unittest discover tests
```


