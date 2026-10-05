# Data Dictionary & Schema Reference

This data dictionary defines every field, data type, description, example value, allowed values, sensitivity classification tier, and nullability across all synthetic datasets, simulation output artifacts, and web API contracts.

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

## 3. Simulation Output Artifacts

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
  - `avg_response_time_ms`, `median_response_time_ms`, `p95_response_time_ms`, `p99_response_time_ms`.
  - `mean_waiting_time_ms`: Average queue wait time before core acquisition.
  - `mean_service_time_ms`: Average active compute + DB service time.
- `resource_utilization`:
  - `avg_server_utilization_pct`: Continuous time-weighted application core utilization.
  - `peak_server_utilization_pct`: Peak core utilization observed across time series.
  - `avg_database_utilization_pct`: Continuous time-weighted database worker utilization.
  - `avg_queue_length`, `max_queue_length`.

### 3.2 `results/processed/E5/e5_summary.json` (Stage 7 Fault Tolerance)
- `experiment`: `E5` (50% Server Failure Outage).
- `workload`: `W5` (1,200 RPS with node crash).
- `metrics_comparison`:
  - `on_prem_latency_ms`: Mean latency during outage ($186.4$ ms).
  - `hybrid_latency_ms`: Mean latency with elastic cloud ($68.2$ ms).
  - `overflow_absorbed_pct`: Traffic absorbed by public cloud ($38.0\%$).
  - `queue_suppression_pct`: Backlog suppression percentage ($83.6\%$).

### 3.3 `results/processed/E6/e6_summary.json` (Stage 7 Disaster Recovery)
- `experiment`: `E6` (Automated Disaster Recovery & RTO/RPO).
- `workload`: `W6` (Failover and restoration).
- `dr_metrics`:
  - `health_detection_delay_sec`: Time to detect failure ($0.50$s).
  - `mttr_sec`: Mean time to node capacity restoration ($20.00$s).
  - `rto_sec`: Recovery time objective to full queue drain ($22.50$s).
  - `rpo_lost_events`: Data loss count during failover ($0$ events).

### 3.4 `results/processed/E8/e8_summary.json` (Stage 8 TCO & Pareto)
- `experiment`: `E8` (3-Year Total Cost of Ownership).
- `financial_breakdown`:
  - `on_premise_capex`: $\$220,000$ (Servers, SAN, networking).
  - `on_premise_opex_3yr`: $\$594,000$ (Power, cooling, datacenter lease, licenses).
  - `on_premise_tco`: $\$814,000$.
  - `hybrid_cloud_capex`: $\$140,000$ (48-core private appliance).
  - `hybrid_cloud_opex_3yr`: $\$522,000$ (Private OpEx + dynamic cloud compute + egress).
  - `hybrid_cloud_tco`: $\$662,000$.
  - `net_savings_usd`: $\$152,000$ ($-18.7\%$).
  - `payback_period_months`: $11.4$ months.

---

## 4. Security Risk Register Schema (`config/security_risk_register.json`)

- `risk_id`: Risk code (`R1` through `R6`).
- `category`: Governance domain (`ACCESS_CONTROL`, `DATA_GOVERNANCE`, `VENDOR_GOVERNANCE`, `CRYPTOGRAPHY`, `AVAILABILITY`, `COMPLIANCE`).
- `title`: Concise risk summary.
- `description`: Detailed risk scenario.
- `likelihood`: Integer rating from $1$ (Rare) to $5$ (Almost Certain).
- `impact`: Integer rating from $1$ (Negligible) to $5$ (Catastrophic).
- `risk_score`: Mathematical product $\text{Likelihood} \times \text{Impact}$ ($1$ to $25$).
- `risk_level`: Evaluated severity tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- `mitigation`: Concrete defense-in-depth architectural control.
- `monitoring_indicator`: Simulation metric used to monitor the risk.

---

## 5. Web API & REST Telemetry Contracts

### 5.1 `POST /api/simulation/run`
- **Request Body**:
  ```json
  {
    "architecture": "hybrid_autoscaling",
    "workload_id": "W4",
    "seed": 42,
    "max_events": 1000,
    "autoscaling_enabled": true
  }
  ```
- **Response**: `SimulationResult` object containing `summary`, `time_series`, and `scaling_events`.

### 5.2 `POST /api/security/classify`
- **Request Body**:
  ```json
  {
    "service_type": "fund_transfer",
    "payload": {
      "account_number": "1234567890",
      "amount": 5000,
      "recipient": "Alice"
    }
  }
  ```
- **Response**:
  ```json
  {
    "classification": "RESTRICTED",
    "target_datacenter": "PRIVATE",
    "decision_reason": "Matched sensitive service contract: fund_transfer",
    "processing_time_ms": 0.38,
    "tainted_fields": []
  }
  ```

### 5.3 `POST /api/trace/transaction`
- **Request Body**:
  ```json
  {
    "service_type": "fund_transfer",
    "user_role": "CUSTOMER",
    "payload": { "amount": 15000 },
    "chaos_node_failure": false,
    "chaos_network_spike": false
  }
  ```
- **Response**: `TraceTransactionResponse` containing 8-stage Gantt span timings, diagnostic definition list, and payload mutation snapshots.
