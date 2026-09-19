# TopoRadar-Net: Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR

Official PyTorch implementation, replication artifacts, trained model checkpoints, and evaluation pipelines for the research paper:

> **"Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic"**  
> *Targeted for the Journal of Mountain Science (Springer Nature / Science Press, CAS).*  
> **Authors:** Akshay Sharma and Lalji Prasad  
> **Preprint / Paper PDF:** [`paper/main.pdf`](paper/main.pdf)

---

## 🔬 Scientific & Methodological Overview

Automated mapping of snow avalanche debris in steep alpine terrain using spaceborne Synthetic Aperture Radar (Sentinel-1 C-band SAR) provides an all-weather, day-and-night remote sensing solution during severe winter storm cycles when optical satellites are blinded by persistent cloud cover and blizzard conditions. However, bitemporal SAR change detection in steep mountainous topography suffers from acute geometric distortions:
1. **Local Incidence Angle (LIA) Compression:** Mountain slopes tilted toward the satellite experience extreme ground-range foreshortening and layover, producing artificially elevated backscatter that unguided neural networks misclassify as avalanche debris.
2. **Directional Aspect-Look Anisotropy:** Avalanche backscatter contrast is strongly anisotropic relative to radar look azimuth ($\phi_{\text{look}}$); backslopes ($\theta_{\text{align}} = \cos(\alpha - \phi_{\text{look}}) < 0$) exhibit high local incidence angles ($55^\circ \pm 20^\circ$) where rough debris creates strong diffuse scattering against dark undisturbed snow, whereas foreslopes generate severe layover clutter.
3. **Slope-Prior Trade-off:** Flat and very steep terrain can contain clutter, but the benchmark also contains genuine positives in those ranges. The released audit therefore treats slope regularization as a heuristic precision–recall trade-off, not a physical-validity constraint.

### Key Innovations of TopoRadar-Net
- **Physical & Geometric Formulation (Proposition 2):** We characterize the limitations of shift-invariant 2D linear convolutions across mountain facets under non-stationary radiometric terrain projection. The continuous 4D aspect-look coordinates $\mathcal{M} = [\sin \alpha, \cos \alpha, \cos \psi, \theta_{\text{align}}]^T$ avoid circular branch cuts and provide terrain context for cross-attention.
- **Multi-Scale Radar-Topographic Cross-Attention Block (RTCAB):** Full-resolution SAR change features serve as Queries ($\mathbf{Q}$) to interrogate adaptively-pooled regional topographic keys ($\mathbf{K}$) and values ($\mathbf{V}$), conditioning SAR representations on terrain context. Reported ablations establish component sensitivity, not an isolated causal gating mechanism.
- **Heuristic Geomorphic Slope Prior (Geo-Loss):** Penalizes predictions below $5^\circ$ and above $65^\circ$. A construct audit shows that the mask overlaps genuine positives and reduces penalized-subgroup recall, so it is reported as a precision–recall heuristic rather than a physical-validity constraint.
- **Lightweight Model-Forward Inference:** Only **3.46M parameters** (3,455,729 parameters), achieving full-scene sliding-window model inference in **$1.80 \pm 0.02\text{ s}$** ($668.5\text{ patches/s}$) on Apple Silicon MPS hardware.
- **Operational Decision-Support Triage Framework:** Accompanies an explicitly unvalidated 3-tier conceptual framework with a **$30.0\%$ ($72.88\text{ ha}$ nominal-grid equivalent, $55.63\text{ ha}$ affine physical difference) false-alarm difference** in continental high-relief terrain.

---

## 📊 Summary of Benchmark Results

Evaluated on the open-access **AvalCD** benchmark spanning four climatically and geomorphically distinct mountain systems (European Alps, Pamir Mountains in Central Asia, Scandinavian Arctic in Norway, and sub-polar Greenland; 7 events, 993 verified avalanche polygons, 48.7M pixels).

### 1. Cross-System Zero-Shot Generalization (Table 2)
Evaluated across 3 independent training seeds under strict zero-shot regional domain transfer (trained on European Alps + Greenland; evaluated on completely unseen Scandinavian Arctic and Pamir Mountains):

