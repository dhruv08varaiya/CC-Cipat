"""
run_e7_experiment.py
Command-line interface to execute Experiment E7: Sensitive Data Classification & Secure Routing.
Usage:
    python run_e7_experiment.py
    python run_e7_experiment.py --seed 42 --workload data/workloads/W1.jsonl
"""

import argparse
from pathlib import Path
import sys

from src.experiments.e7_security_classification import E7SecurityExperimentRunner


def parse_args():
    parser = argparse.ArgumentParser(description="Run Experiment E7: Sensitive Data Classification & Secure Routing.")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed (default: 42)")
    parser.add_argument(
        "--config",
        type=str,
        default="config/simulation_config.json",
        help="Path to simulation config JSON"
    )
    parser.add_argument(
        "--workload",
        type=str,
        default="data/workloads/W1.jsonl",
        help="Path to workload trace JSONL"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root_dir = Path(__file__).resolve().parent

    config_path = root_dir / args.config
    if not config_path.exists():
        print(f"ERROR: Configuration file not found: {config_path}")
        return 1

    workload_path = root_dir / args.workload
    if not workload_path.exists():
        print(f"ERROR: Workload trace not found: {workload_path}")
        return 1

    base_results_dir = root_dir / "results"

    runner = E7SecurityExperimentRunner(
        config_path=config_path,
        workload_path=workload_path,
        base_output_dir=base_results_dir,
        seed=args.seed
    )

    try:
        results = runner.run_experiment()
        print("\nExperiment E7 Report Preview:")
        print("-" * 60)
        report_path = base_results_dir / "processed" / "E7" / "e7_report.md"
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                print(f.read())
        return 0
    except Exception as e:
        print(f"\nERROR: Experiment E7 failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
