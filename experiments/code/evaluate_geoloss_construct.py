#!/usr/bin/env python3
"""Audit Geo-Loss label conflicts and penalized-terrain test performance."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import (
    EVENTS_TEST_PAMIR,
    EVENTS_TEST_TROMSO,
    EVENTS_TRAIN,
    EVENTS_VAL,
    load_event,
)
from models import TopoRadarNet
from train_eval import compute_pixel_metrics, evaluate_full_scene


EXP_DIR = Path(__file__).resolve().parent.parent
CHECKPOINTS_DIR = EXP_DIR / "derived/checkpoints"
OUT_PATH = EXP_DIR / "derived/results/geoloss_construct_audit.json"
SEEDS = (42, 123, 456)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def penalty_mask(event):
    slope = event.topo_geom[1] * 60.0
    return ((slope < 5.0) | (slope > 65.0)) & event.valid_mask


def aggregate(values):
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(array.mean()),
        "std_population": float(array.std(ddof=0)),
        "values": [float(value) for value in array],
    }


def main():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    all_names = list(dict.fromkeys(
        EVENTS_TRAIN + EVENTS_VAL + EVENTS_TEST_TROMSO + EVENTS_TEST_PAMIR
    ))
    events = {name: load_event(name) for name in all_names}

    roles = {
        "train": EVENTS_TRAIN,
        "validation": EVENTS_VAL,
        "heldout_test": EVENTS_TEST_TROMSO + EVENTS_TEST_PAMIR,
        "all": all_names,
    }
    conflict = {}
    for role, names in roles.items():
        positives = 0
        penalized_positives = 0
        per_event = {}
        for name in names:
            event = events[name]
            positive = (event.gt_mask > 0) & event.valid_mask
            penalized = positive & penalty_mask(event)
            count = int(positive.sum())
            conflict_count = int(penalized.sum())
            positives += count
            penalized_positives += conflict_count
            per_event[name] = {
                "valid_positive_pixels": count,
                "penalized_positive_pixels": conflict_count,
                "fraction": conflict_count / count if count else 0.0,
            }
        conflict[role] = {
            "valid_positive_pixels": positives,
            "penalized_positive_pixels": penalized_positives,
            "fraction": penalized_positives / positives if positives else 0.0,
            "events": per_event,
        }

    test_regions = {
        "Tromso_Arctic": events[EVENTS_TEST_TROMSO[0]],
        "Pamir_HighMountain": events[EVENTS_TEST_PAMIR[0]],
    }
    model_files = {
        "Full TopoRadar-Net": "TopoRadar-Net_seed{seed}.pth",
        "No-GeoLoss": "Ablation-NoGeoLoss_seed{seed}.pth",
    }
    per_seed = {}
    checkpoint_hashes = {}
    for seed in SEEDS:
        per_seed[str(seed)] = {}
        for model_name, pattern in model_files.items():
            checkpoint_path = CHECKPOINTS_DIR / pattern.format(seed=seed)
            checkpoint = torch.load(checkpoint_path, map_location="cpu")
            model = TopoRadarNet(
                use_lia=True, use_aspect=True, use_cross_attn=True
            ).to(device)
            model.load_state_dict(checkpoint["model_state_dict"])
            threshold = float(checkpoint["best_threshold"])
            checkpoint_hashes[checkpoint_path.name] = sha256(checkpoint_path)
            per_seed[str(seed)][model_name] = {
                "checkpoint": checkpoint_path.name,
                "threshold": threshold,
                "regions": {},
            }
            for region, event in test_regions.items():
                probability, _ = evaluate_full_scene(
                    model, event, device, patch_size=128, stride=64
                )
                mask = penalty_mask(event)
                positive = (event.gt_mask > 0) & mask
                predicted = (probability >= threshold) & mask
                metrics = compute_pixel_metrics(
                    probability, event.gt_mask, mask, threshold=threshold
                )
                per_seed[str(seed)][model_name]["regions"][region] = {
                    "penalty_pixels": int(mask.sum()),
                    "positive_pixels": int(positive.sum()),
                    "positive_recall": (
                        float(predicted[positive].mean()) if positive.any() else None
                    ),
                    "metrics": metrics,
                }

    summary = {}
    for model_name in model_files:
        summary[model_name] = {}
        for region in test_regions:
            rows = [
                per_seed[str(seed)][model_name]["regions"][region] for seed in SEEDS
            ]
            summary[model_name][region] = {
                "penalty_pixels": rows[0]["penalty_pixels"],
                "positive_pixels": rows[0]["positive_pixels"],
                "positive_recall": aggregate(
                    [row["positive_recall"] for row in rows]
                ),
                "f1": aggregate([row["metrics"]["f1"] for row in rows]),
                "precision": aggregate(
                    [row["metrics"]["precision"] for row in rows]
                ),
            }

    output = {
        "protocol": {
            "scope": "construct audit of the executed heuristic slope prior",
            "penalty_mask": "slope < 5 degrees or slope > 65 degrees",
            "interpretation": "descriptive label conflict and subgroup performance; no causal mechanism claim",
            "checkpoint_sha256": dict(sorted(checkpoint_hashes.items())),
        },
        "positive_label_conflict": conflict,
        "per_seed": per_seed,
        "summary": summary,
    }
    with open(OUT_PATH, "w") as handle:
        json.dump(output, handle, indent=2)
    print(f"Wrote {OUT_PATH}")
    for role, record in conflict.items():
        print(
            f"{role}: {record['penalized_positive_pixels']}/"
            f"{record['valid_positive_pixels']} = {record['fraction']*100:.2f}%"
        )
    for model_name, regions in summary.items():
        print(f"\n{model_name}")
        for region, record in regions.items():
            print(
                f"  {region}: positive recall "
                f"{record['positive_recall']['mean']*100:.2f}"
                f" +- {record['positive_recall']['std_population']*100:.2f}%, "
                f"penalty-stratum F1 {record['f1']['mean']*100:.2f}%"
            )


if __name__ == "__main__":
    main()
