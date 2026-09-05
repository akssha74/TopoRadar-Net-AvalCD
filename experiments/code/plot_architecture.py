#!/usr/bin/env python3
"""Generate publication-quality vector architecture diagram for TopoRadar-Net with flawless spacing, zero text collisions, and pristine typography."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

OUT_DIR = Path("studies/mountain-avalcd-toporadar/paper/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Generous canvas dimensions
fig, ax = plt.subplots(figsize=(16.4, 8.0), dpi=300)
ax.set_xlim(0, 16.4)
ax.set_ylim(0, 8.0)
ax.axis("off")

# Harmonious, high-contrast accessible palette
c_sar_dark = "#1e3a8a"       # Navy Blue
c_sar_light = "#2563eb"      # Blue
c_topo_dark = "#14532d"      # Dark Forest Green
c_topo_light = "#16a34a"     # Green
c_query = "#c2410c"          # Rust / Orange
c_key = "#15803d"            # Forest Green
c_core = "#d97706"           # Amber / Gold
c_dec = "#6b21a8"            # Royal Purple
c_mask = "#1e293b"           # Dark Slate
c_loss = "#991b1b"           # Crimson Red

# Outer container panels (Height: 0.35 to 7.15, giving 0.85 clearance at top of canvas)
containers = [
    # (x, y, w, h, title)
    (0.35, 0.35, 4.85, 6.80, "1. Multi-Modal Inputs & Feature Pyramids"),
    (5.45, 0.35, 4.35, 6.80, "2. Radar-Topographic Cross-Attention (RTCAB)"),
    (10.05, 0.35, 6.00, 6.80, "3. Decoder, Predictions & Physical Loss")
]

for x, y, w, h, title in containers:
    # Outer panel
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc="#f8fafc", ec="#cbd5e1", lw=1.5, zorder=1)
    ax.add_patch(rect)
    # Distinct top header badge (placed safely at top of container: y = 6.65 to 7.05)
    badge = patches.FancyBboxPatch((x + 0.25, 6.65), w - 0.50, 0.40, boxstyle="round,pad=0.04", fc="#e2e8f0", ec="#94a3b8", lw=1.0, zorder=2)
    ax.add_patch(badge)
    ax.text(x + w/2, 6.85, title, ha="center", va="center", weight="bold", fontsize=11.0, color="#0f172a", zorder=3)

# Unified Card drawing function with perfectly calculated vertical spacing and generous padding
def draw_card(x, y, w, h, title, subtext="", box_color="#1e3a8a", text_color="white", title_y_frac=0.72, sub_y_frac=0.34, title_size=10.2, sub_size=8.4):
    card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", fc=box_color, ec="#0f172a", lw=1.2, zorder=3)
    ax.add_patch(card)
    if subtext:
        ax.text(x + w/2, y + h*title_y_frac, title, ha="center", va="center", weight="bold", fontsize=title_size, color=text_color, zorder=4)
        ax.text(x + w/2, y + h*sub_y_frac, subtext, ha="center", va="center", fontsize=sub_size, color=text_color, zorder=4, multialignment="center", linespacing=1.35)
    else:
        ax.text(x + w/2, y + h/2, title, ha="center", va="center", weight="bold", fontsize=title_size, color=text_color, zorder=4)

# Solid Arrow helper
def draw_arrow(x1, y1, x2, y2, color="#334155", lw=2.2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=15), zorder=6)

# =========================================================================
# SECTION 1: Inputs & Feature Pyramids
# All card tops are strictly at y <= 5.85, giving an 0.80 margin to the header badge!
# =========================================================================
# Top Lane: SAR Inputs & Encoder (Center y = 4.95)
draw_card(0.55, 5.05, 1.85, 0.80, "Pre-Event SAR", "Dual-Pol (VV, VH) dB", c_sar_dark)
draw_card(0.55, 4.05, 1.85, 0.80, "Post-Event SAR", "Dual-Pol (VV, VH) dB", c_sar_dark)

draw_card(2.70, 4.05, 2.30, 1.80, "Siamese SAR Encoder", 
          r"$\mathcal{E}_l$: Shared ResNet Stages" + "\n" + 
          r"$\mathbf{F}_{\mathrm{diff}}^l = [\Delta \mathbf{F}, \mathbf{F}_{\mathrm{post}}, \mathbf{F}_{\mathrm{pre}}]$" + "\n" + 
          r"$C_l \in \{32, 64, 128, 256\}$", c_sar_light)

# 100% Horizontal parallel arrows from SAR inputs into Encoder (exact edge-to-edge)
draw_arrow(2.45, 5.45, 2.65, 5.45, color=c_sar_dark)
draw_arrow(2.45, 4.45, 2.65, 4.45, color=c_sar_dark)

# Bottom Lane: Topo Inputs & Pyramid (Center y = 1.85)
draw_card(0.55, 2.05, 1.85, 0.80, "Topographic Vector g", r"[$\cos\psi$, slope, DEM]", c_topo_dark)
draw_card(0.55, 1.05, 1.85, 0.80, "Aspect-Look Vector", r"$\cos(\alpha - \phi_{\mathrm{look}})$, $\sin\alpha, \cos\alpha$", c_topo_dark)

draw_card(2.70, 1.05, 2.30, 1.80, "Topo Feature Pyramid", 
          r"$\mathbf{T}^l$: Multi-scale Conv" + "\n" + 
          r"Matches $C_l \times H_l \times W_l$" + "\n" + 
          r"Continuous Manifold $\mathcal{M}$", c_topo_light)

# 100% Horizontal parallel arrows from Topo inputs into Pyramid (exact edge-to-edge)
draw_arrow(2.45, 2.45, 2.65, 2.45, color=c_topo_dark)
draw_arrow(2.45, 1.45, 2.65, 1.45, color=c_topo_dark)

# =========================================================================
# SECTION 2: Radar-Topographic Cross-Attention Block (RTCAB)
# Perfect horizontal alignment from Section 1
# =========================================================================
# SAR Queries (Center y = 4.95, aligned with SAR Encoder center)
draw_card(5.65, 4.35, 3.95, 1.20, r"SAR Queries $\mathbf{Q}$", 
          r"$\mathbf{F}_{\mathrm{diff}}^l \mathbf{W}_Q \in \mathbb{R}^{B \times N \times C_l}$" + "\n" + 
          "Dense Spatial Change Tokens", c_query)

# 100% HORIZONTAL ARROW: SAR Encoder to SAR Queries Q (exact edge-to-edge)
draw_arrow(5.05, 4.95, 5.60, 4.95, color="#1d4ed8", lw=2.4)

# Topo Keys/Values & Spatial Gate (Center y = 1.85, aligned with Topo Pyramid center)
draw_card(5.65, 1.25, 3.95, 1.20, "Topo Keys / Values & Spatial Gate", 
          r"$\mathbf{K}, \mathbf{V} = \mathrm{Pool}_{8 \times 8}(\mathbf{T}^l) \mathbf{W}_{K, V}$" + "\n" + 
          r"$\mathbf{W}_{\mathrm{gate}} = \sigma\left(\mathrm{Conv}(\mathbf{T}^l)\right)$", c_key)

# 100% HORIZONTAL ARROW: Topo Pyramid to Topo Keys/Values & Gate (exact edge-to-edge)
draw_arrow(5.05, 1.85, 5.60, 1.85, color=c_topo_light, lw=2.4)

# Cross-Attention Core (Center y = 3.40)
draw_card(5.65, 2.70, 3.95, 1.40, "Multi-Head Cross-Attention Core", 
          r"$\mathbf{A} = \mathrm{softmax}\left(\mathbf{Q} \mathbf{K}^T / \sqrt{d_k}\right)$" + "\n" + 
          r"$\mathbf{\tilde{F}}^l = \mathrm{BN}\left(\mathbf{F}_{\mathrm{diff}}^l + \mathbf{A}\mathbf{V}\right) \odot (1 + \mathbf{W}_{\mathrm{gate}})$", 
          c_core)

# Symmetrical VERTICAL arrows entering Attention Core (exact edge-to-edge)
draw_arrow(7.625, 4.30, 7.625, 4.15, color=c_query, lw=2.4)
draw_arrow(7.625, 2.50, 7.625, 2.65, color=c_key, lw=2.4)

# =========================================================================
# SECTION 3: Decoder, Predictions & Physical Loss
# Roomy cards with zero text crowding or edge collisions
# =========================================================================
# 1. Progressive Decoder (Top of section 3: y = 4.40 to 5.85, center y = 5.125)
draw_card(10.35, 4.40, 5.40, 1.45, "Progressive Decoder", 
          r"$\mathrm{ConvTranspose2d}$ + Hierarchical Skip Connections" + "\n" + 
          r"Progressive $4\times$ Upsampling to original $10\text{ m}$ GSD", c_dec,
          title_y_frac=0.72, sub_y_frac=0.34)

# 2. Predicted Mask Y_hat (Middle: y = 2.50 to 3.95, center y = 3.225)
draw_card(10.35, 2.50, 5.40, 1.45, r"Predicted Avalanche Debris Mask $\mathbf{\hat{Y}}$", 
          r"Continuous Probabilities $\hat{y}_i = \sigma(z_i) \in [0, 1]$" + "\n" + 
          r"2D Hanning Window Blending ($1.80\text{ s}$ Full-Scene Latency)", c_mask,
          title_y_frac=0.72, sub_y_frac=0.34)

# 3. Geomorphically Bounded Loss (Bottom: y = 0.55 to 2.15, center y = 1.35)
draw_card(10.35, 0.55, 5.40, 1.60, r"Geomorphically Bounded Physical Loss", 
          r"Segmentation: Weighted BCE ($w_{\mathrm{pos}} = 3.0$) + Soft Dice" + "\n" + 
          r"Geomorphic Penalty $\mathcal{L}_{\mathrm{geom}}$: Valley floors ($< 5^\circ$) & Cliffs ($> 65^\circ$)" + "\n" + 
          r"$\mathbf{\mathcal{L}_{\mathrm{total}} = \mathcal{L}_{\mathrm{BCE}} + \mathcal{L}_{\mathrm{Dice}} + 0.5 \, \mathcal{L}_{\mathrm{geom}}}$", c_loss,
          title_y_frac=0.75, sub_y_frac=0.35)

# Smooth, orthogonal elbow connection from RTCAB Core to Decoder
# Runs from Core right edge (9.65, 3.40) -> (9.975, 3.40) -> (9.975, 5.125) -> (10.30, 5.125)
ax.plot([9.65, 9.975, 9.975, 10.30], [3.40, 3.40, 5.125, 5.125], color=c_core, lw=2.4, zorder=5)
ax.annotate("", xy=(10.30, 5.125), xytext=(10.20, 5.125),
            arrowprops=dict(arrowstyle="-|>", color=c_core, lw=2.4, shrinkA=0, shrinkB=0, mutation_scale=16), zorder=6)

# Feature label placed cleanly ABOVE the entering segment (no lines crossing the text!)
ax.text(10.14, 5.24, r"$\mathbf{\tilde{F}}^l$", ha="center", va="bottom", fontsize=10.5, color=c_core, weight="bold", zorder=7)

# Decoder -> Predicted Mask (100% VERTICAL ARROW, exact edge-to-edge!)
draw_arrow(13.05, 4.35, 13.05, 3.95, color=c_dec, lw=2.4)

# Predicted Mask -> Loss (100% VERTICAL ARROW, exact edge-to-edge!)
draw_arrow(13.05, 2.45, 13.05, 2.20, color=c_mask, lw=2.4)

# Multi-Scale Skip Connection: cleanly broken around the floating central label badge
# Left branch: from top of SAR Encoder at x=3.85, y=5.90 -> up to y=6.25 -> right to badge edge (x=6.70)
ax.plot([3.85, 3.85, 6.70], [5.90, 6.25, 6.25], color="#475569", lw=1.8, linestyle="--", zorder=5)

# Right branch: from badge edge (x=10.70), along y=6.25 to x=13.05 -> down to top of Decoder at y=5.90
ax.plot([10.70, 13.05, 13.05], [6.25, 6.25, 5.90], color="#475569", lw=1.8, linestyle="--", zorder=5)
ax.annotate("", xy=(13.05, 5.90), xytext=(13.05, 6.00),
            arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.8, shrinkA=0, shrinkB=0, mutation_scale=14), zorder=6)

# Central pill label floating cleanly in the gap with zero line cut-through
skip_badge = patches.FancyBboxPatch((6.75, 6.10), 3.90, 0.30, boxstyle="round,pad=0.04", fc="#ffffff", ec="#64748b", lw=1.0, zorder=6)
ax.add_patch(skip_badge)
ax.text(8.70, 6.25, "Multi-Scale Hierarchical Skip Connections", ha="center", va="center", fontsize=8.6, color="#1e293b", weight="bold", zorder=7)

plt.tight_layout(pad=0.2)
fig.savefig(OUT_DIR / "fig_architecture.pdf", bbox_inches="tight")
fig.savefig(OUT_DIR / "fig_architecture.png", bbox_inches="tight", dpi=300)
print(f"Generated clean architecture figure with zero text overlap at {OUT_DIR / 'fig_architecture.pdf'}")
