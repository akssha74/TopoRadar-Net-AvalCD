# Cover Letter — Journal of Mountain Science

**To:**  
Prof. Peng Cui (Editor-in-Chief)  
Prof. Dunlian Qiu (Executive Editor-in-Chief)  
*Journal of Mountain Science*  
Institute of Mountain Hazards and Environment (IMHE), Chinese Academy of Sciences (CAS)  
Email: `jms@imde.ac.cn`

**From:**  
Akshay Sharma (Corresponding Author)  
Department of Computer Science and Engineering  
SAGE University, Indore 452020, Madhya Pradesh, India  
Email: `akssha74@gmail.com`

**Date:** September 5, 2026

**Subject:** Submission of Original Research Article — *"Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic"*

---

Dear Prof. Cui, Prof. Qiu, and Editorial Board,

We are pleased to submit our original research article entitled **"Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic"** for consideration for publication in the *Journal of Mountain Science*.

### 1. Background and Motivation
Snow avalanches represent one of the most destructive natural hazards in alpine and high-mountain regions worldwide, posing acute threats to settlements, transport arteries, and human safety across the European Alps, Central Asian Pamirs, and Arctic mountain belts. Rapid, all-weather mapping of avalanche debris is vital for emergency rescue operations and hazard mitigation. While spaceborne C-band Synthetic Aperture Radar (Sentinel-1 SAR) provides cloud-penetrating surveillance day and night, SAR change detection in rugged alpine topography suffers from severe geometric distortions: local incidence angle (LIA) variation induces intense ground-range foreshortening on radar-facing foreslopes, while slopes facing away from the radar (backslopes) suffer radiometric stretching and radar shadow. Existing deep learning change detection backbones treat SAR channels as flat 2D arrays, ignoring radar-topographic physics and generating spurious false alarms on illuminated ridges while missing shadow-adjacent debris.

### 2. Key Scientific and Methodological Contributions
1. **Analytical Proof of 2D Convolutional Inadequacy (Theorem 1):** We mathematically prove that 2D shift-invariant spatial convolutions operating purely on SAR intensity space cannot invert the non-stationary geometric projection field $\frac{\cos \psi}{\sin \theta_{\text{inc}}}$, establishing an irreducible lower bound on false-alarm ambiguity between foreslope layover clutter and true debris. We prove that projecting terrain into a continuous 4D aspect-look manifold ($\mathcal{M} = [\sin \alpha, \cos \alpha, \cos \psi, \theta_{\text{align}}]^T$) eliminates circular branch-cut discontinuities and is mathematically sufficient to decouple geometric modulation from true backscatter anomalies.
2. **Multi-Scale Radar-Topographic Cross-Attention (RTCAB):** We design a lightweight cross-attention module wherein multi-scale SAR change features interrogate adaptively-pooled regional topographic geometry keys and values, dynamically suppressing foreslope clutter while amplifying backslope debris signatures.
3. **Geomorphically Bounded Loss (Geo-Loss):** We introduce a soft geomorphic penalty regularizing training against physically impossible landforms ($<5^\circ$ valley floors and $>65^\circ$ vertical cliffs), providing a confirmed $+3.16\%$ F1 gain ($p = 0.002$) by directly eliminating valley-floor false positives.
4. **Empirical Rigour and Cross-System Zero-Shot Evaluation:** Evaluated on the open-access AvalCD benchmark across four global mountain ranges (European Alps, Pamir Mountains in Tajikistan, Scandinavian Arctic in Norway, and sub-polar Greenland; 7 events, 993 verified avalanche polygons), TopoRadar-Net achieves competitive cross-system generalization ($63.79\% \pm 1.88\%$ pooled macro F1 across 3 seeds). Across independent spatial clusters, TopoRadar-Net achieves statistically significant paired gains strictly excluding zero over SiamUNet-diff ($+12.77\%$, $p < 0.001$), while multi-seed testing against top-performing vision transformers (Swin-UNet $+0.38\%$, $p = 0.869$) honestly confirms cross-system performance parity, isolating the geomorphic boundaries of auxiliary physical conditioning.
5. **Fine-Grained Topographic Radar Geometry Stratification:** Analysis across aspect-look alignment and slope steepness demonstrates consistent $>+5\%$ F1 advantages on backslopes in both mountain systems ($+5.85\%$ in Tromsø, driven by $+12.28\%$ recall; $+5.09\%$ in Pamir, driven by $+13.95\%$ precision false-alarm suppression), while identifying the extreme steep slope ($>45^\circ$) radar shadow failure boundary.
6. **Operational EAWS Decision Matrix in Land-Management Units:** We formulate a 3-tier triage matrix mapped directly to emergency civil protection responses, demonstrating a $30.0\%$ ($72.88\text{ ha}$) false-alarm clutter reduction in the high-altitude Pamir Mountains and $95.8\%$ Class D4 hazard detection completeness in Tromsø, with $1.80\text{ s}$ full-scene streaming latency and $2.14\text{ GB}$ peak VRAM ($<\$0.02$ compute per Sentinel-1 scene).

