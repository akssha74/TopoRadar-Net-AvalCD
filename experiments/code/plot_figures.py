#!/usr/bin/env python3
"""Generate publication-quality figures for the Journal of Mountain Science paper."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

FIGS_DIR = Path("studies/mountain-avalcd-toporadar/paper/figures")
FIGS_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.linewidth"] = 0.8

EDGE = "#748292"
GRID = "#D6DEE6"
PASTEL_BLUE = "#AFCBE6"
PASTEL_ORANGE = "#F3C49D"
PASTEL_GREEN = "#B8DCC6"

def plot_performance_barchart():
    """Figure: Comparative Cross-System Performance Bar Chart."""
    models = ["SiamUNet-diff", "SiamUNet-conc", "ResU-Net", "Attention U-Net", "TopoRadar-Net (Ours)"]
    tromso_f1 = [72.64, 78.92, 76.60, 78.09, 77.40]
    tromso_err = [0.39, 1.07, 1.30, 0.99, 1.86]
    
    pamir_f1 = [37.11, 47.34, 49.25, 48.73, 50.18]
    pamir_err = [2.44, 0.70, 3.39, 2.74, 4.40]

    pooled_f1 = [54.87, 63.13, 62.92, 63.41, 63.79]
    pooled_err = [1.03, 0.79, 1.42, 1.03, 1.88]

    x = np.arange(len(models))
    width = 0.26

    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    rects1 = ax.bar(x - width, tromso_f1, width, yerr=tromso_err, label="Scandinavian Arctic (Tromsø)", color=PASTEL_BLUE, capsize=3, edgecolor=EDGE, lw=0.7)
    rects2 = ax.bar(x, pamir_f1, width, yerr=pamir_err, label="Pamir Mountains (Pish)", color=PASTEL_ORANGE, capsize=3, edgecolor=EDGE, lw=0.7)
    rects3 = ax.bar(x + width, pooled_f1, width, yerr=pooled_err, label="Pooled Cross-System Benchmark", color=PASTEL_GREEN, capsize=3, edgecolor=EDGE, lw=0.7)

    ax.set_ylabel("Pixel F1-Score (%)", fontsize=11)
    ax.set_title("Zero-Shot Cross-System Generalization on Unseen Mountain Ranges", fontsize=12, weight="semibold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=10, weight="medium")
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e0", fontsize=9.5)
    ax.set_ylim(0, 95)
    ax.grid(axis="y", color=GRID, linestyle="--", linewidth=0.7, alpha=0.8)

    for rects in [rects1, rects2, rects3]:
        rects[-1].set_edgecolor("#5F7F70")
        rects[-1].set_linewidth(1.2)

    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig_performance_comparison.pdf", bbox_inches="tight")
    fig.savefig(FIGS_DIR / "fig_performance_comparison.png", bbox_inches="tight", dpi=300)
    print(f"Generated {FIGS_DIR / 'fig_performance_comparison.pdf'}")

def plot_instance_eaws_hitrate():
    """Figure: Instance-level hit rate across EAWS avalanche size classes."""
    classes = ["D1: Small\n(<100 m³)", "D2: Medium\n(100-1,000 m³)", "D3: Large\n(1,000-10,000 m³)", "D4: Very Large\n(>10,000 m³)", "Overall\n(n=117)"]
    siam_diff = [6.7, 33.3, 71.8, 89.6, 63.2]
    resunet = [6.7, 53.3, 85.9, 95.8, 76.9]
    swin = [6.7, 58.7, 86.9, 100.0, 79.2]
    siam_conc = [13.3, 61.3, 91.1, 100.0, 82.6]
    toporadar = [20.0, 49.3, 84.0, 95.8, 75.5]

    x = np.arange(len(classes))
    width = 0.16

    fig, ax = plt.subplots(figsize=(11, 5), dpi=300)
    ax.bar(x - 2.0*width, siam_diff, width, label="SiamUNet-diff", color="#D5DDE5", edgecolor=EDGE, lw=0.7)
    ax.bar(x - 1.0*width, resunet, width, label="ResU-Net", color="#BDD7EE", edgecolor=EDGE, lw=0.7)
    ax.bar(x, swin, width, label="Attention U-Net", color="#F6D0A8", edgecolor=EDGE, lw=0.7)
    ax.bar(x + 1.0*width, siam_conc, width, label="SiamUNet-conc", color="#D8C7EA", edgecolor=EDGE, lw=0.7)
    ax.bar(x + 2.0*width, toporadar, width, label="TopoRadar-Net (Ours)", color="#B9DFC8", edgecolor="#5F7F70", lw=1.1)

    ax.set_ylabel("Instance Detection Hit Rate (%) [Area Overlap ≥ 30%]", fontsize=11)
    ax.set_title("Instance-Level Avalanche Detection Completeness across EAWS Hazard Scales", fontsize=12, weight="semibold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=10, weight="medium")
    ax.legend(frameon=True, facecolor="white", edgecolor="#cbd5e0", fontsize=9.0, ncol=3, loc="upper left")
    ax.set_ylim(0, 115)
    ax.grid(axis="y", color=GRID, linestyle="--", linewidth=0.7, alpha=0.8)

    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig_instance_hitrate_eaws.pdf", bbox_inches="tight")
    fig.savefig(FIGS_DIR / "fig_instance_hitrate_eaws.png", bbox_inches="tight", dpi=300)
    print(f"Generated {FIGS_DIR / 'fig_instance_hitrate_eaws.pdf'}")

def plot_ablation_contributions():
    """Figure: Component-wise ablation waterfall chart."""
    # Ordered from bottom to top on y-axis:
    # y=0: lowest F1 (No-LIA)
    # y=4: highest F1 (Full TopoRadar-Net)
    components = [
        "w/o Local Incidence Angle",
        "w/o Geomorphic Loss",
        "w/o Cross-Attention",
        "w/o Directional Aspect",
        "Full TopoRadar-Net"
    ]
    f1_scores = [75.67, 76.70, 76.85, 77.38, 77.40]
    drops = [-1.73, -0.70, -0.55, -0.02, 0.0]
    colors = ["#F3C2C2", "#F5D0AD", "#F7DDB8", "#C7DDF0", "#AECBE5"]

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    y = np.arange(len(components))

    bars = ax.barh(y, f1_scores, color=colors, edgecolor=EDGE, lw=0.7, height=0.55)
    ax.set_yticks(y)
    ax.set_yticklabels(components, fontsize=10, weight="medium")
    ax.set_xlabel("Pixel F1-Score on Scandinavian Arctic Test Scene (%)", fontsize=11)
    ax.set_xlim(70, 80)
    ax.grid(axis="x", color=GRID, linestyle="--", linewidth=0.7, alpha=0.8)

    for i, (b, d) in enumerate(zip(bars, drops)):
        val = b.get_width()
        text = f"{val:.2f}% (Baseline)" if d == 0.0 else f"{val:.2f}% ({d:+.2f}%)"
        ax.text(val + 0.15, b.get_y() + b.get_height()/2, text, va="center", fontsize=9.5, weight="semibold", color="#384655")

    ax.set_title("Systematic Ablation: Component Sensitivity", fontsize=11, weight="semibold", pad=10)

    plt.tight_layout()
    fig.savefig(FIGS_DIR / "fig_ablation_breakdown.pdf", bbox_inches="tight")
    fig.savefig(FIGS_DIR / "fig_ablation_breakdown.png", bbox_inches="tight", dpi=300)
    print(f"Generated {FIGS_DIR / 'fig_ablation_breakdown.pdf'}")

if __name__ == "__main__":
    plot_performance_barchart()
    plot_instance_eaws_hitrate()
    plot_ablation_contributions()
    print("All figures successfully created!")
