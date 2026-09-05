#!/usr/bin/env python3
"""Model architectures for TopoRadar-Net and competitive baselines."""

from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# -----------------------------------------------------------------------------
# Reusable Building Blocks
# -----------------------------------------------------------------------------

class ConvBlock(nn.Module):
    """Conv2d -> BatchNorm -> GELU -> Conv2d -> BatchNorm -> GELU with Residual."""
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.conv1 = nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_ch)
        self.act1 = nn.GELU()
        self.conv2 = nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_ch)
        self.act2 = nn.GELU()
        self.shortcut = nn.Sequential()
        if in_ch != out_ch:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, kernel_size=1, bias=False),
                nn.BatchNorm2d(out_ch)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = self.shortcut(x)
        out = self.act1(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return self.act2(out + res)

class RadarTopoCrossAttention(nn.Module):
    """
    Physically-Guided Cross-Attention Block with Pooled Topographic Geometry:
    Queries: High-resolution multiscale SAR change features
    Keys/Values: Regionally-pooled topographic radar-geometry features (LIA, slope, aspect alignment)
    """
    def __init__(self, sar_dim: int, topo_dim: int, num_heads: int = 4, kv_size: int = 8):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = sar_dim // num_heads
        self.scale = 1.0 / math.sqrt(self.head_dim)
        self.kv_pool = nn.AdaptiveAvgPool2d((kv_size, kv_size))

        self.q_proj = nn.Conv2d(sar_dim, sar_dim, kernel_size=1, bias=False)
        self.k_proj = nn.Conv2d(topo_dim, sar_dim, kernel_size=1, bias=False)
        self.v_proj = nn.Conv2d(topo_dim, sar_dim, kernel_size=1, bias=False)
        self.out_proj = nn.Conv2d(sar_dim, sar_dim, kernel_size=1, bias=False)

        # Dynamic Topographic Spatial Gate
        self.topo_gate = nn.Sequential(
            nn.Conv2d(topo_dim, sar_dim // 2, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv2d(sar_dim // 2, sar_dim, kernel_size=1),
            nn.Sigmoid()
        )
        self.norm = nn.BatchNorm2d(sar_dim)

    def forward(self, sar_feat: torch.Tensor, topo_feat: torch.Tensor) -> torch.Tensor:
        B, C, H, W = sar_feat.shape
        N = H * W

        # Queries at full resolution
        q = self.q_proj(sar_feat).view(B, self.num_heads, self.head_dim, N).permute(0, 1, 3, 2) # (B, heads, N, head_dim)

        # Keys and Values from regionally pooled topographic context
        topo_pooled = self.kv_pool(topo_feat)
        M = topo_pooled.shape[2] * topo_pooled.shape[3]
        k = self.k_proj(topo_pooled).view(B, self.num_heads, self.head_dim, M).permute(0, 1, 2, 3) # (B, heads, head_dim, M)
        v = self.v_proj(topo_pooled).view(B, self.num_heads, self.head_dim, M).permute(0, 1, 3, 2) # (B, heads, M, head_dim)

        # Efficient cross-attention matrix: (B, heads, N, M)
        attn = torch.matmul(q, k) * self.scale
        attn = F.softmax(attn, dim=-1)

        out = torch.matmul(attn, v)  # (B, heads, N, head_dim)
        out = out.permute(0, 1, 3, 2).contiguous().view(B, C, H, W)
        out = self.out_proj(out)

        # Topographic spatial gating
        gate = self.topo_gate(topo_feat)
        fused = self.norm(sar_feat + out) * (1.0 + gate)
        return fused

# -----------------------------------------------------------------------------
# Proposed TopoRadar-Net Architecture
# -----------------------------------------------------------------------------

class TopoRadarNet(nn.Module):
    """
    Topographic Radar Geometry-Guided Cross-Attention Network for Alpine SAR Change Detection.
    """
    def __init__(
        self,
        in_sar_ch: int = 2,
        in_topo_ch: int = 6,
        base_ch: int = 32,
        use_lia: bool = True,
        use_aspect: bool = True,
        use_cross_attn: bool = True,
    ):
        super().__init__()
        self.use_lia = use_lia
        self.use_aspect = use_aspect
        self.use_cross_attn = use_cross_attn

        # Siamese SAR Encoder
        self.enc1 = ConvBlock(in_sar_ch, base_ch)            # 128x128
        self.pool1 = nn.MaxPool2d(2)                          # 64x64
        self.enc2 = ConvBlock(base_ch, base_ch * 2)          # 64x64
        self.pool2 = nn.MaxPool2d(2)                          # 32x32
        self.enc3 = ConvBlock(base_ch * 2, base_ch * 4)      # 32x32
        self.pool3 = nn.MaxPool2d(2)                          # 16x16
        self.enc4 = ConvBlock(base_ch * 4, base_ch * 8)      # 16x16

        # Topographic Geometry Multiscale Feature Extractor
        self.topo_conv1 = nn.Sequential(
            nn.Conv2d(in_topo_ch, base_ch, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_ch),
            nn.GELU()
        )
        self.topo_pool1 = nn.AvgPool2d(2)
        self.topo_conv2 = nn.Sequential(
            nn.Conv2d(base_ch, base_ch * 2, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_ch * 2),
            nn.GELU()
        )
        self.topo_pool2 = nn.AvgPool2d(2)
        self.topo_conv3 = nn.Sequential(
            nn.Conv2d(base_ch * 2, base_ch * 4, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_ch * 4),
            nn.GELU()
        )
        self.topo_pool3 = nn.AvgPool2d(2)
        self.topo_conv4 = nn.Sequential(
            nn.Conv2d(base_ch * 4, base_ch * 8, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_ch * 8),
            nn.GELU()
        )

        # Difference Fusion Projections
        self.fuse4 = nn.Conv2d(base_ch * 8 * 3, base_ch * 8, kernel_size=1)
        self.fuse3 = nn.Conv2d(base_ch * 4 * 3, base_ch * 4, kernel_size=1)
        self.fuse2 = nn.Conv2d(base_ch * 2 * 3, base_ch * 2, kernel_size=1)
        self.fuse1 = nn.Conv2d(base_ch * 3, base_ch, kernel_size=1)

        # Radar-Topographic Cross Attention Modules
        if self.use_cross_attn:
            self.attn4 = RadarTopoCrossAttention(base_ch * 8, base_ch * 8, num_heads=4, kv_size=8)
            self.attn3 = RadarTopoCrossAttention(base_ch * 4, base_ch * 4, num_heads=4, kv_size=8)
            self.attn2 = RadarTopoCrossAttention(base_ch * 2, base_ch * 2, num_heads=2, kv_size=8)
            self.attn1 = RadarTopoCrossAttention(base_ch, base_ch, num_heads=1, kv_size=8)
        else:
            self.cat4 = nn.Conv2d(base_ch * 8 * 2, base_ch * 8, kernel_size=1)
            self.cat3 = nn.Conv2d(base_ch * 4 * 2, base_ch * 4, kernel_size=1)
            self.cat2 = nn.Conv2d(base_ch * 2 * 2, base_ch * 2, kernel_size=1)
            self.cat1 = nn.Conv2d(base_ch * 2, base_ch, kernel_size=1)

        # Decoder
        self.up3 = nn.ConvTranspose2d(base_ch * 8, base_ch * 4, kernel_size=2, stride=2)
        self.dec3 = ConvBlock(base_ch * 8, base_ch * 4)

        self.up2 = nn.ConvTranspose2d(base_ch * 4, base_ch * 2, kernel_size=2, stride=2)
        self.dec2 = ConvBlock(base_ch * 4, base_ch * 2)

        self.up1 = nn.ConvTranspose2d(base_ch * 2, base_ch, kernel_size=2, stride=2)
        self.dec1 = ConvBlock(base_ch * 2, base_ch)

        # Final prediction head
        self.head = nn.Sequential(
            nn.Conv2d(base_ch, base_ch // 2, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_ch // 2),
            nn.GELU(),
            nn.Conv2d(base_ch // 2, 1, kernel_size=1)
        )

    def forward(self, pre: torch.Tensor, post: torch.Tensor, topo: torch.Tensor) -> torch.Tensor:
        topo_in = topo.clone()
        if not self.use_lia:
            topo_in[:, 0, :, :] = 0.0
        if not self.use_aspect:
            topo_in[:, 2:4, :, :] = 0.0
            topo_in[:, 5, :, :] = 0.0

        t1 = self.topo_conv1(topo_in)
        t2 = self.topo_conv2(self.topo_pool1(t1))
        t3 = self.topo_conv3(self.topo_pool2(t2))
        t4 = self.topo_conv4(self.topo_pool3(t3))

        p1 = self.enc1(pre)
        p2 = self.enc2(self.pool1(p1))
        p3 = self.enc3(self.pool2(p2))
        p4 = self.enc4(self.pool3(p3))

        q1 = self.enc1(post)
        q2 = self.enc2(self.pool1(q1))
        q3 = self.enc3(self.pool2(q2))
        q4 = self.enc4(self.pool3(q3))

        diff4 = self.fuse4(torch.cat([q4 - p4, q4, p4], dim=1))
        diff3 = self.fuse3(torch.cat([q3 - p3, q3, p3], dim=1))
        diff2 = self.fuse2(torch.cat([q2 - p2, q2, p2], dim=1))
        diff1 = self.fuse1(torch.cat([q1 - p1, q1, p1], dim=1))

        if self.use_cross_attn:
            f4 = self.attn4(diff4, t4)
            f3 = self.attn3(diff3, t3)
            f2 = self.attn2(diff2, t2)
            f1 = self.attn1(diff1, t1)
        else:
            f4 = self.cat4(torch.cat([diff4, t4], dim=1))
            f3 = self.cat3(torch.cat([diff3, t3], dim=1))
            f2 = self.cat2(torch.cat([diff2, t2], dim=1))
            f1 = self.cat1(torch.cat([diff1, t1], dim=1))

        d3 = self.dec3(torch.cat([self.up3(f4), f3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), f2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), f1], dim=1))

        logits = self.head(d1)
        return logits

# -----------------------------------------------------------------------------
# Baseline 1: SiamUNet-diff (Daudt et al.)
# -----------------------------------------------------------------------------

class SiamUNetDiff(nn.Module):
    def __init__(self, in_sar_ch: int = 2, base_ch: int = 32):
        super().__init__()
        self.enc1 = ConvBlock(in_sar_ch, base_ch)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = ConvBlock(base_ch, base_ch * 2)
        self.pool2 = nn.MaxPool2d(2)
        self.enc3 = ConvBlock(base_ch * 2, base_ch * 4)
        self.pool3 = nn.MaxPool2d(2)
        self.enc4 = ConvBlock(base_ch * 4, base_ch * 8)

        self.up3 = nn.ConvTranspose2d(base_ch * 8, base_ch * 4, kernel_size=2, stride=2)
        self.dec3 = ConvBlock(base_ch * 8, base_ch * 4)
        self.up2 = nn.ConvTranspose2d(base_ch * 4, base_ch * 2, kernel_size=2, stride=2)
        self.dec2 = ConvBlock(base_ch * 4, base_ch * 2)
        self.up1 = nn.ConvTranspose2d(base_ch * 2, base_ch, kernel_size=2, stride=2)
        self.dec1 = ConvBlock(base_ch * 2, base_ch)

        self.head = nn.Conv2d(base_ch, 1, kernel_size=1)

    def forward(self, pre: torch.Tensor, post: torch.Tensor, topo: torch.Tensor = None) -> torch.Tensor:
        p1 = self.enc1(pre)
        p2 = self.enc2(self.pool1(p1))
        p3 = self.enc3(self.pool2(p2))
        p4 = self.enc4(self.pool3(p3))

        q1 = self.enc1(post)
        q2 = self.enc2(self.pool1(q1))
        q3 = self.enc3(self.pool2(q2))
        q4 = self.enc4(self.pool3(q3))

        diff4 = torch.abs(q4 - p4)
        diff3 = torch.abs(q3 - p3)
        diff2 = torch.abs(q2 - p2)
        diff1 = torch.abs(q1 - p1)

        d3 = self.dec3(torch.cat([self.up3(diff4), diff3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), diff2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), diff1], dim=1))

        return self.head(d1)

