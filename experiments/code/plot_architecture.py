#!/usr/bin/env python3
"""Generate publication-quality vector architecture diagram for TopoRadar-Net."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_DIR = Path("studies/mountain-avalcd-toporadar/paper/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Set up canvas with optimal aspect ratio for \textwidth
fig, ax = plt.subplots(figsize=(13.5, 6.2), dpi=300)
ax.set_xlim(0, 13.5)
ax.set_ylim(0, 6.2)
ax.axis("off")

# Colors
c_sar_panel = "#ebf4ff"
c_sar_box = "#1e3a8a"       # Deep blue
c_diff_box = "#2563eb"      # Vibrant blue

c_topo_panel = "#f0fdf4"
c_topo_box = "#166534"      # Deep forest green
c_align_box = "#15803d"     # Green

c_siam_panel = "#fefce8"
c_siam_box = "#854d0e"      # Warm amber

c_rtcab_panel = "#faf5ff"
c_query_box = "#c2410c"     # Burnt orange/rust for SAR Query
c_key_box = "#15803d"       # Green for Topo Keys
c_cross_box = "#d97706"     # Amber for Cross-Attention
c_gate_box = "#0d9488"      # Teal for Spatial Gate

c_dec_panel = "#fff1f2"
c_dec_box = "#6b21a8"       # Deep purple
c_mask_box = "#1e293b"      # Slate dark
c_loss_box = "#b91c1c"      # Crimson

# 1. Background panels with soft outlines
panels = [
    # (x, y, w, h, fill, border, title)
    (0.15, 0.15, 2.45, 5.9, "#f8fafc", "#94a3b8", "1. Input Modalities"),
    (2.80, 0.15, 2.50, 5.9, "#f8fafc", "#94a3b8", "2. Feature Pyramids"),
    (5.50, 0.15, 2.70, 5.9, "#f8fafc", "#94a3b8", "3. RTCAB Attention"),
    (8.40, 0.15, 2.45, 5.9, "#f8fafc", "#94a3b8", "4. Decoder"),
    (11.05, 0.15, 2.30, 5.9, "#f8fafc", "#94a3b8", "5. Physical Loss")
]

for x, y, w, h, fc, ec, title in panels:
    p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc=fc, ec=ec, lw=1.5, zorder=1)
    ax.add_patch(p)
    ax.text(x + w/2, y + h - 0.28, title, ha="center", va="center", weight="bold", fontsize=11.5, color="#1e293b", zorder=2)

# Helper function to draw clean boxes with bold titles and legible subtext
def draw_card(x, y, w, h, title, subtext="", box_color="#1e3a8a", text_color="white"):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06", fc=box_color, ec="#0f172a", lw=1.2, zorder=3)
    ax.add_patch(box)
    if subtext:
        ax.text(x + w/2, y + h*0.64, title, ha="center", va="center", weight="bold", fontsize=10.5, color=text_color, zorder=4)
        ax.text(x + w/2, y + h*0.28, subtext, ha="center", va="center", fontsize=8.5, color=text_color, zorder=4)
    else:
        ax.text(x + w/2, y + h/2, title, ha="center", va="center", weight="bold", fontsize=10.5, color=text_color, zorder=4)

# Panel 1: Inputs
draw_card(0.28, 4.30, 2.18, 1.05, "Pre-Event SAR", "Dual-Pol (VV, VH) dB", c_sar_box)
draw_card(0.28, 3.05, 2.18, 1.05, "Post-Event SAR", "Dual-Pol (VV, VH) dB", c_sar_box)
draw_card(0.28, 1.65, 2.18, 1.15, "Topographic Geometry g", "cos(LIA), Slope, DEM", c_topo_box)
draw_card(0.28, 0.35, 2.18, 1.10, "Radar-Aspect Vector", r"$\cos(\alpha - \phi_{\mathrm{look}})$, $\sin \alpha, \cos \alpha$", c_align_box)

# Panel 2: Encoders
draw_card(2.95, 3.65, 2.20, 1.70, "Siamese SAR Encoder", r"$\mathcal{E}_l$: Shared ResNet Stages" + "\n" + r"$C_l \in \{32, 64, 128, 256\}$", c_diff_box)
draw_card(2.95, 1.95, 2.20, 1.35, "Bi-temporal Fusion", r"$\mathbf{F}_{\mathrm{diff}}^l = [\mathbf{F}_{\mathrm{post}} - \mathbf{F}_{\mathrm{pre}}, \mathbf{F}_{\mathrm{post}}, \mathbf{F}_{\mathrm{pre}}]$", "#1d4ed8")
draw_card(2.95, 0.40, 2.20, 1.30, "Topo Pyramid", r"$\mathbf{T}^l$: Multi-scale Conv" + "\n" + r"Matches $C_l \times H_l \times W_l$", c_topo_box)

# Panel 3: RTCAB Module
draw_card(5.65, 4.30, 2.40, 1.05, r"SAR Queries $\mathbf{Q}$", r"$\mathbf{F}_{\mathrm{diff}}^l \mathbf{W}_Q$ (Dense Tokens)", c_query_box)
draw_card(5.65, 3.05, 2.40, 1.05, r"Topo Keys / Values", r"$\mathrm{Pool}_{8 \times 8}(\mathbf{T}^l) \mathbf{W}_{K, V}$", c_key_box)
draw_card(5.65, 1.75, 2.40, 1.10, "Cross-Attention Gate", r"$\mathbf{A} = \mathrm{softmax}(\mathbf{Q}\mathbf{K}^T / \sqrt{d_k}) \mathbf{V}$", c_cross_box)
draw_card(5.65, 0.40, 2.40, 1.15, "Spatial Topo Gate", r"$\mathbf{W}_{\mathrm{gate}} = \sigma(\mathrm{Conv}(\mathbf{T}^l))$" + "\n" + r"$\mathbf{\tilde{F}}^l = (\mathbf{F}_{\mathrm{diff}} + \mathbf{A}\mathbf{V}) \odot (1 + \mathbf{W}_{\mathrm{gate}})$", c_gate_box)

# Panel 4: Decoder & Predictions
draw_card(8.55, 3.65, 2.15, 1.70, "Progressive Decoder", "ConvTranspose2d + Skips\nHierarchical Upsampling", c_dec_box)
draw_card(8.55, 1.30, 2.15, 1.80, r"Predicted Mask $\mathbf{\hat{Y}}$", "Continuous Probabilities\nFull-Scene Blending\n1.80s / Scene Latency", c_mask_box)

# Panel 5: Physical Loss
draw_card(11.20, 4.00, 2.00, 1.35, r"Segmentation $\mathcal{L}$", r"Weighted $\mathrm{BCE} + \mathrm{Dice}$" + "\n" + r"$w_{\mathrm{pos}} = 3.0$ (Imbalance)", "#475569")
draw_card(11.20, 2.00, 2.00, 1.70, r"Geo-Loss $\mathcal{L}_{\mathrm{geom}}$", r"Penalizes mass in:" + "\n" + r"Valley floor $< 5^\circ$" + "\n" + r"Sheer cliff $> 65^\circ$", c_loss_box)
draw_card(11.20, 0.40, 2.00, 1.35, r"Total Loss $\mathcal{L}$", r"$\mathcal{L}_{\mathrm{BCE}} + \mathcal{L}_{\mathrm{Dice}} + 0.5 \mathcal{L}_{\mathrm{geom}}$", "#991b1b")

# Connecting Arrows with clear routing
def connect(x1, y1, x2, y2, color="#334155", lw=1.8):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=3, shrinkB=3,
                                mutation_scale=14))

# Inputs to Encoders
connect(2.46, 4.82, 2.95, 4.60)
connect(2.46, 3.57, 2.95, 4.40)
connect(2.46, 2.22, 2.95, 1.05)
connect(2.46, 0.90, 2.95, 0.90)

# Encoder internal flow
connect(4.05, 3.65, 4.05, 3.30)
connect(4.05, 1.95, 5.65, 4.82)  # Diff to SAR Query
connect(5.15, 2.62, 5.65, 1.10)  # Diff to Spatial Gate
connect(5.15, 1.05, 5.65, 3.57)  # Topo to Keys/Values
connect(5.15, 1.05, 5.65, 0.97)  # Topo to Spatial Gate

# RTCAB internal flow
connect(6.85, 4.30, 6.85, 2.85)
connect(6.85, 3.05, 6.85, 2.85)
connect(6.85, 1.75, 6.85, 1.55)

# RTCAB to Decoder
connect(8.05, 1.10, 8.55, 4.50)

# Decoder to Prediction
connect(9.62, 3.65, 9.62, 3.10)

# Prediction to Losses
connect(10.70, 2.50, 11.20, 4.60)
connect(10.70, 2.20, 11.20, 2.85)

# Losses to Total Loss
connect(12.20, 4.00, 12.20, 3.70)
connect(12.20, 2.00, 12.20, 1.75)

plt.tight_layout(pad=0.2)
fig.savefig(OUT_DIR / "fig_architecture.pdf", bbox_inches="tight")
fig.savefig(OUT_DIR / "fig_architecture.png", bbox_inches="tight", dpi=300)
print(f"Generated crisp, publication-quality architecture figure at {OUT_DIR / 'fig_architecture.pdf'}")
