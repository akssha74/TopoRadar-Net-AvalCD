#!/usr/bin/env python3
"""Multi-seed topographic-stratum evaluation on both held-out test systems."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import EVENTS_TEST_PAMIR, EVENTS_TEST_TROMSO, load_event
from models import AttentionUNetAval, TopoRadarNet
from train_eval import compute_pixel_metrics, evaluate_full_scene


EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "derived/results"
CHECKPOINTS_DIR = EXP_DIR / "derived/checkpoints"
SEEDS = (42, 123, 456)


def _strata(event):
    slope = event.topo_geom[1] * 60.0
    align = event.topo_geom[5]
    return {
        "aspect_alignment": {
            "Foreslopes (Radar-Facing, align > 0.3)": align > 0.3,
            "Cross-slopes (|align| <= 0.3)": (align >= -0.3) & (align <= 0.3),
            "Backslopes (Facing Away, align < -0.3)": align < -0.3,
        },
        "slope_zones": {
            "Runout & Valley (< 25 deg)": slope < 25.0,
            "Avalanche Chutes & Slopes (25 - 45 deg)": (slope >= 25.0) & (slope <= 45.0),
            "Extreme Steep Slopes (> 45 deg)": slope > 45.0,
        },
    }


def _summary(values):
    arr = np.asarray(values, dtype=float)
    return {
        "mean": float(arr.mean()),
        "std_population": float(arr.std(ddof=0)),
        "values": [float(v) for v in arr],
    }


def main():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Multi-seed stratification device: {device}")

    regions = {
        "Tromso_Arctic": load_event(EVENTS_TEST_TROMSO[0]),
        "Pamir_HighMountain": load_event(EVENTS_TEST_PAMIR[0]),
    }
    raw = {region: {} for region in regions}

    for seed in SEEDS:
        models = {
            "TopoRadar-Net": TopoRadarNet().to(device),
            "Attention U-Net": AttentionUNetAval().to(device),
        }
        checkpoint_names = {
            "TopoRadar-Net": f"TopoRadar-Net_seed{seed}.pth",
            "Attention U-Net": f"Swin-UNet_seed{seed}.pth",
        }
        thresholds = {}
        for name, model in models.items():
            checkpoint = torch.load(
                CHECKPOINTS_DIR / checkpoint_names[name], map_location="cpu"
            )
            model.load_state_dict(checkpoint["model_state_dict"])
            thresholds[name] = float(checkpoint["best_threshold"])

        for region_name, event in regions.items():
            probabilities = {}
            for name, model in models.items():
                probabilities[name], _ = evaluate_full_scene(
                    model, event, device, patch_size=128, stride=64
                )

            seed_record = {}
            for family, family_strata in _strata(event).items():
                seed_record[family] = {}
                for stratum_name, condition in family_strata.items():
                    mask = condition & event.valid_mask
                    topo = compute_pixel_metrics(
                        probabilities["TopoRadar-Net"],
                        event.gt_mask,
                        mask,
                        threshold=thresholds["TopoRadar-Net"],
                    )
                    attention = compute_pixel_metrics(
                        probabilities["Attention U-Net"],
                        event.gt_mask,
                        mask,
                        threshold=thresholds["Attention U-Net"],
                    )
                    seed_record[family][stratum_name] = {
                        "positive_pixels": int(((event.gt_mask > 0) & mask).sum()),
                        "total_pixels": int(mask.sum()),
                        "toporadar": topo,
                        "attention_unet": attention,
                        "delta_f1": float(topo["f1"] - attention["f1"]),
                        "delta_precision": float(
                            topo["precision"] - attention["precision"]
                        ),
                        "delta_recall": float(topo["recall"] - attention["recall"]),
                    }
            raw[region_name][str(seed)] = seed_record

    output = {
        "protocol": {
            "seeds": list(SEEDS),
            "test_systems": list(regions),
            "models": ["TopoRadar-Net", "Attention U-Net"],
            "inference": "full-scene frozen validation-selected thresholds",
            "scope": "descriptive multi-seed stratum stability; no causal interpretation",
        },
        "regions": {},
    }

    for region_name in regions:
        output["regions"][region_name] = {}
        for family in ("aspect_alignment", "slope_zones"):
            output["regions"][region_name][family] = {}
            first_seed = raw[region_name][str(SEEDS[0])][family]
            for stratum_name in first_seed:
                rows = [
                    raw[region_name][str(seed)][family][stratum_name]
                    for seed in SEEDS
                ]
                deltas = [row["delta_f1"] for row in rows]
                output["regions"][region_name][family][stratum_name] = {
                    "positive_pixels": rows[0]["positive_pixels"],
                    "total_pixels": rows[0]["total_pixels"],
                    "toporadar_f1": _summary(
                        [row["toporadar"]["f1"] for row in rows]
                    ),
                    "attention_unet_f1": _summary(
                        [row["attention_unet"]["f1"] for row in rows]
                    ),
                    "delta_f1": _summary(deltas),
                    "delta_precision": _summary(
                        [row["delta_precision"] for row in rows]
                    ),
                    "delta_recall": _summary(
                        [row["delta_recall"] for row in rows]
                    ),
                    "positive_delta_seeds": int(sum(delta > 0 for delta in deltas)),
                }

    output["per_seed"] = raw
    out_path = RESULTS_DIR / "topographic_geometry_stratification_multiseed.json"
    with open(out_path, "w") as handle:
        json.dump(output, handle, indent=2)
    print(f"Wrote {out_path}")

    for region_name, region in output["regions"].items():
        print(f"\n[{region_name}]")
        for family, strata in region.items():
            for name, record in strata.items():
                delta = record["delta_f1"]
                print(
                    f"  {family}/{name}: "
                    f"Delta F1={delta['mean'] * 100:+.2f}"
                    f" +- {delta['std_population'] * 100:.2f} pp; "
                    f"positive seeds={record['positive_delta_seeds']}/3"
                )


if __name__ == "__main__":
    main()
