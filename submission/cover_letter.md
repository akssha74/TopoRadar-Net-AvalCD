# Cover Letter — Journal of Mountain Science

**To:**  
Prof. Peng Cui (Editor-in-Chief)  
Prof. Dunlian Qiu (Executive Editor-in-Chief)  
*Journal of Mountain Science*  
Institute of Mountain Hazards and Environment, Chinese Academy of Sciences (CAS)  
Email: `jms@imde.ac.cn`

**From:**  
Akshay Sharma (Corresponding Author)  
Department of Computer Science and Engineering  
SAGE University, Indore 452020, Madhya Pradesh, India  
Email: `akssha74@gmail.com`

**Date:** September 6, 2026

**Subject:** Submission of Original Research Article — *"Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic"*

---

Dear Prof. Cui, Prof. Qiu, and Editorial Board,

We are pleased to submit our original research article entitled **"Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic"** for consideration for publication in the *Journal of Mountain Science*.

### 1. Background and Motivation
Snow avalanches represent one of the most destructive natural hazards in alpine and high-mountain regions worldwide, posing acute threats to settlements, transport arteries, and human safety across the European Alps, Central Asian Pamirs, and Arctic mountain belts. Rapid, all-weather mapping of avalanche debris is vital for emergency rescue operations and hazard mitigation. While spaceborne C-band Synthetic Aperture Radar (Sentinel-1 SAR) provides cloud-penetrating surveillance day and night, SAR change detection in rugged alpine topography suffers from severe geometric distortions: local incidence angle (LIA) variation induces intense ground-range foreshortening on radar-facing foreslopes, while slopes facing away from the radar (backslopes) suffer radiometric stretching and radar shadow. Existing deep learning change detection backbones treat SAR channels as flat 2D arrays, ignoring radar-topographic physics and generating spurious false alarms on illuminated ridges while missing shadow-adjacent debris.

### 2. Key Scientific and Methodological Contributions
1. **Geometric Formulation of 2D Convolutional Inadequacy (Proposition 2):** We formulate the geometric limitations of shift-invariant 2D spatial linear convolutions operating purely on SAR intensity space across sloped mountain facets under non-stationary illumination $\frac{\cos \psi}{\sin \theta_{\text{inc}}}$. We show that projecting terrain into a continuous 4D aspect-look manifold ($\mathcal{M} = [\sin \alpha, \cos \alpha, \cos \psi, \theta_{\text{align}}]^T$) eliminates circular branch-cut discontinuities and provides continuous coordinates to condition feature representations without angular branch cuts.
2. **Multi-Scale Radar-Topographic Cross-Attention (RTCAB):** We design a lightweight cross-attention module wherein multi-scale SAR change features interrogate adaptively-pooled regional topographic geometry keys and values. Component-removal and Seed-42 stratum analyses quantify empirical sensitivity without claiming a causal internal mechanism.
3. **Geomorphically Bounded Loss (Geo-Loss):** We introduce a soft geomorphic penalty on specified terrain ranges. Removing it produces a $-3.16\%$ paired-cluster F1 difference in Tromsø ($p = 0.002$); we do not attribute this difference to a localized false-positive mechanism without valley-specific records or a matched generic regularizer.
4. **Empirical Rigour and Cross-System Zero-Shot Evaluation:** Evaluated on the open-access AvalCD benchmark across four global mountain ranges (European Alps, Pamir Mountains in Tajikistan, Scandinavian Arctic in Norway, and sub-polar Greenland; 7 events, 993 verified avalanche polygons), TopoRadar-Net achieves competitive cross-system generalization ($63.79\% \pm 1.88\%$ pooled macro F1 across 3 seeds). Across spatial cluster blocks, TopoRadar-Net achieves statistically significant paired gains strictly excluding zero over SiamUNet-diff ($+12.77\%$, $p < 0.001$), while multi-seed testing against the benchmark Attention U-Net ($+0.38\%$, $p = 0.869$) honestly confirms cross-system performance parity, examining the geomorphic boundaries of auxiliary physical conditioning.
5. **Multi-Seed Topographic Stratification:** Exploratory Seed-42 backslope differences ($+5.85\%$ in Tromsø; $+5.09\%$ in Pamir) do not persist as stable three-seed effects: mean differences versus Attention U-Net are $-0.34\% \pm 6.28\%$ and $+1.20\% \pm 7.73\%$, respectively. This confirmatory stability check transparently delimits directional-conditioning claims.
6. **Operational Conceptual Triage Framework in Land-Management Units:** We formulate an explicitly unvalidated 3-tier conceptual framework and report a $30.0\%$ ($72.88\text{ ha}$ nominal-grid equivalent, $55.63\text{ ha}$ affine physical difference) Pamir false-alarm difference, $95.8\%$ mean Class D4 completeness in Tromsø, and $1.80\text{ s}$ model-forward latency on Apple Silicon MPS hardware.

