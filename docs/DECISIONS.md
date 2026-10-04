# Architecture & Engineering Decision Log

This log records major architectural decisions, trade-offs, options evaluated, and rationale for future viva defense and technical audit.

---

### DEC-001: Core Simulation Engine & Language Selection
- **Date**: 2026-10-04
- **Decision**: Select Python with SimPy (Option A) as the discrete-event simulation engine.
- **Context**: The project requires reproducible, high-throughput simulation of server queues, network latencies, autoscaling loops, and cryptographic overhead for final-year CIPAT defense.
- **Options Considered**:
  1. *Python + SimPy / Discrete-Event Queueing Engine* (Selected)
  2. *Java + CloudSim / CloudSim Plus*
  3. *Python + FastAPI / Full Web Dashboard*
- **Reason**: Python 3.14 was already installed on the host system with `pandas`, `numpy`, and `cryptography`. Java was not installed. SimPy provides transparent process-based queueing math ($M/G/c$ models), exact reproducibility, and seamless interoperability with data science tools.
- **Consequences**: Fast test iterations, easy inspection of queue mechanics during viva, zero heavy Java build tool dependencies.

---

### DEC-002: Data Formats for Configuration and Workload Traces
- **Date**: 2026-10-04
- **Decision**: Use `JSON` for configurations, `CSV` for tabular banking entities, and `JSON Lines (.jsonl)` for workload request event traces.
- **Context**: Need standard, easily inspectable data formats that guarantee interoperability across generator, simulator, and validation modules.
- **Options Considered**:
  1. *JSON + CSV + JSONL* (Selected)
  2. *SQLite relational database*
  3. *YAML + Parquet*
- **Reason**: Standard library Python parses JSON and CSV without additional dependencies. JSONL allows streaming request events sequentially without loading large arrays into memory at once.
- **Consequences**: Clean separation of configuration from logic, transparent manual and automated inspection.

---

### DEC-003: On-Premise Infrastructure Capacity Derivation Model
- **Date**: 2026-10-04
- **Decision**: Derive processing capacity mathematically from configured hardware parameters rather than hardcoding static limits.
- **Context**: The on-premise baseline must represent a realistic legacy datacenter with explicit physical resource limits.
- **Formula**:
  $$\text{Total Cores} = \text{server\_count} \times \text{cores\_per\_server} = 8 \times 8 = 64 \text{ cores}$$
  $$\text{Nominal Capacity} = 64 \times 25.0 \text{ RPS per core} = 1,600 \text{ RPS}$$
- **Reason**: Prevents artificial tuning of simulation limits to favor one architecture. Provides defensible queueing theory foundations during viva examination.
- **Consequences**: Under normal load (W1: 600 RPS), utilization is ~25%. Under peak load (W2: 1,400 RPS), utilization is ~58%. Under extreme load (W3: 2,600 RPS), cluster saturates at 100% and queuing delay surges.

---

### DEC-004: Continuous Time-Integrated Resource Utilization Formula
- **Date**: 2026-10-04
- **Decision**: Compute average server and database utilization using continuous time-weighted busy time integration rather than relying solely on coarse periodic sampling.
- **Context**: Periodic sampling can miss short spikes or undercount bursts if the sampling interval is larger than request completion durations.
- **Formula**:
  $$\text{Server Utilization} = \frac{\sum T_{\text{cpu\_busy}}}{c \times T_{\text{simulation\_elapsed}}} \times 100\%$$
- **Reason**: Standard in queuing theory ($M/M/c$ / $M/G/c$). Yields mathematically exact utilization regardless of sampling frequency.
- **Consequences**: Time-series snapshots provide peak observation and graph plotting, while time-integrated metrics provide exact summary statistics.

---

