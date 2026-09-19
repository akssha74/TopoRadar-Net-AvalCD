#!/usr/bin/env python3
"""Exploratory calibrated component and transport-corridor validation.

This analysis uses only development-visible validation scenes to fit a one-
dimensional Platt calibrator. It then evaluates frozen connected-component
alerts on the two existing held-out scenes and intersects them with a committed
OpenStreetMap major-road snapshot. It is an operational proxy study, not a
stakeholder or dispatch validation.
"""

from __future__ import annotations

import json
import math
import hashlib
import sys
import time
from pathlib import Path

import numpy as np
import torch
from pyproj import Transformer
from rasterio.features import rasterize
from scipy import ndimage
from shapely.geometry import LineString
from shapely.ops import transform as shapely_transform
from shapely.ops import unary_union
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import (
    EVENTS_TEST_PAMIR,
    EVENTS_TEST_TROMSO,
    EVENTS_VAL,
    load_event,
)
from models import AttentionUNetAval, TopoRadarNet
from train_eval import evaluate_full_scene


EXP_DIR = Path(__file__).resolve().parent.parent
CHECKPOINTS_DIR = EXP_DIR / "derived/checkpoints"
RESULTS_DIR = EXP_DIR / "derived/results"
OSM_PATH = EXP_DIR / "external/osm_major_roads_20260919.json"
OUT_PATH = RESULTS_DIR / "operational_corridor_validation.json"
RUNTIME_PATH = RESULTS_DIR / "operational_corridor_runtime.json"

SEEDS = (42, 123, 456)
MIN_COMPONENT_PIXELS = 10  # nominal 0.1 ha
COMPONENT_TRUTH_OVERLAP = 0.30
ROAD_BUFFER_METRES = 30.0
CONNECTIVITY = np.ones((3, 3), dtype=np.uint8)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def model_and_checkpoint(name: str, seed: int, device):
    if name == "TopoRadar-Net":
        model = TopoRadarNet().to(device)
        filename = f"TopoRadar-Net_seed{seed}.pth"
    elif name == "Attention U-Net":
        model = AttentionUNetAval().to(device)
        filename = f"Swin-UNet_seed{seed}.pth"
    else:
        raise ValueError(name)
    checkpoint = torch.load(CHECKPOINTS_DIR / filename, map_location="cpu")
    model.load_state_dict(checkpoint["model_state_dict"])
    return model, float(checkpoint["best_threshold"]), filename


def road_mask(scene_name, event, osm_payload):
    ways = osm_payload["scenes"][scene_name]["ways"]
    transformer = Transformer.from_crs("EPSG:4326", event.crs, always_xy=True)
    geometries = []
    for way in ways:
        coords = [
            (point["lon"], point["lat"])
            for point in way.get("geometry", [])
            if "lon" in point and "lat" in point
        ]
        if len(coords) >= 2:
            line = LineString(coords)
            geometries.append(
                shapely_transform(
                    lambda x, y, z=None: transformer.transform(x, y), line
                )
            )
    if not geometries:
        return np.zeros_like(event.valid_mask), 0.0, 0
    merged = unary_union(geometries)
    length_km = float(merged.length / 1000.0)
    corridor = merged.buffer(ROAD_BUFFER_METRES)
    mask = rasterize(
        [(corridor, 1)],
        out_shape=event.valid_mask.shape,
        transform=event.transform,
        fill=0,
        dtype=np.uint8,
    ).astype(bool)
    return mask & event.valid_mask, length_km, len(ways)


def components(probability, threshold, ground_truth, valid_mask, roads=None):
    prediction = (probability >= threshold) & valid_mask
    labels, count = ndimage.label(prediction, structure=CONNECTIVITY)
    slices = ndimage.find_objects(labels)
    records = []
    for component_id, component_slice in enumerate(slices, start=1):
        if component_slice is None:
            continue
        local = labels[component_slice] == component_id
        area = int(local.sum())
        if area < MIN_COMPONENT_PIXELS:
            continue
        local_probability = probability[component_slice][local]
        local_truth = (ground_truth[component_slice] > 0)[local]
        road_intersection = (
            bool(roads[component_slice][local].any()) if roads is not None else False
        )
        records.append(
            {
                "component_id": component_id,
                "area_pixels": area,
                "mean_probability": float(local_probability.mean()),
                "peak_probability": float(local_probability.max()),
                "truth_overlap": float(local_truth.mean()),
                "is_true": bool(local_truth.mean() >= COMPONENT_TRUTH_OVERLAP),
                "road_intersection": road_intersection,
                "slice": component_slice,
                "local_mask": local,
            }
        )
    return labels, records


