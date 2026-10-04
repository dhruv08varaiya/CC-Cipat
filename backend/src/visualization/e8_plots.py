"""
e8_plots.py
Stage 9 Publication Figure Generator for Experiment E8 (Financial TCO & Pareto Analysis).
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def generate_e8_figures(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    # Figure 1: 3-Year TCO CapEx vs OpEx Breakdown
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    categories = ['Legacy On-Premise', 'Secure Hybrid Cloud']
    capex = [220.0, 140.0]  # in $1,000 USD
    opex = [594.0, 522.0]   # $16.5k * 36 vs $14.5k * 36

    width = 0.55
    p1 = ax.bar(categories, capex, width, label='CapEx (Hardware/Licensing)', color='#6366f1')
    p2 = ax.bar(categories, opex, width, bottom=capex, label='3-Year OpEx (Power, DC, Staff, Cloud)', color='#0ea5e9')

    ax.set_ylabel('3-Year Total Cost ($ in Thousands USD)', fontweight="bold")
    ax.set_title('E8.1: 3-Year Total Cost of Ownership (TCO) Comparison', fontsize=12, fontweight="bold")
    ax.legend()

    for rect in p2:
        height = rect.get_height() + rect.get_y()
        ax.annotate(f'${height:.0f}K',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold')

    fig.tight_layout()
    fig.savefig(output_dir / "1_e8_tco_3year_comparison.png")
    plt.close(fig)

    # Figure 2: Cost vs. Latency Pareto Frontier
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    costs = [22611, 17800, 18388, 31200]
    latencies = [112.5, 98.4, 61.4, 78.2]
    labels = [
        "Legacy On-Premise\n(64 Fixed Cores)",
        "Fixed Hybrid Cloud\n(No Autoscaling)",
        "Elastic Hybrid Cloud\n(Autoscaled) ⭐ PARETO",
        "100% Public Cloud\n(No Private DC)"
    ]
    colors = ['#ef4444', '#f59e0b', '#10b981', '#64748b']

    for i in range(len(costs)):
        ax.scatter(costs[i], latencies[i], s=180, color=colors[i], zorder=5)
        ax.annotate(labels[i], (costs[i], latencies[i]),
                    xytext=(0, 10 if i!=2 else -25), textcoords="offset points",
                    ha='center', fontsize=9, fontweight='bold')

    ax.set_title("E8.2: Cost-Performance Pareto Frontier (Monthly Cost vs P95 Latency)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Monthly Operational Cost ($ USD)", fontweight="bold")
    ax.set_ylabel("P95 Transaction Latency (ms)", fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.6)
    fig.tight_layout()
    fig.savefig(output_dir / "2_e8_pareto_frontier.png")
    plt.close(fig)

    print(f"[+] Generated E8 publication figures in {output_dir}")

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent.parent / "results" / "figures" / "E8"
    generate_e8_figures(out)