### DEC-005: Hybrid Cloud Resource Partitioning Model (Stage 4)
- **Date**: 2026-10-04
- **Decision**: Partition hybrid cloud compute capacity into 48 Private Cloud cores (6 servers × 8 cores) and 8 initial Public Cloud cores (2 instances × 4 cores).
- **Context**: A fair comparison with the 64-core On-Premise baseline requires a realistic partition reflecting enterprise migration, where core banking data is migrated to enterprise private hardware while non-sensitive services run in the public cloud.
- **Options Considered**:
  1. *48 Private Cores + 8 Public Cores (Total 56 Cores)* (Selected)
  2. *64 Private Cores + 64 Public Cores* (Unrealistic over-provisioning)
  3. *Dynamic Elastic Scaling immediately* (Violates stage isolation rule)
- **Reason**: Stage 4 aims to evaluate static hybrid partitioning. The 56 total cores represents a realistic initial hybrid deployment before autoscaling expands the public tier.
- **Consequences**: Private tier utilization is lower under normal/peak loads (20–47%), but public tier hits 100% saturation during extreme volume (W3), providing an empirical motivation for Stage 5 autoscaling.

---

### DEC-006: Deterministic Compliance Routing Precedence Rule
- **Date**: 2026-10-04
- **Decision**: Establish strict hierarchical precedence: `classification_tier` takes primary precedence, with `service_type` mapping serving as fallback.
- **Context**: Banking regulations (PCI-DSS, RBI, GDPR) demand that data sensitivity strictly dictates where processing occurs.
- **Policy**:
  - `RESTRICTED` & `CONFIDENTIAL` $\to$ `PRIVATE` Cloud (Protected Zone)
  - `PUBLIC` & `INTERNAL` $\to$ `PUBLIC` Cloud (Elastic Zone)
- **Reason**: Avoids ad-hoc routing. Every single request receives a reproducible, auditable routing decision recorded in telemetry (`routing_reason`).
- **Consequences**: 100% deterministic routing across simulation runs; zero sensitive transactions routed to the public tier.

---

### DEC-007: Deferring Autoscaling to Stage 5
- **Date**: 2026-10-04
- **Decision**: Explicitly disable automatic scale-out / scale-in during Stage 4, keeping the public tier fixed at 2 instances (8 cores).
- **Context**: To properly measure the benefit of autoscaling in an academic thesis, one must first measure the performance of a static hybrid architecture under stress.
- **Reason**: Allows the research to isolate the exact performance delta attributable to autoscaling in Stage 5.
- **Consequences**: Under W3 (2,600 RPS), the static public tier experiences queue buildup, demonstrating why static cloud sizing fails under unpredictable loads.

---

### DEC-008: Public Cloud Autoscaling & Load Balancing Policy
- **Date**: 2026-10-04
- **Decision**: Implement horizontal elasticity for the Public Cloud tier using dual-threshold sustained-condition monitoring (Scale-out $\ge 70\%$, Scale-in $\le 35\%$), cooldown hysteresis (1.5s), instance provisioning delay (0.8s), graceful draining, and deterministic Round Robin load balancing across active instances.
- **Context**: Stage 4 revealed that fixed 8-core public allocation caused severe queuing under traffic bursts. In Stage 5, dynamic scaling must absorb sudden surges (W4 burst to 2,800 RPS) without premature scaling on transient noise or rapid oscillation.
- **Options Considered**:
  1. *Instantaneous Threshold Scaling*: Scales on single high sample. (Rejected: causes severe flapping and oscillation).
  2. *Sustained Interval Threshold with Provisioning Delay & Hysteresis* (Selected): Requires $N=2$ consecutive intervals of high utilization before scaling out, enforces cooldown, models virtual instance provisioning delay (0.8s), and performs graceful draining before removal.
  3. *Predictive / ML Scaling*: (Deferred to later research; adds non-deterministic overhead).
- **Load Balancing Strategy**: Round Robin across instances in `ACTIVE` state. Instances in `PROVISIONING`, `DRAINING`, or `REMOVED` states are strictly excluded from receiving new requests.
- **Reason**: Simple, deterministic, provably stable, and easily explained in viva. Reflects production cloud load balancers (e.g. AWS Application Load Balancer target groups).
- **Consequences**: Reduced average latency by 39.3% and P95 latency by 38.2% under W4 burst, eliminating queue backlogs while preventing thrashing.