### 3. Journal Fit and Policy Compliance
* **Format Compliance:** Formatted under the official Springer Nature journal class (`sn-jnl.cls`) with `sn-basic` reference styling, comprising 29 pages with complete high-resolution vector figures and fully articulated proofs.
* **Originality:** This manuscript represents original, previously unpublished research and is not under consideration for publication elsewhere.
* **Open Science and Reproducibility:** The AvalCD benchmark is openly accessible on Zenodo (DOI: [10.5281/zenodo.15863589](https://doi.org/10.5281/zenodo.15863589)). All source code, neural network implementations, evaluation scripts, and replication suites are publicly accessible in our dedicated GitHub repository: [https://github.com/akssha74/TopoRadar-Net-AvalCD](https://github.com/akssha74/TopoRadar-Net-AvalCD). Model checkpoints for all 3 independent training seeds and publication artifacts are openly distributed under Release v1.0.0: [https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.0](https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.0).

### 4. Suggested Independent Reviewers
1. **Dr. Markus Eckerstorfer**, Senior Research Scientist, NORCE Norwegian Research Centre, Tromsø, Norway. Email: `maec@norceresearch.no`  
   *Expertise: Sentinel-1 SAR change detection for snow avalanches, Arctic cryospheric hazards.*
2. **Dr. Yves Bühler**, Head of Alpine Remote Sensing Group, WSL Institute for Snow and Avalanche Research SLF, Davos, Switzerland. Email: `buehler@slf.ch`  
   *Expertise: Automated regional avalanche mapping, alpine optical and radar remote sensing.*
3. **Dr. Achille Gatti**, Department of Electronics, Information and Bioengineering, Politecnico di Milano, Milan, Italy. Email: `achille.gatti@polimi.it`  
   *Expertise: AvalCD benchmark lead author, deep learning change detection on SAR imagery.*
4. **Dr. Silvan Leinss**, Senior Researcher, Institute of Environmental Engineering, ETH Zurich, Switzerland. Email: `leinss@ifu.baug.ethz.ch`  
   *Expertise: Microwave radar backscatter characteristics of snow avalanches, SAR polarimetry.*
5. **Dr. Elisabeth D. Hafner**, Avalanche Warning and Remote Sensing, WSL Institute for Snow and Avalanche Research SLF, Davos, Switzerland. Email: `elisabeth.hafner@slf.ch`  
   *Expertise: Large-scale satellite avalanche mapping, EAWS size classification inventories.*

Thank you very much for your time and consideration of our manuscript.

Sincerely,  
**Akshay Sharma** (on behalf of all authors)  
Department of Computer Science and Engineering  
SAGE University, Indore 452020, India  
Email: `akssha74@gmail.com`
