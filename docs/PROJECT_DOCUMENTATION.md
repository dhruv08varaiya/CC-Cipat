# Comprehensive Technical Project Documentation

**Project Title**: Digital Banking System — Secure Hybrid Cloud Migration Simulation  
**Academic Context**: Final-Year Computer Engineering CIPAT Project (Academic Prototype & Simulation)  
**Authors**: Final-Year Project Team  
**Version**: 1.4.0  
**Current Milestone**: Stage 6 — Security & Data Classification Module (COMPLETE)  

---

## 1. Project Overview
This project simulates the transition of a commercial retail and corporate banking infrastructure from an existing static **On-Premise Datacenter** to a proposed **Secure Hybrid Cloud Architecture**. It provides quantitative, empirically reproducible experimental benchmarks comparing throughput, latency, queueing dynamics, resource utilization, failure recovery, compliance-aware routing, and cloud autoscaling.

> **CRITICAL ACADEMIC INTEGRITY NOTE**:
> This project is strictly an **ACADEMIC SIMULATION PROTOTYPE**. It does **NOT** interface with real banking systems, real customer accounts, financial payment gateways, or live banking APIs. All financial transactions, account profiles, and request traces are 100% synthetically generated. No experimental metrics or results are fabricated.

---

## 2. Problem Statement
The official research problem addressed:
> *"A bank wants to migrate from on-premise servers to the cloud while meeting security and compliance requirements. Recommend an appropriate cloud strategy."*

Financial institutions face conflicting pressures:
- Customer demand for 24/7 high-availability digital banking and sudden promotional burst scaling.
- Strict regulatory governance (PCI-DSS, RBI-CyberSecurity framework, GDPR) requiring zero leakage of sensitive customer financial records, core ledgers, and KYC data.
- Legacy on-premise datacenters suffer from hard capacity limits, provisioning delays, and single points of failure under peak load.

---

## 3. Objectives
1. Simulate the baseline performance, bottlenecks, and queuing behavior of a static on-premise banking datacenter under normal, peak, and extreme workloads.
2. Model a hybrid-cloud environment partitioning workloads across a protected Private Cloud tier and an elastic Public Cloud tier.
3. Quantify latency, throughput, and resource utilization using discrete-event queueing simulation.
4. Model automated data classification and compliance-enforced routing based on data sensitivity tiers.
5. Evaluate fault tolerance, node failure impacts, and disaster recovery restoration.
6. Generate verifiable comparison tables and graphical figures for the final CIPAT report, presentation, and viva.

---

## 4. Research Foundation & Literature Gap
The simulation design is grounded in six literature domains:
1. *Cloud adoption and implications in banking*
2. *Cloud computing and banking efficiency/risk*
3. *Sensitive financial data classification*
4. *Cloud outsourcing and vendor governance*
5. *Privacy/security assessment in financial cloud environments*
6. *Privacy-preserving cloud-based credit risk prediction*

**The Research Gap**: While existing literature addresses these concerns in isolation, our project integrates infrastructure queueing, data classification, and failure resilience into a single, cohesive, reproducible simulation testbed.

---

## 5. Proposed Architecture

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

---

## 6. Technology Stack
- **Language**: Python 3.10+ (Tested on Python 3.14.6)
- **Simulation Framework**: SimPy 4.1.2 (Process-based discrete-event queueing engine)
- **Data Engineering**: Pandas 3.0.6, NumPy 2.5.1
- **Visualization**: Matplotlib 3.11.2
- **Cryptography & Security**: PyCryptodome 3.20.0, Cryptography 42.0.5
- **Configuration & Traces**: Standard JSON (`config/`) and JSON Lines (`data/workloads/`)

---

## 7. Folder Structure
```
Cipat/
├── README.md                           # Main repository entrypoint & quick start
├── CHANGELOG.md                        # Milestone history & stage logs
├── requirements.txt                    # Python dependencies
├── generate_data.py                    # Root runner for synthetic data & workload generation
├── run_on_premise_sim.py               # Root runner for on-premise baseline simulation
├── config/
│   ├── simulation_config.json          # Hardware, network, and database capacities
│   ├── workloads_config.json           # W1–W6 formal profiles
│   ├── dataset_config.json             # Dataset sizing and profile presets
│   └── security_rules.json             # 4-tier data classification rules
├── data/
│   ├── synthetic/                      # Generated CSV banking datasets
│   └── workloads/                      # Generated W1–W6 JSONL request event streams
├── src/
│   ├── data_generator/                 # Synthetic data & workload generation logic
│   ├── simulation/                     # SimPy discrete-event simulation models
│   ├── security/                       # Data classification and encryption modules
│   ├── experiments/                    # Experiment runner harness
│   └── visualization/                  # Graph plotting & table generator
├── results/
│   └── raw/on_premise/                 # Raw simulation outputs (W1, W2, W3)
├── reports/                            # Generated validation reports and comparison tables
├── docs/                               # Comprehensive technical documentation & runbooks
└── tests/                              # Automated unit & regression test suite
```

