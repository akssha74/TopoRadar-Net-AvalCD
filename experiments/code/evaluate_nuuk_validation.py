#!/usr/bin/env python3
"""Evaluate all models across 3 seeds on Nuuk 2021 validation scene."""

import json
from pathlib import Path
import numpy as np
import torch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import load_event
from models import TopoRadarNet, SwinUNetAval, ResUNet, SiamUNetConc, SiamUNetDiff
from train_eval import evaluate_full_scene, compute_pixel_metrics

EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "derived/results"
CHECKPOINTS_DIR = EXP_DIR / "derived/checkpoints"

def main():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    nuuk21 = load_event("Nuuk_20210411")
    seeds = [42, 123, 456]
    models = ["TopoRadar-Net", "Swin-UNet", "ResU-Net", "SiamUNet-conc", "SiamUNet-diff"]
    model_classes = {
        "TopoRadar-Net": TopoRadarNet,
        "Swin-UNet": SwinUNetAval,
        "ResU-Net": ResUNet,
        "SiamUNet-conc": SiamUNetConc,
        "SiamUNet-diff": SiamUNetDiff
    }

    results = {
        "Nuuk_20210411_Validation_Cohort": {
            "positive_pixels": int((nuuk21.gt_mask > 0).sum()),
            "valid_pixels": int(nuuk21.valid_mask.sum()),
            "polygons": len(nuuk21.polygons_gdf) if nuuk21.polygons_gdf is not None else 129,
            "models": {}
        }
    }

    for m_name in models:
        f1s, ious, precs, recs = [], [], [], []
        seed_dict = {}
        for s in seeds:
            ckpt_path = CHECKPOINTS_DIR / f"{m_name}_seed{s}.pth"
            ckpt = torch.load(ckpt_path, map_location="cpu")
            m = model_classes[m_name]().to(device)
            m.load_state_dict(ckpt["model_state_dict"])
            m.eval()
            p, gt = evaluate_full_scene(m, nuuk21, device, patch_size=128, stride=64)
            th = ckpt["best_threshold"]
            met = compute_pixel_metrics(p, gt, nuuk21.valid_mask, threshold=th)
            f1s.append(met["f1"])
            ious.append(met["iou"])
            precs.append(met["precision"])
            recs.append(met["recall"])
            seed_dict[str(s)] = {
                "f1": float(met["f1"]),
                "prec": float(met["precision"]),
                "rec": float(met["recall"]),
                "iou": float(met["iou"])
            }
        results["Nuuk_20210411_Validation_Cohort"]["models"][m_name] = {
            "f1_mean": float(np.mean(f1s)),
            "f1_std": float(np.std(f1s)),
            "iou_mean": float(np.mean(ious)),
            "prec_mean": float(np.mean(precs)),
            "rec_mean": float(np.mean(recs)),
            "seeds": seed_dict
        }

    with open(RESULTS_DIR / "nuuk_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Nuuk validation evaluation completed successfully!")

if __name__ == "__main__":
    main()
