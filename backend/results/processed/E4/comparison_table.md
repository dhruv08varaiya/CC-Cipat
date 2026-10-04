# Experiment E4: Burst Workload & Public Cloud Autoscaling Dynamics

## Executive Summary
- **Workload**: W4 (Burst 600 -> 2,800 RPS)
- **Total Requests Tested**: 12,000
- **Validation**: 100% Request ID Match between Fixed and Autoscaling runs
- **Elastic Public Instances**: Min = 2, Peak = 6, Avg = 3.0
- **Scaling Actions**: 3 events (Scale-Out: 1, Scale-In: 2)

## Empirical Benchmark Comparison Table

| Metric | Hybrid Fixed (No Autoscaling) | Hybrid Autoscaling (Elastic) | Delta (Absolute) | Shift (%) |
| :--- | :--- | :--- | :--- | :--- |
| **Throughput (RPS)** | 1226.34 | 1322.28 | +95.94 | +7.82% |
| **Average Response Time** | 101.13 ms | 61.38 ms | -39.75 ms | -39.31% |
| **Median Response Time** | 27.60 ms | 27.57 ms | -0.03 ms | -0.11% |
| **P95 Response Time** | 555.02 ms | 343.10 ms | -211.92 ms | -38.18% |
| **P99 Response Time** | 698.39 ms | 500.21 ms | -198.18 ms | -28.38% |
| **Public Tier Avg Latency** | 297.40 ms | 153.91 ms | -143.49 ms | -48.25% |
| **Average Queue Length** | 85.00 | 30.29 | -54.71 | -64.36% |
| **Maximum Queue Length** | 435 | 234 | -201 | -46.21% |
| **Average Resource Utilization** | 49.02% | 52.85% | +3.83% | +7.81% |

## Academic Invariants Verified
- $\text{Total Requests} = \text{Completed} + \text{Dropped} + \text{Failed}$ held for both runs.
- $100\%$ of request IDs matched between Fixed and Autoscaling architectures.
- Availability = $100.00\%$ across both architectures.
