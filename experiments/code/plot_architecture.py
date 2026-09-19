#!/usr/bin/env python3
"""Generate the pastel, reviewer-friendly TopoRadar-Net architecture figure."""

from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt


STUDY_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = STUDY_ROOT / "paper" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(8.0, 4.06), dpi=300)
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
ARROW_COLOR = "#74869A"
TRAINING_ARROW_COLOR = "#A97874"


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
stage_panel(3.15, 2.75, "2  Encoders")
stage_panel(6.15, 5.05, "3  Conditioning")
stage_panel(11.45, 3.25, "4  Outputs")


def draw_box(x, y, width, height, text, key, fontsize=9.2, subtext=""):
    fill, edge, text_color = PALETTE[key]
    box = patches.FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.08",
        fc=fill,
        ec=edge,
        lw=1.0,
        zorder=3,
    )
    ax.add_patch(box)
    if subtext:
        main_label = ax.text(
            x + width / 2,
            y + height * 0.67,
            text,
            ha="center",
            va="center",
            multialignment="center",
            weight="semibold",
            fontsize=fontsize,
            color=text_color,
            linespacing=1.0,
            zorder=4,
        )
        main_label.set_clip_path(box)
        sub_label = ax.text(
            x + width / 2,
            y + height * 0.23,
            subtext,
            ha="center",
            va="center",
            multialignment="center",
            fontsize=fontsize,
            color="#5F6D7A",
            linespacing=1.0,
            zorder=4,
        )
        sub_label.set_clip_path(box)
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
    1.30,
    2.05,
    2.00,
    "Radar–\ntopographic\ntensor",
    "topo",
    subtext="LIA · slope\naspect · DEM\nlook alignment",
)

# Stage 2 — encoders.
draw_box(
    3.45,
    4.95,
    2.15,
    1.45,
    "Shared SAR\nencoder",
    "sar",
    subtext="shared weights\nmultiscale maps",
)
draw_box(
    3.45,
    1.75,
    2.15,
    1.25,
    "Topographic\npyramid",
    "topo",
    subtext="conv + pooling",
)

# Stage 3 — conditioning.
draw_box(
    6.45,
    5.10,
    2.05,
    1.10,
    "Difference\nfusion",
    "fusion",
    subtext="pre · post · ΔSAR",
)
draw_box(
    6.45,
    3.50,
    2.05,
    1.10,
    "Pooled topo\nK / V",
    "topo",
    subtext="8×8 context",
)
draw_box(
    6.45,
    1.80,
    2.05,
    1.10,
    "Spatial topo\ngate",
    "gate",
    subtext="pixel gate",
)
draw_box(
    9.15,
    4.45,
    1.8,
    1.25,
    "RTCAB",
    "attention",
    subtext="SAR queries\nterrain K / V",
)

# Stage 4 — decoder and outputs.
draw_box(
    11.80,
    4.40,
    2.55,
    1.20,
    "Progressive\ndecoder",
    "decoder",
    subtext="upsampling + skips",
)
draw_box(
    11.80,
    2.85,
    2.55,
    1.15,
    "Avalanche\nprobability map",
    "output",
    subtext="full-scene output",
)
draw_box(
    11.80,
    1.10,
    2.55,
    1.20,
    "Geo-Loss\n(training only)",
    "loss",
    subtext="heuristic slope prior\n<5° or >65°",
)


def arrow(start, end, dashed=False, shrink_a=2, shrink_b=2):
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
            shrinkA=shrink_a,
            shrinkB=shrink_b,
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
        solid_joinstyle="round",
        dash_joinstyle="round",
        zorder=2,
    )
    arrow(points[-2], points[-1], dashed=dashed, shrink_a=0)


# Straight inference paths; no connector crosses a block.
arrow((2.60, 6.15), (3.45, 6.15))
routed_arrow([(2.60, 4.85), (3.15, 4.85), (3.15, 5.25), (3.45, 5.25)])
arrow((5.60, 5.65), (6.45, 5.65))
arrow((2.60, 2.42), (3.45, 2.42))
routed_arrow([(5.60, 2.42), (5.95, 2.42), (5.95, 4.05), (6.45, 4.05)])
routed_arrow([(5.60, 2.42), (6.05, 2.42), (6.05, 2.35), (6.45, 2.35)])
routed_arrow([(8.50, 5.65), (8.82, 5.65), (8.82, 5.25), (9.15, 5.25)])
routed_arrow([(8.50, 4.05), (8.92, 4.05), (8.92, 4.85), (9.15, 4.85)])
arrow((10.95, 5.08), (11.80, 5.08))
routed_arrow(
    [(8.50, 2.35), (11.32, 2.35), (11.32, 4.70), (11.80, 4.70)]
)
arrow((13.08, 4.40), (13.08, 4.00))

# Training-only loss path is dashed and visually separate.
arrow((13.08, 2.85), (13.08, 2.30), dashed=True)

ax.text(
    10.0,
    0.75,
    "solid: inference path",
    fontsize=9.2,
    color="#6F7D8B",
    ha="right",
)
ax.text(
    10.15,
    0.75,
    "– –  training-only loss",
    fontsize=9.2,
    color=TRAINING_ARROW_COLOR,
    ha="left",
)

plt.tight_layout()
fig.savefig(OUT_DIR / "fig_architecture.pdf", bbox_inches="tight")
fig.savefig(OUT_DIR / "fig_architecture.png", bbox_inches="tight", dpi=300)
print(f"Generated architecture figure at {OUT_DIR / 'fig_architecture.pdf'}")
