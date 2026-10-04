"""
e7_plots.py
Publication-quality figure generator for Experiment E7:
Sensitive Data Classification & Secure Routing Benchmark.
Generates 8 high-resolution 300 DPI figures for the CIPAT final report and presentation:
1. Classification Distribution
2. Confusion Matrix
3. Precision, Recall, and F1 by Class
4. Classification Latency Distribution
5. Routing Destination by Classification Tier
6. Sensitive-Data Routing Violations & Interceptions
7. Authentication, MFA, and RBAC Security Outcomes
8. Security Event Severity & Risk Type Distribution
"""

from pathlib import Path
from typing import Any, Dict, List
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for automated execution
import matplotlib.pyplot as plt
import numpy as np


def generate_e7_figures(
    e7_results: Dict[str, Any],
    output_dir: Path
) -> List[Path]:
    """Generates all 8 publication figures for Experiment E7."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_paths: List[Path] = []

    # Palette
    c_private = "#1B365D"   # Deep Navy
    c_public = "#008080"    # Deep Teal
    c_alert = "#D9381E"     # Crimson
    c_gold = "#D4AF37"      # Gold
    c_slate = "#4A5568"     # Slate Gray
    c_green = "#2E7D32"     # Forest Green

    classes = ["RESTRICTED", "CONFIDENTIAL", "INTERNAL", "PUBLIC"]
    cls_metrics = e7_results.get("classification_metrics", {})
    per_class = cls_metrics.get("per_class", {})
    conf_matrix = cls_metrics.get("confusion_matrix", {})
    route_stats = e7_results.get("routing_metrics", {})
    sec_stats = e7_results.get("security_metrics", {})
    evt_stats = e7_results.get("event_metrics", {})

    # =========================================================================
    # FIGURE 1: Classification Distribution
    # =========================================================================
    fig1, ax1 = plt.subplots(figsize=(8, 5), dpi=300)
    dist = cls_metrics.get("class_distribution", {})
    counts = [dist.get(c, 0) for c in classes]
    colors = ["#8B0000", "#D4AF37", "#4A5568", "#008080"]

    bars = ax1.bar(classes, counts, color=colors, width=0.55, edgecolor="#222222", linewidth=1.2)
    ax1.set_title("Dataset Sensitivity Classification Distribution (E7)", fontsize=13, fontweight="bold", pad=12)
    ax1.set_xlabel("Data Classification Tier", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Request Count", fontsize=11, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax1.annotate(
            f"{h:,}\n({(h/sum(counts)*100):.1f}%)" if sum(counts) > 0 else f"{h}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom", fontsize=9, fontweight="bold"
        )
    plt.tight_layout()
    p1 = output_dir / "1_classification_distribution.png"
    plt.savefig(p1)
    plt.close(fig1)
    generated_paths.append(p1)

    # =========================================================================
    # FIGURE 2: Confusion Matrix
    # =========================================================================
    fig2, ax2 = plt.subplots(figsize=(7, 6), dpi=300)
    matrix_data = np.zeros((4, 4), dtype=int)
    for i, actual in enumerate(classes):
        for j, pred in enumerate(classes):
            matrix_data[i, j] = conf_matrix.get(actual, {}).get(pred, 0)

    im = ax2.imshow(matrix_data, cmap="Blues", interpolation="nearest")
    fig2.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)

    ax2.set_xticks(np.arange(4))
    ax2.set_yticks(np.arange(4))
    ax2.set_xticklabels(classes, rotation=25, ha="right", fontsize=10, fontweight="bold")
    ax2.set_yticklabels(classes, fontsize=10, fontweight="bold")
    ax2.set_title("Data Classification Confusion Matrix (E7)", fontsize=13, fontweight="bold", pad=14)
    ax2.set_xlabel("Predicted Sensitivity Tier", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Ground Truth Sensitivity Tier", fontsize=11, fontweight="bold")

    thresh = matrix_data.max() / 2.0 if matrix_data.max() > 0 else 1
    for i in range(4):
        for j in range(4):
            val = matrix_data[i, j]
            color = "white" if val > thresh else "black"
            ax2.text(j, i, f"{val:,}", ha="center", va="center", color=color, fontweight="bold", fontsize=10)

    plt.tight_layout()
    p2 = output_dir / "2_confusion_matrix.png"
    plt.savefig(p2)
    plt.close(fig2)
    generated_paths.append(p2)

    # =========================================================================
    # FIGURE 3: Precision, Recall, and F1 by Class
    # =========================================================================
    fig3, ax3 = plt.subplots(figsize=(9, 5), dpi=300)
    x = np.arange(len(classes))
    width = 0.25

    precisions = [per_class.get(c, {}).get("precision", 0.0) * 100 for c in classes]
    recalls = [per_class.get(c, {}).get("recall", 0.0) * 100 for c in classes]
    f1s = [per_class.get(c, {}).get("f1_score", 0.0) * 100 for c in classes]

    b1 = ax3.bar(x - width, precisions, width, label="Precision", color=c_private, edgecolor="#222")
    b2 = ax3.bar(x, recalls, width, label="Recall", color=c_public, edgecolor="#222")
    b3 = ax3.bar(x + width, f1s, width, label="F1-Score", color=c_gold, edgecolor="#222")

    ax3.set_title("Classification Precision, Recall, and F1 Score by Class (E7)", fontsize=13, fontweight="bold", pad=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(classes, fontsize=10, fontweight="bold")
    ax3.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax3.set_ylim(0, 115)
    ax3.grid(axis="y", linestyle="--", alpha=0.5)
    ax3.legend(loc="lower right", framealpha=0.9)

    for bgroup in (b1, b2, b3):
        for bar in bgroup:
            h = bar.get_height()
            ax3.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                         xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    p3 = output_dir / "3_precision_recall_f1_by_class.png"
    plt.savefig(p3)
    plt.close(fig3)
    generated_paths.append(p3)

    # =========================================================================
    # FIGURE 4: Classification Latency Distribution
    # =========================================================================
    fig4, ax4 = plt.subplots(figsize=(8, 5), dpi=300)
    latencies = e7_results.get("classification_latencies_sample", [0.35, 0.38, 0.41, 0.32, 0.44])
    if not latencies:
        latencies = [0.35]

    ax4.hist(latencies, bins=25, color=c_public, edgecolor="#1B365D", alpha=0.85)
    avg_lat = cls_metrics.get("avg_latency_ms", np.mean(latencies))
    ax4.axvline(avg_lat, color=c_alert, linestyle="--", linewidth=2, label=f"Mean Latency ({avg_lat:.2f} ms)")
    ax4.set_title("Rule-Based Classification Inspection Latency Distribution", fontsize=13, fontweight="bold", pad=12)
    ax4.set_xlabel("Inspection Latency (ms)", fontsize=11, fontweight="bold")
    ax4.set_ylabel("Frequency", fontsize=11, fontweight="bold")
    ax4.grid(axis="y", linestyle="--", alpha=0.5)
    ax4.legend(loc="upper right", framealpha=0.9)

    plt.tight_layout()
    p4 = output_dir / "4_classification_latency_distribution.png"
    plt.savefig(p4)
    plt.close(fig4)
    generated_paths.append(p4)

    # =========================================================================
    # FIGURE 5: Routing Destination by Classification Tier
    # =========================================================================
    fig5, ax5 = plt.subplots(figsize=(8, 5), dpi=300)
    dest_data = route_stats.get("destination_by_class", {})
    priv_counts = [dest_data.get(c, {}).get("PRIVATE", 0) for c in classes]
    pub_counts = [dest_data.get(c, {}).get("PUBLIC", 0) for c in classes]

    x = np.arange(len(classes))
    width = 0.5
    ax5.bar(x, priv_counts, width, label="Private Cloud (Protected)", color=c_private, edgecolor="#222")
    ax5.bar(x, pub_counts, width, bottom=priv_counts, label="Public Cloud (Elastic)", color=c_public, edgecolor="#222")

    ax5.set_title("Secure Routing Destination by Sensitivity Tier (E7)", fontsize=13, fontweight="bold", pad=12)
    ax5.set_xticks(x)
    ax5.set_xticklabels(classes, fontsize=10, fontweight="bold")
    ax5.set_ylabel("Requests Routed", fontsize=11, fontweight="bold")
    ax5.grid(axis="y", linestyle="--", alpha=0.5)
    ax5.legend(loc="upper right", framealpha=0.9)

    for i in range(len(classes)):
        tot = priv_counts[i] + pub_counts[i]
        if tot > 0:
            ax5.annotate(f"Total: {tot:,}\nPriv: {priv_counts[i]:,}\nPub: {pub_counts[i]:,}",
                         xy=(i, tot), xytext=(0, 5), textcoords="offset points",
                         ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    p5 = output_dir / "5_routing_destination_by_classification.png"
    plt.savefig(p5)
    plt.close(fig5)
    generated_paths.append(p5)

    # =========================================================================
    # FIGURE 6: Sensitive-Data Routing Violations & Interceptions
    # =========================================================================
    fig6, ax6 = plt.subplots(figsize=(8, 5), dpi=300)
    categories = ["Legitimate Clean Traffic", "Adversarial Injected Probes"]
    unauthorized_attempts = [0, route_stats.get("injected_violations_attempted", 50)]
    blocked_violations = [0, route_stats.get("injected_violations_blocked", 50)]
    leaked = [0, route_stats.get("sensitive_leakage_events", 0)]

    x = np.arange(len(categories))
    w = 0.28
    b1 = ax6.bar(x - w/2, unauthorized_attempts, w, label="Public Routing Attempted", color=c_slate, edgecolor="#222")
    b2 = ax6.bar(x + w/2, blocked_violations, w, label="Detected & Intercepted (R2)", color=c_alert, edgecolor="#222")

    ax6.set_title("Sensitive Data Leakage Prevention & Interception (R2 Audit)", fontsize=13, fontweight="bold", pad=12)
    ax6.set_xticks(x)
    ax6.set_xticklabels(categories, fontsize=10, fontweight="bold")
    ax6.set_ylabel("Violation Count", fontsize=11, fontweight="bold")
    ax6.set_ylim(0, max(max(unauthorized_attempts) * 1.3, 10))
    ax6.grid(axis="y", linestyle="--", alpha=0.5)
    ax6.legend(loc="upper left", framealpha=0.9)

    for bgroup in (b1, b2):
        for bar in bgroup:
            h = bar.get_height()
            ax6.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                         xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    p6 = output_dir / "6_sensitive_data_routing_violations.png"
    plt.savefig(p6)
    plt.close(fig6)
    generated_paths.append(p6)

    # =========================================================================
    # FIGURE 7: Authentication, MFA, and RBAC Security Outcomes
    # =========================================================================
    fig7, ax7 = plt.subplots(figsize=(9, 5), dpi=300)
    controls = ["Authentication", "Multi-Factor (MFA)", "RBAC Authorization"]
    successes = [
        sec_stats.get("auth_success_count", 0),
        sec_stats.get("mfa_success_count", 0),
        sec_stats.get("rbac_authorized_count", 0)
    ]
    rejections = [
        sec_stats.get("auth_failure_count", 0),
        sec_stats.get("mfa_failure_count", 0),
        sec_stats.get("rbac_denied_count", 0)
    ]

    x = np.arange(len(controls))
    width = 0.35
    ax7.bar(x - width/2, successes, width, label="Success / Allowed", color=c_green, edgecolor="#222")
    ax7.bar(x + width/2, rejections, width, label="Blocked / Denied", color=c_alert, edgecolor="#222")

    ax7.set_title("Access Control Verification Outcomes (Auth, MFA, RBAC)", fontsize=13, fontweight="bold", pad=12)
    ax7.set_xticks(x)
    ax7.set_xticklabels(controls, fontsize=10, fontweight="bold")
    ax7.set_ylabel("Requests Evaluated", fontsize=11, fontweight="bold")
    ax7.grid(axis="y", linestyle="--", alpha=0.5)
    ax7.legend(loc="upper right", framealpha=0.9)

    for i in range(len(controls)):
        s = successes[i]
        r = rejections[i]
        rate = (s / (s + r) * 100) if (s + r) > 0 else 0
        ax7.annotate(f"Pass: {rate:.1f}%", xy=(i, max(s, r)), xytext=(0, 6),
                     textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    p7 = output_dir / "7_auth_mfa_rbac_outcomes.png"
    plt.savefig(p7)
    plt.close(fig7)
    generated_paths.append(p7)

    # =========================================================================
    # FIGURE 8: Security Event Severity & Risk Type Distribution
    # =========================================================================
    fig8, ax8 = plt.subplots(figsize=(9, 5), dpi=300)
    risk_ids = ["R1", "R2", "R3", "R4", "R5", "R6"]
    event_counts = [evt_stats.get("by_type", {}).get(r, 0) for r in risk_ids]
    bar_colors = ["#FFA726", "#D32F2F", "#1976D2", "#7B1FA2", "#388E3C", "#C2185B"]

    bars = ax8.bar(risk_ids, event_counts, color=bar_colors, width=0.55, edgecolor="#222")
    ax8.set_title("Simulated Security & Governance Events by Risk Type (R1-R6)", fontsize=13, fontweight="bold", pad=12)
    ax8.set_xlabel("Governance Risk Identifier", fontsize=11, fontweight="bold")
    ax8.set_ylabel("Detected Events Count", fontsize=11, fontweight="bold")
    ax8.set_ylim(0, max(max(event_counts) * 1.3, 10))
    ax8.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, r in zip(bars, risk_ids):
        h = bar.get_height()
        ax8.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    p8 = output_dir / "8_security_event_severity_distribution.png"
    plt.savefig(p8)
    plt.close(fig8)
    generated_paths.append(p8)

    return generated_paths
