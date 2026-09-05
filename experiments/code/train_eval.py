#!/usr/bin/env python3
"""
Comprehensive training and cross-region evaluation pipeline for TopoRadar-Net,
competitive baselines, and ablations on the AvalCD Mountain Hazard Benchmark.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import random
import sys
import time
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import (
    RAW_DATA_DIR,
    EVENTS_TRAIN,
    EVENTS_VAL,
    EVENTS_TEST_TROMSO,
    EVENTS_TEST_PAMIR,
    EventData,
    load_event,
    AvalPatchDataset,
)
from models import (
    TopoRadarNet,
    SiamUNetDiff,
    SiamUNetConc,
    ResUNet,
    SwinUNetAval,
    CombinedGeoLoss,
)

STUDY_DIR = Path(__file__).resolve().parent.parent.parent
EXP_DIR = STUDY_DIR / "experiments"
DERIVED_DIR = EXP_DIR / "derived"
RESULTS_DIR = DERIVED_DIR / "results"
CHECKPOINTS_DIR = DERIVED_DIR / "checkpoints"
LOGS_DIR = EXP_DIR / "logs"

for d in [RESULTS_DIR, CHECKPOINTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def get_hanning_window(patch_size: int = 128) -> np.ndarray:
    w1 = np.hanning(patch_size)
    w2 = np.hanning(patch_size)
    win = np.outer(w1, w2)
    win = np.maximum(win, 0.05)  # avoid zeros at edges
    return win.astype(np.float32)

def evaluate_full_scene(
    model: nn.Module,
    event_data: EventData,
    device: torch.device,
    patch_size: int = 128,
    stride: int = 64,
    batch_size: int = 16,
) -> tuple[np.ndarray, np.ndarray]:
    """Run sliding window inference with Hanning-window blending over a full scene."""
    model.eval()
    h, w = event_data.height, event_data.width
    prob_map = np.zeros((h, w), dtype=np.float32)
    weight_map = np.zeros((h, w), dtype=np.float32)
    win = get_hanning_window(patch_size)

    rows = list(range(0, h - patch_size + 1, stride))
    if (h - patch_size) % stride != 0:
        rows.append(h - patch_size)
    cols = list(range(0, w - patch_size + 1, stride))
    if (w - patch_size) % stride != 0:
        cols.append(w - patch_size)

    coords = [(r, c) for r in rows for c in cols]
    
    with torch.no_grad():
        for i in range(0, len(coords), batch_size):
            batch_coords = coords[i : i + batch_size]
            pre_tensors = []
            post_tensors = []
            topo_tensors = []
            valid_batch_coords = []

            for r, c in batch_coords:
                v_patch = event_data.valid_mask[r : r + patch_size, c : c + patch_size]
                if v_patch.mean() < 0.2:  # skip completely invalid margin tiles
                    continue
                pre_tensors.append(torch.from_numpy(event_data.pre_sar[:, r : r + patch_size, c : c + patch_size]))
                post_tensors.append(torch.from_numpy(event_data.post_sar[:, r : r + patch_size, c : c + patch_size]))
                topo_tensors.append(torch.from_numpy(event_data.topo_geom[:, r : r + patch_size, c : c + patch_size]))
                valid_batch_coords.append((r, c))

            if not pre_tensors:
                continue

            pre_b = torch.stack(pre_tensors).float().to(device)
            post_b = torch.stack(post_tensors).float().to(device)
            topo_b = torch.stack(topo_tensors).float().to(device)

            logits = model(pre_b, post_b, topo_b)
            probs = torch.sigmoid(logits).squeeze(1).cpu().numpy()

            for idx, (r, c) in enumerate(valid_batch_coords):
                prob_map[r : r + patch_size, c : c + patch_size] += probs[idx] * win
                weight_map[r : r + patch_size, c : c + patch_size] += win

    weight_map = np.maximum(weight_map, 1e-5)
    prob_map = prob_map / weight_map
    prob_map[~event_data.valid_mask] = 0.0
    return prob_map, event_data.gt_mask

def compute_pixel_metrics(probs: np.ndarray, gt: np.ndarray, valid_mask: np.ndarray, threshold: float = 0.5) -> dict[str, float]:
    pred = (probs >= threshold) & valid_mask
    target = (gt > 0) & valid_mask

    tp = float((pred & target).sum())
    fp = float((pred & ~target).sum())
    fn = float((~pred & target).sum())
    tn = float((~pred & ~target).sum())

    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2.0 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    f2 = 5.0 * prec * rec / (4.0 * prec + rec) if (4.0 * prec + rec) > 0 else 0.0
    iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0

    return {
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "f2": f2,
        "iou": iou,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn
    }

def find_best_threshold(probs: np.ndarray, gt: np.ndarray, valid_mask: np.ndarray) -> tuple[float, float]:
    best_thresh = 0.5
    best_f1 = 0.0
    for t in np.linspace(0.2, 0.8, 31):
        m = compute_pixel_metrics(probs, gt, valid_mask, threshold=t)
        if m["f1"] > best_f1:
            best_f1 = m["f1"]
            best_thresh = float(t)
    return best_thresh, best_f1

def compute_instance_metrics(
    probs: np.ndarray,
    event_data: EventData,
    threshold: float = 0.5,
    min_coverage_30: float = 0.3,
    min_coverage_50: float = 0.5,
) -> dict:
    gdf = event_data.polygons_gdf
    if gdf is None or len(gdf) == 0:
        return {"hits_30": 0, "hits_50": 0, "total": 0, "hit_rate_30": 0.0, "hit_rate_50": 0.0}

    pred_mask = (probs >= threshold) & event_data.valid_mask
    h, w = event_data.height, event_data.width
    trans = event_data.transform

    hits_30 = 0
    hits_50 = 0
    size_hits_30 = {1: 0, 2: 0, 3: 0, 4: 0}
    size_hits_50 = {1: 0, 2: 0, 3: 0, 4: 0}
    size_totals = {1: 0, 2: 0, 3: 0, 4: 0}

    for idx, row in gdf.iterrows():
        geom = row.geometry
        sz = int(row.get("size", 0)) if "size" in row else 0
        if sz in size_totals:
            size_totals[sz] += 1

        try:
            poly_mask = rasterize(
                [(geom, 1)],
                out_shape=(h, w),
                transform=trans,
                fill=0,
                dtype=np.uint8
            )
        except Exception:
            continue

        poly_pixels = poly_mask.sum()
        if poly_pixels == 0:
            continue

        overlap = (poly_mask & pred_mask).sum()
        coverage = overlap / poly_pixels

        if coverage >= min_coverage_30:
            hits_30 += 1
            if sz in size_hits_30:
                size_hits_30[sz] += 1
        if coverage >= min_coverage_50:
            hits_50 += 1
            if sz in size_hits_50:
                size_hits_50[sz] += 1

    total = len(gdf)
    res = {
        "total_polygons": total,
        "hits_30": hits_30,
        "hit_rate_30": hits_30 / total if total > 0 else 0.0,
        "hits_50": hits_50,
        "hit_rate_50": hits_50 / total if total > 0 else 0.0,
        "size_totals": size_totals,
        "size_hits_30": size_hits_30,
        "size_hits_50": size_hits_50,
        "size_hit_rates_30": {k: (size_hits_30[k] / size_totals[k]) if size_totals[k] > 0 else 0.0 for k in size_totals},
        "size_hit_rates_50": {k: (size_hits_50[k] / size_totals[k]) if size_totals[k] > 0 else 0.0 for k in size_totals},
    }
    return res

def train_one_model(
    model_name: str,
    seed: int,
    device: torch.device,
    all_events: dict[str, EventData],
    epochs: int = 10,
    batch_size: int = 16,
    lr: float = 2e-4,
) -> tuple[nn.Module, float, dict]:
    set_seed(seed)
    train_events = {k: all_events[k] for k in EVENTS_TRAIN}
    val_events = {k: all_events[k] for k in EVENTS_VAL}

    train_ds = AvalPatchDataset(train_events, patch_size=128, stride=64, is_train=True, neg_ratio=1.0, seed=seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=True)
    val_ds = AvalPatchDataset(val_events, patch_size=128, stride=128, is_train=False, seed=seed)
    val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)

    # Initialize model
    if model_name == "TopoRadar-Net":
        model = TopoRadarNet(use_lia=True, use_aspect=True, use_cross_attn=True).to(device)
    elif model_name == "Ablation-NoLIA":
        model = TopoRadarNet(use_lia=False, use_aspect=True, use_cross_attn=True).to(device)
    elif model_name == "Ablation-NoAspect":
        model = TopoRadarNet(use_lia=True, use_aspect=False, use_cross_attn=True).to(device)
    elif model_name == "Ablation-NoCrossAttn":
        model = TopoRadarNet(use_lia=True, use_aspect=True, use_cross_attn=False).to(device)
    elif model_name == "Ablation-NoGeoLoss":
        model = TopoRadarNet(use_lia=True, use_aspect=True, use_cross_attn=True).to(device)
    elif model_name == "Swin-UNet":
        model = SwinUNetAval().to(device)
    elif model_name == "ResU-Net":
        model = ResUNet().to(device)
    elif model_name == "SiamUNet-diff":
        model = SiamUNetDiff().to(device)
    elif model_name == "SiamUNet-conc":
        model = SiamUNetConc().to(device)
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    geo_w = 0.0 if model_name == "Ablation-NoGeoLoss" else 0.5
    criterion = CombinedGeoLoss(pos_weight=3.0, dice_weight=1.0, geo_weight=geo_w)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    best_val_f1 = 0.0
    best_weights = None
    train_history = []

    print(f"--- Training {model_name} (Seed {seed}) for {epochs} epochs on {len(train_ds)} patches ---", flush=True)
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_losses = []
        for batch in train_loader:
            pre = batch["pre"].to(device)
            post = batch["post"].to(device)
            topo = batch["topo"].to(device)
            mask = batch["mask"].to(device)

            optimizer.zero_grad()
            if isinstance(model, (SiamUNetDiff, SiamUNetConc, ResUNet, SwinUNetAval)):
                logits = model(pre, post)
            else:
                logits = model(pre, post, topo)

            loss, _ = criterion(logits, mask, topo)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            optimizer.step()
            epoch_losses.append(loss.item())

        scheduler.step()
        mean_loss = float(np.mean(epoch_losses))

        # Fast patch-level validation
        model.eval()
        val_losses = []
        all_val_probs = []
        all_val_masks = []
        with torch.no_grad():
            for v_batch in val_loader:
                v_pre = v_batch["pre"].to(device)
                v_post = v_batch["post"].to(device)
                v_topo = v_batch["topo"].to(device)
                v_mask = v_batch["mask"].to(device)

                if isinstance(model, (SiamUNetDiff, SiamUNetConc, ResUNet, SwinUNetAval)):
                    v_logits = model(v_pre, v_post)
                else:
                    v_logits = model(v_pre, v_post, v_topo)

                v_loss, _ = criterion(v_logits, v_mask, v_topo)
                val_losses.append(v_loss.item())
                v_probs = torch.sigmoid(v_logits).cpu().numpy().flatten()
                v_gts = v_mask.cpu().numpy().flatten()
                all_val_probs.append(v_probs)
                all_val_masks.append(v_gts)

        p_cat = np.concatenate(all_val_probs)
        g_cat = np.concatenate(all_val_masks)
        # Compute patch val F1 at default 0.5
        val_m = compute_pixel_metrics(p_cat, g_cat, np.ones_like(g_cat, dtype=bool), threshold=0.5)
        val_f1 = val_m["f1"]
        train_history.append({"epoch": epoch, "loss": mean_loss, "val_loss": float(np.mean(val_losses)), "val_f1": val_f1})

        if val_f1 > best_val_f1 or best_weights is None:
            best_val_f1 = val_f1
            best_weights = copy.deepcopy(model.state_dict())

        print(f"  Epoch {epoch:2d}/{epochs}: Train Loss={mean_loss:.4f}, Val F1={val_f1:.4f} (best={best_val_f1:.4f})", flush=True)

    elapsed = time.time() - start_time
    print(f"Finished {model_name} in {elapsed:.1f}s. Restoring best weights (Val F1={best_val_f1:.4f}). Calibrating threshold...", flush=True)
    model.load_state_dict(best_weights)

    # Calibrate optimal operating threshold on full validation scenes
    val_thresh_list = []
    for val_ev_name, val_ev in val_events.items():
        prob_map, gt_map = evaluate_full_scene(model, val_ev, device, patch_size=128, stride=128)
        th, _ = find_best_threshold(prob_map, gt_map, val_ev.valid_mask)
        val_thresh_list.append(th)
    best_threshold = float(np.mean(val_thresh_list))
    print(f"  Calibrated operating threshold on validation scenes: tau = {best_threshold:.2f}", flush=True)
    model.load_state_dict(best_weights)

    # Save checkpoint
    ckpt_path = CHECKPOINTS_DIR / f"{model_name}_seed{seed}.pth"
    torch.save({
        "model_state_dict": model.state_dict(),
        "best_val_f1": best_val_f1,
        "best_threshold": best_threshold,
        "seed": seed,
        "model_name": model_name
    }, ckpt_path)

    return model, best_threshold, {"val_f1": best_val_f1, "best_threshold": best_threshold, "history": train_history, "elapsed": elapsed}

def run_experiment_suite(epochs: int = 6, models_list: list[str] = None):
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Starting experiment suite on device: {device}")

    # Load all 7 events
    print("Loading all 7 AvalCD events into RAM...")
    all_events = {}
    for ev in EVENTS_TRAIN + EVENTS_VAL + EVENTS_TEST_TROMSO + EVENTS_TEST_PAMIR:
        all_events[ev] = load_event(ev)
        print(f"  Loaded {ev}: shape={all_events[ev].height}x{all_events[ev].width}")

    if models_list is None:
        models_to_run = [
            "TopoRadar-Net",
            "Swin-UNet",
            "ResU-Net",
            "SiamUNet-diff",
            "SiamUNet-conc",
            "Ablation-NoLIA",
            "Ablation-NoAspect",
            "Ablation-NoCrossAttn",
            "Ablation-NoGeoLoss",
        ]
    else:
        models_to_run = models_list

    seeds = [42, 123, 456]
    test_events = {
        "Tromso_Arctic": all_events[EVENTS_TEST_TROMSO[0]],
        "Pamir_HighMountain": all_events[EVENTS_TEST_PAMIR[0]],
    }

    results_by_model = {m: {"seeds": {}, "summary": {}} for m in models_to_run}
    raw_predictions = {}

    for model_name in models_to_run:
        results_by_model[model_name]["seeds"] = {}
        for s in seeds:
            model, calib_th, train_meta = train_one_model(
                model_name=model_name,
                seed=s,
                device=device,
                all_events=all_events,
                epochs=epochs,
                batch_size=16,
            )

            # Evaluate on unseen mountain systems
            seed_res = {"calib_threshold": calib_th, "train_meta": train_meta, "regions": {}}
            for r_name, r_ev in test_events.items():
                prob_map, gt_map = evaluate_full_scene(model, r_ev, device, patch_size=128, stride=64)
                pix_metrics = compute_pixel_metrics(prob_map, gt_map, r_ev.valid_mask, threshold=calib_th)
                inst_metrics = compute_instance_metrics(prob_map, r_ev, threshold=calib_th)

                seed_res["regions"][r_name] = {
                    "pixel": pix_metrics,
                    "instance": inst_metrics
                }

                pred_key = f"{model_name}_seed{s}_{r_name}"
                raw_predictions[pred_key] = {
                    "probs": prob_map,
                    "gt": gt_map,
                    "valid": r_ev.valid_mask,
                    "calib_th": calib_th
                }

            results_by_model[model_name]["seeds"][str(s)] = seed_res

    # Compute mean and std across seeds for each model and region
    for model_name in models_to_run:
        summary = {"regions": {}, "pooled": {}}
        for r_name in test_events:
            metrics_acc = {"f1": [], "f2": [], "iou": [], "precision": [], "recall": [], "hit_rate_30": [], "hit_rate_50": []}
            for s in seeds:
                m = results_by_model[model_name]["seeds"][str(s)]["regions"][r_name]
                metrics_acc["f1"].append(m["pixel"]["f1"])
                metrics_acc["f2"].append(m["pixel"]["f2"])
                metrics_acc["iou"].append(m["pixel"]["iou"])
                metrics_acc["precision"].append(m["pixel"]["precision"])
                metrics_acc["recall"].append(m["pixel"]["recall"])
                metrics_acc["hit_rate_30"].append(m["instance"]["hit_rate_30"])
                metrics_acc["hit_rate_50"].append(m["instance"]["hit_rate_50"])

            summary["regions"][r_name] = {
                k: {
                    "mean": float(np.mean(v)),
                    "std": float(np.std(v)),
                    "min": float(np.min(v)),
                    "max": float(np.max(v))
                } for k, v in metrics_acc.items()
            }

        # Pooled test score across both unseen mountain systems
        pooled_f1 = [
            0.5 * (results_by_model[model_name]["seeds"][str(s)]["regions"]["Tromso_Arctic"]["pixel"]["f1"] +
                   results_by_model[model_name]["seeds"][str(s)]["regions"]["Pamir_HighMountain"]["pixel"]["f1"])
            for s in seeds
        ]
        pooled_iou = [
            0.5 * (results_by_model[model_name]["seeds"][str(s)]["regions"]["Tromso_Arctic"]["pixel"]["iou"] +
                   results_by_model[model_name]["seeds"][str(s)]["regions"]["Pamir_HighMountain"]["pixel"]["iou"])
            for s in seeds
        ]
        pooled_f2 = [
            0.5 * (results_by_model[model_name]["seeds"][str(s)]["regions"]["Tromso_Arctic"]["pixel"]["f2"] +
                   results_by_model[model_name]["seeds"][str(s)]["regions"]["Pamir_HighMountain"]["pixel"]["f2"])
            for s in seeds
        ]
        pooled_hr30 = [
            0.5 * (results_by_model[model_name]["seeds"][str(s)]["regions"]["Tromso_Arctic"]["instance"]["hit_rate_30"] +
                   results_by_model[model_name]["seeds"][str(s)]["regions"]["Pamir_HighMountain"]["instance"]["hit_rate_30"])
            for s in seeds
        ]

        summary["pooled"] = {
            "f1": {"mean": float(np.mean(pooled_f1)), "std": float(np.std(pooled_f1))},
            "iou": {"mean": float(np.mean(pooled_iou)), "std": float(np.std(pooled_iou))},
            "f2": {"mean": float(np.mean(pooled_f2)), "std": float(np.std(pooled_f2))},
            "hit_rate_30": {"mean": float(np.mean(pooled_hr30)), "std": float(np.std(pooled_hr30))},
        }
        results_by_model[model_name]["summary"] = summary

    # Statistical significance testing via 1,000-draw paired cluster bootstrap
    print("\n--- Running 1,000-draw Paired Cluster Bootstrap Significance Testing ---")
    bootstrap_results = {}
    n_boot = 1000
    rng = np.random.default_rng(2026)

    # We evaluate bootstrap on Tromso test patches
    tromso_ev = test_events["Tromso_Arctic"]
    h, w = tromso_ev.height, tromso_ev.width
    tile_h, tile_w = 128, 128
    grid_rows = list(range(0, h - tile_h + 1, tile_h))
    grid_cols = list(range(0, w - tile_w + 1, tile_w))
    grid_cells = [(r, c) for r in grid_rows for c in grid_cols]

    topo_pred_seed42 = raw_predictions[f"TopoRadar-Net_seed42_Tromso_Arctic"]
    p_topo = topo_pred_seed42["probs"] >= topo_pred_seed42["calib_th"]
    gt_tromso = tromso_ev.gt_mask > 0
    valid_tromso = tromso_ev.valid_mask

    for other_model in [m for m in models_to_run if m != "TopoRadar-Net"]:
        other_pred = raw_predictions[f"{other_model}_seed42_Tromso_Arctic"]
        p_other = other_pred["probs"] >= other_pred["calib_th"]

        delta_f1_samples = []
        for _ in range(n_boot):
            sampled_cells = rng.choice(len(grid_cells), size=len(grid_cells), replace=True)
            # Accumulate TPs, FPs, FNs across sampled grid blocks
            tp_t, fp_t, fn_t = 0, 0, 0
            tp_o, fp_o, fn_o = 0, 0, 0
            for idx in sampled_cells:
                r, c = grid_cells[idx]
                v = valid_tromso[r : r + tile_h, c : c + tile_w]
                g = gt_tromso[r : r + tile_h, c : c + tile_w]
                pred_t = p_topo[r : r + tile_h, c : c + tile_w]
                pred_o = p_other[r : r + tile_h, c : c + tile_w]

                tp_t += int(((pred_t & g) & v).sum())
                fp_t += int(((pred_t & ~g) & v).sum())
                fn_t += int(((~pred_t & g) & v).sum())

                tp_o += int(((pred_o & g) & v).sum())
                fp_o += int(((pred_o & ~g) & v).sum())
                fn_o += int(((~pred_o & g) & v).sum())

            f1_t = (2.0 * tp_t) / (2.0 * tp_t + fp_t + fn_t) if (2.0 * tp_t + fp_t + fn_t) > 0 else 0.0
            f1_o = (2.0 * tp_o) / (2.0 * tp_o + fp_o + fn_o) if (2.0 * tp_o + fp_o + fn_o) > 0 else 0.0
            delta_f1_samples.append(f1_t - f1_o)

        delta_f1_samples = np.array(delta_f1_samples)
        mean_delta = float(np.mean(delta_f1_samples))
        ci_lower = float(np.percentile(delta_f1_samples, 2.5))
        ci_upper = float(np.percentile(delta_f1_samples, 97.5))
        p_val = float(2.0 * min((delta_f1_samples <= 0).mean(), (delta_f1_samples >= 0).mean()))
        p_val = min(p_val, 1.0)

        bootstrap_results[other_model] = {
            "mean_gain": mean_delta,
            "ci_95": [ci_lower, ci_upper],
            "p_value": p_val,
            "statistically_significant": bool(ci_lower > 0.0 and p_val < 0.05)
        }
        print(f"  TopoRadar-Net vs {other_model:20s}: delta F1 = +{mean_delta*100:.2f}% (95% CI: [{ci_lower*100:.2f}%, {ci_upper*100:.2f}%], p={p_val:.4f})")

    # Save all output JSON files
    with open(RESULTS_DIR / "confirmatory_results_summary.json", "w") as f:
        json.dump(results_by_model, f, indent=2)

    with open(RESULTS_DIR / "bootstrap_significance.json", "w") as f:
        json.dump(bootstrap_results, f, indent=2)

    print(f"\nSaved all results to {RESULTS_DIR}")
    print("Execution completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--models", type=str, default=None, help="Comma separated models to run")
    args = parser.parse_args()

    models_list = args.models.split(",") if args.models else None
    run_experiment_suite(epochs=args.epochs, models_list=models_list)
