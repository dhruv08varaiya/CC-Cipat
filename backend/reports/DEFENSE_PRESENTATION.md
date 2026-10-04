# Final-Year Capstone Defense Presentation Guide: CC-CIPAT
## Comparative Infrastructure Performance Analysis & Secure Hybrid Cloud Migration Simulation

---

### Slide 1: Title & Project Overview
* **Title**: CC-CIPAT: Secure Hybrid Cloud Migration & Performance Simulation for Digital Banking
* **Candidate**: Dhruv Varaiya
* **Degree**: Final-Year Computer Engineering Capstone Project
* **Speaker Notes**: *"Good morning, respected examiners. Today I present CC-CIPAT, a discrete-event digital twin modeling the secure migration of a core banking infrastructure to an elastic hybrid cloud."*

---

### Slide 2: The Core Problem Statement
* **The Dilemma**: 
  1. *Scalability*: Banking traffic experiences sudden 5x spikes (promotional burst days).
  2. *Compliance*: Regulatory laws (PCI-DSS/GDPR) prohibit storing sensitive credentials or PII on unapproved public cloud instances.
* **Research Question**: *Can a bank achieve sub-65ms latency during 2,800 RPS bursts while maintaining 100% zero data leakage and reducing 3-year TCO?*

---

### Slide 3: 6-Layer Simulation Architecture
* **Layer 1: Data Layer**: 8 synthetic relational tables (170K rows) + 6 Poisson/bursty workload traces (W1–W6).
* **Layer 2: Discrete Engine**: SimPy 4.1 with $M/G/c/K$ queueing models and slotted dataclasses.
* **Layer 3: Infrastructure**: On-Premise (64 cores) vs. Hybrid Cloud (48 private + 2–20 public cores).
* **Layer 4: Zero-Trust Security**: 4-Tier data classification + live taint tracking + AES-256 latency modeling.
* **Layer 5: Experiment Suite**: Comprehensive benchmark runners E1–E8.
* **Layer 6: Interactive Terminal UI**: Full-stack FastAPI + React/Vite dashboard with live action inspector.

---

### Slide 4: Key Results & Experimental Findings (E1–E4)
* **E1 (Normal 600 RPS)**: Hybrid cloud provides -7.3% latency advantage by offloading 28% public traffic.
* **E2 (Peak 1,400 RPS)**: Fixed public tier maintains 100% availability.
* **E3 (Extreme 2,600 RPS)**: On-premise saturates (284ms latency); proves the necessity of autoscaling.
* **E4 (Burst 600→2,800 RPS)**: Autoscaling cuts avg response time by **39.3%** and queue depth by **64.4%**.

---

### Slide 5: Security & Chaos Resilience (E5–E7)
* **E7 (Zero-Trust Security)**: **99.49% classification accuracy** (Macro F1 = 0.9962), 100% attack probes (R1–R6) intercepted, zero data leakage.
* **E5 (50% Outage Fault)**: Hybrid cloud maintains sub-70ms response while on-premise collapses.
* **E6 (Disaster Recovery)**: Automated failover achieves **MTTR = 20.0s** and **RTO = 22.5s** with zero lost transactions.

---

### Slide 6: Financial TCO & Pareto Analysis (E8)
* **3-Year On-Premise TCO**: $814,000 USD.
* **3-Year Hybrid Cloud TCO**: $662,000 USD.
* **Net Savings**: **$152,000 (18.7% reduction)** with payback in 11.4 months.
* **Pareto Frontier**: Elastic Hybrid Cloud is the mathematically optimal choice between performance and operating cost.

---

### Slide 7: Live Demonstration & Q&A
* **Live System Demo**:
  1. *Action Inspector*: Tracing a $15,000 wire transfer step-by-step through zero-trust security to the private zone.
  2. *Chaos Lab*: Triggering a 50% node drop mid-simulation and watching the queue recover.
  3. *Data Explorer*: Browsing 170,000 synthetic records.
* **Conclusion**: Secure Hybrid Cloud provides the optimal balance of compliance, performance, and cost.
