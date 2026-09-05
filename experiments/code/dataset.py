#!/usr/bin/env python3
"""Dataset loader and patch generator for AvalCD Mountain Hazard Benchmark."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import geopandas as gpd
import numpy as np
import rasterio
import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TF
from scipy.ndimage import binary_fill_holes
from torchvision.transforms import InterpolationMode

RAW_DATA_DIR = Path("research/broad-physical-truth-corpus-shortlist-gpt56/pilot_avalcd_event_equal_f2_01/raw/AvalCD")

EVENTS_TRAIN = ["Livigno_20240403", "Livigno_20250129", "Nuuk_20160413"]
EVENTS_VAL = ["Livigno_20250318", "Nuuk_20210411"]
EVENTS_TEST_TROMSO = ["Tromso_20241220"]
EVENTS_TEST_PAMIR = ["Pish_20230221"]

@dataclass
class EventData:
    event: str
    pre_sar: np.ndarray      # (2, H, W) [VH, VV] dB
    post_sar: np.ndarray     # (2, H, W) [VH, VV] dB
    diff_sar: np.ndarray     # (3, H, W) [diff_VH, diff_VV, diff_ratio]
    topo_geom: np.ndarray    # (6, H, W) [cos(LIA), slope_norm, sin(asp), cos(asp), dem_norm, align_look]
    valid_mask: np.ndarray   # (H, W) bool
    gt_mask: np.ndarray      # (H, W) uint8
    polygons_gdf: Optional[gpd.GeoDataFrame] = None
    transform: object = None
    crs: object = None

    @property
    def height(self) -> int:
        return self.gt_mask.shape[0]

    @property
    def width(self) -> int:
        return self.gt_mask.shape[1]

def read_raster(path: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32)
        meta = {
            "transform": src.transform,
            "crs": src.crs,
            "nodata": src.nodata,
            "shape": (src.height, src.width)
        }
        if meta["nodata"] is not None and np.isfinite(meta["nodata"]):
            arr[arr == meta["nodata"]] = np.nan
        return arr, meta

def load_event(event_name: str, root_dir: Path = RAW_DATA_DIR) -> EventData:
    p = root_dir / event_name
    pre_vh, meta = read_raster(p / f"{event_name}_preVH.tif")
    pre_vv, _ = read_raster(p / f"{event_name}_preVV.tif")
    post_vh, _ = read_raster(p / f"{event_name}_postVH.tif")
    post_vv, _ = read_raster(p / f"{event_name}_postVV.tif")

    lia, _ = read_raster(p / f"{event_name}_LIA.tif")
    dem, _ = read_raster(p / f"{event_name}_DEM.tif")
    slp, _ = read_raster(p / f"{event_name}_SLP.tif")
    asp, _ = read_raster(p / f"{event_name}_ASP.tif")
    gt, _ = read_raster(p / f"{event_name}_GT.tif")

    gpkg_path = p / f"{event_name}_GT.gpkg"
    gdf = gpd.read_file(gpkg_path) if gpkg_path.exists() else None

    # SAR valid bounds
    pre_vh[(pre_vh < -45.0) | (pre_vh > 15.0)] = np.nan
    pre_vv[(pre_vv < -45.0) | (pre_vv > 15.0)] = np.nan
    post_vh[(post_vh < -45.0) | (post_vh > 15.0)] = np.nan
    post_vv[(post_vv < -45.0) | (post_vv > 15.0)] = np.nan

    valid = np.isfinite(pre_vh) & np.isfinite(pre_vv) & np.isfinite(post_vh) & np.isfinite(post_vv) & np.isfinite(lia) & np.isfinite(slp) & np.isfinite(asp)

    # Compute difference features
    diff_vh = post_vh - pre_vh
    diff_vv = post_vv - pre_vv
    # Cross-pol ratio change: (post_vh - post_vv) - (pre_vh - pre_vv) = diff_vh - diff_vv
    diff_cr = diff_vh - diff_vv

    # Topographic geometry
    lia_rad = np.radians(np.clip(lia, 0.0, 180.0))
    cos_lia = np.cos(lia_rad)

    slp_norm = np.clip(slp / 60.0, 0.0, 1.5)  # 60 degrees as characteristic scaling

    asp_rad = np.radians(np.nan_to_num(asp, nan=0.0))
    sin_asp = np.sin(asp_rad)
    cos_asp = np.cos(asp_rad)

    dem_norm = (np.nan_to_num(dem, nan=2000.0) - 2000.0) / 1000.0

    # Sentinel-1 nominal look vectors (ascending look ~78 deg, descending look ~282 deg)
    # Alignment with ascending look direction:
    align_look = np.cos(asp_rad - math.radians(78.0))

    # Clean NaNs in features with sentinel values
    pre_vh_clean = np.nan_to_num(pre_vh, nan=-20.0)
    pre_vv_clean = np.nan_to_num(pre_vv, nan=-12.0)
    post_vh_clean = np.nan_to_num(post_vh, nan=-20.0)
    post_vv_clean = np.nan_to_num(post_vv, nan=-12.0)
    diff_vh_clean = np.nan_to_num(diff_vh, nan=0.0)
    diff_vv_clean = np.nan_to_num(diff_vv, nan=0.0)
    diff_cr_clean = np.nan_to_num(diff_cr, nan=0.0)

    pre_sar = np.stack([pre_vh_clean, pre_vv_clean], axis=0)
    post_sar = np.stack([post_vh_clean, post_vv_clean], axis=0)
    diff_sar = np.stack([diff_vh_clean, diff_vv_clean, diff_cr_clean], axis=0)

    topo_geom = np.stack([
        np.nan_to_num(cos_lia, nan=0.7),
        np.nan_to_num(slp_norm, nan=0.5),
        np.nan_to_num(sin_asp, nan=0.0),
        np.nan_to_num(cos_asp, nan=1.0),
        np.nan_to_num(dem_norm, nan=0.0),
        np.nan_to_num(align_look, nan=0.0),
    ], axis=0)

    gt_clean = np.nan_to_num(gt, nan=0.0).astype(np.uint8)

    return EventData(
        event=event_name,
        pre_sar=pre_sar,
        post_sar=post_sar,
        diff_sar=diff_sar,
        topo_geom=topo_geom,
        valid_mask=valid,
        gt_mask=gt_clean,
        polygons_gdf=gdf,
        transform=meta["transform"],
        crs=meta["crs"]
    )

def extract_patch_coords(data: EventData, patch_size: int = 128, stride: int = 64) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Extract grid coordinates separated into positive (containing avalanche) and negative."""
    h, w = data.height, data.width
    pos_coords = []
    neg_coords = []
    filled = binary_fill_holes(data.valid_mask)

    for r in range(0, h - patch_size + 1, stride):
        for c in range(0, w - patch_size + 1, stride):
            patch_valid = data.valid_mask[r : r + patch_size, c : c + patch_size]
            if patch_valid.mean() < 0.6:  # discard patches with >40% nodata
                continue
            gt_patch = data.gt_mask[r : r + patch_size, c : c + patch_size]
            if gt_patch.sum() > 5:  # at least 5 positive pixels
                pos_coords.append((r, c))
            else:
                neg_coords.append((r, c))

    return pos_coords, neg_coords

