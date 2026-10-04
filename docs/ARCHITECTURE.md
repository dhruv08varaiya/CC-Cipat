# System Architecture Documentation

**Current Milestone**: Stage 6 — Security & Data-Classification Module (COMPLETE)  
**Project**: Digital Banking System — Secure Hybrid Cloud Migration Simulation  

---

## 1. Stage 3 — On-Premise Baseline Simulation Architecture

```
                    USERS / BANKING CLIENTS
                              │
                              ▼
                      ON-PREMISE NETWORK
                   (Inbound Latency: 2.5 ms)
                              │
                              ▼
                   APPLICATION SERVER POOL
                [ 8 Physical Servers × 8 Cores ]
                 Total Processing Cores = 64
             Finite FIFO Queue (Depth = 5,000)
                 /          |           \
                /           |            \
            Server 1     Server 2     Server 3 ... Server 8
                              │
                              ▼
                        CORE DATABASE
             [ Shared Connection Pool = 64 Workers ]
              Base Query Latency = 12.0 ms nominal
                              │
                              ▼
                      BACKUP / ARCHIVE
                 (Daily Cold Snapshot Storage)
```

---

## 2. Component Responsibilities (Stage 3)

| Component | Class / Configuration | Responsibilities | Constraints |
| :--- | :--- | :--- | :--- |
| **Workload Feeder** | `SimulationEngine` | Reads pre-generated JSONL traces (`W1.jsonl`, etc.) and injects timestamped arrival events into SimPy. | Deterministic sequence, non-blocking asynchronous dispatch. |
| **Network Hop** | `OnPremiseDatacenter` | Simulates WAN/LAN inbound and outbound transmission latencies (5.0 ms round-trip). | Symmetrical delay model ($2.5$ ms in, $2.5$ ms out). |
| **Request Queue** | `OnPremiseDatacenter` | Finite FIFO buffer holding pending requests before a server core becomes free. | Hard limit: 5,000 requests. Rejections trigger `QUEUE_OVERFLOW`. |
| **Application Server Pool** | `simpy.Resource(capacity=64)` | Multi-core compute resource executing request workloads. | Fixed capacity (64 cores). M/G/c service time distribution ($15.0$ ms nominal + payload scaling). |
| **Core Database** | `simpy.Resource(capacity=64)` | Models transactional database contention for balance inquiries, transfers, loans, and KYC updates. | Fixed connection pool (64 concurrent connections). |
| **Telemetry & Metrics** | `SimulationMetrics` | Records timestamps, queue length, waiting times, response times, and enforces accounting invariants. | Invariant check: $\text{Total} = \text{Completed} + \text{Dropped} + \text{Failed}$. |

---

## 3. Data Flow Lifecycle (Stage 3)

1. **Request Ingestion**:
   A workload event arrives from the trace file with `timestamp_sec`, `request_type`, `payload_size_bytes`, and `classification_tier`.
2. **Queue Admission Check**:
   If `current_queue_length >= max_queue_depth` (5,000), request is immediately marked as `DROPPED` with reason `QUEUE_OVERFLOW`.
3. **Queueing & Core Allocation**:
   Request increments `current_queue_length`, traverses the inbound network hop ($2.5$ ms), and requests an available application core from the 64-core pool.
4. **Execution & Database Contention**:
   Once allocated, request leaves the queue. An app execution delay is simulated based on CPU processing time and payload size. If the service requires DB access, the request acquires a database connection from the pool and simulates query latency ($12.0$ ms nominal).
5. **Outbound Hop & Metric Logging**:
   Request traverses outbound network hop ($2.5$ ms). Total latency ($T_{\text{completion}} - T_{\text{arrival}}$) is recorded to telemetry.

---

## 4. Stage 4 — Hybrid Cloud Simulation Architecture

