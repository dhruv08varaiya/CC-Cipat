"""
run_on_premise_sim.py
Command-line interface to execute the On-Premise Baseline discrete-event simulation.
Usage:
    python run_on_premise_sim.py --workload W1
    python run_on_premise_sim.py --workload W2 --seed 42
    python run_on_premise_sim.py --workload W3 --config config/simulation_config.json
"""

import argparse
import json
from pathlib import Path
import sys

from src.simulation.engine import SimulationEngine


def parse_args():
    parser = argparse.ArgumentParser(description="Run On-Premise Baseline Banking Simulation.")
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
        help="Optional limit on number of workload events to process (useful for calibration)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory to save results (defaults to results/raw/on_premise/<workload>)"
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

    out_dir = Path(args.output_dir) if args.output_dir else (root_dir / "results" / "raw" / "on_premise" / args.workload)

    print("=" * 70)
    print("DIGITAL BANKING SYSTEM — ON-PREMISE BASELINE SIMULATION")
    print(f"Workload: {args.workload} | Seed: {args.seed}")
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
        print(f"Loaded {len(engine.workload_events):,} workload events. Running discrete-event simulation...")
        summary = engine.run_on_premise(output_dir=out_dir)

        print("\nSimulation Completed Successfully!")
        print("-" * 50)
        req = summary["request_accounting"]
        perf = summary["performance_metrics"]
        res = summary["resource_utilization"]

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
