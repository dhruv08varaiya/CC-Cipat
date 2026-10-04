"""
run_comparison.py
CLI script to run automated comparison validation between On-Premise baseline and Hybrid Cloud.
Generates results/raw/comparison/E1, E2, E3 summaries and comparison tables.
"""

from pathlib import Path
import sys

from src.experiments.comparison import ComparisonChecker


def main():
    root_dir = Path(__file__).resolve().parent
    checker = ComparisonChecker(root_dir)

    experiments = [
        ("E1", "W1"),
        ("E2", "W2"),
        ("E3", "W3")
    ]

    print("=" * 70)
    print("DIGITAL BANKING SYSTEM — AUTOMATED COMPARISON VALIDATION (E1, E2, E3)")
    print("=" * 70)

    all_passed = True
    for exp_id, workload_id in experiments:
        out_dir = root_dir / "results" / "raw" / "comparison" / exp_id
        try:
            comparison = checker.compare_experiment(exp_id, workload_id, out_dir)
            val = comparison["academic_validation"]
            deltas = comparison["comparative_deltas"]
            print(f"[{exp_id} - {workload_id}] Validation: PASS ({val['validation_message']})")
            print(f"       On-Premise Latency: {comparison['on_premise']['avg_response_time_ms']:.2f} ms | Hybrid: {comparison['hybrid_cloud']['avg_response_time_ms']:.2f} ms (Delta: {deltas['avg_response_time_delta_ms']:+.2f} ms)")
            print(f"       On-Premise P95:     {comparison['on_premise']['p95_response_time_ms']:.2f} ms | Hybrid: {comparison['hybrid_cloud']['p95_response_time_ms']:.2f} ms (Delta: {deltas['p95_response_time_delta_ms']:+.2f} ms)")
            print(f"       Saved to: {out_dir / 'comparison_table.md'}\n")
        except Exception as e:
            print(f"[{exp_id} - {workload_id}] Validation FAILED: {e}", file=sys.stderr)
            all_passed = False

    if all_passed:
        print("All comparison validations PASSED successfully!")
        return 0
    else:
        print("Comparison validation errors encountered!", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
