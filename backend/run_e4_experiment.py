"""
run_e4_experiment.py
Command-line interface to execute Experiment E4: Burst Workload & Public Cloud Autoscaling.
Usage:
    python run_e4_experiment.py
    python run_e4_experiment.py --seed 42 --config config/simulation_config.json
"""

import argparse
from pathlib import Path
import sys

from src.experiments.e4_burst_autoscaling import E4ExperimentRunner


def parse_args():
    parser = argparse.ArgumentParser(description="Run Experiment E4: Burst Workload + Autoscaling.")
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
        default="data/workloads/W4.jsonl",
        help="Path to W4 workload trace"
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

    runner = E4ExperimentRunner(
        config_path=config_path,
        workload_path=workload_path,
        base_output_dir=base_results_dir,
        seed=args.seed
    )

    try:
        results = runner.run_experiment()
        print("\nExperiment Summary Table:")
        print("-" * 50)
        table_path = base_results_dir / "processed" / "E4" / "comparison_table.md"
        if table_path.exists():
            with open(table_path, "r", encoding="utf-8") as f:
                print(f.read())
        return 0
    except Exception as e:
        print(f"\nERROR: Experiment E4 failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
