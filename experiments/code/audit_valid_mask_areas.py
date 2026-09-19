#!/usr/bin/env python3
"""Derive evaluated scene areas directly from authoritative raw valid masks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import EVENTS_TEST_PAMIR, EVENTS_TEST_TROMSO, load_event


EXP_DIR = Path(__file__).resolve().parent.parent
OUT_PATH = EXP_DIR / "derived/results/valid_mask_area_audit.json"


def record(event_name: str):
    event = load_event(event_name)
    transform = event.transform
    pixel_area_m2 = abs(transform.a * transform.e - transform.b * transform.d)
    valid_pixels = int(event.valid_mask.sum())
    full_pixels = int(event.height * event.width)
    return {
        "event": event_name,
        "shape": [event.height, event.width],
        "full_grid_pixels": full_pixels,
        "valid_pixels": valid_pixels,
        "invalid_pixels": full_pixels - valid_pixels,
        "valid_fraction": valid_pixels / full_pixels,
        "nominal_pixel_area_m2": 100.0,
        "nominal_valid_area_km2": valid_pixels * 100.0 / 1_000_000.0,
        "affine_pixel_area_m2": pixel_area_m2,
        "affine_valid_area_km2": valid_pixels * pixel_area_m2 / 1_000_000.0,
        "crs": str(event.crs),
        "transform": list(transform)[:6],
    }


def main():
    output = {
        "authority": "dataset.load_event valid_mask from finite pre/post VH/VV, LIA, slope, and aspect rasters",
        "regions": {
            "Tromso_Arctic": record(EVENTS_TEST_TROMSO[0]),
            "Pamir_HighMountain": record(EVENTS_TEST_PAMIR[0]),
        },
    }
    with open(OUT_PATH, "w") as handle:
        json.dump(output, handle, indent=2)
    print(f"Wrote {OUT_PATH}")
    for region, row in output["regions"].items():
        print(
            f"{region}: valid={row['valid_pixels']:,}/"
            f"{row['full_grid_pixels']:,}; nominal={row['nominal_valid_area_km2']:.4f} km2; "
            f"affine={row['affine_valid_area_km2']:.4f} km2"
        )


if __name__ == "__main__":
    main()
