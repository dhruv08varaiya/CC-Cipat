# Comparative Analysis: E3 (W3)

**Validation Status**: `Verified: Identical 15,000 unique request IDs evaluated in both architectures.`

| Metric | On-Premise Baseline | Hybrid Cloud (Stage 4) | Delta / Change |
| :--- | :--- | :--- | :--- |
| **Total Ingested Requests** | 15,000 | 15,000 | 0 (Identical) |
| **Completed Requests** | 15,000 | 15,000 | 0 |
| **Dropped Requests** | 0 | 0 | 0 |
| **Simulated Availability** | 100.00% | 100.00% | 0.00% |
| **Throughput (RPS)** | 2547.84 | 2169.25 | -378.59 RPS |
| **Average Response Time** | 36.46 ms | 181.09 ms | +144.63 ms (+396.7%) |
| **Median Response Time** | 35.54 ms | 27.38 ms | -8.16 ms |
| **P95 Response Time** | 57.48 ms | 912.10 ms | +854.62 ms (+1486.8%) |
| **P99 Response Time** | 65.50 ms | 1058.86 ms | +993.36 ms |
| **Mean Queue Waiting Time** | 9.40 ms | 158.74 ms | +149.34 ms |
| **Average Compute Util** | 100.00% (64 cores) | 86.56% (56 cores) | -13.44% |
| **Average Database Util** | 33.93% | 24.07% | -9.86% |
| **Maximum Queue Length** | 24 | 560 | +536 |

### Hybrid Cloud Tier Partitioning Breakdown
- **Private Cloud Tier** (48 cores): 10,736 requests (71.57%) | Util: 72.83% | Avg Latency: 25.63 ms | P95: 31.46 ms
- **Public Cloud Tier** (8 cores): 4,264 requests (28.43%) | Util: 100.0% | Avg Latency: 572.49 ms | P95: 1052.29 ms
