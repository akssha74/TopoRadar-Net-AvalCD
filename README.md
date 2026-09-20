# TopoRadar-Net: Terrain-Conditioned Sentinel-1 Avalanche Mapping

Official code, model definitions, reproducibility artifacts, and submission source for:

> **Terrain-Conditioned Cross-Attention for Cross-Region Avalanche Debris Mapping with Sentinel-1 SAR**

Current manuscript target: *Journal of the Indian Society of Remote Sensing* (Research Article).  
Authors: Akshay Sharma and Lalji Prasad.

## Scope and evidence boundary

TopoRadar-Net conditions bitemporal Sentinel-1 change features on terrain and local-incidence information through multiscale cross-attention. The study uses seven AvalCD events across the Alps, Greenland, Tromsø, and the Pamirs, with Alps/Greenland development scenes and geographically held-out Tromsø/Pish tests.

The evidence does **not** establish uniform superiority or deployment readiness:

- pooled macro F1 is `63.79 ± 1.88%` over three fixed seeds (descriptive population SD);
- the difference from the internal bottleneck self-attention U-Net is `+0.38` percentage points (`p=0.869`);
- only the `+8.92`-point difference from SiamUNet-diff is significant across seeds (`p=0.021`);
- No-Aspect and No-CrossAttn ablations have higher pooled macro F1 than the full model;
- the slope-prior mask overlaps `18.47%` of training positives;
- the retrospective Pish corridor proxy reaches `83.0%` precision and `62.5%` recall, while every seed misses the only Tromsø corridor reference avalanche.

## Executed input semantics

The released checkpoints use the executed loader in `experiments/code/dataset.py`:

- SAR inputs remain in the supplied decibel representation; no percentile scaling is applied;
- values outside `[-45, 15]` dB are invalidated before valid-mask construction;
- missing cross/co values are then filled with `-20/-12` dB;
- Livigno, Tromsø, and Pish use VV/VH; Nuuk uses HH/HV;
- channel position 0 is cross-polarized (VH or HV), and position 1 is co-polarized (VV or HH);
- the sixth terrain feature is `cos(aspect − 78°)`, a fixed nominal ascending-reference coordinate—not authoritative per-event radar heading.

The event-level binding and interpretation limits are recorded in:

`experiments/derived/results/event_sensor_manifest.json`

## Models

- **TopoRadar-Net** — bitemporal residual encoder, SAR-query/terrain-key-value cross-attention, terrain gate, progressive decoder
- **SiamUNet-diff / SiamUNet-conc** — Daudt-style Siamese baselines
- **ResU-Net** — residual U-Net baseline
- **Bottleneck self-attention U-Net** — internal baseline with four-head self-attention only at the deepest feature map; it is not canonical Attention U-Net or Swin-UNet

For provenance continuity, this baseline's three checkpoint members retain the legacy filenames `Swin-UNet_seed{42,123,456}.pth`. The filenames are aliases only; the instantiated class is `AttentionUNetAval` and contains no shifted-window transformer blocks.

## Reproduce manuscript metrics

```bash
git clone https://github.com/akssha74/TopoRadar-Net-AvalCD.git
cd TopoRadar-Net-AvalCD
pip install -r requirements.txt

python experiments/code/reproduce_all_metrics.py
python reviews/harness.py
python submission-jisrs/verify_package.py
```

Expected terminal messages include:

- `STORED-SUMMARY ARITHMETIC VERIFIED`
- `Harness check PASS`
- `PASS: JISRS package, anonymity, Word, source, and scientific gates`

## Data

AvalCD is publicly available from Zenodo:

https://doi.org/10.5281/zenodo.15863589

Set the raw-data location with:

```bash
export AVALCD_RAW_DIR=/path/to/AvalCD
```

## Train and evaluate

```bash
python experiments/code/train_eval.py --epochs 6
python experiments/code/evaluate_multiseed_stratification.py
python experiments/code/evaluate_geoloss_construct.py
python experiments/code/evaluate_operational_corridors.py
python experiments/code/reconcile_primary_tn.py
```

Training uses the disclosed checkpoint-era directional augmentation convention. The fixed-reference aspect feature is spatially transformed but not directionally recomputed under every rotation/reflection; directional findings are therefore sensitivity analyses, not causal or equivariance claims.

## Repository layout

```text
paper-jisrs/
  main.tex                         anonymous JISRS LaTeX manuscript
  main.pdf                         compiled anonymous proof
  supplementary_information.tex   anonymous Online Resource 1
  references.bib                   cited-only APA bibliography
  figures/Fig1.*                   architecture figure (EPS/PDF/PNG)
  figures/Fig2.*                   cross-region results (EPS/PDF/PNG)

submission-jisrs/
  JISRS_Main_Manuscript_Anonymous.docx
  JISRS_Title_Page.docx
  JISRS_Supplementary_Information.pdf
  cover_letter.pdf
  source_package.zip
  check_compliance.py
  verify_package.py

experiments/
  code/                             training/evaluation/reproduction code
  derived/results/                  committed result and audit artifacts
  external/                         versioned external snapshots

reviews/harness.py                  independent assertion harness
evidence/claim-ledger.jsonl         claim/evidence ledger
```

## Submission package status

The JISRS package is **prepared, not submitted**. It is double-blind, A4, 12-point Times New Roman, double-spaced, continuously line-numbered, and mechanically checked against the current JISRS Research Article limits.

## License

Code is released under the MIT License. Dataset and third-party resource licenses remain governed by their original providers.
