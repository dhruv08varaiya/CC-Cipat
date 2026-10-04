# Changelog

All notable changes to the **Digital Banking System — Secure Hybrid Cloud Migration Simulation** project will be documented here.

## [Stage 1: Project Structure] - 2026-10-04

### Added
- Created complete modular project directory layout:
  - `config/` for simulation parameters, workload specifications, and security rules.
  - `data/synthetic/` and `data/workloads/` for datasets.
  - `src/` modular packages: `data_generator`, `simulation`, `security`, `experiments`, `visualization`.
  - `results/` hierarchy: `raw/`, `processed/`, `figures/`.
  - `reports/` for generated tables and executive summaries.
  - `tests/` for validation and regression tests.
- Core configuration files:
  - `config/simulation_config.json`: Baseline datacenter, private/public cloud parameters, network latencies.
  - `config/workloads_config.json`: Formally specified workload parameters for W1–W6.
  - `config/security_rules.json`: 4-tier data classification model (`RESTRICTED`, `CONFIDENTIAL`, `INTERNAL`, `PUBLIC`) and routing mapping.
- Core documentation:
  - `README.md`: Project charter, architecture diagram, workload profiles, experimental plan, and setup guide.
  - `requirements.txt`: Python package requirements (`simpy`, `matplotlib`, `pandas`, `numpy`, `cryptography`).
- Automated tests:
  - `tests/test_project_structure.py`: Validates all directories and JSON configuration structures.

## [Stage 2: Synthetic Banking Dataset & Workload Generation] - 2026-10-04

### Added
- Generator modules in `src/data_generator/`:
  - `customer_generator.py`: Generates synthetic customers and accounts with guaranteed 1-to-many referential integrity.
  - `transaction_generator.py`: Generates transactions, login events, payment requests, risk evaluation requests, notifications, and audit logs with strict foreign key validation.
  - `workload_generator.py`: Deterministic generator for event streams W1 (Normal), W2 (Peak), W3 (Extreme), W4 (Burst), W5 (Failure), and W6 (Recovery) in JSON Lines format with adaptive phase milestones.
  - `validator.py`: Automated referential integrity validator, constraint checker, and statistical reporting engine.
  - `generate_data.py`: CLI orchestration script with profile presets (`small`, `medium`, `large`).
- Root runner:
  - `generate_data.py`: Convenience command-line runner.
- Configuration:
  - `config/dataset_config.json`: Configuration for dataset profiles (`small`, `medium`, `large`) and workload limits.
- Generated Data Artifacts (`data/synthetic/`):
  - `customers.csv` (10,000 records)
  - `accounts.csv` (10,000 records)
  - `transactions.csv` (50,000 records)
  - `login_events.csv` (15,000 records)
  - `payment_requests.csv` (25,000 records)
  - `risk_requests.csv` (5,000 records)
  - `notifications.csv` (25,000 records)
  - `audit_logs.csv` (30,000 records)
- Generated Workload Traces (`data/workloads/`):
  - `W1_normal.jsonl` / `W1.jsonl` (5,000 events)
  - `W2_peak.jsonl` / `W2.jsonl` (10,000 events)
  - `W3_extreme.jsonl` / `W3.jsonl` (15,000 events)
  - `W4_burst.jsonl` / `W4.jsonl` (12,000 events with burst rates >= 2800 RPS)
  - `W5_failure.jsonl` / `W5.jsonl` (8,000 events with injected node failures)
  - `W6_recovery.jsonl` / `W6.jsonl` (10,000 events with failover and DR recovery)
- Statistical Reports (`reports/`):
  - `reports/dataset_statistics.json`
  - `reports/dataset_statistics.md`
- Tests:
  - `tests/test_synthetic_data.py`: Unit and regression test suite verifying referential integrity, bit-for-bit reproducibility with `seed=42`, and constraint tampering detection.

## [Stage 3: On-Premise Baseline Simulation] - 2026-10-04

### Added
- Core simulation modules in `src/simulation/`:
  - `metrics.py`: Telemetry collector, request record tracker, accounting invariant verifier, and continuous time-weighted resource utilization compiler.
  - `on_premise.py`: Fixed-capacity 64-core on-premise datacenter model with finite FIFO queueing (depth = 5,000), database connection pooling (64 workers), and inbound/outbound network delays.
  - `engine.py`: Simulation orchestrator reading pre-generated JSONL traces and executing deterministic discrete-event runs.
