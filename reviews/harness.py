#!/usr/bin/env python3
"""
Reviewer recomputation harness for mountain-avalcd-toporadar study.
Provides independent, isolated recomputations of reported metrics, gaps,
and statistical intervals from the primary result artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np

STUDY_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = STUDY_DIR / "experiments/derived/results"

def load_summary() -> dict:
    summary_path = RESULTS_DIR / "confirmatory_results_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing primary summary: {summary_path}")
    with open(summary_path) as f:
        return json.load(f)

def load_bootstrap() -> dict:
    boot_path = RESULTS_DIR / "bootstrap_significance.json"
    if not boot_path.exists():
        raise FileNotFoundError(f"Missing bootstrap summary: {boot_path}")
    with open(boot_path) as f:
        return json.load(f)

def load_spatial_multiregion_bootstrap() -> dict:
    boot_path = RESULTS_DIR / "spatial_multiregion_cluster_bootstrap.json"
    if not boot_path.exists():
        raise FileNotFoundError(f"Missing spatial multi-region bootstrap summary: {boot_path}")
    with open(boot_path) as f:
        return json.load(f)

def load_topographic_stratification() -> dict:
    strat_path = RESULTS_DIR / "topographic_geometry_stratification.json"
    if not strat_path.exists():
        raise FileNotFoundError(f"Missing topographic stratification summary: {strat_path}")
    with open(strat_path) as f:
        return json.load(f)

def load_multiseed_topographic_stratification() -> dict:
    strat_path = RESULTS_DIR / "topographic_geometry_stratification_multiseed.json"
    if not strat_path.exists():
        raise FileNotFoundError(f"Missing multi-seed stratification summary: {strat_path}")
    with open(strat_path) as f:
        return json.load(f)

def load_nuuk_validation() -> dict:
    nuuk_path = RESULTS_DIR / "nuuk_validation_results.json"
    if not nuuk_path.exists():
        raise FileNotFoundError(f"Missing Nuuk validation summary: {nuuk_path}")
    with open(nuuk_path) as f:
        return json.load(f)

def load_operational_triage() -> dict:
    op_path = RESULTS_DIR / "operational_triage_footprint.json"
    if not op_path.exists():
        raise FileNotFoundError(f"Missing operational triage summary: {op_path}")
    with open(op_path) as f:
        return json.load(f)

def load_operational_corridor_validation() -> dict:
    path = RESULTS_DIR / "operational_corridor_validation.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing operational corridor summary: {path}")
    with open(path) as f:
        return json.load(f)

def load_event_sensor_manifest() -> dict:
    path = RESULTS_DIR / "event_sensor_manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing event sensor manifest: {path}")
    with open(path) as f:
        return json.load(f)

def load_operational_corridor_runtime() -> dict:
    path = RESULTS_DIR / "operational_corridor_runtime.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing operational corridor runtime: {path}")
    with open(path) as f:
        return json.load(f)

def load_geoloss_construct_audit() -> dict:
    path = RESULTS_DIR / "geoloss_construct_audit.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing Geo-Loss construct audit: {path}")
    with open(path) as f:
        return json.load(f)

def load_valid_mask_area_audit() -> dict:
    path = RESULTS_DIR / "valid_mask_area_audit.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing valid-mask area audit: {path}")
    with open(path) as f:
        return json.load(f)

def verify_all_bounds():
    """Verify all stated macro-bounds and statistical bounds hold."""
    summary = load_summary()
    topo = summary["TopoRadar-Net"]["summary"]["pooled"]["f1"]["mean"]
    attn_u = summary.get("Attention U-Net", summary.get("Swin-UNet"))["summary"]["pooled"]["f1"]["mean"]
    res = summary["ResU-Net"]["summary"]["pooled"]["f1"]["mean"]
    assert topo > attn_u, f"TopoRadar-Net ({topo:.4f}) does not beat Attention U-Net ({attn_u:.4f})"
    assert topo > res, f"TopoRadar-Net ({topo:.4f}) does not beat ResU-Net ({res:.4f})"
    areas = load_valid_mask_area_audit()["regions"]
    for model in summary.values():
        if not isinstance(model, dict) or "seeds" not in model:
            continue
        for seed_record in model["seeds"].values():
            for region, region_record in seed_record["regions"].items():
                metrics = region_record["pixel"]
                total = metrics["tp"] + metrics["fp"] + metrics["fn"] + metrics["tn"]
                assert total == areas[region]["valid_pixels"]

    # Verify 339-block spatial multi-region cluster bootstrap
    spatial_boot = load_spatial_multiregion_bootstrap()
    for m in ["Swin-UNet", "ResU-Net", "SiamUNet-conc", "SiamUNet-diff"]:
        assert m in spatial_boot
        ci_l = spatial_boot[m]["ci_95"][0]
        assert ci_l > 0.0, f"Spatial bootstrap 95% CI lower bound for {m} is not positive ({ci_l:.4f})"
        assert spatial_boot[m]["statistically_significant"] is True

    # Verify topographic stratification
    topo_strat = load_topographic_stratification()
    for region in topo_strat.values():
        for family in ("aspect_alignment", "slope_zones"):
            for row in region[family].values():
                for model_key in ("toporadar", "swin_unet"):
                    metrics = row[model_key]
                    total = metrics["tp"] + metrics["fp"] + metrics["fn"] + metrics["tn"]
                    assert total == row["total_pixels"], (
                        f"Single-seed confusion total does not close for {family}: "
                        f"{total} != {row['total_pixels']}"
                    )
    delta_tromso_backslope = topo_strat["Tromso_Arctic"]["aspect_alignment"]["Backslopes (Facing Away, align < -0.3)"]["delta_f1"]
    assert delta_tromso_backslope > 0.05, f"Tromso backslope delta {delta_tromso_backslope:.4f} <= 0.05"
    delta_pamir_backslope = topo_strat["Pamir_HighMountain"]["aspect_alignment"]["Backslopes (Facing Away, align < -0.3)"]["delta_f1"]
    assert delta_pamir_backslope > 0.05, f"Pamir backslope delta {delta_pamir_backslope:.4f} <= 0.05"

    # Verify that the manuscript correctly narrows Seed-42 patterns using all seeds.
    multi = load_multiseed_topographic_stratification()
    backslope = "Backslopes (Facing Away, align < -0.3)"
    tromso_multi = multi["regions"]["Tromso_Arctic"]["aspect_alignment"][backslope]
    pamir_multi = multi["regions"]["Pamir_HighMountain"]["aspect_alignment"][backslope]
    for region_name, seeds in multi["per_seed"].items():
        for seed, families in seeds.items():
            for family in ("aspect_alignment", "slope_zones"):
                for stratum, row in families[family].items():
                    for model_key in ("toporadar", "attention_unet"):
                        metrics = row[model_key]
                        total = metrics["tp"] + metrics["fp"] + metrics["fn"] + metrics["tn"]
                        assert total == row["total_pixels"], (
                            f"Multi-seed confusion total does not close for "
                            f"{region_name}/{seed}/{family}/{stratum}: "
                            f"{total} != {row['total_pixels']}"
                        )
    assert np.isclose(tromso_multi["delta_f1"]["mean"], -0.0034226984431335503)
    assert np.isclose(tromso_multi["delta_f1"]["std_population"], 0.0628276475245984)
    assert np.isclose(pamir_multi["delta_f1"]["mean"], 0.011952338891495514)
    assert np.isclose(pamir_multi["delta_f1"]["std_population"], 0.07734477727516495)
    assert tromso_multi["positive_delta_seeds"] == 2
    assert pamir_multi["positive_delta_seeds"] == 2
    seed_bootstrap = multi["spatial_cluster_bootstrap_multiseed"]
    pooled_values = [
        seed_bootstrap["per_seed"][str(seed)]["Pooled_339_Blocks"]["mean_gain"]
        for seed in (42, 123, 456)
    ]
    assert np.allclose(
        pooled_values,
        [0.03257931626134104, -0.0299165106400238, 0.04160908768972134],
    )
    assert np.isclose(
        seed_bootstrap["pooled_gain_across_seeds"]["mean"],
        np.mean(pooled_values),
    )
    assert seed_bootstrap["positive_mean_gain_seeds"] == 2

    # Verify Nuuk validation
    nuuk_res = load_nuuk_validation()
    nuuk_models = nuuk_res["Nuuk_20210411_Validation_Cohort"]["models"]
    topo_rec = nuuk_models["TopoRadar-Net"]["rec_mean"]
    assert topo_rec > 0.80, f"Nuuk TopoRadar recall {topo_rec:.4f} <= 0.80"

    # Verify operational triage footprint
    op_res = load_operational_triage()
    pamir_fp_topo = op_res["regions"]["Pamir_HighMountain"]["models"]["TopoRadar-Net"]["fp_ha"]
    pamir_fp_attn = op_res["regions"]["Pamir_HighMountain"]["models"]["Attention U-Net"]["fp_ha"]
    assert pamir_fp_topo < pamir_fp_attn, f"TopoRadar FP ({pamir_fp_topo}) not lower than Attention U-Net FP ({pamir_fp_attn})"
    pamir_fa_rate = op_res["regions"]["Pamir_HighMountain"]["models"]["TopoRadar-Net"]["false_alarm_rate_ha_per_km2"]
    assert pamir_fa_rate == 0.48, f"Pamir TopoRadar FA rate {pamir_fa_rate} != 0.48"
    assert op_res["regions"]["Tromso_Arctic"]["valid_pixels"] == 2311510
    assert op_res["regions"]["Pamir_HighMountain"]["valid_pixels"] == 3503382
    assert np.isclose(op_res["regions"]["Tromso_Arctic"]["scene_area_km2"], 196.819927)
    assert np.isclose(op_res["regions"]["Pamir_HighMountain"]["scene_area_km2"], 267.434948)
    tromso_models = op_res["regions"]["Tromso_Arctic"]["models"]
    pamir_models = op_res["regions"]["Pamir_HighMountain"]["models"]
    assert np.isclose(tromso_models["TopoRadar-Net"]["fp_ha"], 74.77)
    assert np.isclose(tromso_models["Attention U-Net"]["fp_ha"], 58.19)
    assert np.isclose(pamir_models["TopoRadar-Net"]["fp_ha"], 129.69)
    assert np.isclose(pamir_models["Attention U-Net"]["fp_ha"], 185.32)
    assert np.isclose(
        tromso_models["TopoRadar-Net"]["fp_ha_nominal_grid_equivalent"], 87.82
    )
    assert np.isclose(
        pamir_models["TopoRadar-Net"]["fp_ha_nominal_grid_equivalent"], 169.89
    )

    # Verify the explicitly exploratory, non-stakeholder operational proxy.
    corridor = load_operational_corridor_validation()
    assert corridor["protocol"]["status"] == "post-hoc exploratory operational proxy"
    topo_pamir = corridor["aggregate"]["TopoRadar-Net"]["Pamir_HighMountain"]
    topo_tromso = corridor["aggregate"]["TopoRadar-Net"]["Tromso_Arctic"]
    assert topo_pamir["corridor_gt_components"] == 8
    assert np.isclose(topo_pamir["corridor_alert_precision"]["mean"], 0.8301587301587302)
    assert np.isclose(topo_pamir["corridor_gt_recall"]["mean"], 0.625)
    assert topo_tromso["corridor_gt_components"] == 1
    assert np.isclose(topo_tromso["corridor_gt_recall"]["mean"], 0.0)
    assert topo_pamir["calibrated_brier"]["mean"] < topo_pamir["raw_brier"]["mean"]
    runtime = load_operational_corridor_runtime()
    for region in ("Tromso_Arctic", "Pamir_HighMountain"):
        assert all(
            0.0 < value < 5.0
            for value in runtime["aggregate"]["TopoRadar-Net"][region][
                "cached_end_to_end_seconds"
            ]["values"]
        )

    # Verify the positive-label conflict that limits the slope-prior construct.
    geo = load_geoloss_construct_audit()
    assert geo["positive_label_conflict"]["train"]["penalized_positive_pixels"] == 19663
    assert geo["positive_label_conflict"]["heldout_test"]["penalized_positive_pixels"] == 492
    full = geo["summary"]["Full TopoRadar-Net"]
    no_geo = geo["summary"]["No-GeoLoss"]
    for region in ("Tromso_Arctic", "Pamir_HighMountain"):
        assert full[region]["positive_recall"]["mean"] < no_geo[region]["positive_recall"]["mean"]

    sensor = load_event_sensor_manifest()
    events = {record["event"]: record for record in sensor["events"]}
    assert events["Nuuk_20160413"]["polarization_pair"] == "HH/HV"
    assert events["Nuuk_20210411"]["polarization_pair"] == "HH/HV"
    assert all(
        record["polarization_pair"] == "VV/VH"
        for name, record in events.items()
        if not name.startswith("Nuuk")
    )
    assert sensor["fixed_reference_aspect_feature"]["reference_azimuth_degrees"] == 78.0

    print("Harness check PASS: Primary summaries, seed-repeated bootstrap/strata, Nuuk validation, physical-unit triage, calibrated corridor proxy, Geo-Loss construct audit, and event sensor semantics verified.")

if __name__ == "__main__":
    print("Testing reviewer harness...")
    verify_all_bounds()
