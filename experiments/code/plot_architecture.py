#!/usr/bin/env python3
"""Generate publication-quality vector architecture diagram for TopoRadar-Net."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_DIR = Path("studies/mountain-avalcd-toporadar/paper/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis("off")

# Colors
c_sar = "#2b5c8f"        # Steel blue for SAR
c_diff = "#4682b4"       # Light steel blue
c_topo = "#2e8b57"       # Sea green for Topography
c_attn = "#e67e22"       # Orange for Cross-Attention
c_dec = "#8e44ad"        # Purple for Decoder
c_loss = "#c0392b"       # Crimson for Loss
c_box = "#f8f9fa"        # Light background

# Background panels
p1 = patches.FancyBboxPatch((0.2, 4.3), 3.0, 3.4, boxstyle="round,pad=0.1", fc="#edf2f7", ec="#cbd5e0", lw=1.5)
p2 = patches.FancyBboxPatch((0.2, 0.3), 3.0, 3.6, boxstyle="round,pad=0.1", fc="#f0fff4", ec="#c6f6d5", lw=1.5)
p3 = patches.FancyBboxPatch((3.6, 1.8), 3.2, 5.9, boxstyle="round,pad=0.1", fc="#fefcbf", ec="#faf089", lw=1.5)
p4 = patches.FancyBboxPatch((7.2, 1.8), 3.0, 5.9, boxstyle="round,pad=0.1", fc="#faf5ff", ec="#e9d8fd", lw=1.5)
p5 = patches.FancyBboxPatch((10.6, 2.5), 3.2, 5.2, boxstyle="round,pad=0.1", fc="#fff5f5", ec="#fed7d7", lw=1.5)

for p in [p1, p2, p3, p4, p5]:
    ax.add_patch(p)

# Titles of major blocks
ax.text(1.7, 7.4, "Bitemporal SAR Streams", ha="center", va="center", weight="bold", fontsize=11, color=c_sar)
ax.text(1.7, 3.6, "Topographic Radar Geometry", ha="center", va="center", weight="bold", fontsize=11, color=c_topo)
ax.text(5.2, 7.4, "Siamese Feature Pyramid", ha="center", va="center", weight="bold", fontsize=11, color="#b7791f")
ax.text(8.7, 7.4, "RTCAB Cross-Attention", ha="center", va="center", weight="bold", fontsize=11, color=c_dec)
ax.text(12.2, 7.4, "Decoder & Geo-Loss", ha="center", va="center", weight="bold", fontsize=11, color=c_loss)

# Box helper
def draw_box(x, y, w, h, text, color, text_col="white", fontsize=9, subtext=""):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=color, ec="black", lw=1.0)
    ax.add_patch(box)
    if subtext:
        ax.text(x + w/2, y + h*0.62, text, ha="center", va="center", weight="bold", fontsize=fontsize, color=text_col)
        ax.text(x + w/2, y + h*0.28, subtext, ha="center", va="center", fontsize=fontsize-2, color=text_col)
    else:
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", weight="bold", fontsize=fontsize, color=text_col)

# 1. SAR Inputs
draw_box(0.5, 6.2, 2.4, 0.8, "Pre-Event SAR", c_sar, subtext="VV, VH [2x128x128]")
draw_box(0.5, 4.8, 2.4, 0.8, "Post-Event SAR", c_sar, subtext="VV, VH [2x128x128]")

# 2. Topo Inputs
draw_box(0.5, 2.5, 2.4, 0.8, "Topographic Geometry g", c_topo, subtext="[cos(LIA), slope, sin/cos(asp), dem, align]")
draw_box(0.5, 0.8, 2.4, 1.2, "Radar-Aspect Alignment", "#276749", subtext="θ_align = cos(α - φ_look)\nForeslope vs Backslope")

# 3. Siamese & Difference
draw_box(3.9, 6.2, 2.6, 0.7, "Shared Encoder E_l", c_sar, subtext="Pre & Post Residual Conv")
draw_box(3.9, 4.8, 2.6, 0.8, "Multi-scale Diff Fusion", c_diff, subtext="[q - p, q, p] -> F_diff")
draw_box(3.9, 2.4, 2.6, 0.8, "Topo Pyramid T_l", c_topo, subtext="Multi-scale Conv & Pooling")

# 4. RTCAB Details
draw_box(7.5, 5.8, 2.4, 0.8, "SAR Queries (Q)", c_attn, subtext="Dense Change Tokens")
draw_box(7.5, 4.4, 2.4, 0.8, "Topo Keys / Values (K, V)", c_topo, subtext="8x8 Regionally Pooled")
draw_box(7.5, 3.0, 2.4, 0.8, "Cross-Attention A·V", "#d69e2e", subtext="Softmax(QK^T / √d) · V")
draw_box(7.5, 2.0, 2.4, 0.7, "Spatial Topo Gate W_gate", "#319795", subtext="σ(Conv(T_l)) [Pixel Gate]")

# 5. Decoder & Loss
draw_box(10.9, 5.8, 2.6, 0.8, "Progressive Decoder", c_dec, subtext="ConvTranspose2d + Skips")
draw_box(10.9, 4.4, 2.6, 0.8, "Avalanche Mask Ŷ", "#4a5568", subtext="Full-Scene Probabilities")
draw_box(10.9, 2.8, 2.6, 1.2, "Geomorphic Loss L_geom", c_loss, subtext="Soft Inadmissibility:\nSlope < 5° or > 65°")

# Arrows
def draw_arrow(x1, y1, x2, y2, color="#4a5568", lw=1.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw, shrinkA=3, shrinkB=3))

draw_arrow(2.9, 6.6, 3.9, 6.6)
draw_arrow(2.9, 5.2, 3.9, 6.4)
draw_arrow(5.2, 6.2, 5.2, 5.6)
draw_arrow(2.9, 2.9, 3.9, 2.8)
draw_arrow(6.5, 5.2, 7.5, 6.2)
draw_arrow(6.5, 2.8, 7.5, 4.8)
draw_arrow(6.5, 2.8, 7.5, 2.35)
draw_arrow(8.7, 5.8, 8.7, 3.8)
draw_arrow(8.7, 4.4, 8.7, 3.8)
draw_arrow(9.9, 3.4, 10.9, 6.2)
draw_arrow(12.2, 5.8, 12.2, 5.2)
draw_arrow(12.2, 4.4, 12.2, 4.0)

plt.tight_layout()
fig.savefig(OUT_DIR / "fig_architecture.pdf", bbox_inches="tight")
fig.savefig(OUT_DIR / "fig_architecture.png", bbox_inches="tight", dpi=300)
print(f"Generated architecture figure at {OUT_DIR / 'fig_architecture.pdf'}")