- Root CLI runner:
  - `run_on_premise_sim.py`: Command-line interface to execute on-premise simulation across workloads W1–W6 with seed and config options.
- Automated tests:
  - `tests/test_on_premise_sim.py`: Unit test suite covering workload loading, empty traces, accounting invariants, queue overflow rejections, reproducibility, and metrics range validation.
- Documentation:
  - `docs/PROJECT_DOCUMENTATION.md`: Comprehensive 16-section technical reference manual.
  - `docs/ARCHITECTURE.md`: Architecture document updated with Stage 3 On-Premise baseline diagram and component specs.
  - `docs/IMPLEMENTATION_STATUS.md`: Global stage completion tracker.
  - `docs/DECISIONS.md`: Formal decision log for DEC-001 through DEC-004.
  - `docs/EXPERIMENTS.md`: Experimental documentation tracking E1, E2, E3 actual execution and E4–E8 status.
  - `docs/DATA_DICTIONARY.md`: Complete data dictionary for all datasets, traces, and metrics.
  - `docs/RUNBOOK.md`: Step-by-step developer runbook.

### Changed
- `config/simulation_config.json`: Added database connection pool capacity (64) and query latency parameters.
- `README.md`: Added "New Developer Quick Start" section and Stage 3 execution instructions.

### Tests
- Ran 15 unit tests across the test suite (`test_project_structure.py`, `test_synthetic_data.py`, `test_on_premise_sim.py`).
- 15 passed in 0.103s (Exit code 0).

### Output
- Calibration run: 200 events, 100% availability, verified invariant accounting.
- Executed Baseline Runs (`results/raw/on_premise/`):
  - `W1` (Normal, 5,000 requests): Throughput = 589.37 RPS, Avg Latency = 29.72 ms, Server Util = 25.07%, DB Util = 7.95%.
  - `W2` (Peak, 10,000 requests): Throughput = 1,381.93 RPS, Avg Latency = 29.55 ms, Server Util = 58.41%, DB Util = 18.57%.
  - `W3` (Extreme, 15,000 requests): Throughput = 2,547.84 RPS, Avg Latency = 36.46 ms, Server Util = 100.00%, DB Util = 33.93%, Max Queue = 24.
- Exact bit-for-bit reproducibility verified across runs with `seed=42`.

## [Stage 4: Hybrid Cloud Simulation] - 2026-10-04

### Added
- Core simulation modules:
  - `src/simulation/hybrid_cloud.py`: Dual-tier Hybrid Cloud architecture modeling:
    - **Private Cloud**: 6 servers × 8 cores = 48 processing cores, dedicated core banking DB (64 workers), finite FIFO queue.
    - **Public Cloud**: 2 fixed instances × 4 cores = 8 processing cores (elastic maximum of 20 instances reserved for Stage 5, no autoscaling in Stage 4), separate finite FIFO queue.
    - **Deterministic Routing**: Hierarchical classification and service policy router with explicit precedence (`classification_policy` > `service_policy` > `default_private_fallback`).
    - **Interconnect**: Configurable round-trip network latency (8.0 ms) and TLS 1.3 encryption overhead (1.2 ms).
    - **Traceability**: Every processed request records `target_tier` and `routing_reason` in `raw_requests.jsonl`.
- Comparison and experimentation harness:
  - `src/experiments/comparison.py`: Comparative evaluator calculating throughput, latency shifts, queue differentials, and mathematical ratio shifts.
  - Automated academic integrity validator enforcing $\text{Total Requests}_{\text{on\_prem}} = \text{Total Requests}_{\text{hybrid}}$ and identical request IDs.
- Root CLI runners:
  - `run_hybrid_cloud_sim.py`: Standalone CLI to execute hybrid cloud simulation across W1–W6 with seed and trace options.
  - `run_comparison.py`: Automated evaluator producing comparative summary JSON and Markdown reports.