---

## 8. Data Model
Stage 2 generated 8 synthetic operational tables (170,000 records total) with complete referential integrity:
1. `customers.csv` (10,000 records) — `customer_id` primary key, demographic data, KYC status, risk score, RESTRICTED.
2. `accounts.csv` (10,000 records) — `account_id` primary key, `customer_id` foreign key, balances, RESTRICTED.
3. `transactions.csv` (50,000 records) — `tx_id` primary key, `source_account_id` and `target_account_id` foreign keys, CONFIDENTIAL.
4. `login_events.csv` (15,000 records) — `event_id`, auth method, MFA flag, RESTRICTED.
5. `payment_requests.csv` (25,000 records) — `payment_id`, valid account/customer relationship, CONFIDENTIAL.
6. `risk_requests.csv` (5,000 records) — `request_id`, credit & fraud scores, CONFIDENTIAL.
7. `notifications.csv` (25,000 records) — `notification_id`, alerts, INTERNAL.
8. `audit_logs.csv` (30,000 records) — `log_id`, actor and resource audit trail, INTERNAL.

---

## 9. Simulation Model (Stage 3 Implementation)
The On-Premise Datacenter is modeled as an $M/G/c$ queueing system with finite queue capacity:
- **Server Resources**: $c = \text{server\_count} \times \text{cores\_per\_server} = 8 \times 8 = 64$ processing cores.
- **Database Resources**: Finite connection pool capacity = 64 concurrent database workers.
- **Queue Model**: FIFO finite waiting queue with `max_queue_depth = 5,000`. Requests arriving when queue is full are dropped with `QUEUE_OVERFLOW`.
- **Request Flow**: Inbound network hop ($2.5$ ms) $\to$ App Core contention $\to$ App execution ($15$ ms nominal + payload scaling) $\to$ DB access ($12$ ms nominal, if required) $\to$ Outbound network hop ($2.5$ ms) $\to$ Completion metrics.
- **Mathematical Processing Capacity**:
  $$\text{Nominal Core Capacity} = 25.0 \text{ RPS per core} \implies \text{Cluster Peak Capacity} = 64 \times 25.0 = 1,600 \text{ RPS}$$

---

## 10. Workload Model
Six deterministic, seed-based workload traces (`seed=42`) stored as JSON Lines in `data/workloads/`:
- **W1 (Normal)**: Baseline steady-state arrival (600 RPS, 5,000 events).
- **W2 (Peak)**: Daytime peak arrival (1,400 RPS, 10,000 events).
- **W3 (Extreme)**: Over-capacity stress test (2,600 RPS, 15,000 events).
- **W4 (Burst)**: Sudden traffic spike (600 $\to$ 2,800 RPS, 12,000 events).
- **W5 (Failure)**: Injected 50% node failure (1,200 RPS, 8,000 events).
- **W6 (Recovery)**: Failure followed by automated DR restoration (1,200 RPS, 10,000 events).

---

## 11. Security & Data Classification Model (Stage 6 Implementation)
The security architecture enforces fine-grained governance, policy-based routing, and access control across four regulatory sensitivity tiers:

### 11.1 Sensitivity Tiers
1. `RESTRICTED` (Level 4): PII, KYC records, authentication credentials, passwords, cryptographic keys, core ledger balances. Destination: `PRIVATE_CLOUD_ONLY`. Encryption: AES-256-GCM at rest + TLS 1.3 in transit.
2. `CONFIDENTIAL` (Level 3): Transaction records, loan applications, credit/risk evaluations, customer balances. Destination: `PRIVATE_CLOUD_PREFERRED`. Encryption: AES-256-CBC at rest + TLS 1.3 in transit.
3. `INTERNAL` (Level 2): Non-PII operational logs, aggregated branch volume, batch reports, system health metrics. Destination: `HYBRID_ALLOW_PUBLIC`. Encryption: TLS 1.3 in transit.
4. `PUBLIC` (Level 1): Publicly accessible info (forex rates, branch locations, interest rate FAQs). Destination: `PUBLIC_CLOUD_PRIMARY`. Encryption: TLS 1.3 in transit.