```
                    USERS / CLIENT APPS
                            │
                            ▼
                    SECURITY GATEWAY
               [ Inbound WAF Delay: 1.5 ms ]
                            │
                            ▼
                DETERMINISTIC REQUEST ROUTER
         Policy: Classification Precedence (RESTRICTED/CONFIDENTIAL -> Private,
                                            PUBLIC/INTERNAL -> Public)
                     /             \
                    /               \
       PRIVATE CLOUD                 PUBLIC CLOUD
       (Protected Zone)              (Elastic Zone - Fixed in Stage 4)
       ────────────────              ─────────────────────────────────
       • 6 Servers × 8 Cores = 48    • 2 Fixed Instances × 4 Cores = 8
       • Network Latency: 3.0 ms     • WAN Network Latency: 18.0 ms
       • Finite Queue: 6,000         • Finite Queue: 2,000
       • Compute: 10.0 ms nominal    • Compute: 12.0 ms nominal
       • Dedicated Core DB (64 conn) • No Direct Core DB Access
              │                             │
              └──────────────┬──────────────┘
                             │
              [ Encrypted Interconnect ]
             (DirectConnect / IPsec VPN)
           8.0 ms round-trip + 1.2 ms crypto
```

---

## 5. Component Responsibilities (Stage 4)

| Component | Class / Configuration | Responsibilities | Constraints |
| :--- | :--- | :--- | :--- |
| **Security Gateway** | `HybridCloudEnvironment` | Simulates front-door API gateway and WAF security check ($1.5$ ms delay). | Initial ingress point for all client requests. |
| **Request Router** | `HybridCloudEnvironment` | Deterministic compliance routing engine. Evaluates `classification_tier` with fallback to `service_type`. | RESTRICTED & CONFIDENTIAL strictly bound to Private Cloud; PUBLIC & INTERNAL to Public Cloud. |
| **Private Cloud Tier** | `simpy.Resource(capacity=48)` | Hosts protected core banking services (transfers, balances, KYC, loans). | 48 physical compute cores, dedicated 64-worker DB cluster, high-speed 3.0 ms private network. |
| **Public Cloud Tier** | `simpy.Resource(capacity=8)` | Hosts elastic microservices (forex lookup, ATM locators, public FAQs, analytics). | Fixed 2 instances (8 cores) in Stage 4 (Autoscaling deferred to Stage 5). 18.0 ms WAN latency. |
| **Private Database** | `simpy.Resource(capacity=64)` | Models transactional core banking database contention ($10.0$ ms nominal query latency). | Dedicated to private tier; isolates sensitive banking data from the public internet. |
| **Interconnect** | Configuration | DirectConnect / IPsec VPN tunnel between private and public tiers. | $8.0$ ms round-trip + $1.2$ ms encryption overhead. |

---

## 6. Tier Routing & Precedence Rules

1. **Precedence Rule**:
   - **Primary Check**: If `classification_tier` is present:
     - `RESTRICTED` $\to$ `PRIVATE` (Reason: `classification_policy`)
     - `CONFIDENTIAL` $\to$ `PRIVATE` (Reason: `classification_policy`)
     - `INTERNAL` $\to$ `PUBLIC` (Reason: `classification_policy`)
     - `PUBLIC` $\to$ `PUBLIC` (Reason: `classification_policy`)
   - **Fallback Check**: If classification is missing/undefined, `service_type` mapping is consulted (`service_policy`).
   - **Default Safe Fallback**: In the event of any unknown attribute, the request is routed to `PRIVATE` (`default_safe_fallback`).
2. **Traceability**: Every processed request records `target_tier` and `routing_reason` in `raw_requests.jsonl`.

---

## 7. Stage 5 — Load Balancing & Public Cloud Autoscaling Architecture