# -----------------------------------------------------------------------------
# Baseline 2: SiamUNet-conc (Daudt et al.)
# -----------------------------------------------------------------------------

class SiamUNetConc(nn.Module):
    def __init__(self, in_sar_ch: int = 2, base_ch: int = 32):
        super().__init__()
        self.enc1 = ConvBlock(in_sar_ch, base_ch)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = ConvBlock(base_ch, base_ch * 2)
        self.pool2 = nn.MaxPool2d(2)
        self.enc3 = ConvBlock(base_ch * 2, base_ch * 4)
        self.pool3 = nn.MaxPool2d(2)
        self.enc4 = ConvBlock(base_ch * 4, base_ch * 8)

        self.up3 = nn.ConvTranspose2d(base_ch * 8 * 2, base_ch * 4, kernel_size=2, stride=2)
        self.dec3 = ConvBlock(base_ch * 4 + base_ch * 4 * 2, base_ch * 4)
        self.up2 = nn.ConvTranspose2d(base_ch * 4, base_ch * 2, kernel_size=2, stride=2)
        self.dec2 = ConvBlock(base_ch * 2 + base_ch * 2 * 2, base_ch * 2)
        self.up1 = nn.ConvTranspose2d(base_ch * 2, base_ch, kernel_size=2, stride=2)
        self.dec1 = ConvBlock(base_ch + base_ch * 2, base_ch)

        self.head = nn.Conv2d(base_ch, 1, kernel_size=1)

    def forward(self, pre: torch.Tensor, post: torch.Tensor, topo: torch.Tensor = None) -> torch.Tensor:
        p1 = self.enc1(pre)
        p2 = self.enc2(self.pool1(p1))
        p3 = self.enc3(self.pool2(p2))
        p4 = self.enc4(self.pool3(p3))

        q1 = self.enc1(post)
        q2 = self.enc2(self.pool1(q1))
        q3 = self.enc3(self.pool2(q2))
        q4 = self.enc4(self.pool3(q3))

        d3 = self.dec3(torch.cat([self.up3(torch.cat([p4, q4], dim=1)), p3, q3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), p2, q2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), p1, q1], dim=1))

        return self.head(d1)