### 3. Journal Fit and Policy Compliance
* **Format Compliance:** In accordance with the Editorial Office instructions for double-blind external review, the main manuscript is submitted as an editable Word (`.docx`) document with all author and institutional identifying information removed; the 4 figures and 8 tables are embedded within the single main document (file size well under 10 MB). Author names, affiliations, and e-mail addresses are provided separately in the online submission system.
* **Originality:** This manuscript represents original, previously unpublished research and is not under consideration for publication elsewhere.
* **Open Science and Reproducibility:** The AvalCD benchmark is openly accessible on Zenodo (DOI: [10.5281/zenodo.15863589](https://doi.org/10.5281/zenodo.15863589)). All source code, neural network implementations, evaluation scripts, and replication suites are publicly accessible in our dedicated GitHub repository: [https://github.com/akssha74/TopoRadar-Net-AvalCD](https://github.com/akssha74/TopoRadar-Net-AvalCD). Model checkpoints for all 3 independent training seeds and publication artifacts are openly distributed under immutable post-freeze Release v1.0.4: [https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.4](https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.4).

### 4. Suggested Independent Reviewers
1. **Dr. Markus Eckerstorfer**, Senior Research Scientist, NORCE Norwegian Research Centre, Tromsø, Norway. Email: `maec@norceresearch.no`  
   *Expertise: Sentinel-1 SAR change detection for snow avalanches, Arctic cryospheric hazards.*
2. **Dr. Achille Gatti**, Department of Electronics, Information and Bioengineering, Politecnico di Milano, Milan, Italy. Email: `achille.gatti@polimi.it`  
   *Expertise: AvalCD benchmark lead author, deep learning change detection on SAR imagery.*
3. **Dr. Silvan Leinss**, Senior Researcher, Institute of Environmental Engineering, ETH Zurich, Switzerland. Email: `leinss@ifu.baug.ethz.ch`  
   *Expertise: Microwave radar backscatter characteristics of snow avalanches, SAR polarimetry.*

### 5. Conflict of Interest Statement
The authors declare that they have no financial or non-financial conflicts of interest with any person, institution, or company in relation to the work reported in this manuscript. The suggested reviewers listed above are independent researchers with no personal, professional, financial, or collaborative relationship with the authors; none of them has co-authored publications with the authors, shared institutional affiliation, or participated in this study. This work received no external grant funding, and the authors have no competing commercial interests.

### 6. Opposed Reviewers (Reviewer Exclusions)
The authors do not request the exclusion of any specific individual from the pool of potential reviewers. Should the Editorial Office nevertheless wish to avoid any perception of conflict, we have no objection to the standard exclusion of reviewers sharing the authors' current institutional affiliation.

### 7. Author Agreement
All authors have read and approved the final version of the manuscript and agree to its submission to the *Journal of Mountain Science*. This manuscript represents original, previously unpublished work that is not under consideration for publication elsewhere, in whole or in part.

Thank you very much for your time and consideration of our manuscript.

Sincerely,  
**Akshay Sharma** (on behalf of all authors)  
Department of Computer Science and Engineering  
SAGE University, Indore 452020, India  
Email: `akssha74@gmail.com`
