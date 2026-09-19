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
| **Primary Manuscript PDF** | `paper/main.pdf` (13 pages) | **Main Document** |
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
* **Submission-portal abstract:** (Plain-text condensed rendering; consult `paper/sections/abstract.tex` for the authoritative typeset abstract):
  ```text
  Rapid, all-weather mapping of snow avalanche debris across rugged mountain terrain is critical for alpine civil protection, emergency response, and search-and-rescue operations. We propose TopoRadar-Net, a physics-guided change-detection network coupling bitemporal Sentinel-1 C-band SAR with local topographic radar geometry. The method combines a continuous aspect-look representation, multi-scale Radar-Topographic Cross-Attention Blocks, and a Geomorphically Bounded Loss. Evaluated on the AvalCD benchmark across four mountain systems (7 events; 993 verified avalanche polygons), TopoRadar-Net reaches 63.79% +- 1.88% pooled macro F1, compared with 63.41% for Attention U-Net, 63.13% for SiamUNet-conc, 62.92% for ResU-Net, and 54.87% for SiamUNet-diff. Across three seeds, the margin over competitive baselines is non-significant (p = 0.869 versus Attention U-Net), while the gain over SiamUNet-diff is significant (+8.92%, p = 0.021). Exploratory Seed-42 backslope differences do not persist as stable three-seed effects (-0.34% +- 6.28% in Tromso; +1.20% +- 7.73% in Pamir). In the Pamir scene, the false-alarm footprint is 30.0% lower than Attention U-Net (72.9 ha nominal-grid equivalent; 55.6 ha affine physical difference). On the Tromso scene TopoRadar-Net achieves 77.40% +- 1.86% pixel F1 and 95.8% mean D4 instance completeness. We explicitly disclose regime-dependent performance and the checkpoint-era augmentation convention, under which the directional tensor is not fully reflection/rotation equivariant.
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
  The AvalCD benchmark dataset is publicly available on Zenodo (DOI: 10.5281/zenodo.15863589). All code, publication-bound TopoRadar-Net and Attention U-Net checkpoints (seeds 42, 123, 456), and evaluation scripts are publicly available on GitHub at https://github.com/akssha74/TopoRadar-Net-AvalCD under immutable post-freeze Release v1.0.6 (https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.6).
  ```

#### Step 8: PDF Review & Submit
1. ScholarOne will merge the files and generate a proof PDF.
2. Inspect the proof: confirm that all figures, tables (Tables 1–8), and mathematical equations (Propositions 1–3) render cleanly.
3. Click **"Submit Manuscript"**.
4. Save the generated **Manuscript Tracking ID** (e.g., `JMS-2026-XXXX`).
