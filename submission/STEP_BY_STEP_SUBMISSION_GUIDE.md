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
  TopoRadar-Net couples bitemporal Sentinel-1 SAR with radar-topographic geometry through cross-attention and a heuristic slope-prior loss. On AvalCD (7 events, 4 mountain systems, 993 polygons), it reaches 63.79% +- 1.88% pooled macro F1 versus 63.41% for Attention U-Net; this difference is non-significant across seeds (p=0.869), while the +8.92% difference versus SiamUNet-diff is significant (p=0.021). The slope-prior mask overlaps 18.47% of training positives and lowers held-out positive recall inside the mask relative to No-GeoLoss, so it is presented as a precision-recall heuristic rather than a physical constraint. Validation-calibrated Pamir corridor alerts achieve 83.0% precision and 62.5% recall, but every seed misses the single Tromso corridor avalanche. The paper therefore reports competitive pixel performance, region- and seed-dependent sensitivity, and explicit operational failure boundaries rather than a causal mechanism or deployment-ready system.
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
  The AvalCD benchmark dataset is publicly available on Zenodo (DOI: 10.5281/zenodo.15863589). All code and publication-bound TopoRadar-Net, Attention U-Net, and No-GeoLoss checkpoints (seeds 42, 123, 456) are available under versioned post-freeze Release v1.0.10 (https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.10).
  ```

#### Step 8: PDF Review & Submit
1. ScholarOne will merge the files and generate a proof PDF.
2. Inspect the proof: confirm that all figures, tables (Tables 1–8), and mathematical equations (Propositions 1–3) render cleanly.
3. Click **"Submit Manuscript"**.
4. Save the generated **Manuscript Tracking ID** (e.g., `JMS-2026-XXXX`).
