# Experimental Documentation & Results Log

This document records the empirical execution, configuration, observations, and actual numerical results for experiments **E1 through E8**.

> **RESULT INTEGRITY RULE**:
> All numerical results recorded under "Actual Results" are generated directly from executed simulation runs. Unexecuted experiments or architectural variants are explicitly labeled as **"Not yet executed"**.

---

## E1: Normal Workload — Baseline vs Hybrid Cloud

### Objective
Evaluate steady-state system behavior, baseline latency, and resource utilization under normal daily banking volume (600 RPS).

### Workload
- **Trace**: `data/workloads/W1.jsonl` (5,000 events, 600.0 RPS nominal arrival rate, Poisson distribution, `seed=42`).

### Architectures
1. **On-Premise Baseline** (Executed in Stage 3)
2. **Hybrid Cloud** (Executed in Stage 4)

### Execution Commands
```powershell
python run_on_premise_sim.py --workload W1 --seed 42
python run_hybrid_cloud_sim.py --workload W1 --seed 42
python run_comparison.py
```

### Expected Observation
Both architectures operate well within capacity. Hybrid cloud routes ~72% of traffic to the protected Private tier and ~28% to the Public tier. Private tier latency will be lower due to optimized internal network (3 ms vs 5 ms on-prem), while public tier will show WAN round-trip latency (18 ms).

### Actual Results Comparison

| Metric | On-Premise Baseline | Hybrid Cloud (Stage 4) | Delta / Change |
| :--- | :--- | :--- | :--- |
| **Total Ingested Requests** | 5,000 | 5,000 | 0 (Identical) |
| **Completed Requests** | 5,000 | 5,000 | 0 |
| **Dropped Requests** | 0 | 0 | 0 |
| **Simulated Availability** | 100.00% | 100.00% | 0.00% |
| **Throughput** | 589.37 RPS | 589.85 RPS | +0.48 RPS |
| **Average Response Time** | **29.72 ms** | **27.55 ms** | **-2.17 ms (-7.3%)** |
| **Median Response Time** | 30.92 ms | 27.22 ms | -3.70 ms |
| **P95 Response Time** | **39.81 ms** | **35.03 ms** | **-4.78 ms (-12.0%)** |
| **P99 Response Time** | 43.20 ms | 40.67 ms | -2.53 ms |
| **Mean Queue Waiting Time** | 2.50 ms | 5.10 ms | +2.60 ms |
| **Compute Core Utilization** | 25.07% (64 cores) | 23.64% (56 cores) | -1.43% |
| **Database Utilization** | 7.95% (64 conn) | 6.63% (64 conn) | -1.32% |
| **Maximum Queue Length** | 2 | 6 | +4 |

**Hybrid Cloud Tier Breakdown (E1)**:
- **Private Tier** (48 cores): 3,599 served (71.98%) | Util: 19.99% | Avg Latency: 25.60 ms | P95: 31.43 ms
- **Public Tier** (8 cores): 1,401 served (28.02%) | Util: 45.51% | Avg Latency: 32.54 ms | P95: 38.94 ms

### Academic Interpretation
In normal operations, Hybrid Cloud achieves a **7.3% reduction in average response time** and a **12.0% improvement in P95 latency**. Core banking requests benefit from the high-speed private cloud zone, while public inquiries are cleanly offloaded to the public tier without accessing the core banking database.

---

## E2: Peak Workload — Baseline vs Hybrid Cloud

### Objective
Evaluate system performance and resource stress under daily peak business volume (1,400 RPS).

### Workload
- **Trace**: `data/workloads/W2.jsonl` (10,000 events, 1,400.0 RPS nominal arrival rate, `seed=42`).

### Execution Commands
```powershell
python run_on_premise_sim.py --workload W2 --seed 42
python run_hybrid_cloud_sim.py --workload W2 --seed 42
python run_comparison.py
```

### Expected Observation
Both architectures handle the peak load without dropped requests. Hybrid cloud offloads ~28% of traffic to the public tier, keeping the private tier utilization under 50%.

