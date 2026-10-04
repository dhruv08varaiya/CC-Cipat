"""
e4_plots.py
Generates academic publication-quality figures for Experiment E4:
Burst Workload & Public Cloud Autoscaling Dynamics.
Outputs are saved to results/figures/E4/.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_e4_figures(
    fixed_raw_dir: Path,
    auto_raw_dir: Path,
    output_fig_dir: Path,
    w4_workload_path: Path
) -> List[Path]:
    """Generates all 8 required experiment figures for E4."""
    output_fig_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []

    # Configure publication aesthetic
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "figure.dpi": 300
    })

    # Load time series
    df_fixed = pd.read_csv(fixed_raw_dir / "time_series.csv")
    df_auto = pd.read_csv(auto_raw_dir / "time_series.csv")

    # Load requests
    reqs_fixed = []
    with open(fixed_raw_dir / "raw_requests.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                reqs_fixed.append(json.loads(line))
    df_req_fixed = pd.DataFrame(reqs_fixed)

    reqs_auto = []
    with open(auto_raw_dir / "raw_requests.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                reqs_auto.append(json.loads(line))
    df_req_auto = pd.DataFrame(reqs_auto)

    # Load scaling events
    scaling_events = []
    scaling_file = auto_raw_dir / "scaling_events.jsonl"
    if scaling_file.exists():
        with open(scaling_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    scaling_events.append(json.loads(line))

    # -------------------------------------------------------------
    # 1. W4 Arrival Rate vs Time
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    w4_times = []
    w4_rates = []
    with open(w4_workload_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                w4_times.append(d["timestamp_sec"])
                w4_rates.append(d.get("arrival_rate_rps", 600.0))

    ax.plot(w4_times, w4_rates, color="#1f77b4", linewidth=2.0, label="Workload W4 Offered Load")
    ax.axvline(x=6.0, color="#d62728", linestyle="--", linewidth=1.5, label="Burst Inception (t = 6.0s)")
    ax.set_title("Figure 1: W4 Burst Workload Arrival Rate Profile")
    ax.set_xlabel("Simulation Elapsed Time (seconds)")
    ax.set_ylabel("Arrival Rate (Requests per Second)")
    ax.set_ylim(0, 3200)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)
    p1 = output_fig_dir / "1_w4_arrival_rate_vs_time.png"
    fig.tight_layout()
    fig.savefig(p1)
    plt.close(fig)
    generated_files.append(p1)

    # -------------------------------------------------------------
    # 2. Public-Cloud Utilization vs Time (Fixed vs Autoscaling)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(
        df_fixed["timestamp_sec"],
        df_fixed["public_utilization_pct"],
        color="#d62728",
        linewidth=2.0,
        label="Hybrid Fixed (2 instances / 8 cores)"
    )
    ax.plot(
        df_auto["timestamp_sec"],
        df_auto["public_utilization_pct"],
        color="#2ca02c",
        linewidth=2.0,
        linestyle="-",
        label="Hybrid Autoscaling (2–20 instances)"
    )
    ax.axhline(y=70.0, color="#ff7f0e", linestyle=":", linewidth=1.5, label="Scale-Out Threshold (70%)")
    ax.axhline(y=35.0, color="#17becf", linestyle=":", linewidth=1.5, label="Scale-In Threshold (35%)")
    ax.set_title("Figure 2: Public Cloud Utilization Dynamics (Fixed vs Autoscaling)")
    ax.set_xlabel("Simulation Elapsed Time (seconds)")
    ax.set_ylabel("Simulated Resource Utilization (%)")
    ax.set_ylim(-5, 110)
    ax.legend(loc="lower right")
    ax.grid(True, linestyle=":", alpha=0.6)
    p2 = output_fig_dir / "2_public_utilization_vs_time.png"
    fig.tight_layout()
    fig.savefig(p2)
    plt.close(fig)
    generated_files.append(p2)

    # -------------------------------------------------------------
    # 3. Active Public Instances vs Time
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    inst_col = "public_instances" if "public_instances" in df_auto.columns else None
    if inst_col:
        ax.step(
            df_auto["timestamp_sec"],
            df_auto[inst_col],
            where="post",
            color="#2ca02c",
            linewidth=2.2,
            label="Active Public Instances"
        )
    ax.axhline(y=2, color="#7f7f7f", linestyle="--", linewidth=1.2, label="Min Instances (2)")
    ax.axhline(y=20, color="#d62728", linestyle="--", linewidth=1.2, label="Max Instances (20)")
    ax.set_title("Figure 3: Active Public Cloud Instances Over Time")
    ax.set_xlabel("Simulation Elapsed Time (seconds)")
    ax.set_ylabel("Instance Count")
    ax.set_ylim(0, 22)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)
    p3 = output_fig_dir / "3_active_public_instances_vs_time.png"
    fig.tight_layout()
    fig.savefig(p3)
    plt.close(fig)
    generated_files.append(p3)

    # -------------------------------------------------------------
    # 4. Public Queue Length vs Time (Fixed vs Autoscaling)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    q_col = "public_queue_length" if "public_queue_length" in df_fixed.columns else "queue_length"
    ax.plot(
        df_fixed["timestamp_sec"],
        df_fixed[q_col],
        color="#d62728",
        linewidth=2.0,
        label="Hybrid Fixed (No Autoscaling)"
    )
    ax.plot(
        df_auto["timestamp_sec"],
        df_auto[q_col],
        color="#2ca02c",
        linewidth=2.0,
        label="Hybrid Autoscaling"
    )
    ax.set_title("Figure 4: Public Tier Queue Backlog Dynamics")
    ax.set_xlabel("Simulation Elapsed Time (seconds)")
    ax.set_ylabel("Queued Request Count")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)
    p4 = output_fig_dir / "4_public_queue_length_vs_time.png"
    fig.tight_layout()
    fig.savefig(p4)
    plt.close(fig)
    generated_files.append(p4)

    # -------------------------------------------------------------
    # 5. Average/Rolling Response Time vs Time
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    comp_fixed = df_req_fixed[df_req_fixed["status"] == "COMPLETED"].sort_values("completion_time_sec")
    comp_auto = df_req_auto[df_req_auto["status"] == "COMPLETED"].sort_values("completion_time_sec")

    if not comp_fixed.empty:
        comp_fixed["rolling_rt"] = comp_fixed["total_response_time_ms"].rolling(window=100, min_periods=10).mean()
        ax.plot(
            comp_fixed["completion_time_sec"],
            comp_fixed["rolling_rt"],
            color="#d62728",
            linewidth=1.8,
            label="Hybrid Fixed (Rolling 100-req Avg)"
        )
    if not comp_auto.empty:
        comp_auto["rolling_rt"] = comp_auto["total_response_time_ms"].rolling(window=100, min_periods=10).mean()
        ax.plot(
            comp_auto["completion_time_sec"],
            comp_auto["rolling_rt"],
            color="#2ca02c",
            linewidth=1.8,
            label="Hybrid Autoscaling (Rolling 100-req Avg)"
        )

    ax.set_title("Figure 5: Rolling Average End-to-End Latency Profile")
    ax.set_xlabel("Completion Time (seconds)")
    ax.set_ylabel("Latency (ms)")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)
    p5 = output_fig_dir / "5_rolling_response_time_vs_time.png"
    fig.tight_layout()
    fig.savefig(p5)
    plt.close(fig)
    generated_files.append(p5)

    # -------------------------------------------------------------
    # 6. Fixed vs Autoscaling Response Time Percentiles
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    with open(fixed_raw_dir / "summary_metrics.json", "r", encoding="utf-8") as f:
        s_fixed = json.load(f)["performance_metrics"]
    with open(auto_raw_dir / "summary_metrics.json", "r", encoding="utf-8") as f:
        s_auto = json.load(f)["performance_metrics"]

    metrics_names = ["Avg", "Median", "P95", "P99"]
    vals_fixed = [
        s_fixed["avg_response_time_ms"],
        s_fixed["median_response_time_ms"],
        s_fixed["p95_response_time_ms"],
        s_fixed["p99_response_time_ms"]
    ]
    vals_auto = [
        s_auto["avg_response_time_ms"],
        s_auto["median_response_time_ms"],
        s_auto["p95_response_time_ms"],
        s_auto["p99_response_time_ms"]
    ]

    x = np.arange(len(metrics_names))
    width = 0.35
    rects1 = ax.bar(x - width/2, vals_fixed, width, label="Hybrid Fixed", color="#d62728", alpha=0.85)
    rects2 = ax.bar(x + width/2, vals_auto, width, label="Hybrid Autoscaling", color="#2ca02c", alpha=0.85)

    ax.set_title("Figure 6: Response Time Benchmark Comparison (Percentiles)")
    ax.set_ylabel("Response Time (ms)")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names)
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.6)

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

    p6 = output_fig_dir / "6_response_time_comparison.png"
    fig.tight_layout()
    fig.savefig(p6)
    plt.close(fig)
    generated_files.append(p6)

    # -------------------------------------------------------------
    # 7. Fixed vs Autoscaling Queue Length Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 4.5))
    with open(fixed_raw_dir / "summary_metrics.json", "r", encoding="utf-8") as f:
        res_fixed = json.load(f)["resource_utilization"]
    with open(auto_raw_dir / "summary_metrics.json", "r", encoding="utf-8") as f:
        res_auto = json.load(f)["resource_utilization"]

    q_labels = ["Average Queue", "Maximum Queue"]
    q_fixed = [res_fixed["avg_queue_length"], res_fixed["max_queue_length"]]
    q_auto = [res_auto["avg_queue_length"], res_auto["max_queue_length"]]

    x = np.arange(len(q_labels))
    width = 0.35
    r1 = ax.bar(x - width/2, q_fixed, width, label="Hybrid Fixed", color="#d62728", alpha=0.85)
    r2 = ax.bar(x + width/2, q_auto, width, label="Hybrid Autoscaling", color="#2ca02c", alpha=0.85)

    ax.set_title("Figure 7: Queue Backlog Comparison")
    ax.set_ylabel("Queued Requests")
    ax.set_xticks(x)
    ax.set_xticklabels(q_labels)
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.6)

    for rect in r1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    for rect in r2:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

    p7 = output_fig_dir / "7_queue_length_comparison.png"
    fig.tight_layout()
    fig.savefig(p7)
    plt.close(fig)
    generated_files.append(p7)

    # -------------------------------------------------------------
    # 8. Scaling Events Over Time
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if scaling_events:
        times_out = [e["timestamp_sec"] for e in scaling_events if e["event_type"] == "SCALE_OUT"]
        inst_out = [e["new_instance_count"] for e in scaling_events if e["event_type"] == "SCALE_OUT"]
        times_in = [e["timestamp_sec"] for e in scaling_events if e["event_type"] == "SCALE_IN"]
        inst_in = [e["new_instance_count"] for e in scaling_events if e["event_type"] == "SCALE_IN"]

        if times_out:
            ax.scatter(times_out, inst_out, color="#2ca02c", s=80, marker="^", label="Scale-Out Event", zorder=5)
        if times_in:
            ax.scatter(times_in, inst_in, color="#ff7f0e", s=80, marker="v", label="Scale-In Event", zorder=5)

        # Plot instance trajectory
        if inst_col:
            ax.step(df_auto["timestamp_sec"], df_auto[inst_col], where="post", color="#1f77b4", alpha=0.5, label="Instance Trajectory")
    else:
        ax.text(0.5, 0.5, "No Scaling Events Recorded", ha="center", va="center", transform=ax.transAxes)

    ax.set_title("Figure 8: Scaling Events and Elasticity Trajectory Timeline")
    ax.set_xlabel("Simulation Elapsed Time (seconds)")
    ax.set_ylabel("Instance Count")
    ax.set_ylim(0, 22)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)
    p8 = output_fig_dir / "8_scaling_events_timeline.png"
    fig.tight_layout()
    fig.savefig(p8)
    plt.close(fig)
    generated_files.append(p8)

    return generated_files
