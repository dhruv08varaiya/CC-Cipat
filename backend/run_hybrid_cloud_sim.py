"""
run_hybrid_cloud_sim.py
Command-line interface to execute the Secure Hybrid Cloud banking simulation.
Usage:
    python run_hybrid_cloud_sim.py --workload W1
    python run_hybrid_cloud_sim.py --workload W2 --seed 42
    python run_hybrid_cloud_sim.py --workload W3 --config config/simulation_config.json
"""

import argparse
import json
from pathlib import Path
import sys

from src.simulation.engine import SimulationEngine


def parse_args():
    parser = argparse.ArgumentParser(description="Run Secure Hybrid Cloud Banking Simulation.")
    parser.add_argument(
        "--workload",
        type=str,
        default="W1",
        choices=["W1", "W2", "W3", "W4", "W5", "W6"],
        help="Workload trace to execute (e.g. W1, W2, W3)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed (default: 42)")
    parser.add_argument(
        "--config",
        type=str,
        default="config/simulation_config.json",
        help="Path to simulation configuration JSON"
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=None,
        help="Optional limit on number of workload events to process"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory to save results"
    )
    parser.add_argument(
        "--autoscaling",
        action="store_true",
        help="Enable public cloud autoscaling (default: False, fixed 2 instances)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root_dir = Path(__file__).resolve().parent

    config_path = root_dir / args.config
    if not config_path.exists():
        print(f"ERROR: Configuration file not found: {config_path}")
        return 1

    workload_path = root_dir / "data" / "workloads" / f"{args.workload}.jsonl"
    if not workload_path.exists():
        print(f"ERROR: Workload trace not found: {workload_path}")
        return 1

    default_subdir = "hybrid_autoscaling" if args.autoscaling else "hybrid_cloud"
    out_dir = Path(args.output_dir) if args.output_dir else (root_dir / "results" / "raw" / default_subdir / args.workload)

    print("=" * 70)
    print("DIGITAL BANKING SYSTEM — SECURE HYBRID CLOUD SIMULATION")
    print(f"Workload: {args.workload} | Seed: {args.seed} | Autoscaling: {args.autoscaling}")
    print(f"Trace Source: {workload_path.name}")
    print(f"Output Directory: {out_dir}")
    print("=" * 70)

    try:
        engine = SimulationEngine(
            config_path=config_path,
            workload_path=workload_path,
            seed=args.seed,
            max_events=args.max_events
        )
        print(f"Loaded {len(engine.workload_events):,} workload events. Running hybrid-cloud simulation...")
        summary = engine.run_hybrid_cloud(output_dir=out_dir, autoscaling_enabled=args.autoscaling)

        print("\nSimulation Completed Successfully!")
        print("-" * 50)
        req = summary["request_accounting"]
        perf = summary["performance_metrics"]
        res = summary["resource_utilization"]
        tier = summary.get("tier_breakdown", {})

        print(f"Total Requests:       {req['total_requests']:,}")
        print(f"Completed Requests:   {req['completed_requests']:,}")
        print(f"Dropped Requests:     {req['dropped_requests']:,}")
        print(f"Availability:         {req['availability_pct']:.2f}%")
        print(f"Throughput:           {perf['throughput_rps']:.2f} RPS")
        print(f"Avg Response Time:    {perf['avg_response_time_ms']:.2f} ms")
        print(f"Median Response Time: {perf['median_response_time_ms']:.2f} ms")
        print(f"P95 Response Time:    {perf['p95_response_time_ms']:.2f} ms")
        print(f"P99 Response Time:    {perf['p99_response_time_ms']:.2f} ms")
        print(f"Mean Queue Wait Time: {perf['mean_waiting_time_ms']:.2f} ms")
        print(f"Avg Server Util:      {res['avg_server_utilization_pct']:.2f}%")
        print(f"Peak Server Util:     {res['peak_server_utilization_pct']:.2f}%")
        print(f"Avg DB Util:          {res['avg_database_utilization_pct']:.2f}%")
        print(f"Max Queue Length:     {res['max_queue_length']:,}")

        if tier:
            priv = tier.get("private_tier", {})
            pub = tier.get("public_tier", {})
            rout = tier.get("routing_summary", {})
            print("\nTier Breakdown:")
            print(f"  Private Tier ({priv.get('total_cores', 48)} cores): {priv.get('completed_requests', 0):,} served ({rout.get('private_ratio_pct', 0)}%) | Util: {priv.get('avg_utilization_pct', 0)}% | Avg Latency: {priv.get('avg_response_time_ms', 0)} ms")
            print(f"  Public Tier  ({pub.get('total_cores', 8)} cores):  {pub.get('completed_requests', 0):,} served ({rout.get('public_ratio_pct', 0)}%) | Util: {pub.get('avg_utilization_pct', 0)}% | Avg Latency: {pub.get('avg_response_time_ms', 0)} ms")

        print("-" * 50)
        print(f"Results saved to: {out_dir}")
        return 0

    except Exception as e:
        print(f"SIMULATION ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