# -----------------------------------------------------------------------------
# Baseline 3: ResU-Net (Zhang et al. 2018)
# -----------------------------------------------------------------------------

class ResUNet(nn.Module):
    def __init__(self, in_ch: int = 4, base_ch: int = 32):
        super().__init__()
        self.enc1 = ConvBlock(in_ch, base_ch)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = ConvBlock(base_ch, base_ch * 2)
        self.pool2 = nn.MaxPool2d(2)
        self.enc3 = ConvBlock(base_ch * 2, base_ch * 4)
        self.pool3 = nn.MaxPool2d(2)
        self.enc4 = ConvBlock(base_ch * 4, base_ch * 8)

        self.up3 = nn.ConvTranspose2d(base_ch * 8, base_ch * 4, kernel_size=2, stride=2)
        self.dec3 = ConvBlock(base_ch * 8, base_ch * 4)
        self.up2 = nn.ConvTranspose2d(base_ch * 4, base_ch * 2, kernel_size=2, stride=2)
        self.dec2 = ConvBlock(base_ch * 4, base_ch * 2)
        self.up1 = nn.ConvTranspose2d(base_ch * 2, base_ch, kernel_size=2, stride=2)
        self.dec1 = ConvBlock(base_ch * 2, base_ch)

        self.head = nn.Conv2d(base_ch, 1, kernel_size=1)

    def forward(self, pre: torch.Tensor, post: torch.Tensor, topo: torch.Tensor = None) -> torch.Tensor:
        x = torch.cat([pre, post], dim=1)
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        e4 = self.enc4(self.pool3(e3))

        d3 = self.dec3(torch.cat([self.up3(e4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))

        return self.head(d1)

# -----------------------------------------------------------------------------
# Baseline 4: Swin-UNet (Gatti et al. 2026 Reference Benchmark Architecture)
# -----------------------------------------------------------------------------

class SwinUNetAval(nn.Module):
    def __init__(self, in_sar_ch: int = 2, base_ch: int = 32):
        super().__init__()
        self.diff_conv = nn.Sequential(
            nn.Conv2d(in_sar_ch * 2 + 1, base_ch, kernel_size=3, padding=1),
            nn.BatchNorm2d(base_ch),
            nn.GELU()
        )
        self.enc1 = ConvBlock(base_ch, base_ch)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = ConvBlock(base_ch, base_ch * 2)
        self.pool2 = nn.MaxPool2d(2)
        self.enc3 = ConvBlock(base_ch * 2, base_ch * 4)
        self.pool3 = nn.MaxPool2d(2)
        self.enc4 = ConvBlock(base_ch * 4, base_ch * 8)

        # Spatial Self-Attention over bottleneck with adaptive pooling
        self.attn = nn.MultiheadAttention(embed_dim=base_ch * 8, num_heads=4, batch_first=True)

        self.up3 = nn.ConvTranspose2d(base_ch * 8, base_ch * 4, kernel_size=2, stride=2)
        self.dec3 = ConvBlock(base_ch * 8, base_ch * 4)
        self.up2 = nn.ConvTranspose2d(base_ch * 4, base_ch * 2, kernel_size=2, stride=2)
        self.dec2 = ConvBlock(base_ch * 4, base_ch * 2)
        self.up1 = nn.ConvTranspose2d(base_ch * 2, base_ch, kernel_size=2, stride=2)
        self.dec1 = ConvBlock(base_ch * 2, base_ch)

        self.head = nn.Conv2d(base_ch, 1, kernel_size=1)

    def forward(self, pre: torch.Tensor, post: torch.Tensor, topo: torch.Tensor = None) -> torch.Tensor:
        diff_mag = torch.norm(post - pre, dim=1, keepdim=True)
        x = torch.cat([pre, post, diff_mag], dim=1)
        feat = self.diff_conv(x)

        e1 = self.enc1(feat)
        e2 = self.enc2(self.pool1(e1))
        e3 = self.enc3(self.pool2(e2))
        e4 = self.enc4(self.pool3(e3))

        B, C, H, W = e4.shape
        tokens = e4.flatten(2).permute(0, 2, 1)
        attn_out, _ = self.attn(tokens, tokens, tokens)
        e4_attn = (tokens + attn_out).permute(0, 2, 1).view(B, C, H, W)

        d3 = self.dec3(torch.cat([self.up3(e4_attn), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))

        return self.head(d1)

# -----------------------------------------------------------------------------
# Loss Formulation: BCE + Dice + Geomorphically Bounded Loss
# -----------------------------------------------------------------------------

class CombinedGeoLoss(nn.Module):
    def __init__(self, pos_weight: float = 3.0, dice_weight: float = 1.0, geo_weight: float = 0.5):
        super().__init__()
        self.pos_weight = pos_weight
        self.dice_weight = dice_weight
        self.geo_weight = geo_weight

    def forward(
        self,
        logits: torch.Tensor,
        targets: torch.Tensor,
        topo: torch.Tensor = None
    ) -> tuple[torch.Tensor, dict[str, float]]:
        bce = F.binary_cross_entropy_with_logits(
            logits,
            targets,
            pos_weight=torch.tensor([self.pos_weight], device=logits.device)
        )

        probs = torch.sigmoid(logits)
        intersection = (probs * targets).sum(dim=[1, 2, 3])
        union = probs.sum(dim=[1, 2, 3]) + targets.sum(dim=[1, 2, 3]) + 1e-6
        dice = 1.0 - (2.0 * intersection / union).mean()

        geo_penalty = torch.tensor(0.0, device=logits.device)
        if topo is not None and self.geo_weight > 0.0:
            slope_deg = topo[:, 1:2, :, :] * 60.0
            inadmissible = (slope_deg < 5.0) | (slope_deg > 65.0)
            if inadmissible.any():
                geo_penalty = (probs * inadmissible.float()).sum() / (inadmissible.float().sum() + 1e-6)

        total_loss = bce + self.dice_weight * dice + self.geo_weight * geo_penalty

        loss_dict = {
            "total": float(total_loss.detach().cpu()),
            "bce": float(bce.detach().cpu()),
            "dice": float(dice.detach().cpu()),
            "geo": float(geo_penalty.detach().cpu())
        }
        return total_loss, loss_dict
