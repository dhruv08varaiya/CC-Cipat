# Changelog

All notable changes to the **Digital Banking System — Secure Hybrid Cloud Migration Simulation** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Stage 10: Living Digital Twin & Industrial Monochrome Telemetry UI] - 2026-10-05

### Added
- **Industrial Monochrome Design System**:
  - Implemented high-density dark-mode design system (`#090A0F` canvas, `#12131A` card surfaces, `#27272A` structural borders) inspired by Linear and Vercel.
  - Replaced all puffy nested cards, AI-slop glowing gradients, and cartoon HUD badges with crisp 1px borders, tabular monospace typography, and purposeful semantic indicators.
- **Living Digital Twin Console (`components/digital_twin/`)**:
  - `DigitalTwinControls.tsx`: 36px unified flat toolbar integrating scenario presets (`Normal 600 RPS`, `Peak 1400 RPS`, `Flash Burst 2800 RPS`), continuous rate slider with numeric badge (`[ 600 RPS ]`), speed multipliers (`0.5x`, `1x`, `2x`), play/pause controls, and popover chaos fault injection menu.
  - `DigitalTwinTopology.tsx`: Real interactive SVG service mesh topology rendering directed Bézier curves between `Ingress Gateway` $\rightarrow$ `4-Tier Security Classifier` $\rightarrow$ `Hybrid Router` $\rightarrow$ `Private DC & Public Cloud`, displaying live animated packet particles, real path latency metrics (`0.4ms`, `14.2ms`), and CPU saturation meters.
  - `DigitalTwinOscilloscope.tsx`: High-contrast Recharts time-series waveform on `#090A0F` with prominent orange SLA 30ms threshold guidelines.
  - `DigitalTwinLedger.tsx`: High-density live streaming transaction event ledger with monospace right-aligned numbers and status badges (`COMPLETED`, `BLOCKED`, `DROPPED`).
  - `AcademicSnapshotModal.tsx`: IEEE LaTeX and raw CSV telemetry export modal with syntax styling and one-click clipboard copying.
- **Distributed 8-Layer Transaction Trace Inspector (`components/LifecycleInspectorTab.tsx`)**:
  - Interactive Gantt span waterfall visualizing execution timing across 8 simulation phases (`Ingestion & Taint`, `4-Tier Classifier`, `Auth/RBAC`, `Hybrid Router`, `Network Transit`, `Core Allocation`, and `Cryptographic Audit`).
  - Split inspection drawer with formatted payload JSON viewer and execution diagnostics definition list.
- **Academic Benchmark Suite (`components/ExperimentsTab.tsx`)**:
  - Interactive runner for experiments E1 through E8 with sharp, unrounded Recharts bar charts and quantitative verification tables.
- **Security & Data Classifier Sandbox (`components/SecurityTab.tsx`)**:
  - Interactive payload tester with live taint keyword scanning, compliance routing destination feedback, and R1–R6 risk register cards.

### Changed
- `App.tsx` & `Navbar.tsx`: Refactored to 48px flush header with high-contrast tab links and monospace status indicators.
- `SimulationTab.tsx`, `OverviewTab.tsx`, `DataExplorerTab.tsx`: Standardized to Industrial Monochrome palette and tabular layouts.
- `README.md`: Completely rewritten with shields.io badges, comprehensive executive summary, capabilities, architecture diagram, benchmark matrix, quickstart, and file tree.

---

## [Stage 9: FastAPI Backend Service & REST Telemetry Engine] - 2026-10-04

### Added
- **FastAPI Application Framework (`backend/app/`)**:
  - `main.py`: Asynchronous application entry point with CORS middleware, lifecycle hooks, and router mounting.
  - `routes/simulation.py`: REST endpoints for initiating parameterized SimPy discrete-event runs (`/api/simulation/run`) and polling status.
  - `routes/experiments.py`: Dedicated benchmark runners for executing E1 through E8 suites (`/api/experiments/{id}`).
  - `routes/security.py`: Real-time payload taint inspection and classification endpoint (`/api/security/classify`).
  - `routes/datasets.py`: Paginated dataset explorer endpoints (`/api/datasets/preview`, `/api/datasets/statistics`).
  - `routes/trace.py`: Single-transaction distributed lifecycle execution endpoint (`/api/trace/transaction`).
- **Telemetry & State Management (`backend/app/services/`)**:
  - `sim_runner.py`: Background worker thread managing non-blocking simulation execution and time-series aggregation.
- **React Frontend Client (`frontend/src/api/client.ts`)**:
  - Typed Axios client interfacing with backend endpoints.

---

## [Stage 8: End-to-End Comparative Evaluation Suite & 3-Year TCO Analysis] - 2026-10-04

### Added
- **Comprehensive Benchmark Runner (`src/experiments/comparison.py`)**:
  - Multi-workload batch evaluator running W1 through W6 across On-Premise, Fixed Hybrid, and Elastic Hybrid Cloud configurations.
- **Experiment E8: 3-Year Total Cost of Ownership (TCO) & Pareto Optimization**:
  - Modeled CapEx and OpEx across hardware procurement, power, cooling, datacenter real estate, public cloud compute ($0.04/core-hour), bandwidth egress, and enterprise licensing.
  - Proved **$152,000 net savings (-18.7%)** for Hybrid Cloud ($662,000 vs $814,000 On-Premise) with an **11.4-month payback period**.
  - Generated Pareto efficiency frontier charts identifying optimal cost-performance trade-offs.

