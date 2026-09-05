# Step-by-Step Submission Guide for Journal of Mountain Science (JMS)

This comprehensive guide walks you through submitting the research manuscript to the **Journal of Mountain Science** (Springer Nature / Science Press, Chinese Academy of Sciences) via ScholarOne Manuscripts.

---

### 1. Key Journal & Portal Details
* **Journal Name:** *Journal of Mountain Science* (JMS)
* **Publisher:** Science Press China / Springer Nature
* **Indexing:** SCIE (Clarivate, JCR Q2), Scopus (Elsevier Q2), CAS
* **Online Submission Portal:** [https://mc03.manuscriptcentral.com/jmsjournal](https://mc03.manuscriptcentral.com/jmsjournal)
* **Editorial Office Contact:** `jms@imde.ac.cn`
* **Article Type:** Original Research Article

---

### 2. Pre-Prepared Submission Assets

All assets are located in:  
📁 `/Users/akshay.sharma/Projects/paper-activities/studies/mountain-avalcd-toporadar/`

| Submission Asset | Path | Upload Role in ScholarOne |
|---|---|---|
| **Primary Manuscript PDF** | `paper/main.pdf` (29 pages) | **Main Document** |
| **Cover Letter (PDF)** | `submission/cover_letter.pdf` | **Cover Letter** |
| **Complete LaTeX Source (ZIP)**| `submission/source_package.zip` | **Supplemental / Source Files** |
| **Individual Vector Figures** | `paper/figures/*.pdf` | **Figure / Graphic** |

---

### 3. Step-by-Step Portal Submission Walkthrough

#### Step 1: Portal Login & Initialization
1. Navigate to: [https://mc03.manuscriptcentral.com/jmsjournal](https://mc03.manuscriptcentral.com/jmsjournal)
2. Log in with your ScholarOne / ORCID credentials (or click *Create an Account* if not registered).
3. In the **Author Dashboard**, click **"Start New Submission"** $\rightarrow$ **"Begin Submission"**.

#### Step 2: Manuscript Type & Title
* **Manuscript Type:** Select **"Original Research Article"** from the dropdown menu.
* **Full Title:**
  ```text
  Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic
  ```
* **Running Head / Short Title:**
  ```text
  TopoRadar-Net for Alpine Avalanche Debris Mapping in Sentinel-1 SAR
  ```

#### Step 3: Abstract & Keywords
* **Abstract:** (Copy and paste from `paper/sections/abstract.tex`):
  ```text
  Rapid, all-weather mapping of snow avalanche debris across rugged mountain terrain is critical for alpine civil protection, emergency response, and search-and-rescue operations. Synthetic Aperture Radar (SAR) sensors such as Sentinel-1 provide cloud-penetrating and day-and-night imaging capabilities essential for winter hazard monitoring. However, bitemporal SAR change detection in steep mountainous topography suffers from severe geometric distortions: local incidence angle (LIA) variation induces extreme foreshortening on slopes facing the radar look direction, while backslopes experience radiometric stretching and radar shadow. Existing deep learning change detection models (including vision transformers such as Swin-UNet, ChangeFormer, and Siamese convolutional networks) treat SAR channels as flat Euclidean arrays, ignoring radar-topographic physics and leading to spurious false alarms on illuminated ridges and missed detections on shadow-adjacent slopes. In this study, we propose TopoRadar-Net, a physics-guided deep change detection network that explicitly couples bitemporal Sentinel-1 C-band SAR backscatter with local topographic radar geometry. TopoRadar-Net introduces: (1) an analytical formulation and proof (Theorem 1) establishing that 2D shift-invariant convolutions cannot invert the non-stationary geometric projection cos(psi) / sin(theta_inc), proving an irreducible ambiguity between foreslope layover clutter and true debris that is resolved via a continuous 4D aspect-look manifold; (2) a multi-scale Radar-Topographic Cross-Attention Block (RTCAB) where regional terrain geometry dynamically queries and gates multi-scale SAR change features; (3) a Geomorphically Bounded Loss (Geo-Loss) that penalizes false alarms in geomorphically inadmissible terrain (<5 deg valley floors and >65 deg sheer rock walls); and (4) an operational EAWS triage protocol quantifying clutter reduction in physical units (hectares). Evaluated on the AvalCD benchmark across four climatically and geomorphically distinct mountain systems (European Alps, Pamir Mountains in Central Asia, Scandinavian Arctic in Norway, and sub-polar Greenland; 7 events, 993 verified avalanche polygons), TopoRadar-Net achieves competitive cross-system generalization under zero-shot transfer, reaching 63.79% +- 1.88% pooled macro F1 and outperforming the benchmark Swin-UNet (63.41%), SiamUNet-conc (63.13%), ResU-Net (62.92%), and SiamUNet-diff (54.87%). Across independent spatial blocks, TopoRadar-Net achieves a +12.77% gain over SiamUNet-diff (p < 0.001) and competitive parity with advanced vision transformers (Swin-UNet +0.38% pooled macro F1 across 3 seeds), with seed-level paired testing revealing that cross-system gains over top-performing baselines are non-significant across seeds (p = 0.869 vs Swin-UNet, where Swin leads on Seed 123), honestly isolating the boundaries of auxiliary physical conditioning. Fine-grained topographic stratification isolates the physical mechanism, confirming consistent >+5% F1 advantages on backslopes in both mountain systems (+5.85% in Tromso, driven by +12.28% recall; +5.09% in Pamir, driven by +13.95% precision false-alarm suppression), reducing operational clutter in continental high relief by 30.0% (72.9 ha) with 1.80 s full-scene streaming latency. On the Scandinavian Arctic test scene (Tromso), TopoRadar-Net achieves 77.40% +- 1.86% pixel F1 (IoU 63.16%), yielding statistically confirmed paired cluster-bootstrap gains over Swin-UNet (+2.30%, p = 0.030), ResU-Net (+4.35%, p = 0.010), and SiamUNet-diff (+6.39%, p < 0.001), with 100% instance completeness on catastrophic Class D4 avalanches in 2 of 3 seeds (mean 95.8%). We disclose that terrain geometry conditioning behaves in a regime-dependent manner: while providing essential layover suppression and +2.04% F1 gain (p < 0.001) in maritime fjords, extreme high-relief continental shadow in the Pamirs moderates global gains, establishing verifiable physical and mathematical criteria for operational satellite avalanche monitoring.
  ```
* **Keywords:**
  ```text
  Snow avalanche mapping, Sentinel-1 SAR, Mountain hazards, Radar-topographic geometry, Cross-attention network, Cross-system generalization, Disaster response
  ```

#### Step 4: Author Information
1. **Corresponding Author:**
   * **First Name:** Akshay
   * **Last Name:** Sharma
   * **Email:** `akssha74@gmail.com`
   * **Affiliation:** Department of Computer Science and Engineering, SAGE University, Indore 452020, Madhya Pradesh, India
2. **Co-Author:**
   * **First Name:** Lalji
   * **Last Name:** Prasad
   * **Email:** `lalji.research@gmail.com`
   * **Affiliation:** Department of Computer Science and Engineering, SAGE University, Indore 452020, Madhya Pradesh, India

#### Step 5: Suggested Reviewers (Recommended by ScholarOne)
Enter the 5 independent domain experts from the cover letter:
1. **Dr. Markus Eckerstorfer** (`maec@norceresearch.no`), NORCE Norwegian Research Centre, Norway.
2. **Dr. Yves Bühler** (`buehler@slf.ch`), WSL Institute for Snow and Avalanche Research SLF, Switzerland.
3. **Dr. Achille Gatti** (`achille.gatti@polimi.it`), Politecnico di Milano, Italy.
4. **Dr. Silvan Leinss** (`leinss@ifu.baug.ethz.ch`), ETH Zurich, Switzerland.
5. **Dr. Elisabeth D. Hafner** (`elisabeth.hafner@slf.ch`), WSL Institute for Snow and Avalanche Research SLF, Switzerland.

#### Step 6: File Uploads
1. Upload `studies/mountain-avalcd-toporadar/paper/main.pdf` $\rightarrow$ File Designation: **"Main Document"**.
2. Upload `studies/mountain-avalcd-toporadar/submission/cover_letter.pdf` $\rightarrow$ File Designation: **"Cover Letter"**.
3. Upload `studies/mountain-avalcd-toporadar/submission/source_package.zip` $\rightarrow$ File Designation: **"Supplementary File for Review"** or **"LaTeX Source Files"**.

#### Step 7: Declarations & Checklists
* **Conflict of Interest:** Select "None / The authors declare no competing interests".
* **Funding Statement:** Select "No external funding received for this research".
* **Data Availability:** Check "Data available in public repository" and provide:
  ```text
  The AvalCD benchmark dataset is publicly available on Zenodo (DOI: 10.5281/zenodo.15863589). All code, trained model checkpoints (seeds 42, 123, 456), and evaluation scripts are publicly available on GitHub at https://github.com/akssha74/TopoRadar-Net-AvalCD under Release v1.0.0 (https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.0).
  ```

#### Step 8: PDF Review & Submit
1. ScholarOne will merge the files and generate a proof PDF.
2. Inspect the proof: confirm that all figures, tables (Tables 1–8), and mathematical equations (Theorem 1, Propositions 1–2) render cleanly.
3. Click **"Submit Manuscript"**.
4. Save the generated **Manuscript Tracking ID** (e.g., `JMS-2026-XXXX`).
