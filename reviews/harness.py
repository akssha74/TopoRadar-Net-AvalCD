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

def verify_all_bounds():
    """Verify all stated macro-bounds and statistical bounds hold."""
    summary = load_summary()
    topo = summary["TopoRadar-Net"]["summary"]["pooled"]["f1"]["mean"]
    attn_u = summary.get("Attention U-Net", summary.get("Swin-UNet"))["summary"]["pooled"]["f1"]["mean"]
    res = summary["ResU-Net"]["summary"]["pooled"]["f1"]["mean"]
    assert topo > attn_u, f"TopoRadar-Net ({topo:.4f}) does not beat Attention U-Net ({attn_u:.4f})"
    assert topo > res, f"TopoRadar-Net ({topo:.4f}) does not beat ResU-Net ({res:.4f})"

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
    assert pamir_fa_rate == 0.47, f"Pamir TopoRadar FA rate {pamir_fa_rate} != 0.47"

    print("Harness check PASS: Primary summaries, 339-block bootstrap, exploratory Seed-42 and confirmatory multi-seed stratification, Nuuk validation, and operational triage verified.")

if __name__ == "__main__":
    print("Testing reviewer harness...")
    verify_all_bounds()