- Automated tests:
  - `tests/test_hybrid_cloud_sim.py`: Unit and regression test suite covering hybrid configuration parsing, private routing, public routing, unknown service safe fallback, 100% request decision coverage, routing determinism, dual queue handling, database access isolation, accounting invariants ($\text{Total} = \text{Completed} + \text{Dropped} + \text{Failed}$), metric ranges, and reproducibility.
- Documentation:
  - `docs/ARCHITECTURE.md`: Added comprehensive Stage 4 Hybrid Cloud Architecture section, ASCII topology diagram, tier specs, and routing matrix.
  - `docs/IMPLEMENTATION_STATUS.md`: Marked Stage 4 as COMPLETE and verified all 11 criteria.
  - `docs/DECISIONS.md`: Logged DEC-005 (Resource Partitioning), DEC-006 (Routing Precedence), and DEC-007 (Interconnect Network Model).
  - `docs/EXPERIMENTS.md`: Documented full empirical comparison between On-Premise and Hybrid Cloud for E1 (Normal), E2 (Peak), and E3 (Extreme).
  - `docs/DATA_DICTIONARY.md`: Added data schemas for hybrid-cloud telemetry and comparative evaluation artifacts.
  - `docs/RUNBOOK.md`: Added operational commands for hybrid cloud simulation and automated comparative validations.

### Changed
- `config/simulation_config.json`: Added `hybrid_cloud` section defining private cloud, public cloud, interconnect, and routing policies without modifying Stage 3 on-premise configuration.
- `src/simulation/metrics.py`: Extended telemetry collector with per-tier counters (`private_requests`, `public_requests`, `private_completed`, `public_completed`), per-tier queue tracking, and per-tier time-weighted utilization.
- `src/simulation/engine.py`: Enhanced playback harness to support hybrid cloud architecture instantiation.
- `README.md`: Updated Quick Start and operational instructions for Stage 4.
- `docs/PROJECT_DOCUMENTATION.md`: Updated to v1.2.0 with empirical Stage 4 comparative tables and findings.

### Tests
- Ran 20 unit tests across the test suite (`test_project_structure.py`, `test_synthetic_data.py`, `test_on_premise_sim.py`, `test_hybrid_cloud_sim.py`).
- 20 passed in 0.275s (Exit code 0).

### Output
- Hybrid Cloud Simulation Runs (`results/raw/hybrid_cloud/`):
  - `W1` (5,000 requests): Throughput = 589.37 RPS, Avg Latency = 27.55 ms, Private Util = 19.99%, Public Util = 45.51%, Availability = 100.00%.
  - `W2` (10,000 requests): Throughput = 1,381.93 RPS, Avg Latency = 27.50 ms, Private Util = 46.73%, Public Util = 100.00%, Availability = 100.00%.
  - `W3` (15,000 requests): Throughput = 2,467.50 RPS, Avg Latency = 181.09 ms, Private Util = 72.83%, Public Util = 100.00% (saturated, queue = 560), Availability = 100.00%.
- Comparative Reports (`results/raw/comparison/`):
  - `E1`: Request counts match exactly (5,000/5,000, 100% ID match). Latency improved -7.30%, P95 improved -12.01%.
  - `E2`: Request counts match exactly (10,000/10,000, 100% ID match). Latency improved -6.94%, P95 improved -10.74%.
  - `E3`: Request counts match exactly (15,000/15,000, 100% ID match). Private tier protected at 25.63 ms, public tier saturated at 572.49 ms due to static 8-core allocation without autoscaling.
- Reproducibility verified: Repeated execution of W1 seed=42 yielded identical 5,000 completed requests, identical 27.55 ms average latency, and 100% identical per-request routing decisions.

## [Stage 5: Load Balancing & Public Cloud Autoscaling] - 2026-10-04

### Added
- Core simulation components in `src/simulation/hybrid_cloud.py`:
  - `PublicCloudInstance`: Virtual compute node model with 4 cores, tracking lifecycle states (`PROVISIONING`, `ACTIVE`, `DRAINING`, `REMOVED`), active requests, and queue depth.
  - `PublicLoadBalancer`: Request distributor supporting deterministic Round Robin (default), Least Connections, and Least Loaded strategies, routing exclusively to `ACTIVE` instances.
  - `PublicCloudAutoscaler`: Horizontal elastic scaling controller executing sustained-condition dual-threshold monitoring (Scale-out $\ge 70\%$, Scale-in $\le 35\%$), cooldown hysteresis (1.5s), instance provisioning delay (0.8s), graceful draining, and instance bounds (min 2, max 20).
