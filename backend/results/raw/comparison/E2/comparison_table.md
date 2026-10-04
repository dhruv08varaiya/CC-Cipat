# Comparative Analysis: E2 (W2)

**Validation Status**: `Verified: Identical 10,000 unique request IDs evaluated in both architectures.`

| Metric | On-Premise Baseline | Hybrid Cloud (Stage 4) | Delta / Change |
| :--- | :--- | :--- | :--- |
| **Total Ingested Requests** | 10,000 | 10,000 | 0 (Identical) |
| **Completed Requests** | 10,000 | 10,000 | 0 |
| **Dropped Requests** | 0 | 0 | 0 |
| **Simulated Availability** | 100.00% | 100.00% | 0.00% |
| **Throughput (RPS)** | 1381.93 | 1383.43 | +1.50 RPS |
| **Average Response Time** | 29.55 ms | 27.50 ms | -2.05 ms (-6.9%) |
| **Median Response Time** | 30.75 ms | 27.10 ms | -3.65 ms |
| **P95 Response Time** | 39.58 ms | 35.33 ms | -4.25 ms (-10.7%) |
| **P99 Response Time** | 42.87 ms | 40.80 ms | -2.07 ms |
| **Mean Queue Waiting Time** | 2.50 ms | 5.21 ms | +2.71 ms |
| **Average Compute Util** | 58.41% (64 cores) | 55.06% (56 cores) | -3.35% |
| **Average Database Util** | 18.57% | 15.49% | -3.08% |
| **Maximum Queue Length** | 4 | 12 | +8 |

### Hybrid Cloud Tier Partitioning Breakdown
- **Private Cloud Tier** (48 cores): 7,215 requests (72.15%) | Util: 46.73% | Avg Latency: 25.47 ms | P95: 31.3 ms
- **Public Cloud Tier** (8 cores): 2,785 requests (27.85%) | Util: 100.0% | Avg Latency: 32.74 ms | P95: 39.34 ms
