# Experiment E7: Sensitive Data Classification & Secure Routing Benchmark

## 1. Executive Summary
- **Workload Evaluated**: `W1.jsonl` (5,100 total requests including security probes)
- **Overall Classification Accuracy**: **99.49%** (Macro F1: **0.9962**)
- **Average Classification Latency**: **0.38 ms**
- **Routing Compliance Rate**: **100.00%**
- **Sensitive Data Leakage to Public Cloud**: **0 events (100% Interception Rate for R2)**
- **Total Security Events Detected (R1-R6)**: **190 events**

## 2. Classification Performance by Sensitivity Tier

| Sensitivity Tier | Support (Count) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **RESTRICTED** | 1,310 | 98.05% | 100.00% | **0.9902** |
| **CONFIDENTIAL** | 2,389 | 100.00% | 98.91% | **0.9945** |
| **INTERNAL** | 120 | 100.00% | 100.00% | **1.0000** |
| **PUBLIC** | 1,281 | 100.00% | 100.00% | **1.0000** |

## 3. Confusion Matrix

| Ground Truth \ Predicted | RESTRICTED | CONFIDENTIAL | INTERNAL | PUBLIC |
| :--- | :---: | :---: | :---: | :---: |
| **RESTRICTED** | 1,310 | 0 | 0 | 0 |
| **CONFIDENTIAL** | 26 | 2,363 | 0 | 0 |
| **INTERNAL** | 0 | 0 | 120 | 0 |
| **PUBLIC** | 0 | 0 | 0 | 1,281 |

## 4. Secure Hybrid Routing & Interception (R2 Audit)

| Routing Metric | Value | Compliance Status |
| :--- | :---: | :--- |
| **Total Requests Routed** | 5,100 | Processed |
| **Private Cloud Ingress (Protected)** | 3,699 | Core Banking Enclave |
| **Public Cloud Ingress (Elastic)** | 1,401 | Non-Sensitive Microservices |
| **Sensitive Records to Private** | 3,699 | Strictly Compliant |
| **Injected Public Routing Probes** | 25 | Attack / Error Simulation |
| **Violations Detected & Intercepted** | 25 | **100% R2 Detection** |
| **Undetected Sensitive Leakage** | **0** | **Zero Leakage Invariant** |

## 5. Access Control & Cryptographic Telemetry

| Control Subsystem | Invocations | Passed | Blocked / Denied | Success Rate |
| :--- | :---: | :---: | :---: | :---: |
| **Authentication (Auth)** | 5,100 | 5,044 | 56 | 98.90% |
| **Multi-Factor Auth (MFA)** | 1,453 | 1,400 | 53 | 96.35% |
| **Role-Based Access (RBAC)** | 5,100 | 5,019 | 81 | 98.41% |

- **Data-at-Rest Encrypted Records (AES-256)**: 3,679
- **Data-in-Transit Encrypted Records (TLS 1.3)**: 5,079
- **Mean Cryptographic Overhead**: 0.975 ms per request

## 6. Simulated Security Risk Events (R1-R6)

| Risk ID | Title | Events Detected | Severity Breakdown | Action Taken |
| :--- | :--- | :---: | :--- | :--- |
| **R1** | Unauthorized Internal Access / MFA Failure | 134 | Medium/High | BLOCKED |
| **R2** | Sensitive Data to Public Cloud | 25 | Critical/High | REDIRECTED_TO_PRIVATE |
| **R3** | Cloud Provider Dependency / Control Deviation | 0 | Medium | ALERT_LOGGED |
| **R4** | Cryptographic Key Failure | 21 | High | QUARANTINED |
| **R5** | Security Availability Outage | 0 | High | TRAFFIC_SHED |
| **R6** | Cross-Border Data Residency Breach | 10 | Critical | BLOCKED |

## 7. Academic Integrity & Reproducibility Statement
> **DISCLAIMER**: Stage 6 security mechanisms are simulation abstractions for academic evaluation and are not production banking security controls. All customer records and credentials are synthetically generated. Results are 100% reproducible with `seed=42`.