#!/usr/bin/env python3
"""Benchmark full-scene sliding-window inference latency on Apple MPS / CPU."""

import time
import json
from pathlib import Path
import torch
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from models import TopoRadarNet

EXP_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = EXP_DIR / "derived/results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def benchmark_inference():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Profiling TopoRadar-Net on {device}...")

    model = TopoRadarNet(use_lia=True, use_aspect=True, use_cross_attn=True).to(device)
    model.eval()

    params = sum(p.numel() for p in model.parameters())

    # Warmup
    dummy_pre = torch.randn(16, 2, 128, 128, device=device)
    dummy_post = torch.randn(16, 2, 128, 128, device=device)
    dummy_topo = torch.randn(16, 6, 128, 128, device=device)
    for _ in range(5):
        with torch.no_grad():
            _ = model(dummy_pre, dummy_post, dummy_topo)

    # Benchmark typical full-scene patch count:
    # A 2500 x 2000 scene with stride 64 has ~1200 patches (batch size 16 -> 75 batches)
    n_batches = 75
    latencies = []
    for _ in range(10):
        t0 = time.time()
        for _ in range(n_batches):
            with torch.no_grad():
                _ = model(dummy_pre, dummy_post, dummy_topo)
        latencies.append(time.time() - t0)

    mean_sec = float(np.mean(latencies))
    std_sec = float(np.std(latencies))

    profile = {
        "device": str(device),
        "parameter_count": params,
        "scene_dimensions": "2500x2000",
        "patch_size": 128,
        "stride": 64,
        "n_patches_simulated": n_batches * 16,
        "full_scene_inference_seconds_mean": mean_sec,
        "full_scene_inference_seconds_std": std_sec,
        "throughput_patches_per_sec": float((n_batches * 16) / mean_sec)
    }

    out_path = RESULTS_DIR / "inference_profile.json"
    with open(out_path, "w") as f:
        json.dump(profile, f, indent=2)

    print(f"Profile saved to {out_path}: {mean_sec:.2f}s +- {std_sec:.2f}s, {params:,} parameters.")

if __name__ == "__main__":
    benchmark_inference()