### 11.2 Core Security Subsystems
- **Two-Stage Rule-Based Data Classifier (`DataClassifier`)**:
  - *Stage 1*: Deep-payload taint scanning for secret credentials (`*password*`, `*secret*`, `*token*`, `*kyc*`). Escalate immediately to `RESTRICTED`.
  - *Stage 2*: Service catalog contract lookup and schema field-pattern analysis.
  - *Zero-Trust Safe Fallback*: Unrecognized payloads default to `RESTRICTED` and route to the Private Cloud.
  - Achieved **99.49% classification accuracy** and **0.9962 Macro F1** with $0.38$ ms inspection latency.
- **Access Control & Identity (`Authenticator`, `MFACoordinator`, `RBACAuthorizer`)**:
  - Evaluates user sessions, simulated token verification (98.90% success).
  - Enforces mandatory multi-factor authentication for high-impact operations (`fund_transfer`, `kyc_verification`, `loan_application`) (96.35% pass rate).
  - Enforces four-tier banking role matrix (`CUSTOMER`, `BANK_OPERATOR`, `SECURITY_AUDITOR`, `ADMIN`) (98.41% authorization rate).
- **Cryptographic Abstraction (`EncryptionManager`)**:
  - Simulates computational overhead for Data-at-Rest (`AES-256-GCM`, $0.8$ ms) and Data-in-Transit (`TLS 1.3`, $0.4$ ms). Mean cryptographic overhead: $0.975$ ms per request.
- **Security Event & Violation Detection (`SecurityViolationDetector`)**:
  - Tracks simulation governance risks R1–R6. Intercepts 100% of attempted sensitive-to-public routing probes (R2).
- **Immutable Audit Logging (`SecurityAuditLogger`)**:
  - Structured JSON Lines audit log (`results/raw/security/audit_log.jsonl`).
- **Security Risk Register (`RiskRegister`)**:
  - Formally documents 6 cloud governance risks (R1–R6) with mathematical scoring ($\text{Risk Score} = \text{Likelihood} \times \text{Impact}$).

> **ACADEMIC DISCLAIMER**: Stage 6 security mechanisms are simulation abstractions for academic evaluation and are not production banking security controls.


---

## 12. Experiment Methodology
Every experiment:
1. Takes pre-generated workload traces (no on-the-fly random generation).
2. Executes through the discrete-event engine using fixed seeds.
3. Automatically validates accounting invariants:
   $$\text{Total Requests} = \text{Completed Requests} + \text{Dropped Requests} + \text{Failed Requests}$$
4. Exports machine-readable raw event logs (`raw_requests.jsonl`), periodic time-series metrics (`time_series.csv`), configuration snapshot (`config_snapshot.json`), and summary statistics (`summary_metrics.json`).

---

## 13. Metrics Definitions & Formulas
1. **Total Requests ($N_{\text{total}}$)**: Total arrival events received.
2. **Completed Requests ($N_{\text{comp}}$)**: Requests successfully served to completion.
3. **Dropped Requests ($N_{\text{drop}}$)**: Requests rejected due to queue overflow.
4. **Availability**:
   $$\text{Availability} = \frac{N_{\text{comp}}}{N_{\text{total}}} \times 100\%$$
5. **Throughput**:
   $$\text{Throughput} = \frac{N_{\text{comp}}}{T_{\text{simulation\_elapsed}}}$$
6. **Response Time ($T_{\text{resp}}$)**: $T_{\text{completion}} - T_{\text{arrival}}$ (tracked via mean, median, P95, P99).
7. **Waiting Time ($T_{\text{wait}}$)**: Time spent in queue before core allocation.
8. **Service Time ($T_{\text{serv}}$)**: Time spent actively computing and querying database.
9. **Time-Weighted Server Utilization**:
   $$\text{Server Utilization} = \frac{\sum T_{\text{serv}}}{c \times T_{\text{simulation\_elapsed}}} \times 100\%$$
10. **Time-Weighted Database Utilization**:
    $$\text{DB Utilization} = \frac{\sum T_{\text{db\_query}}}{\text{DB\_Capacity} \times T_{\text{simulation\_elapsed}}} \times 100\%$$

---

## 14. Empirical Results (Stages 3, 4 & 5 Executed)

### Baseline On-Premise vs Fixed Hybrid Cloud (E1, E2, E3)

