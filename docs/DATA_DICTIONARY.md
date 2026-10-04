# Data Dictionary & Schema Reference

This data dictionary defines every field, data type, description, example value, allowed values, sensitivity classification tier, and nullability across all synthetic datasets and simulation output artifacts.

---

## 1. Synthetic Banking Datasets (`data/synthetic/`)

### 1.1 `customers.csv`
| Field | Type | Description | Example | Allowed / Constraints | Classification | Nullable |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `customer_id` | String | Unique synthetic customer ID | `CUST_000001` | Pattern: `CUST_\d{6}` | `RESTRICTED` | No |
| `name` | String | Synthetic customer full name | `Morgan Smith (Synth-0001)` | Non-real names | `RESTRICTED` | No |
| `age` | Integer | Customer age | `46` | Range: `[18, 120]` | `INTERNAL` | No |
| `phone` | String | Synthetic contact telephone | `+1-555-0145-0001` | Synthetic 555 exchange | `RESTRICTED` | No |
| `email` | String | Synthetic email address | `synth_user_000001@synth-bank.test` | `.test` TLD | `RESTRICTED` | No |
| `address` | String | Synthetic postal address | `101 Synthetic Way, Suite 2, Region-2` | Non-real addresses | `RESTRICTED` | No |
| `kyc_status` | String | Verification status | `VERIFIED` | `VERIFIED`, `PENDING`, `FLAGGED` | `RESTRICTED` | No |
| `customer_risk_score` | Float | Credit/fraud risk score | `0.09` | Range: `[0.0, 1.0]` | `RESTRICTED` | No |
| `classification_tier` | String | Security data tier | `RESTRICTED` | `RESTRICTED` | `INTERNAL` | No |

### 1.2 `accounts.csv`
| Field | Type | Description | Example | Allowed / Constraints | Classification | Nullable |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `account_id` | String | Unique synthetic account ID | `ACC_000001` | Pattern: `ACC_\d{6}` | `RESTRICTED` | No |
| `customer_id` | String | Foreign key to `customers.csv` | `CUST_000001` | Must exist in `customers` | `RESTRICTED` | No |
| `account_type` | String | Account classification | `SAVINGS` | `SAVINGS`, `CURRENT`, `SALARY`, `FIXED_DEPOSIT` | `INTERNAL` | No |
| `balance` | Float | Account balance | `38306.45` | $\ge 0.0$ | `RESTRICTED` | No |
| `status` | String | Account operational status | `ACTIVE` | `ACTIVE`, `DORMANT`, `FROZEN` | `RESTRICTED` | No |
| `kyc_status` | String | KYC status | `VERIFIED` | Inherited from customer | `RESTRICTED` | No |
| `risk_score` | Float | Account risk rating | `0.09` | Range: `[0.0, 1.0]` | `RESTRICTED` | No |
| `classification_tier` | String | Security data tier | `RESTRICTED` | `RESTRICTED` | `INTERNAL` | No |

### 1.3 `transactions.csv`
| Field | Type | Description | Example | Allowed / Constraints | Classification | Nullable |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `tx_id` | String | Unique transaction ID | `TX_0000001` | Pattern: `TX_\d{7}` | `CONFIDENTIAL` | No |
| `timestamp` | String | ISO 8601 transaction time | `2026-10-01T08:00:00.506Z` | Valid UTC ISO format | `CONFIDENTIAL` | No |
| `source_account_id` | String | Debited account ID | `ACC_000410` | Must exist in `accounts` | `CONFIDENTIAL` | No |
| `target_account_id` | String | Credited account ID | `ACC_004507` | Must exist in `accounts` | `CONFIDENTIAL` | No |
| `amount` | Float | Transaction monetary value | `32.03` | $> 0.0$ | `CONFIDENTIAL` | No |
| `transaction_type` | String | Transaction category | `TRANSFER` | `TRANSFER`, `PAYMENT`, `WITHDRAWAL`, `DEPOSIT` | `CONFIDENTIAL` | No |
| `channel` | String | Access channel | `MOBILE_APP` | `MOBILE_APP`, `ONLINE_BANKING`, `ATM`, `BRANCH_PORTAL` | `CONFIDENTIAL` | No |
| `status` | String | Processing status | `SUCCESS` | `SUCCESS`, `PENDING`, `FAILED` | `CONFIDENTIAL` | No |
| `classification_tier` | String | Security data tier | `CONFIDENTIAL` | `CONFIDENTIAL` | `INTERNAL` | No |

