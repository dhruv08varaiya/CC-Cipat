# Comparative Analysis: E1 (W1)

**Validation Status**: `Verified: Identical 5,000 unique request IDs evaluated in both architectures.`

| Metric | On-Premise Baseline | Hybrid Cloud (Stage 4) | Delta / Change |
| :--- | :--- | :--- | :--- |
| **Total Ingested Requests** | 5,000 | 5,000 | 0 (Identical) |
| **Completed Requests** | 5,000 | 5,000 | 0 |
| **Dropped Requests** | 0 | 0 | 0 |
| **Simulated Availability** | 100.00% | 100.00% | 0.00% |
| **Throughput (RPS)** | 589.37 | 589.85 | +0.48 RPS |
| **Average Response Time** | 29.72 ms | 27.55 ms | -2.17 ms (-7.3%) |
| **Median Response Time** | 30.92 ms | 27.22 ms | -3.70 ms |
| **P95 Response Time** | 39.81 ms | 35.03 ms | -4.78 ms (-12.0%) |
| **P99 Response Time** | 43.20 ms | 40.67 ms | -2.53 ms |
| **Mean Queue Waiting Time** | 2.50 ms | 5.10 ms | +2.60 ms |
| **Average Compute Util** | 25.07% (64 cores) | 23.64% (56 cores) | -1.43% |
| **Average Database Util** | 7.95% | 6.63% | -1.32% |
| **Maximum Queue Length** | 2 | 6 | +4 |

### Hybrid Cloud Tier Partitioning Breakdown
- **Private Cloud Tier** (48 cores): 3,599 requests (71.98%) | Util: 19.99% | Avg Latency: 25.6 ms | P95: 31.43 ms
- **Public Cloud Tier** (8 cores): 1,401 requests (28.02%) | Util: 45.51% | Avg Latency: 32.54 ms | P95: 38.94 ms
