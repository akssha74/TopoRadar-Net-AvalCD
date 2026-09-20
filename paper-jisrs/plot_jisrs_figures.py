#!/usr/bin/env python3
"""Generate JISRS-sized result figures with non-overlapping labels."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


FIGURES = Path(__file__).resolve().parent / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

models = [
    "SiamUNet-\ndiff",
    "SiamUNet-\nconc",
    "ResU-Net",
    "Self-attn\nU-Net",
    "TopoRadar-Net\n(Ours)",
]
tromso = [72.64, 78.92, 76.60, 78.09, 77.40]
tromso_err = [0.39, 1.07, 1.30, 0.99, 1.86]
pish = [37.11, 47.34, 49.25, 48.73, 50.18]
pish_err = [2.44, 0.70, 3.39, 2.74, 4.40]
pooled = [54.87, 63.13, 62.92, 63.41, 63.79]
pooled_err = [1.03, 0.79, 1.42, 1.03, 1.88]

x = np.arange(len(models))
width = 0.25

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 12,
        "axes.linewidth": 0.8,
        "hatch.linewidth": 0.8,
    }
)

fig, ax = plt.subplots(figsize=(7.2, 4.3), dpi=300)
common = dict(capsize=3, edgecolor="#657586", linewidth=0.8)
bars_tromso = ax.bar(
    x - width,
    tromso,
    width,
    yerr=tromso_err,
    label="Scandinavian Arctic (Tromsø)",
    color="#AFCBE6",
    **common,
)
bars_pish = ax.bar(
    x,
    pish,
    width,
    yerr=pish_err,
    label="Pamir Mountains (Pish)",
    color="#EDB47F",
    hatch="//",
    **common,
)
bars_pooled = ax.bar(
    x + width,
    pooled,
    width,
    yerr=pooled_err,
    label="Pooled macro F1",
    color="#C3E0CE",
    hatch="..",
    **common,
)
for bars in (bars_tromso, bars_pish, bars_pooled):
    bars[-1].set_edgecolor("#496C5C")
    bars[-1].set_linewidth(1.2)

ax.set_ylabel("Pixel F1 (%)", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=10.5)
ax.set_ylim(0, 96)
ax.tick_params(axis="y", labelsize=11)
ax.grid(axis="y", color="#D6DEE6", linestyle="--", linewidth=0.7, alpha=0.8)
ax.legend(
    loc="lower center",
    bbox_to_anchor=(0.5, 1.01),
    ncol=3,
    frameon=True,
    facecolor="white",
    edgecolor="#CBD5E0",
    fontsize=10,
)

fig.tight_layout()
for suffix in ("pdf", "png", "eps"):
    fig.savefig(
        FIGURES / f"Fig2.{suffix}",
        bbox_inches="tight",
        dpi=600 if suffix == "png" else None,
    )
print(f"Generated {FIGURES / 'Fig2.pdf'}")