| Workload / Experiment | Architecture | Throughput (RPS) | Avg Latency | P95 Latency | Server Util | DB Util | Max Queue | Availability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **W1 (E1: Normal, 600 RPS)** | On-Premise (64 cores) | 589.37 | 29.72 ms | 39.81 ms | 25.07% | 7.95% | 2 | 100.00% |
| | **Hybrid Cloud (48+8 cores)** | **589.37** | **27.55 ms** | **35.03 ms** | **23.64%** | **7.95%** | **1** | **100.00%** |
| | *Delta / Shift* | *0.00%* | *-7.30%* | *-12.01%* | *-1.43%* | *0.00%* | *-1* | *0.00%* |
| **W2 (E2: Peak, 1,400 RPS)** | On-Premise (64 cores) | 1,381.93 | 29.55 ms | 39.58 ms | 58.41% | 18.57% | 4 | 100.00% |
| | **Hybrid Cloud (48+8 cores)** | **1,381.93** | **27.50 ms** | **35.33 ms** | **55.06%** | **18.57%** | **2** | **100.00%** |
| | *Delta / Shift* | *0.00%* | *-6.94%* | *-10.74%* | *-3.35%* | *0.00%* | *-2* | *0.00%* |
| **W3 (E3: Extreme, 2,600 RPS)** | On-Premise (64 cores) | 2,547.84 | 36.46 ms | 57.48 ms | 100.00% | 33.93% | 24 | 100.00% |
| | **Hybrid Cloud (48+8 cores)** | **2,467.50** | **181.09 ms** | **912.10 ms** | **76.71%** | **33.93%** | **560** | **100.00%** |
| | *Delta / Shift* | *-3.15%* | *+396.68%* | *+1486.81%* | *-23.29%* | *0.00%* | *+536* | *0.00%* |

### Experiment E4: Fixed Hybrid vs Autoscaling Hybrid (Burst Workload W4)