### Actual Results Comparison

| Metric | On-Premise Baseline | Hybrid Cloud (Stage 4) | Delta / Change |
| :--- | :--- | :--- | :--- |
| **Total Ingested Requests** | 10,000 | 10,000 | 0 (Identical) |
| **Completed Requests** | 10,000 | 10,000 | 0 |
| **Dropped Requests** | 0 | 0 | 0 |
| **Simulated Availability** | 100.00% | 100.00% | 0.00% |
| **Throughput** | 1,381.93 RPS | 1,383.43 RPS | +1.50 RPS |
| **Average Response Time** | **29.55 ms** | **27.50 ms** | **-2.05 ms (-6.9%)** |
| **Median Response Time** | 30.75 ms | 27.10 ms | -3.65 ms |
| **P95 Response Time** | **39.58 ms** | **35.33 ms** | **-4.25 ms (-10.7%)** |
| **P99 Response Time** | 42.87 ms | 40.80 ms | -2.07 ms |
| **Mean Queue Waiting Time** | 2.50 ms | 5.21 ms | +2.71 ms |
| **Compute Core Utilization** | 58.41% (64 cores) | 55.06% (56 cores) | -3.35% |
| **Database Utilization** | 18.57% (64 conn) | 15.49% (64 conn) | -3.08% |
| **Maximum Queue Length** | 4 | 12 | +8 |

**Hybrid Cloud Tier Breakdown (E2)**:
- **Private Tier** (48 cores): 7,215 served (72.15%) | Util: 46.73% | Avg Latency: 25.47 ms | P95: 31.42 ms
- **Public Tier** (8 cores): 2,785 served (27.85%) | Util: 100.00% | Avg Latency: 32.74 ms | P95: 39.26 ms

### Academic Interpretation
During peak traffic, the Private Tier operates with comfortable headroom (46.73% utilization), and private latency remains low (25.47 ms). However, the static Public Tier (fixed at 2 instances = 8 cores in Stage 4) reaches 100.00% capacity. This confirms that while hybrid segmentation protects core banking workloads, static public sizing reaches saturation under peak traffic.

---

## E3: Extreme Workload — Bottleneck & Capacity Saturation

### Objective
Stress-test both architectures beyond on-premise static capacity (2,600 RPS) to evaluate queuing bottlenecks and latency degradation.

### Workload
- **Trace**: `data/workloads/W3.jsonl` (15,000 events, 2,600.0 RPS nominal arrival rate, `seed=42`).

### Execution Commands
```powershell
python run_on_premise_sim.py --workload W3 --seed 42
python run_hybrid_cloud_sim.py --workload W3 --seed 42
python run_comparison.py
```

### Expected Observation
In On-Premise, all 64 cores saturate at 100%, causing queue delays across all services. In Hybrid Cloud without autoscaling, the private tier remains protected, but the fixed public tier experiences severe queue buildup.

### Actual Results Comparison

| Metric | On-Premise Baseline | Hybrid Cloud (Stage 4) | Delta / Change |
| :--- | :--- | :--- | :--- |
| **Total Ingested Requests** | 15,000 | 15,000 | 0 (Identical) |
| **Completed Requests** | 15,000 | 15,000 | 0 |
| **Dropped Requests** | 0 | 0 | 0 |
| **Simulated Availability** | 100.00% | 100.00% | 0.00% |
| **Throughput** | 2,547.84 RPS | 2,169.25 RPS | -378.59 RPS |
| **Average Response Time** | **36.46 ms** | **181.09 ms** | **+144.63 ms** |
| **Median Response Time** | 35.54 ms | 27.38 ms | -8.16 ms |
| **P95 Response Time** | **57.48 ms** | **912.10 ms** | **+854.62 ms** |
| **P99 Response Time** | **65.50 ms** | **1058.86 ms** | **+993.36 ms** |
| **Mean Queue Waiting Time** | 9.40 ms | 158.74 ms | +149.34 ms |
| **Compute Core Utilization** | 100.00% (64 cores) | 86.56% (56 cores) | -13.44% |
| **Database Utilization** | 33.93% (64 conn) | 24.07% (64 conn) | -9.86% |
| **Maximum Queue Length** | 24 | 560 | +536 |