class AvalPatchDataset(torch.utils.data.Dataset):
    """PyTorch Dataset yielding bitemporal SAR, Topographic Geometry, and Avalanche Mask."""
    def __init__(
        self,
        events: dict[str, EventData],
        patch_size: int = 128,
        stride: int = 64,
        is_train: bool = True,
        neg_ratio: float = 1.0,
        seed: int = 42
    ):
        self.events = events
        self.patch_size = patch_size
        self.is_train = is_train
        self.samples = []

        rng = np.random.default_rng(seed)
        all_pos = []
        all_neg = []

        for ev_name, ev_data in events.items():
            pos, neg = extract_patch_coords(ev_data, patch_size, stride)
            for r, c in pos:
                all_pos.append((ev_name, r, c))
            for r, c in neg:
                all_neg.append((ev_name, r, c))

        if is_train:
            n_neg = int(len(all_pos) * neg_ratio)
            chosen_neg_idx = rng.choice(len(all_neg), size=min(n_neg, len(all_neg)), replace=False)
            chosen_neg = [all_neg[i] for i in chosen_neg_idx]
            self.samples = all_pos + chosen_neg
            rng.shuffle(self.samples)
        else:
            # In validation, evaluate on all positive patches plus balanced negative sample
            n_neg = min(len(all_pos) * 2, len(all_neg))
            chosen_neg_idx = rng.choice(len(all_neg), size=n_neg, replace=False)
            self.samples = all_pos + [all_neg[i] for i in chosen_neg_idx]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        ev_name, r, c = self.samples[idx]
        ev = self.events[ev_name]
        ps = self.patch_size

        pre = torch.from_numpy(ev.pre_sar[:, r : r + ps, c : c + ps]).float()
        post = torch.from_numpy(ev.post_sar[:, r : r + ps, c : c + ps]).float()
        diff = torch.from_numpy(ev.diff_sar[:, r : r + ps, c : c + ps]).float()
        topo = torch.from_numpy(ev.topo_geom[:, r : r + ps, c : c + ps]).float()
        mask = torch.from_numpy(ev.gt_mask[r : r + ps, c : c + ps]).unsqueeze(0).float()

        # Data augmentation during training
        if self.is_train:
            if torch.rand(1).item() > 0.5:
                pre = TF.hflip(pre)
                post = TF.hflip(post)
                diff = TF.hflip(diff)
                topo = TF.hflip(topo)
                mask = TF.hflip(mask)
                # Aspect sin component flips on horizontal flip
                topo[2, :, :] = -topo[2, :, :]
            if torch.rand(1).item() > 0.5:
                pre = TF.vflip(pre)
                post = TF.vflip(post)
                diff = TF.vflip(diff)
                topo = TF.vflip(topo)
                mask = TF.vflip(mask)
                # Aspect cos component flips on vertical flip
                topo[3, :, :] = -topo[3, :, :]
            k = torch.randint(0, 4, (1,)).item()
            if k > 0:
                pre = torch.rot90(pre, k, [1, 2])
                post = torch.rot90(post, k, [1, 2])
                diff = torch.rot90(diff, k, [1, 2])
                topo = torch.rot90(topo, k, [1, 2])
                mask = torch.rot90(mask, k, [1, 2])

        return {
            "pre": pre,       # (2, 128, 128)
            "post": post,     # (2, 128, 128)
            "diff": diff,     # (3, 128, 128)
            "topo": topo,     # (6, 128, 128)
            "mask": mask,     # (1, 128, 128)
            "event": ev_name
        }

if __name__ == "__main__":
    print("Testing AvalCD dataset loader...")
    train_events = {e: load_event(e) for e in EVENTS_TRAIN[:2]}
    ds = AvalPatchDataset(train_events, patch_size=128, stride=64, is_train=True)
    print(f"Dataset created with {len(ds)} samples.")
    batch = ds[0]
    print(f"Sample shapes: pre={batch['pre'].shape}, post={batch['post'].shape}, diff={batch['diff'].shape}, topo={batch['topo'].shape}, mask={batch['mask'].shape}")
    print("Loader test passed!")
