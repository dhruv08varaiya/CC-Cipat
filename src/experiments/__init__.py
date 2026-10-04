"""
src/experiments
Harness to execute reproducible experiments E1 through E8 and record telemetry.
Exports:
- ComparisonChecker: E1-E3 On-Premise vs Hybrid Cloud comparative benchmark
- E4ExperimentRunner: E4 Burst Workload & Autoscaling Dynamics
- E7SecurityExperimentRunner: E7 Sensitive Data Classification & Secure Routing
"""

from src.experiments.comparison import ComparisonChecker
from src.experiments.e4_burst_autoscaling import E4ExperimentRunner
from src.experiments.e7_security_classification import E7SecurityExperimentRunner

__all__ = [
    "ComparisonChecker",
    "E4ExperimentRunner",
    "E7SecurityExperimentRunner",
]