**Hybrid Cloud Tier Breakdown (E3)**:
- **Private Tier** (48 cores): 10,736 served (71.57%) | **Util: 72.83%** | **Avg Latency: 25.63 ms** | P95: 32.18 ms
- **Public Tier** (8 cores): 4,264 served (28.43%) | **Util: 100.00%** | **Avg Latency: 572.49 ms** | P95: 986.42 ms

### Critical Academic Finding
1. **Private Tier Shielding**: The Private Cloud tier successfully shielded core banking data: utilization stayed at 72.83% and average response time remained at 25.63 ms with P95 under 33 ms!
2. **Public Tier Bottleneck**: Because Stage 4 deliberately maintains a **fixed** public pool (2 instances = 8 cores), the public tier was overwhelmed by 4,264 incoming requests, causing public service latency to surge to 572 ms and maximum queue depth to reach 560.
3. **Justification for Stage 5**: This finding proves empirically that static hybrid cloud partitioning is insufficient under extreme load. Dynamic autoscaling (Stage 5) is strictly required to scale the public tier from 2 instances up to 20 instances during surges.

---

## E4: Burst Workload & Public Cloud Autoscaling Dynamics

### Objective
Evaluate the effectiveness of public cloud horizontal autoscaling and load balancing in absorbing a sudden traffic surge (from 600 RPS to 2,800 RPS) compared against a static fixed-capacity hybrid cloud baseline.

### Workload
- **Trace**: `data/workloads/W4.jsonl` (12,000 events, 600.0 RPS base transitioning to 2,800.0 RPS promotional burst at $t=6.0$s, `seed=42`).

### Architectures Compared
1. **HYBRID_FIXED**: Dual-tier hybrid cloud with fixed public tier (2 instances = 8 cores, autoscaling disabled).
2. **HYBRID_AUTOSCALING**: Dual-tier hybrid cloud with elastic public tier (starts at 2 instances = 8 cores, scales up to 20 instances = 80 cores, Round Robin load balancing).

### Execution Commands
```powershell
python run_e4_experiment.py --seed 42
```

### Expected Observation (Hypothesis)
Under the sudden 2,800 RPS burst, the fixed 8-core public tier will saturate at 100%, causing a massive request queue to accumulate and inflating P95/P99 latency. With autoscaling enabled, the controller will detect sustained utilization $\ge 70\%$, trigger horizontal scale-out, provision additional virtual instances, and distribute requests via the Round Robin load balancer. Once traffic subsides, the controller will detect sustained low utilization $\le 35\%$ and execute graceful scale-in back to baseline.

### Actual Results Comparison