```
                          PUBLIC REQUEST STREAM
                                    │
                         [ Public Load Balancer ]
                         (Round Robin across ACTIVE)
                        /           │            \
                       v            v             v
                [ Instance 1 ] [ Instance 2 ] [ Instance N ]
                   (ACTIVE)       (ACTIVE)      (PROVISIONING /
                   4 Cores        4 Cores         DRAINING)
                      │              │                │
                      └──────────────┴────────────────┘
                                     │
                        [ Public Cloud Autoscaler ]
                        ───────────────────────────
                        • Monitoring Interval: 0.5s
                        • Scale-Out: Util >= 70% (2 consecutive)
                        • Scale-In:  Util <= 35% (2 consecutive)
                        • Provisioning Delay: 0.8s
                        • Cooldown Hysteresis: 1.5s
                        • Elastic Bounds: Min 2, Max 20 instances
```

### Component Details
1. **Public Cloud Instance Model (`PublicCloudInstance`)**:
   - Encapsulates virtual compute nodes, each configured with 4 CPU cores (`simpy.Resource(capacity=4)`).
   - Lifecycle state machine:
     - `PROVISIONING`: Instance requested by autoscaler; undergoing simulated VM launch delay (`0.8`s). Ineligible for traffic.
     - `ACTIVE`: Fully booted and registered; actively serving requests via load balancer.
     - `DRAINING`: Marked for scale-in termination; receives zero new requests, but finishes in-flight requests.
     - `REMOVED`: Work completed; instance deregistered and resources freed.
2. **Public Load Balancer (`PublicLoadBalancer`)**:
   - Implements deterministic Round Robin request distribution across active instances.
   - Strictly excludes `PROVISIONING`, `DRAINING`, and `REMOVED` instances.
   - Dynamically adapts rotation when instances are added or drained.
3. **Horizontal Autoscaling Controller (`PublicCloudAutoscaler`)**:
   - **Metrics Monitoring**: Periodic sampler evaluates aggregate public utilization every `0.5` seconds:
     $$\text{Public Utilization} = \frac{\sum \text{Active Cores across ACTIVE instances}}{\text{Total Cores across ACTIVE instances}} \times 100\%$$
   - **Scale-Out Trigger**: When utilization $\ge 70.0\%$ for 2 consecutive monitoring intervals (1.0s sustained surge) and cooldown ($\ge 1.5$s) has elapsed, provisions 4 new instances (`scale_out_step = 4`), up to `max_instances = 20`.
   - **Scale-In Trigger**: When utilization $\le 35.0\%$ for 2 consecutive monitoring intervals and cooldown has elapsed, marks up to 2 instances as `DRAINING` (`scale_in_step = 2`), down to `min_instances = 2`.
   - **Hysteresis & Flapping Protection**: Cooldown window (1.5s) prevents rapid alternation between scale-out and scale-in.
   - **Telemetry Tracking**: Every scaling decision is logged to `scaling_events.jsonl` with timestamps, triggers, instance transitions, queue backlogs, and utilization metrics.

---

## 8. Stage 6 — Security & Data Classification Architecture

```
                    USERS / CLIENT APPS
                            │
                            ▼
               [ API GATEWAY / WAF PERIMETER ]
               (Gateway Delay: 1.5 ms, IP Filtering)
                            │
                            ▼
              [ AUTHENTICATOR & MFA COORDINATOR ]
              • Session Validation (0.4 ms)
              • MFA Challenge for Sensitive Ops (0.6 ms)
                            │
                            ▼
                     [ RBAC AUTHORIZER ]
              (Role Matrix: CUSTOMER, BANK_OPERATOR,
               SECURITY_AUDITOR, ADMIN)
                            │
                            ▼
              [ TWO-STAGE DATA CLASSIFIER ]
              • Stage 1: Deep Credential Taint Scan
              • Stage 2: Service Contract Catalog & Rules
              • Output: RESTRICTED / CONFIDENTIAL /
                        INTERNAL / PUBLIC
                            │
                            ▼
              [ COMPLIANCE ROUTING & INTERCEPTOR ]
              • RESTRICTED / CONFIDENTIAL ──► PRIVATE CLOUD
              • PUBLIC / INTERNAL        ──► PUBLIC CLOUD
              • R2 Interception: Blocks Sensitive -> Public
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
     PRIVATE CLOUD                    PUBLIC CLOUD
     (Protected Enclave)              (Elastic Zone)
     • 48 Compute Cores               • Elastic 2–20 Nodes
     • Core Banking DB (64 conn)      • Public Microservices
     • AES-256-GCM At Rest            • TLS 1.3 In Transit
            │                               │
            └───────────────┬───────────────┘
                            │
                            ▼
             [ SECURITY VIOLATION DETECTOR ]
             • Monitors Governance Risks R1–R6
             • R1: Unauthorized Internal Access
             • R2: Sensitive Data to Public Cloud
             • R4: Key / Crypto Failure
             • R6: Cross-Border Residency Breach
                            │
                            ▼
             [ IMMUTABLE SECURITY AUDIT LOG ]
             (`results/raw/security/audit_log.jsonl`)
```