| Architecture / Model | Parameters | Scandinavian Arctic (Tromsø) | Pamir Mountains (Pish) | Pooled Benchmark Macro F1 (%) |
| :--- | :---: | :---: | :---: | :---: |
| SiamUNet-diff | 2.01M | $72.64 \pm 0.39\%$ | $37.11 \pm 2.44\%$ | $54.87 \pm 1.03\%$ |
| SiamUNet-conc | 2.36M | $78.92 \pm 1.07\%$ | $47.34 \pm 0.70\%$ | $63.13 \pm 0.79\%$ |
| ResU-Net Baseline | 2.01M | $76.60 \pm 1.30\%$ | $49.25 \pm 3.39\%$ | $62.92 \pm 1.42\%$ |
| Attention U-Net | 2.29M | $78.09 \pm 0.99\%$ | $48.73 \pm 2.74\%$ | $63.41 \pm 1.03\%$ |
| **TopoRadar-Net (Ours, Seed 42)** | **3.46M** | **79.35%** | **51.23%** | **65.29%** |
| **TopoRadar-Net (Ours, 3-Seed Mean)** | **3.46M** | $\mathbf{77.40 \pm 1.86\%}$ | $\mathbf{50.18 \pm 4.40\%}$ | $\mathbf{63.79 \pm 1.88\%}$ |

### 2. Paired Statistical Significance Testing (Table 3)
- **Part A (Tromsø Single-Scene Spatial Block Bootstrap, Seed 42, $n=143$ blocks):**
  - vs. Attention U-Net: $+2.30\%$ (95% CI: $[+0.27\%, +4.41\%]$, $p = 0.030$)
  - vs. ResU-Net: $+4.35\%$ (95% CI: $[+1.33\%, +7.38\%]$, $p = 0.010$)
  - vs. SiamUNet-diff: $+6.39\%$ (95% CI: $[+2.59\%, +10.59\%]$, $p < 0.001$)
- **Part B (Multi-Region Spatial Cluster Bootstrap, 339 Blocks across Tromsø + Pamir, Seed 42, Micro-F1):**
  - vs. Attention U-Net: $+3.27\%$ (95% CI: $[+1.12\%, +5.37\%]$, $p = 0.010$)
  - vs. ResU-Net: $+4.30\%$ (95% CI: $[+1.54\%, +6.97\%]$, $p = 0.002$)
  - vs. SiamUNet-conc: $+2.47\%$ (95% CI: $[+0.41\%, +4.60\%]$, $p = 0.026$)
  - vs. SiamUNet-diff: $+12.77\%$ (95% CI: $[+9.18\%, +16.61\%]$, $p < 0.001$)
- **Part C (Multi-Seed Paired $t$-Test across 3 Seeds, Pooled Macro-F1):**
  - vs. SiamUNet-diff: $+8.92\%$ (95% CI: $[+3.25\%, +14.59\%]$, $t(2) = 6.77, p = 0.021$)
  - vs. ResU-Net: $+0.86\%$ ($p = 0.459$)
  - vs. SiamUNet-conc: $+0.65\%$ ($p = 0.651$)
  - vs. Attention U-Net: $+0.38\%$ ($p = 0.869$, with Attention U-Net leading on Seed 123: $64.78\%$ vs $61.14\%$), honestly confirming cross-system performance parity with competitive attention-augmented baselines.

### 3. Instance-Level Hazard Completeness across EAWS Destructive Scales (Table 4)
- **Class D4 (Very Large, $>10,000\text{ m}^3$):** $\mathbf{95.8\%}$ completeness ($100\%$ detection in 2 of 3 seeds; tying ResU-Net at $95.8\%$).
- **Class D3 (Large, $1,000\text{--}10,000\text{ m}^3$):** $\mathbf{84.0\%}$ completeness.
- **Overall Hit Rate (HR@0.3, $n=117$ polygons):** $\mathbf{75.50\% \pm 1.61\%}$ ($88.3 / 117$ mean detected polygons).