| Metric | Hybrid Fixed (No Autoscaling) | Hybrid Autoscaling (Elastic) | Delta (Absolute) | Shift (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Total Ingested Requests** | 12,000 | 12,000 | 0 | 0.00% (Identical Set) |
| **Completed Requests** | 12,000 | 12,000 | 0 | 0.00% |
| **Dropped Requests** | 0 | 0 | 0 | 0.00% |
| **Simulated Availability** | 100.00% | 100.00% | 0.00% | 0.00% |
| **Effective Throughput** | 1,226.34 RPS | 1,322.28 RPS | +95.94 RPS | **+7.82%** |
| **Average Response Time** | **101.13 ms** | **61.38 ms** | **-39.75 ms** | **-39.31%** |
| **Median Response Time** | 27.60 ms | 27.57 ms | -0.03 ms | -0.11% |
| **P95 Response Time** | **555.02 ms** | **343.10 ms** | **-211.92 ms** | **-38.18%** |
| **P99 Response Time** | **698.39 ms** | **500.21 ms** | **-198.18 ms** | **-28.38%** |
| **Public Tier Avg Latency** | **297.40 ms** | **153.91 ms** | **-143.49 ms** | **-48.25%** |
| **Average Queue Length** | **85.00** | **30.29** | **-54.71** | **-64.36%** |
| **Maximum Queue Length** | **435** | **234** | **-201** | **-46.21%** |
| **Average Resource Utilization**| 49.02% | 52.85% | +3.83% | +7.81% |

### Elastic Scaling Telemetry Log
- **Total Scaling Events**: 3 events recorded in `results/raw/hybrid_autoscaling/W4/scaling_events.jsonl`
  1. `SCALE_EVT_001` ($t = 7.00$s): **SCALE_OUT** from 2 to 6 instances (Trigger: sustained utilization 100.0% $\ge 70.0\%$ for 2 intervals, queue = 165). Provisioning delay = 0.8s. Activated at $t = 7.80$s.
  2. `SCALE_EVT_002` ($t = 11.50$s): **SCALE_IN** from 6 to 4 instances (Trigger: sustained utilization 0.0% $\le 35.0\%$ for 2 intervals). Graceful connection draining.
  3. `SCALE_EVT_003` ($t = 13.50$s): **SCALE_IN** from 4 to 2 instances (Trigger: sustained utilization 0.0% $\le 35.0\%$ for 2 intervals). Reached minimum capacity bound (2 instances).

### Generated Publication Figures (`results/figures/E4/`)
1. `1_w4_arrival_rate_vs_time.png`: Step-wise arrival rate profile showing baseline 600 RPS transitioning to 2,800 RPS burst.
2. `2_public_utilization_vs_time.png`: Dynamic utilization comparing fixed saturation (100%) against autoscaled capacity.
3. `3_active_public_instances_vs_time.png`: Step function of active instances over time (2 $\to$ 6 $\to$ 4 $\to$ 2).
4. `4_public_queue_length_vs_time.png`: Queue backlog buildup and rapid drainage under autoscaling.
5. `5_rolling_response_time_vs_time.png`: Rolling 100-request window mean latency over time.
6. `6_response_time_comparison.png`: Percentile bar chart (Mean, Median, P95, P99).
7. `7_queue_length_comparison.png`: Comparative bar chart of average and peak queue backlogs.
8. `8_scaling_events_timeline.png`: Event scatter points marking exact scale-out and scale-in triggers over the instance trajectory.

### Critical Academic Finding
1. **Queue Collapse**: Autoscaling reduced the average queue length by **64.36%** and cut the peak queue from 435 to 234 requests (-46.21%).
2. **Latency Mitigation**: Public service response time improved by **48.25%**, reducing overall P95 latency from 555.02 ms to 343.10 ms.
3. **Elasticity Loop Completed**: The autoscaler successfully executed the full lifecycle: detected burst $\to$ provisioned 4 additional instances $\to$ absorbed load $\to$ detected traffic cessation $\to$ safely drained and terminated idle instances back to baseline.

---

## E5–E8 Planned Experiments Status Tracker

| Experiment ID | Title | Workload | Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **E1** | Normal Workload Comparison | W1 (Normal) | **COMPLETE** | On-Premise vs Fixed Hybrid |
| **E2** | Peak Workload Comparison | W2 (Peak) | **COMPLETE** | On-Premise vs Fixed Hybrid |
| **E3** | Extreme Workload Comparison | W3 (Extreme) | **COMPLETE** | Fixed Capacity Saturation Bottleneck |
| **E4** | Burst Workload + Autoscaling | W4 (Burst) | **COMPLETE** | Fixed Hybrid vs Autoscaling Hybrid |
| **E5** | Application Server Failure Resilience | W5 (Failure) | *Not yet executed* | Scheduled for Stage 7 |
| **E6** | Backup & Disaster Recovery (RTO/RPO) | W6 (Recovery) | *Not yet executed* | Scheduled for Stage 7 |
| **E7** | Sensitive Data Classification & Routing | Multi-tier | *Not yet executed* | Scheduled for Stage 6 |
| **E8** | Privacy-Preserving ML / Encryption Overhead | Optional | *Not yet executed* | Scheduled for Stage 8 |