### Component Details
1. **Two-Stage Rule-Based Data Classifier (`DataClassifier`)**:
   - **Stage 1 (Taint Scanning)**: Scans payload fields and text for high-sensitivity credential patterns (`*password*`, `*secret*`, `*key*`, `*token*`, `*kyc*`). Any positive match immediately escalates the request to `RESTRICTED`.
   - **Stage 2 (Service Catalog Mapping)**: Maps banking operations to sensitivity tiers based on regulatory guidelines:
     - `RESTRICTED`: `fund_transfer`, `kyc_verification`
     - `CONFIDENTIAL`: `account_balance_inquiry`, `loan_application`, `credit_risk_evaluation`, `transaction_history`
     - `INTERNAL`: `batch_analytics_report`
     - `PUBLIC`: `branch_atm_locator`, `exchange_rate_lookup`, `interest_rate_calculator`, `customer_support_faq`
   - **Zero-Trust Fallback**: Unrecognized schemas default to `RESTRICTED` and route to the protected Private tier.
   - **Latency Overhead**: Computes inspection overhead ($0.25$ to $0.55$ ms, mean $0.38$ ms).

2. **Access Control: Authentication & MFA (`Authenticator`, `MFACoordinator`)**:
   - Generates simulated session tokens with configurable session expiry ($900$s).
   - Enforces second-factor challenge-response for high-impact financial and KYC operations (`fund_transfer`, `kyc_verification`, `loan_application`).
   - Rejections trigger an `R1` security event.

3. **Role-Based Access Control (`RBACAuthorizer`)**:
   - Enforces a four-tier enterprise banking role matrix (`CUSTOMER`, `BANK_OPERATOR`, `SECURITY_AUDITOR`, `ADMIN`).
   - Denies non-privileged roles from invoking internal underwriting or administrative functions.

4. **Cryptographic Overhead Model (`EncryptionManager`)**:
   - Models dual cryptographic envelopes: Data-at-Rest (`AES-256-GCM`, $\sim 0.8$ ms) and Data-in-Transit (`TLS 1.3`, $\sim 0.4$ ms).
   - Applied selectively: `RESTRICTED` and `CONFIDENTIAL` require both At-Rest and In-Transit encryption; `INTERNAL` and `PUBLIC` enforce In-Transit protection.

5. **Security Violation Detection (`SecurityViolationDetector`)**:
   - Evaluates simulation events against the 6-risk register (`R1` through `R6`).
   - Automatically detects and intercepts attempted sensitive-data leakage to public clouds (`R2`), re-routing payloads to the private cloud to maintain a zero-leakage invariant.

6. **Immutable Structured Audit Logging (`SecurityAuditLogger`)**:
   - Records all access attempts, classification decisions, routing hops, cryptographic events, and security violations into `results/raw/security/audit_log.jsonl`.
   - Guaranteed deterministic across identical seeds (`seed=42`).

> **ACADEMIC DISCLAIMER**: Stage 6 security mechanisms are simulation abstractions for academic evaluation and are not production banking security controls.