| Metric | Hybrid Fixed (No Autoscaling) | Hybrid Autoscaling (Elastic) | Delta (Absolute) | Shift (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Throughput (RPS)** | 1,226.34 | 1,322.28 | +95.94 | +7.82% |
| **Average Response Time** | 101.13 ms | 61.38 ms | -39.75 ms | -39.31% |
| **Median Response Time** | 27.60 ms | 27.57 ms | -0.03 ms | -0.11% |
| **P95 Response Time** | 555.02 ms | 343.10 ms | -211.92 ms | -38.18% |
| **P99 Response Time** | 698.39 ms | 500.21 ms | -198.18 ms | -28.38% |
| **Public Tier Avg Latency** | 297.40 ms | 153.91 ms | -143.49 ms | -48.25% |
| **Average Queue Length** | 85.00 | 30.29 | -54.71 | -64.36% |
| **Maximum Queue Length** | 435 | 234 | -201 | -46.21% |
| **Average Resource Utilization** | 49.02% | 52.85% | +3.83% | +7.81% |

### Experiment E7: Sensitive Data Classification & Secure Routing (Stage 6)

| Metric Category | Performance Metric | Measured Empirical Value | Target / Requirement |
| :--- | :--- | :--- | :--- |
| **Classification Accuracy** | Overall Accuracy | **99.49%** | $\ge 95.0\%$ |
| | Macro Precision / Recall / F1 | **0.9951 / 0.9973 / 0.9962** | $\ge 0.95$ |
| | RESTRICTED Class F1 Score | **0.9902** (100% recall, 0 false negatives) | Zero leakage |
| | CONFIDENTIAL Class F1 Score | **0.9945** (1.000 precision, 2,363 TP) | High precision |
| | INTERNAL & PUBLIC Class F1 | **1.0000 & 1.0000** | Perfect separation |
| | Mean Classification Latency | **0.377 ms** | $\le 1.0$ ms |
| **Secure Compliance Routing** | Total Requests Evaluated | **5,100** (5,000 W1 baseline + 100 probe requests) | Full trace |
| | Routed to Private Tier | **3,699** (72.53%) | Sensitive containment |
| | Routed to Public Elastic Tier | **1,401** (27.47%) | Non-sensitive offload |
| | Injected Violation Probes Attempted | **25 probes** (attempting public breach) | Active probing |
| | Injected Violation Probes Intercepted | **25 probes (100.0% blocked & re-routed)** | 100% interception |
| | Undetected Sensitive Leakage Events | **0 (Zero Tolerance Maintained)** | Exactly 0 |
| **Access Control & Identity** | Authentication Success Rate | **98.90%** (5,044 allowed, 56 rejected) | Realistic telemetry |
| | MFA Step-up Success Rate | **96.35%** (1,400 passed, 53 rejected) | Sensitive operations |
| | RBAC Authorization Success Rate | **98.41%** (5,019 allowed, 81 denied) | 4-tier matrix |
| **Cryptographic Abstraction** | Mean Crypto Overhead per Request | **0.975 ms** (AES-256 + TLS 1.3 models) | Calibrated model |
| | At-Rest Encrypted Records | **3,679** (RESTRICTED + CONFIDENTIAL) | Storage protection |
| | In-Transit Encrypted Records | **5,079** (TLS 1.3 across hybrid boundary) | Channel protection |
| | Total Security Violations Detected | **190 events** (R1: 134, R2: 25, R4: 21, R6: 10) | JSON Lines audit log |

### Key Experimental Insights
1. **Normal & Peak Offloading (E1 & E2)**: Offloading 28% of non-sensitive queries to the public tier reduced overall average latency by 7.3% and P95 latency by 12.0%, avoiding private core contention.
2. **Fixed Public Tier Bottleneck under Extreme Load (E3)**: Because Stage 4 deliberately uses a fixed public capacity (8 cores) with **NO AUTOSCALING YET**, the public tier queue surged to 560 requests under 2,600 RPS, causing public average latency to spike to 572.49 ms. Meanwhile, the protected private core tier remained shielded and stable (72.83% utilization, 25.63 ms latency).
3. **Autoscaling Queue Collapse & Latency Mitigation (E4)**: Under the W4 promotional burst (600 $\to$ 2,800 RPS), horizontal elasticity cut average queue length by **64.36%** and reduced public service latency by **48.25%**, confirming that dynamic autoscaling successfully absorbs traffic spikes without manual operator intervention.
4. **Data Classification Precision & Zero-Leakage Routing (E7)**: The two-stage automated classifier separated synthetic banking workloads with **99.49% accuracy** and 0.38 ms overhead. Crucially, all 25 intentionally corrupted violation probes attempting to route sensitive data to the public cloud were **100% intercepted**, achieving **zero undetected sensitive data leaks** to external cloud infrastructure.
5. **Defense-in-Depth Layering (E7)**: Enforcing simulated MFA on sensitive banking endpoints intercepted 53 unauthorized transactional attempts, while RBAC authorization policies prevented 81 role-escalation violations without impacting legitimate customer transactions.

---

## 15. Limitations
1. **Simulation Abstraction**: Interconnect, gateway, and VM provisioning delays are mathematical models calibrated from literature benchmarks, not live cloud hypervisors.
2. **Security & Cryptographic Abstractions**: Stage 6 security mechanisms (data classifier, auth tokens, MFA challenges, RBAC checks, cryptographic latency) are transparent simulation abstractions designed for academic evaluation. They do not claim live PCI-DSS/SOC2 certification, real hardware HSM/KMS integration, or full homomorphic encryption.
3. **Rule-Based Classification**: Classification uses a deterministic two-stage rule engine rather than deep neural network models (e.g., PPDNN-CRP or UP-SDCG), prioritizing full explainability and reproducible testing.
4. **Risk Scoring Simplification**: The security risk register utilizes a standard $5 \times 5$ matrix ($\text{Likelihood} \times \text{Impact}$), not complex FAHP + Dempster-Shafer evidential reasoning.
5. **Load Balancing Granularity**: Round Robin distributes requests evenly across active instances; advanced predictive or reinforcement-learning load balancers are out of scope.

---

## 16. Roadmap (Stages 6–10)
- **Stage 1**: Complete Project Structure (COMPLETE)
- **Stage 2**: Synthetic Banking Dataset & Workload Traces (COMPLETE)
- **Stage 3**: On-Premise Baseline Simulation (COMPLETE)
- **Stage 4**: Hybrid Cloud Simulation — Fixed Partition Baseline (COMPLETE)
- **Stage 5**: Dynamic Load Balancing & Elastic Autoscaling (COMPLETE)
- **Stage 6**: Advanced Data Classification & Security Enforcement (COMPLETE)
- **Stage 7**: Failure, Chaos Injection & Automated Disaster Recovery (NEXT)
- **Stage 8**: End-to-End Comparative Evaluation (E1–E8)
- **Stage 9**: Visualizations, Charts & Statistical Analysis
- **Stage 10**: Final Academic Documentation, CIPAT Report & Presentation Deck