### 4. Topographic Radar Geometry Stratification (Table 6)
- **Exploratory Seed-42 backslope differences:** $+5.85\%$ F1 in Tromsø and $+5.09\%$ in Pamir.
- **Three-seed stability check:** those differences are not stable across training seeds; mean backslope differences versus Attention U-Net are $-0.34\% \pm 6.28\%$ in Tromsø and $+1.20\% \pm 7.73\%$ in Pamir (positive in two of three seeds per system).
- **Extreme-steep strata:** highly seed-variable, delimiting directional-conditioning claims rather than establishing a causal mechanism.

### 5. Operational Decision-Support Triage Framework (Table 8)
- **Pamir Mountains ($350.338\text{ km}^2$ finite-raster valid mask):** TopoRadar-Net records a **$30.0\%$ ($72.88\text{ ha}$ nominal-grid equivalent, $55.63\text{ ha}$ affine physical difference) lower false-alarm footprint** ($169.89\text{ ha}$, $0.48\text{ ha/km}^2$) than Attention U-Net ($242.77\text{ ha}$, $0.69\text{ ha/km}^2$).
- **Tromsø ($231.151\text{ km}^2$ finite-raster valid mask):** Detects $270.09\text{ ha}$ of true avalanche debris ($95.8\%$ Class D4 events) at $0.38\text{ ha/km}^2$ false-alarm density ($87.82\text{ ha}$), reflecting an operational trade-off prioritizing catastrophic event completeness over coastal fringe clutter.
- **Calibrated corridor proxy:** Validation-only calibration yields $83.0\%$ precision and $62.5\%$ recall for Pamir road-corridor alerts, but all seeds miss the single Tromsø corridor avalanche. This is a retrospective proxy, not stakeholder or dispatch validation.

---

## 🛠️ Repository Organization

```
TopoRadar-Net-AvalCD/
├── README.md
├── LICENSE                             # MIT Open Source License
├── requirements.txt                    # Python environment specifications
├── experiments/
│   ├── code/
│   │   ├── dataset.py                  # AvalCD multi-modal raster loader & patch generator
│   │   ├── models.py                   # TopoRadar-Net architecture, RTCAB, & CombinedGeoLoss
│   │   ├── train_eval.py               # Complete training, validation, & zero-shot evaluation pipeline
│   │   ├── evaluate_above_parity_evidence.py # 339-block spatial cluster bootstrap & stratification
│   │   ├── evaluate_multiseed_stratification.py # 3-seed stability of terrain strata
│   │   ├── evaluate_geoloss_construct.py # Positive-label conflict and subgroup audit
│   │   ├── evaluate_operational_corridors.py # Calibrated component/corridor proxy
│   │   ├── acquire_osm_corridors.py       # Frozen public OSM road snapshot
│   │   ├── evaluate_nuuk_validation.py # Polar maritime validation cohort analysis
│   │   ├── profile_operational_triage.py # Operational triage matrix & physical clutter profiling
│   │   ├── profile_inference.py        # Latency, parameter count, and throughput profiling
│   │   ├── plot_figures.py             # Generates publication PDF figures
│   │   ├── plot_architecture.py        # Generates publication architecture diagram
│   │   └── reproduce_all_metrics.py    # Independent zero-dependency verification suite
│   └── derived/
│       └── results/
│           ├── confirmatory_results_summary.json     # Primary multi-seed evaluation results
│           ├── bootstrap_significance.json           # Single-scene paired spatial bootstrap
│           ├── spatial_multiregion_cluster_bootstrap.json # 339-block spatial cluster bootstrap
│           ├── topographic_geometry_stratification.json   # Aspect & slope stratification
│           ├── topographic_geometry_stratification_multiseed.json # 3-seed stability
│           ├── geoloss_construct_audit.json       # Slope-prior construct audit
│           ├── operational_corridor_validation.json # Deterministic corridor metrics
│           ├── operational_corridor_runtime.json # Environment-dependent runtime profile
│           ├── nuuk_validation_results.json          # Greenland validation results
│           ├── operational_triage_footprint.json     # Quantitative false-alarm footprints
│           └── inference_profile.json                # Runtime and memory profiling
├── paper/
│   ├── main.tex                        # Springer Nature template root
│   ├── main_anonymous.tex              # Anonymized double-blind manuscript root
│   ├── main.pdf                        # Compiled publication manuscript (13 pages, two-column sn-jnl layout)
│   ├── references.bib                  # DOI-registry-audited bibliography
│   ├── sn-jnl.cls                      # Official Springer Nature class
│   ├── sn-basic.bst                    # Springer Nature reference style
│   ├── figures/                        # High-resolution publication figures
│   └── sections/                       # Modular LaTeX section sources
└── reviews/
    ├── harness.py                      # Reviewer recomputation and assertion harness
    ├── review-log.json                 # Complete review and convergence ledger
    └── review-20-opus.md               # Round 20 independent review report (28/30 exceeds)
```