---

## [Stage 7: Chaos Engineering & Failure Recovery Simulation] - 2026-10-04

### Added
- **Fault-Tolerance & Disaster Recovery Engine (`src/simulation/hybrid_cloud.py`)**:
  - Dynamic fault injection model supporting 50% compute node loss, WAN latency spikes (4.5x degradation), database pool exhaustion, and SQL injection attack probes.
  - Automated health-check polling detecting node failures in 0.5 seconds and initiating traffic rerouting.
- **Experiments E5 & E6**:
  - **Experiment E5 (50% Node Loss @ 1,200 RPS)**: Demonstrated that fixed on-premise capacity saturates (latency spikes to 186.4 ms, queue > 500), while Hybrid Cloud dynamically provisions public instances, maintaining mean latency at 68.2 ms (-63.4%).
  - **Experiment E6 (Disaster Recovery & Node Restoration)**: Measured **MTTR = 20.0s**, **RTO = 22.5s**, and **RPO = 0 events** (zero transactional data loss during failover).

---

## [Stage 6: Security & Data-Classification Module] - 2026-10-04

### Added
- **Security Modules in `src/security/`**:
  - `data_classifier.py`: Two-stage automated classifier (`RESTRICTED`, `CONFIDENTIAL`, `INTERNAL`, `PUBLIC`) with field-level regex taint scanning.
  - `authentication.py` & `mfa.py`: Synthetic credential validation and step-up MFA challenge coordination.
  - `rbac.py`: 4-tier role-based access control matrix (`CUSTOMER`, `BANK_OPERATOR`, `SECURITY_AUDITOR`, `ADMIN`).
  - `encryption.py`: Latency modeling for AES-256-GCM storage encryption (0.8 ms) and TLS 1.3 transit encryption (0.4 ms).
  - `security_audit.py` & `security_events.py`: Immutable JSON Lines audit logger and violation detector.
- **Experiment E7**:
  - Evaluated 5,100 requests measuring classification accuracy (**99.49%**, Macro F1 = **0.9962**), routing compliance (**100.0%**), and attack probe interception (**25/25 blocked**, 0 sensitive leaks).

---

## [Stage 5: Load Balancing & Public Cloud Autoscaling] - 2026-10-04

### Added
- **Elastic Autoscaler & Load Balancer (`src/simulation/hybrid_cloud.py`)**:
  - `PublicCloudAutoscaler`: Horizontal elastic scaling controller with sustained dual-threshold triggers ($\ge 70\%$ scale-out, $\le 35\%$ scale-in), cooldown hysteresis (1.5s), and instance boundaries (2 to 20 instances).
  - `PublicLoadBalancer`: Request distributor supporting Round Robin, Least Connections, and Least Loaded strategies.
- **Experiment E4 (Autoscaling Burst)**:
  - Validated under W4 promotional burst trace (2,800 RPS): achieved **39.3% latency reduction** (61.4 ms vs 101.1 ms) and **64.4% queue dampening**.

---

## [Stage 4: Hybrid Cloud Simulation Baseline] - 2026-10-04

### Added
- **Dual-Tier Infrastructure Model (`src/simulation/hybrid_cloud.py`)**:
  - Modeled 48-core Private Datacenter + 8-core fixed Public Cloud with interconnect network latency (8.0 ms) and TLS 1.3 overhead (1.2 ms).
  - Implemented deterministic classification-based routing policy.
- **Experiments E1, E2, E3**:
  - E1 (Normal 600 RPS): -7.3% average latency reduction.
  - E2 (Peak 1,400 RPS): -6.9% average latency reduction.
  - E3 (Extreme 2,600 RPS): Proved static public tier saturation (572 ms latency), establishing the necessity for elastic autoscaling.

---

## [Stage 3: On-Premise Baseline Simulation] - 2026-10-04

### Added
- **On-Premise Core Datacenter (`src/simulation/on_premise.py`)**:
  - 64-core fixed datacenter model with finite FIFO queueing (depth = 5,000) and database connection pooling (64 workers).
  - Deterministic discrete-event simulation runner (`src/simulation/engine.py`).
- **Telemetry Collector (`src/simulation/metrics.py`)**:
  - Time-weighted utilization compiler and invariant verifier ($\text{Total} = \text{Completed} + \text{Dropped} + \text{Failed}$).

---

## [Stage 2: Synthetic Banking Dataset & Workload Generation] - 2026-10-04

### Added
- **Dataset Generators (`src/data_generator/`)**:
  - Generated 8 synthetic relational tables (170,000 records) with foreign key referential integrity: `customers.csv`, `accounts.csv`, `transactions.csv`, `login_events.csv`, `payment_requests.csv`, `risk_requests.csv`, `notifications.csv`, and `audit_logs.csv`.
- **Workload Traces (`data/workloads/`)**:
  - Generated W1 (Normal 600 RPS), W2 (Peak 1,400 RPS), W3 (Extreme 2,600 RPS), W4 (Burst 2,800 RPS), W5 (Failure), and W6 (Recovery) in JSON Lines format.

---

## [Stage 1: Project Structure & Configuration] - 2026-10-04

### Added
- Initial modular project layout (`config/`, `data/`, `src/`, `results/`, `reports/`, `tests/`, `docs/`).
- Formal configuration files (`simulation_config.json`, `workloads_config.json`, `security_rules.json`).
- Automated validation test suite (`tests/test_project_structure.py`).