---

## 2. Workload Event Traces (`data/workloads/*.jsonl`)

| Field | Type | Description | Example | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | String | Unique workload request identifier | `W1_EVT_0000001` | Pattern: `W\d_EVT_\d{7}` |
| `timestamp_sec` | Float | Arrival time offset in seconds | `0.0015` | Non-negative, monotonic |
| `request_type` | String | Service invoked | `fund_transfer` | Mapped in `security_rules.json` |
| `customer_id` | String | Customer initiating request | `CUST_007980` | Synthetic customer reference |
| `account_id` | String | Associated account reference | `ACC_002710` | Synthetic account reference |
| `payload_size_bytes` | Integer | Request payload size | `1024` | Range: `[128, 16384]` |
| `priority` | Integer | Scheduling priority | `1` | `1` (High), `2` (Medium), `3` (Low) |
| `classification_tier` | String | Sensitivity tier | `RESTRICTED` | `RESTRICTED`, `CONFIDENTIAL`, `INTERNAL`, `PUBLIC` |
| `expected_service` | String | Target backend service name | `fund_transfer` | Valid service string |
| `arrival_rate_rps` | Float | Instantaneous arrival rate | `600.0` | Positive float |
| `failure_metadata` | Object / Null | Injected failure / recovery state | `{"failure_injected": true}` | Null during normal operation |

---

## 3. Simulation Output Artifacts (`results/raw/on_premise/`)

### 3.1 `summary_metrics.json`
- `metadata`: Contains architecture name, workload ID, seed, and elapsed simulation time.
- `request_accounting`:
  - `total_requests`: Total arrival events received.
  - `completed_requests`: Successfully processed requests.
  - `dropped_requests`: Requests dropped due to finite queue overflow (`QUEUE_OVERFLOW`).
  - `failed_requests`: Requests that failed during processing.
  - `availability_pct`: Ratio $\frac{N_{\text{comp}}}{N_{\text{total}}} \times 100\%$.
- `performance_metrics`:
  - `throughput_rps`: Completed requests per simulation second.
  - `avg_response_time_ms`, `median_response_time_ms`, `p95_response_time_ms`, `p99_response_time_ms`, `min_response_time_ms`, `max_response_time_ms`, `std_response_time_ms`.
  - `mean_waiting_time_ms`: Average queue wait time before core acquisition.
  - `mean_service_time_ms`: Average active compute + DB service time.
- `resource_utilization`:
  - `avg_server_utilization_pct`: Continuous time-weighted application core utilization.
  - `peak_server_utilization_pct`: Peak core utilization observed across time series.
  - `avg_database_utilization_pct`: Continuous time-weighted database worker utilization.
  - `avg_queue_length`, `max_queue_length`.

### 3.2 `time_series.csv`
- `timestamp_sec`: Sample timestamp.
- `queue_length`: Pending request count in queue at sample tick.
- `active_cores`: Cores currently executing requests ($0$ to $64$).
- `server_utilization_pct`: Instantaneous percentage of busy cores.
- `active_db_connections`: Active database connections ($0$ to $64$).
- `db_utilization_pct`: Instantaneous percentage of busy DB connections.
- `cumulative_completed`: Completed count up to sample tick.
- `cumulative_dropped`: Dropped count up to sample tick.
- `cumulative_failed`: Failed count up to sample tick.
- `private_queue_length`, `public_queue_length`: Tier-specific queues (Hybrid Cloud).
- `private_active_cores`, `public_active_cores`: Tier-specific busy cores (Hybrid Cloud).
- `private_utilization_pct`, `public_utilization_pct`: Tier-specific instantaneous utilizations.