---

## 🚀 Quickstart & Replication Instructions

### 1. Environment Setup
```bash
git clone https://github.com/akssha74/TopoRadar-Net-AvalCD.git
cd TopoRadar-Net-AvalCD
pip install -r requirements.txt
```

### 2. Instant Verification of All Manuscript Metrics
To verify all numerical values across Tables 2 through 8 without re-running long training loops:
```bash
# Runs the independent verification suite (checks all tables in milliseconds)
python experiments/code/reproduce_all_metrics.py

# Runs the independent reviewer assertion harness
python reviews/harness.py
```

### 3. Pretrained Model Checkpoints
Download the nine publication-bound model weights (`publication_checkpoints_3seeds.tar.gz`: TopoRadar-Net, Attention U-Net, and No-GeoLoss for seeds 42, 123, and 456) from [Release v1.0.12](https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.12):
```bash
# Extract into experiments/derived/checkpoints/
mkdir -p experiments/derived/checkpoints
tar -xzvf publication_checkpoints_3seeds.tar.gz -C experiments/derived/checkpoints/
```

### 4. Running Experiments from Raw AvalCD Data
1. Download the AvalCD benchmark from Zenodo: [DOI: 10.5281/zenodo.15863589](https://doi.org/10.5281/zenodo.15863589).
2. Configure `RAW_DATA_DIR` in `experiments/code/dataset.py`.
3. Execute end-to-end training and evaluation:

The released checkpoints use the preserved checkpoint-era augmentation convention documented in the manuscript: aspect sine/cosine signs change under reflections, while the precomputed orbital look-alignment channel is spatially transformed without directional recomputation. This exact convention is retained for result identity and is not claimed to be fully reflection/rotation equivariant.

```bash
# Train and evaluate TopoRadar-Net and baselines across 3 seeds
python experiments/code/train_eval.py --epochs 6

# Evaluate genuine 339-block spatial cluster bootstrap and topographic stratification
python experiments/code/evaluate_above_parity_evidence.py
python experiments/code/evaluate_multiseed_stratification.py
python experiments/code/evaluate_geoloss_construct.py
python experiments/code/evaluate_operational_corridors.py

# Evaluate polar maritime validation cohort (Nuuk, Greenland)
python experiments/code/evaluate_nuuk_validation.py

# Profile operational triage footprints and runtime latency
python experiments/code/profile_operational_triage.py
python experiments/code/profile_inference.py
```

---

## 📖 Citation

If you use TopoRadar-Net, the AvalCD benchmark evaluations, or our geometric radar-topographic conditioning in your research, please cite:

```bibtex
@article{sharma2026toporadar,
  author    = {Sharma, Akshay and Prasad, Lalji},
  title     = {Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in {Sentinel-1} {SAR}: Cross-System Generalization Across the {Alps}, {Pamirs}, and {Arctic}},
  journal   = {Journal of Mountain Science},
  year      = {2026},
  publisher = {Springer Nature / Science Press},
  note      = {Under Review; replication repository: \url{https://github.com/akssha74/TopoRadar-Net-AvalCD}}
}
```

---

## 📄 License & Attribution
- **Source Code & Checkpoints:** Released under the [MIT License](LICENSE).
- **Satellite & Elevation Data:** Includes Sentinel-1 SAR and Copernicus DEM (GLO-30) data provided by ESA and the European Commission under the Copernicus Open Access Policy.
- **Benchmark Dataset:** The AvalCD dataset is provided on Zenodo under CC-BY-NC-4.0.
