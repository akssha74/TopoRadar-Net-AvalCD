#!/usr/bin/env python3
"""Reconcile stored TN counts to raw valid-mask denominators without retraining."""

from __future__ import annotations

import json
from pathlib import Path


EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "derived/results"
SUMMARY_PATH = RESULTS_DIR / "confirmatory_results_summary.json"
AREA_PATH = RESULTS_DIR / "valid_mask_area_audit.json"


def main():
    with open(SUMMARY_PATH) as handle:
        summary = json.load(handle)
    with open(AREA_PATH) as handle:
        areas = json.load(handle)["regions"]

    changed = 0
    for model_name, model in summary.items():
        if not isinstance(model, dict) or "seeds" not in model:
            continue
        for seed, seed_record in model["seeds"].items():
            for region, region_record in seed_record["regions"].items():
                metrics = region_record["pixel"]
                valid = int(areas[region]["valid_pixels"])
                tn = valid - int(metrics["tp"]) - int(metrics["fp"]) - int(metrics["fn"])
                if tn < 0:
                    raise AssertionError(f"Negative TN for {model_name}/{seed}/{region}")
                if metrics.get("tn") != float(tn):
                    metrics["tn"] = float(tn)
                    changed += 1

    with open(SUMMARY_PATH, "w") as handle:
        json.dump(summary, handle, indent=2)
    print(f"Reconciled {changed} TN values in {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