### 3.3 `results/raw/hybrid_cloud/summary_metrics.json`
Includes all fields from `summary_metrics.json` plus the `tier_breakdown` object:
- `tier_breakdown.private_tier`:
  - `total_cores`: Configured private cores (48).
  - `total_requests`, `completed_requests`, `dropped_requests`.
  - `avg_utilization_pct`: Continuous time-weighted private core utilization.
  - `avg_response_time_ms`, `p95_response_time_ms`.
- `tier_breakdown.public_tier`:
  - `total_cores`: Configured public cores (8).
  - `total_requests`, `completed_requests`, `dropped_requests`.
  - `avg_utilization_pct`: Continuous time-weighted public core utilization.
  - `avg_response_time_ms`, `p95_response_time_ms`.
- `tier_breakdown.routing_summary`:
  - `private_ratio_pct`: Percentage of requests routed to private cloud.
  - `public_ratio_pct`: Percentage of requests routed to public cloud.

### 3.4 `results/raw/comparison/E*/comparison_summary.json`
- `experiment_id`: E1, E2, or E3.
- `workload_id`: W1, W2, or W3.
- `academic_validation`:
  - `request_identity_verified`: Boolean verifying identical request sets were processed.
  - `validation_message`: Verification summary.
- `on_premise`: Metrics snapshot for On-Premise baseline.
- `hybrid_cloud`: Metrics snapshot for Hybrid Cloud.
- `comparative_deltas`:
  - `avg_response_time_delta_ms`: Hybrid latency minus On-Premise latency.
  - `avg_response_time_pct_change`: Percentage delta in response time.
  - `p95_response_time_delta_ms`, `p95_response_time_pct_change`.
  - `throughput_delta_rps`: Throughput difference.

### 3.5 `results/raw/hybrid_autoscaling/*/scaling_events.jsonl`
Every row represents a horizontal elasticity event:
- `event_id`: Unique identifier (e.g. `SCALE_EVT_001`).
- `timestamp_sec`: Simulation time when scaling action triggered.
- `event_type`: `SCALE_OUT` or `SCALE_IN`.
- `old_instance_count`: Number of active instances prior to event.
- `new_instance_count`: Target instance count after event.
- `trigger`: Condition trigger (`sustained_high_utilization`, `sustained_low_utilization`).
- `utilization_pct`: Monitored aggregate public utilization at decision tick.
- `queue_length`: Public request queue depth at decision tick.
- `reason`: Explanatory description including threshold and sustained interval count.
- `provisioning_delay_sec`: Simulated VM launch latency (0.8s for scale-out, 0.0s for scale-in).

### 3.6 Extended `time_series.csv` Schema (Stage 5)
In addition to Stage 4 telemetry fields:
- `public_instances`: Number of active public instances at sample tick ($2$ to $20$).
- `public_provisioning_instances`: Number of nodes undergoing provisioning delay.
- `public_draining_instances`: Number of nodes undergoing graceful scale-in connection draining.

### 3.7 `results/processed/E4/comparison_summary.json`
- `experiment`: E4 (Burst Workload + Autoscaling).
- `workload`: W4 (Burst 600 $\to$ 2,800 RPS).
- `validation`: Academic fairness validator (100% request ID match, invariant verification).
- `fixed_architecture`: Configuration and baseline metrics (fixed 2 instances / 8 cores).
- `autoscaling_architecture`: Dynamic metrics, peak instances (6), scaling action counts.
- `metrics_comparison`: Absolute deltas and percentage shifts across throughput, avg/median/P95/P99 latency, queue lengths, and resource utilization.