- Telemetry & metrics enhancements:
  - Scaling event telemetry logged to `scaling_events.jsonl` with event IDs, timestamps, triggers, instance counts, queue depths, and utilization.
  - Extended time-series tracking in `time_series.csv` for `public_instances`, `public_provisioning_instances`, and `public_draining_instances`.
- Experiment harness:
  - `src/experiments/e4_burst_autoscaling.py`: Orchestrator for Experiment E4 comparing `HYBRID_FIXED` vs `HYBRID_AUTOSCALING` under the exact Stage 2 `W4.jsonl` burst trace (12,000 events).
  - Enforced academic fairness validator: $100\%$ request ID identity match and exact accounting invariant verification ($\text{Total} = \text{Completed} + \text{Dropped} + \text{Failed}$).
  - `run_e4_experiment.py`: Root CLI runner.
- Publication visualization suite (`src/visualization/e4_plots.py`):
  - Generates 8 high-resolution publication charts in `results/figures/E4/`:
    1. `1_w4_arrival_rate_vs_time.png` (Arrival rate surge 600 $\to$ 2,800 RPS)
    2. `2_public_utilization_vs_time.png` (Fixed saturation vs dynamic capacity)
    3. `3_active_public_instances_vs_time.png` (Instance lifecycle timeline: 2 $\to$ 6 $\to$ 4 $\to$ 2)
    4. `4_public_queue_length_vs_time.png` (Queue surge and collapse)
    5. `5_rolling_response_time_vs_time.png` (Rolling mean latency)
    6. `6_response_time_comparison.png` (Mean, Median, P95, P99 comparison)
    7. `7_queue_length_comparison.png` (Average and peak queue comparison)
    8. `8_scaling_events_timeline.png` (Scaling event triggers over time)
- Automated tests:
  - `tests/test_autoscaling.py`: 9 comprehensive test cases covering min/max boundaries, active-only load balancing, provisioning delays, cooldown prevention of flapping, sustained utilization triggers, graceful draining, accounting invariants, and seed reproducibility.
- Documentation:
  - `docs/DECISIONS.md`: Logged DEC-008 (Public Cloud Autoscaling & Load Balancing Policy).
  - `docs/EXPERIMENTS.md`: Full empirical comparison and findings for Experiment E4.
  - `docs/DATA_DICTIONARY.md`: Added schemas for `scaling_events.jsonl` and E4 processed comparison artifacts.
  - `docs/RUNBOOK.md`: Added operational guidelines for running Experiment E4.

### Changed
- `config/simulation_config.json`: Added `autoscaling` block under `hybrid_cloud` specifying min/max instances, thresholds, cooldowns, provisioning delays, and load-balancing strategy.
- `src/simulation/engine.py`: Enhanced to accept `autoscaling_enabled` parameter for fair A/B comparison.
- `docs/IMPLEMENTATION_STATUS.md`: Marked Stage 5 as COMPLETE.

### Tests
- Ran 29 unit tests across all test suites (`test_project_structure.py`, `test_synthetic_data.py`, `test_on_premise_sim.py`, `test_hybrid_cloud_sim.py`, `test_autoscaling.py`).
- 29 passed in 0.160s (Exit code 0).

### Output
- Experiment E4 Results (`results/raw/hybrid_fixed/W4/`, `results/raw/hybrid_autoscaling/W4/`, `results/processed/E4/`):
  - Fixed Hybrid: Throughput = 1,226.34 RPS, Avg Latency = 101.13 ms, P95 = 555.02 ms, Max Queue = 435.
  - Autoscaling Hybrid: Throughput = 1,322.28 RPS (+7.82%), Avg Latency = 61.38 ms (-39.31%), P95 = 343.10 ms (-38.18%), Public Latency = 153.91 ms (-48.25%), Max Queue = 234 (-46.21%), Avg Queue = 30.29 (-64.36%).
  - Scaling Telemetry: 3 events (1 scale-out to 6 instances, 2 scale-ins back to 2 instances), 0 dropped requests, 100.00% availability.


