#!/usr/bin/env python3
"""
Evaluate Above-Parity Evidence for TopoRadar-Net on the AvalCD Mountain Hazard Benchmark:
1. Genuine 339-Block Spatial Cluster Bootstrap across both unseen mountain test regions (Tromso + Pamir).
2. Topographic Radar Geometry Stratification (Radar-Aspect Look Alignment & Slope Gradient Zones).
"""

import json
from pathlib import Path
import numpy as np
import torch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import load_event, EVENTS_TEST_TROMSO, EVENTS_TEST_PAMIR
from models import TopoRadarNet, SwinUNetAval, ResUNet, SiamUNetConc, SiamUNetDiff
from train_eval import evaluate_full_scene, compute_pixel_metrics

EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "derived/results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINTS_DIR = EXP_DIR / "derived/checkpoints"

def main():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Evaluating above-parity evidence on device: {device}")

    tromso = load_event(EVENTS_TEST_TROMSO[0])
    pamir = load_event(EVENTS_TEST_PAMIR[0])

    model_constructors = {
        "TopoRadar-Net": lambda: TopoRadarNet().to(device),
        "Swin-UNet": lambda: SwinUNetAval().to(device),
        "ResU-Net": lambda: ResUNet().to(device),
        "SiamUNet-conc": lambda: SiamUNetConc().to(device),
        "SiamUNet-diff": lambda: SiamUNetDiff().to(device),
    }

    preds = {}
    models_inst = {}
    for m_name, ctor in model_constructors.items():
        m = ctor()
        ckpt = torch.load(CHECKPOINTS_DIR / f"{m_name}_seed42.pth", map_location="cpu")
        m.load_state_dict(ckpt["model_state_dict"])
        th = ckpt["best_threshold"]
        models_inst[m_name] = (m, th)

        p_tr, _ = evaluate_full_scene(m, tromso, device, patch_size=128, stride=64)
        p_pa, _ = evaluate_full_scene(m, pamir, device, patch_size=128, stride=64)

        preds[m_name] = {
            "tromso_prob": p_tr,
            "tromso_pred": (p_tr >= th) & tromso.valid_mask,
            "pamir_prob": p_pa,
            "pamir_pred": (p_pa >= th) & pamir.valid_mask,
            "th": th
        }

    gt_tr_bin = (tromso.gt_mask > 0) & tromso.valid_mask
    gt_pa_bin = (pamir.gt_mask > 0) & pamir.valid_mask

    # -------------------------------------------------------------------------
    # 1. Genuine 339-Block Spatial Cluster Bootstrap (Tromso 143 + Pamir 196)
    # -------------------------------------------------------------------------
    print("\n--- 1. Running Genuine 339-Block Spatial Cluster Bootstrap ---")
    tile_h, tile_w = 128, 128
    blocks = []

    # Tromso blocks (143 blocks)
    for r in range(0, tromso.height - tile_h + 1, tile_h):
        for c in range(0, tromso.width - tile_w + 1, tile_w):
            v = tromso.valid_mask[r : r + tile_h, c : c + tile_w]
            if v.mean() > 0.1:
                blocks.append(("tromso", r, c))

    # Pamir blocks (196 blocks)
    for r in range(0, pamir.height - tile_h + 1, tile_h):
        for c in range(0, pamir.width - tile_w + 1, tile_w):
            v = pamir.valid_mask[r : r + tile_h, c : c + tile_w]
            if v.mean() > 0.1:
                blocks.append(("pamir", r, c))

    print(f"Total independent geographic spatial blocks: {len(blocks)} (Tromso={sum(1 for b in blocks if b[0]=='tromso')}, Pamir={sum(1 for b in blocks if b[0]=='pamir')})")

    block_data = {}
    for m_name in model_constructors:
        block_data[m_name] = []
        for reg, r, c in blocks:
            if reg == "tromso":
                p = preds[m_name]["tromso_pred"][r : r + tile_h, c : c + tile_w]
                g = gt_tr_bin[r : r + tile_h, c : c + tile_w]
                v = tromso.valid_mask[r : r + tile_h, c : c + tile_w]
            else:
                p = preds[m_name]["pamir_pred"][r : r + tile_h, c : c + tile_w]
                g = gt_pa_bin[r : r + tile_h, c : c + tile_w]
                v = pamir.valid_mask[r : r + tile_h, c : c + tile_w]
            tp = int(((p & g) & v).sum())
            fp = int(((p & ~g) & v).sum())
            fn = int(((~p & g) & v).sum())
            block_data[m_name].append((tp, fp, fn))
        block_data[m_name] = np.array(block_data[m_name])

    topo_blocks = block_data["TopoRadar-Net"]
    N = len(blocks)
    n_boot = 1000
    rng = np.random.default_rng(2026)

    spatial_bootstrap_results = {}
    for other in [m for m in model_constructors if m != "TopoRadar-Net"]:
        other_blocks = block_data[other]
        deltas = []
        for _ in range(n_boot):
            idx = rng.choice(N, size=N, replace=True)
            t_sample = topo_blocks[idx]
            o_sample = other_blocks[idx]

            tp_t, fp_t, fn_t = t_sample[:, 0].sum(), t_sample[:, 1].sum(), t_sample[:, 2].sum()
            tp_o, fp_o, fn_o = o_sample[:, 0].sum(), o_sample[:, 1].sum(), o_sample[:, 2].sum()

            f1_t = 2.0 * tp_t / (2.0 * tp_t + fp_t + fn_t) if (2.0 * tp_t + fp_t + fn_t) > 0 else 0.0
            f1_o = 2.0 * tp_o / (2.0 * tp_o + fp_o + fn_o) if (2.0 * tp_o + fp_o + fn_o) > 0 else 0.0
            deltas.append(f1_t - f1_o)

        deltas = np.array(deltas)
        mean_d = float(np.mean(deltas))
        ci_l = float(np.percentile(deltas, 2.5))
        ci_u = float(np.percentile(deltas, 97.5))
        p_val = float(2.0 * min((deltas <= 0).mean(), (deltas >= 0).mean()))
        p_val = min(p_val, 1.0)

        spatial_bootstrap_results[other] = {
            "mean_gain": mean_d,
            "ci_95": [ci_l, ci_u],
            "p_value": p_val,
            "statistically_significant": bool(ci_l > 0.0 and p_val < 0.05),
            "n_spatial_clusters": N
        }
        print(f"  TopoRadar-Net vs {other:15s}: Mean Gain = {mean_d*100:+.2f}% (95% CI: [{ci_l*100:+.2f}%, {ci_u*100:+.2f}%], p={p_val:.4f})")

    with open(RESULTS_DIR / "spatial_multiregion_cluster_bootstrap.json", "w") as f:
        json.dump(spatial_bootstrap_results, f, indent=2)

    # -------------------------------------------------------------------------
    # 2. Topographic Radar Geometry Stratification (Tromso & Pamir)
    # -------------------------------------------------------------------------
    print("\n--- 2. Computing Topographic Radar Geometry Stratification ---")
    stratification_results = {"Tromso_Arctic": {}, "Pamir_HighMountain": {}}

    regions_data = [
        ("Tromso_Arctic", tromso, preds["TopoRadar-Net"]["tromso_prob"], preds["Swin-UNet"]["tromso_prob"], preds["TopoRadar-Net"]["th"], preds["Swin-UNet"]["th"]),
        ("Pamir_HighMountain", pamir, preds["TopoRadar-Net"]["pamir_prob"], preds["Swin-UNet"]["pamir_prob"], preds["TopoRadar-Net"]["th"], preds["Swin-UNet"]["th"]),
    ]

    for reg_name, ev_data, p_topo, p_swin, th_t, th_s in regions_data:
        gt = ev_data.gt_mask
        slp_deg = ev_data.topo_geom[1] * 60.0
        align = ev_data.topo_geom[5]

        reg_dict = {"aspect_alignment": {}, "slope_zones": {}}

        # Aspect strata
        aspect_strata = [
            ("Foreslopes (Radar-Facing, align > 0.3)", align > 0.3),
            ("Cross-slopes (|align| <= 0.3)", (align >= -0.3) & (align <= 0.3)),
            ("Backslopes (Facing Away, align < -0.3)", align < -0.3),
        ]
        for s_name, cond in aspect_strata:
            m_cond = cond & ev_data.valid_mask
            n_pos = int(((gt > 0) & m_cond).sum())
            n_total = int(m_cond.sum())
            res_t = compute_pixel_metrics(p_topo, gt, m_cond, threshold=th_t)
            res_s = compute_pixel_metrics(p_swin, gt, m_cond, threshold=th_s)

            reg_dict["aspect_alignment"][s_name] = {
                "positive_pixels": n_pos,
                "total_pixels": n_total,
                "toporadar": res_t,
                "swin_unet": res_s,
                "delta_f1": float(res_t["f1"] - res_s["f1"]),
                "delta_iou": float(res_t["iou"] - res_s["iou"]),
                "delta_recall": float(res_t["recall"] - res_s["recall"])
            }
            print(f"[{reg_name}] {s_name} (pos={n_pos:,}): TopoRadar F1={res_t['f1']*100:.2f}% vs Swin F1={res_s['f1']*100:.2f}% (Delta = {res_t['f1']*100 - res_s['f1']*100:+.2f}%)")

        # Slope strata
        slope_strata = [
            ("Runout & Valley (< 25 deg)", slp_deg < 25.0),
            ("Avalanche Chutes & Slopes (25 - 45 deg)", (slp_deg >= 25.0) & (slp_deg <= 45.0)),
            ("Extreme Steep Slopes (> 45 deg)", slp_deg > 45.0),
        ]
        for s_name, cond in slope_strata:
            m_cond = cond & ev_data.valid_mask
            n_pos = int(((gt > 0) & m_cond).sum())
            n_total = int(m_cond.sum())
            res_t = compute_pixel_metrics(p_topo, gt, m_cond, threshold=th_t)
            res_s = compute_pixel_metrics(p_swin, gt, m_cond, threshold=th_s)

            reg_dict["slope_zones"][s_name] = {
                "positive_pixels": n_pos,
                "total_pixels": n_total,
                "toporadar": res_t,
                "swin_unet": res_s,
                "delta_f1": float(res_t["f1"] - res_s["f1"]),
                "delta_iou": float(res_t["iou"] - res_s["iou"]),
                "delta_recall": float(res_t["recall"] - res_s["recall"])
            }
            print(f"[{reg_name}] {s_name} (pos={n_pos:,}): TopoRadar F1={res_t['f1']*100:.2f}% vs Swin F1={res_s['f1']*100:.2f}% (Delta = {res_t['f1']*100 - res_s['f1']*100:+.2f}%)")

        stratification_results[reg_name] = reg_dict

    with open(RESULTS_DIR / "topographic_geometry_stratification.json", "w") as f:
        json.dump(stratification_results, f, indent=2)

    print(f"\nAll above-parity artifacts generated successfully in {RESULTS_DIR}")

if __name__ == "__main__":
    main()
