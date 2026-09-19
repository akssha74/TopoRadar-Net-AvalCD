#!/usr/bin/env python3
"""Generate the pastel, reviewer-friendly TopoRadar-Net architecture figure."""

from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt


OUT_DIR = Path("studies/mountain-avalcd-toporadar/paper/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(10, 5.1), dpi=300)
ax.set_xlim(0, 15)
ax.set_ylim(0, 7.6)
ax.axis("off")

# Pastel fills, muted borders, dark text, and low-contrast connectors.
PALETTE = {
    "sar": ("#DCEAF7", "#7EA6C9", "#234E70"),
    "topo": ("#DFF2E7", "#7EB99A", "#245B45"),
    "fusion": ("#E7EEF6", "#91A8C0", "#354A5F"),
    "attention": ("#FAEED8", "#D7AF6C", "#75531F"),
    "gate": ("#DDF1EF", "#79B6B0", "#285E59"),
    "decoder": ("#EEE5F5", "#AA8FC1", "#5B3D73"),
    "output": ("#E7EBF0", "#9DA9B5", "#34404C"),
    "loss": ("#F8E5E3", "#CE928D", "#793D38"),
}
ARROW_COLOR = "#9AA9B9"
TRAINING_ARROW_COLOR = "#C3A09C"


def stage_panel(x, width, title):
    panel = patches.FancyBboxPatch(
        (x, 0.45),
        width,
        6.65,
        boxstyle="round,pad=0.08",
        fc="#FBFCFD",
        ec="#D9E0E7",
        lw=0.9,
        zorder=0,
    )
    ax.add_patch(panel)
    ax.text(
        x + width / 2,
        6.82,
        title,
        ha="center",
        va="center",
        fontsize=9.5,
        weight="semibold",
        color="#536273",
    )


stage_panel(0.25, 2.65, "1  Inputs")
stage_panel(3.15, 2.75, "2  Multi-scale\nencoders")
stage_panel(6.15, 5.05, "3  Radar–topographic\nconditioning")
stage_panel(11.45, 3.25, "4  Decoder\nand outputs")


def draw_box(x, y, width, height, text, key, fontsize=9, subtext=""):
    fill, edge, text_color = PALETTE[key]
    box = patches.FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.06",
        fc=fill,
        ec=edge,
        lw=1.0,
        zorder=3,
    )
    ax.add_patch(box)
    if subtext:
        ax.text(
            x + width / 2,
            y + height * 0.63,
            text,
            ha="center",
            va="center",
            weight="semibold",
            fontsize=fontsize,
            color=text_color,
            zorder=4,
        )
        ax.text(
            x + width / 2,
            y + height * 0.27,
            subtext,
            ha="center",
            va="center",
            fontsize=fontsize - 1.0,
            color="#5F6D7A",
            zorder=4,
        )
    else:
        ax.text(
            x + width / 2,
            y + height / 2,
            text,
            ha="center",
            va="center",
            weight="semibold",
            fontsize=fontsize,
            color=text_color,
            zorder=4,
        )


# Stage 1 — inputs.
draw_box(0.55, 5.75, 2.05, 0.8, "Pre-event SAR", "sar", subtext="VV, VH")
draw_box(0.55, 4.45, 2.05, 0.8, "Post-event SAR", "sar", subtext="VV, VH")
draw_box(
    0.55,
    1.75,
    2.05,
    1.35,
    "Radar–topographic\ntensor",
    "topo",
    subtext="LIA · slope · aspect\nDEM · look alignment",
)

# Stage 2 — encoders.
draw_box(
    3.45,
    5.05,
    2.15,
    1.55,
    "Shared SAR\nencoder",
    "sar",
    subtext="shared weights\nmulti-scale features",
)
draw_box(
    3.45,
    1.85,
    2.15,
    1.15,
    "Topographic\npyramid",
    "topo",
    subtext="multi-scale conv + pooling",
)

# Stage 3 — conditioning.
draw_box(
    6.45,
    5.25,
    2.05,
    0.95,
    "Difference\nfusion",
    "fusion",
    subtext="[post−pre, post, pre]",
)
draw_box(
    6.45,
    3.65,
    2.05,
    0.95,
    "Pooled topo\nK / V",
    "topo",
    subtext="8×8 regional context",
)
draw_box(
    6.45,
    1.85,
    2.05,
    0.95,
    "Spatial topo\ngate",
    "gate",
    subtext="pixel-wise conditioning",
)
draw_box(
    9.15,
    4.55,
    1.8,
    1.15,
    "RTCAB",
    "attention",
    subtext="SAR queries ×\ntopographic K / V",
)

# Stage 4 — decoder and outputs.
draw_box(
    11.80,
    4.55,
    2.55,
    1.0,
    "Progressive\ndecoder",
    "decoder",
    subtext="upsampling + skip features",
)
draw_box(
    11.80,
    2.95,
    2.55,
    1.05,
    "Avalanche\nprobability map",
    "output",
    subtext="full-scene output",
)
draw_box(
    11.80,
    1.20,
    2.55,
    1.15,
    "Geo-Loss\n(training only)",
    "loss",
    subtext="heuristic slope prior\n<5° or >65°",
)


def arrow(start, end, dashed=False):
    color = TRAINING_ARROW_COLOR if dashed else ARROW_COLOR
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=1.15,
            mutation_scale=9,
            linestyle="--" if dashed else "-",
            shrinkA=2,
            shrinkB=2,
        ),
        zorder=2,
    )


def routed_arrow(points, dashed=False):
    color = TRAINING_ARROW_COLOR if dashed else ARROW_COLOR
    xs, ys = zip(*points[:-1])
    ax.plot(
        xs,
        ys,
        color=color,
        lw=1.15,
        linestyle="--" if dashed else "-",
        solid_capstyle="round",
        zorder=1,
    )
    arrow(points[-2], points[-1], dashed=dashed)


# Straight inference paths; no connector crosses a block.
arrow((2.60, 6.15), (3.45, 6.15))
arrow((2.60, 4.85), (3.45, 5.35))
arrow((5.60, 5.82), (6.45, 5.82))
arrow((2.60, 2.42), (3.45, 2.42))
arrow((5.60, 2.42), (6.45, 4.12))
arrow((5.60, 2.42), (6.45, 2.32))
arrow((8.50, 5.72), (9.15, 5.18))
arrow((8.50, 4.12), (9.15, 4.88))
arrow((10.95, 5.12), (11.80, 5.05))
routed_arrow(
    [(8.50, 2.32), (11.32, 2.32), (11.32, 4.75), (11.80, 4.75)]
)
arrow((13.08, 4.55), (13.08, 4.00))

# Training-only loss path is dashed and visually separate.
arrow((13.08, 2.95), (13.08, 2.35), dashed=True)

ax.text(
    10.0,
    0.75,
    "solid: inference path",
    fontsize=8,
    color="#6F7D8B",
    ha="right",
)
ax.text(
    10.15,
    0.75,
    "– –  training-only loss",
    fontsize=8,
    color=TRAINING_ARROW_COLOR,
    ha="left",
)

plt.tight_layout()
fig.savefig(OUT_DIR / "fig_architecture.pdf", bbox_inches="tight")
fig.savefig(OUT_DIR / "fig_architecture.png", bbox_inches="tight", dpi=300)
print(f"Generated architecture figure at {OUT_DIR / 'fig_architecture.pdf'}")
