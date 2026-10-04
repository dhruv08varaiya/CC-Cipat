# Synthetic Banking Dataset & Workload Statistics Report

**Validation Status**: `PASSED` (Errors: 0)

## 1. Dataset Row Counts
| Dataset Name | Record Count | Primary Key | Description |
| :--- | :--- | :--- | :--- |
| `customers.csv` | 10,000 | Unique ID | Synthetic banking operational data |
| `accounts.csv` | 10,000 | Unique ID | Synthetic banking operational data |
| `transactions.csv` | 50,000 | Unique ID | Synthetic banking operational data |
| `login_events.csv` | 15,000 | Unique ID | Synthetic banking operational data |
| `payment_requests.csv` | 25,000 | Unique ID | Synthetic banking operational data |
| `risk_requests.csv` | 5,000 | Unique ID | Synthetic banking operational data |
| `notifications.csv` | 25,000 | Unique ID | Synthetic banking operational data |
| `audit_logs.csv` | 30,000 | Unique ID | Synthetic banking operational data |

## 2. Workload Event Counts (JSONL)
| Workload ID | Profile Name | Event Count | Description |
| :--- | :--- | :--- | :--- |
| `W1` | Normal steady-state (600 RPS baseline) | 5,000 | Trace stream |
| `W2` | Peak business volume (1400 RPS) | 10,000 | Trace stream |
| `W3` | Extreme volume stress test (2600 RPS) | 15,000 | Trace stream |
| `W4` | Bursty spike traffic (2800 RPS) | 12,000 | Trace stream |
| `W5` | Node outage injected (50% dropped) | 8,000 | Trace stream |
| `W6` | Node outage with automated DR recovery | 10,000 | Trace stream |

## 3. Financial & Risk Statistical Summary
- **Account Balances**: Mean = $25,347.68, Max = $49,997.21, Total System Liquidity = $253,476,797.94
- **Transaction Amounts**: Mean = $254.44, Median = $177.40, Max = $2,777.58
- **Customer Risk Score**: Mean = 0.285, Min = 0.010, Max = 0.889

## 4. Security Classification Distribution
| Classification Tier | Total Records | Routing Policy |
| :--- | :--- | :--- |
| `RESTRICTED` | 35,000 | Governed by security_rules.json |
| `CONFIDENTIAL` | 80,000 | Governed by security_rules.json |
| `INTERNAL` | 30,000 | Governed by security_rules.json |