def fit_platt(records):
    scores = np.asarray([row["mean_probability"] for row in records])
    labels = np.asarray([row["is_true"] for row in records], dtype=int)
    clipped = np.clip(scores, 1e-6, 1 - 1e-6)
    logits = np.log(clipped / (1 - clipped)).reshape(-1, 1)
    if len(np.unique(labels)) < 2:
        raise RuntimeError("Validation components do not contain both classes")
    calibrator = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
    calibrator.fit(logits, labels)
    return calibrator, int(labels.sum()), int(len(labels) - labels.sum())


def calibrated_probabilities(calibrator, records):
    scores = np.asarray([row["mean_probability"] for row in records])
    clipped = np.clip(scores, 1e-6, 1 - 1e-6)
    logits = np.log(clipped / (1 - clipped)).reshape(-1, 1)
    return calibrator.predict_proba(logits)[:, 1]


def select_alert_threshold(probabilities, labels):
    labels = np.asarray(labels, dtype=bool)
    best = (0.0, 0.5)
    for threshold in np.linspace(0.05, 0.95, 19):
        predicted = probabilities >= threshold
        tp = int((predicted & labels).sum())
        fp = int((predicted & ~labels).sum())
        fn = int((~predicted & labels).sum())
        f2 = 5 * tp / (5 * tp + fp + 4 * fn) if (5 * tp + fp + 4 * fn) else 0.0
        if f2 > best[0] or (math.isclose(f2, best[0]) and threshold > best[1]):
            best = (float(f2), float(threshold))
    return best[1], best[0]


def ece(probabilities, labels, bins=10):
    probabilities = np.asarray(probabilities)
    labels = np.asarray(labels, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    value = 0.0
    for index in range(bins):
        if index == bins - 1:
            member = (probabilities >= edges[index]) & (
                probabilities <= edges[index + 1]
            )
        else:
            member = (probabilities >= edges[index]) & (
                probabilities < edges[index + 1]
            )
        if member.any():
            value += member.mean() * abs(
                probabilities[member].mean() - labels[member].mean()
            )
    return float(value)


def corridor_ground_truth_recall(alert_labels, alert_ids, event, roads):
    gt = (event.gt_mask > 0) & event.valid_mask
    gt_labels, gt_count = ndimage.label(gt, structure=CONNECTIVITY)
    road_gt = []
    detected = 0
    alert_mask = np.isin(alert_labels, list(alert_ids))
    for gt_id in range(1, gt_count + 1):
        component = gt_labels == gt_id
        if component.sum() < MIN_COMPONENT_PIXELS or not (component & roads).any():
            continue
        road_gt.append(gt_id)
        overlap = (component & alert_mask).sum() / component.sum()
        if overlap >= COMPONENT_TRUTH_OVERLAP:
            detected += 1
    total = len(road_gt)
    return total, detected, (detected / total if total else None)


def summarize(values):
    values = np.asarray(values, dtype=float)
    return {
        "mean": float(values.mean()),
        "std_population": float(values.std(ddof=0)),
        "values": [float(value) for value in values],
    }


def main():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    with open(OSM_PATH) as handle:
        osm_payload = json.load(handle)

    validation_events = {name: load_event(name) for name in EVENTS_VAL}
    test_names = {
        "Tromso_Arctic": EVENTS_TEST_TROMSO[0],
        "Pamir_HighMountain": EVENTS_TEST_PAMIR[0],
    }
    test_events = {}
    load_seconds = {}
    for region, name in test_names.items():
        started = time.perf_counter()
        test_events[region] = load_event(name)
        load_seconds[region] = time.perf_counter() - started
    roads = {}
    road_seconds = {}
    for region, event in test_events.items():
        started = time.perf_counter()
        roads[region] = road_mask(region, event, osm_payload)
        road_seconds[region] = time.perf_counter() - started

    per_seed = {}
    runtime_per_seed = {}
    checkpoint_hashes = {}
    for seed in SEEDS:
        per_seed[str(seed)] = {}
        runtime_per_seed[str(seed)] = {}
        for model_name in ("TopoRadar-Net", "Attention U-Net"):
            model, threshold, checkpoint_name = model_and_checkpoint(
                model_name, seed, device
            )
            checkpoint_hashes[checkpoint_name] = sha256(
                CHECKPOINTS_DIR / checkpoint_name
            )
            validation_records = []
            for event in validation_events.values():
                probability, _ = evaluate_full_scene(
                    model, event, device, patch_size=128, stride=64
                )
                _, records = components(
                    probability,
                    threshold,
                    event.gt_mask,
                    event.valid_mask,
                )
                validation_records.extend(records)
            calibrator, validation_true, validation_false = fit_platt(
                validation_records
            )
            validation_calibrated = calibrated_probabilities(
                calibrator, validation_records
            )
            validation_labels = np.asarray(
                [row["is_true"] for row in validation_records], dtype=bool
            )
            alert_probability, validation_component_f2 = select_alert_threshold(
                validation_calibrated, validation_labels
            )

            model_results = {
                "checkpoint": checkpoint_name,
                "threshold": threshold,
                "platt": {
                    "coefficient": float(calibrator.coef_[0, 0]),
                    "intercept": float(calibrator.intercept_[0]),
                    "validation_true_components": validation_true,
                    "validation_false_components": validation_false,
                    "validation_selected_alert_probability": alert_probability,
                    "validation_component_f2": validation_component_f2,
                },
                "regions": {},
            }
            runtime_per_seed[str(seed)][model_name] = {}

            for region, event in test_events.items():
                road_raster, road_length_km, way_count = roads[region]
                started = time.perf_counter()
                probability, _ = evaluate_full_scene(
                    model, event, device, patch_size=128, stride=64
                )
                labels, records = components(
                    probability,
                    threshold,
                    event.gt_mask,
                    event.valid_mask,
                    roads=road_raster,
                )
                calibrated = calibrated_probabilities(calibrator, records)
                elapsed = time.perf_counter() - started

                truth = np.asarray([row["is_true"] for row in records], dtype=float)
                raw = np.asarray([row["mean_probability"] for row in records])
                for row, value in zip(records, calibrated):
                    row["calibrated_probability"] = float(value)
                alerts = [
                    row
                    for row in records
                    if row["road_intersection"]
                    and row["calibrated_probability"] >= alert_probability
                ]
                alert_ids = {row["component_id"] for row in alerts}
                true_alerts = sum(row["is_true"] for row in alerts)
                gt_total, gt_detected, gt_recall = corridor_ground_truth_recall(
                    labels, alert_ids, event, road_raster
                )

                model_results["regions"][region] = {
                    "component_count": len(records),
                    "true_component_count": int(truth.sum()),
                    "raw_brier": float(np.mean((raw - truth) ** 2)),
                    "calibrated_brier": float(
                        np.mean((calibrated - truth) ** 2)
                    ),
                    "raw_ece_10bin": ece(raw, truth),
                    "calibrated_ece_10bin": ece(calibrated, truth),
                    "road_way_count": way_count,
                    "road_length_km": road_length_km,
                    "road_buffer_m": ROAD_BUFFER_METRES,
                    "corridor_alert_count": len(alerts),
                    "corridor_true_alerts": int(true_alerts),
                    "corridor_false_alerts": int(len(alerts) - true_alerts),
                    "corridor_alert_precision": (
                        float(true_alerts / len(alerts)) if alerts else None
                    ),
                    "corridor_gt_components": gt_total,
                    "corridor_gt_detected": gt_detected,
                    "corridor_gt_recall": gt_recall,
                }
                runtime_per_seed[str(seed)][model_name][region] = {
                    "scene_data_load_seconds": load_seconds[region],
                    "road_rasterization_seconds": road_seconds[region],
                    "scene_inference_plus_postprocess_seconds": elapsed,
                    "cached_end_to_end_seconds": (
                        load_seconds[region] + road_seconds[region] + elapsed
                    ),
                }
            per_seed[str(seed)][model_name] = model_results

    aggregate = {}
    metric_names = (
        "raw_brier",
        "calibrated_brier",
        "raw_ece_10bin",
        "calibrated_ece_10bin",
        "corridor_alert_count",
        "corridor_false_alerts",
        "corridor_alert_precision",
        "corridor_gt_recall",
    )
    for model_name in ("TopoRadar-Net", "Attention U-Net"):
        aggregate[model_name] = {}
        for region in test_names:
            aggregate[model_name][region] = {}
            for metric in metric_names:
                values = [
                    per_seed[str(seed)][model_name]["regions"][region][metric]
                    for seed in SEEDS
                ]
                non_null = [value for value in values if value is not None]
                aggregate[model_name][region][metric] = (
                    summarize(non_null) if non_null else None
                )
            aggregate[model_name][region]["road_length_km"] = per_seed["42"][
                model_name
            ]["regions"][region]["road_length_km"]
            aggregate[model_name][region]["corridor_gt_components"] = per_seed[
                "42"
            ][model_name]["regions"][region]["corridor_gt_components"]

    output = {
        "protocol": {
            "status": "post-hoc exploratory operational proxy",
            "calibration_fit": "Platt logistic calibration on connected components from two development-visible validation scenes",
            "component_min_pixels": MIN_COMPONENT_PIXELS,
            "component_truth_overlap": COMPONENT_TRUTH_OVERLAP,
            "alert_probability_selection": "validation component-F2 grid, 0.05 to 0.95 in 0.05 steps",
            "road_buffer_metres": ROAD_BUFFER_METRES,
            "road_source": str(OSM_PATH.relative_to(EXP_DIR.parent)),
            "road_snapshot_sha256": sha256(OSM_PATH),
            "road_snapshot_content_hash": osm_payload[
                "content_sha256_without_hash_field"
            ],
            "checkpoint_sha256": dict(sorted(checkpoint_hashes.items())),
            "limitations": [
                "No stakeholder or dispatch outcome was measured.",
                "Road proximity is a retrospective proxy, not operational benefit.",
                "The held-out scenes were previously used for the primary paper evaluation; this extension is exploratory.",
            ],
        },
        "per_seed": per_seed,
        "aggregate": aggregate,
    }
    with open(OUT_PATH, "w") as handle:
        json.dump(output, handle, indent=2)

    runtime_aggregate = {}
    for model_name in ("TopoRadar-Net", "Attention U-Net"):
        runtime_aggregate[model_name] = {}
        for region in test_names:
            runtime_aggregate[model_name][region] = {
                metric: summarize(
                    [
                        runtime_per_seed[str(seed)][model_name][region][metric]
                        for seed in SEEDS
                    ]
                )
                for metric in (
                    "scene_data_load_seconds",
                    "road_rasterization_seconds",
                    "scene_inference_plus_postprocess_seconds",
                    "cached_end_to_end_seconds",
                )
            }
    runtime_output = {
        "device": str(device),
        "scope": "cached OSM snapshot; raster load + corridor rasterization + full-scene inference + component post-processing",
        "n_seeds": len(SEEDS),
        "per_seed": runtime_per_seed,
        "aggregate": runtime_aggregate,
        "reproducibility_note": "wall-clock values are environment-dependent and are verified by bounds, not byte identity",
    }
    with open(RUNTIME_PATH, "w") as handle:
        json.dump(runtime_output, handle, indent=2)
    print(f"Wrote {OUT_PATH}")
    print(f"Wrote {RUNTIME_PATH}")
    for model_name, regions in aggregate.items():
        print(f"\n{model_name}")
        for region, metrics in regions.items():
            print(
                f"  {region}: road={metrics['road_length_km']:.1f} km, "
                f"GT corridor components={metrics['corridor_gt_components']}, "
                f"precision={metrics['corridor_alert_precision']}, "
                f"recall={metrics['corridor_gt_recall']}, "
                f"Brier {metrics['raw_brier']['mean']:.3f}->"
                f"{metrics['calibrated_brier']['mean']:.3f}, "
                f"cached end-to-end="
                f"{runtime_aggregate[model_name][region]['cached_end_to_end_seconds']['mean']:.2f}s"
            )


if __name__ == "__main__":
    main()
