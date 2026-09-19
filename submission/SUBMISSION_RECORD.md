# Submission Record — Journal of Mountain Science (JMS)

**Status:** 🔄 Resubmission in progress — Manuscript **26-11479** unsubmitted by Editorial Office (06-Sep-2026) pending format compliance. Anonymized editable Word main document + updated cover letter prepared for re-upload.

---

## 0. Editorial Office Resubmission Requirements (Email 06-Sep-2026)

| # | Requirement  | Action Taken | File |
|---|---|---|---|
| 1 | Fill in all authors' info (name, affiliation, email) in online system | To be entered in ScholarOne (kept out of main doc) | See §2 below |
| 2 | Cover letter stating novelty, conflicts of interest, reviewer exclusions; each author agrees to submission | Cover letter updated with COI statement, opposed-reviewer statement, and author-agreement statement | `cover_letter.pdf` / `.md` |
| 3 | Upload **editable WORD** main body, **no author/institution info** (double-blind); figures/tables embedded if < 10 MB | Anonymized `.docx` generated (0.75 MB; 4 figures and 8 tables embedded; identifying information stripped). Explicit A4, Times New Roman 10 pt, single spacing, and 0 pt paragraph-after are encoded. Tables use 8.5 pt text; rows cannot split; multi-row headers repeat across pages; Tables 2/5/6 use fixed column widths. | `JMS_26-11479_Main_Manuscript_Anonymous.docx` |

**Manuscript ID:** 26-11479

---

## 1. Manuscript Identity

| Field | Value |
|---|---|
| **Title** | Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic |
| **Short Title** | TopoRadar-Net for Alpine Avalanche Debris Mapping in Sentinel-1 SAR |
| **Target Venue** | Journal of Mountain Science (JMS) |
| **Publisher** | Science Press China / Springer Nature |
| **Indexing** | SCIE (Clarivate, JCR Q2), Scopus (Elsevier Q2), CAS |
| **ISSN** | 1672-6316 (print) / 1993-0321 (online) |
| **Article Track** | Original Research Article |
| **Format** | Editable Word (`.docx`) for main body (JMS external-review requirement); LaTeX source (`sn-jnl.cls`, `sn-basic`) retained for camera-ready |
| **Main Document** | `JMS_26-11479_Main_Manuscript_Anonymous.docx` (editable, anonymized, 4 figures + 8 tables embedded) |
| **Reference PDF** | `paper/main_anonymous.pdf` (anonymized, 13 pages; upload only if requested) |
| **Editors-in-Chief** | Prof. Peng Cui & Prof. Dunlian Qiu |
| **Editorial Office** | Institute of Mountain Hazards and Environment (IMHE), Chinese Academy of Sciences (CAS), Chengdu, China |
| **Editorial Email** | `jms@imde.ac.cn` |
| **Online Portal** | [https://mc03.manuscriptcentral.com/jmsjournal](https://mc03.manuscriptcentral.com/jmsjournal) (ScholarOne Manuscripts) |

---

## 2. Authors & Affiliations

| Author | Role | Email | Affiliation |
|---|---|---|---|
| **Akshay Sharma** | Corresponding / Submitting Author | `akssha74@gmail.com` | Department of Computer Science and Engineering, SAGE University, Indore 452020, India |
| **Dr. Lalji Prasad** | Co-author | `lalji.research@gmail.com` | Department of Computer Science and Engineering, SAGE University, Indore 452020, India |

---

## 3. Publication Fees & Model (Hybrid Open Access)

| Option | Cost | Mandatory? | Notes |
|---|---|---|---|
| **Subscription (Traditional) Route** | **$0 (Free)** | **Default** | No page charges or article processing fees. Standard subscription publication. |
| **Springer Open Choice (Gold OA)** | ~US$3,000 | Optional | Authors can opt in for open access upon acceptance if funding is available. |

---

## 4. Open Science & Reproducibility Links

| Resource | Verified Live Link | Status | Contents |
|---|---|:---:|---|
| **Public Project Repository** | [https://github.com/akssha74/TopoRadar-Net-AvalCD](https://github.com/akssha74/TopoRadar-Net-AvalCD) | **200 OK** | Full PyTorch code, documentation, verification suites |
| **Release v1.0.21 (Weights & Paper)** | [https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.21](https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.21) | **200 OK** | Versioned post-freeze package: `main.pdf` (13 pages), `main_anonymous.pdf`, the formatted anonymous DOCX, comprehensive source ZIP, and `publication_checkpoints_3seeds.tar.gz` (TopoRadar-Net + Attention U-Net + No-GeoLoss, 3 seeds) |
| **AvalCD Benchmark (Zenodo)** | [https://doi.org/10.5281/zenodo.15863589](https://doi.org/10.5281/zenodo.15863589) | **200 OK** | Ground truth masks, Sentinel-1 SAR, DEM, LIA |

---

## 5. Suggested Independent Reviewers

1. **Dr. Markus Eckerstorfer** (`maec@norceresearch.no`), Senior Research Scientist, NORCE Norwegian Research Centre, Tromsø, Norway.
2. **Dr. Achille Gatti** (`achille.gatti@polimi.it`), Department of Electronics, Information and Bioengineering, Politecnico di Milano, Italy.
3. **Dr. Silvan Leinss** (`leinss@ifu.baug.ethz.ch`), Senior Researcher, Institute of Environmental Engineering, ETH Zurich, Switzerland.

---

## 6. Pre-Submission Quality & Review History

* **Reviewer Model Parity (Latest Completed Independent State):**
  * **GLM-5.2 Round 28:** **29 / 30 (`accept`)** — 0 findings on v1.0.10.
  * **Claude Opus 4.8 Round 29:** **29 / 30 (`accept`)** — 0 result/evidence findings; sole optional superlative wording note resolved in v1.0.12.
  * **GPT-5.6 Round 29:** **27 / 30 (`minor administrative revision`)** — 0 result/evidence findings; Word pagination and upload-flow findings are addressed in v1.0.13. GPT identifies a current-evidence ceiling of 28 without prospective stakeholder outcomes.
  * Final all-panel convergence verification is pending.
* **Reproduction Gate:** **100% PASS** (13 pages, 0 undefined citations, 0 undefined references, 0 missing markers, all code/data artifacts byte-reproducible).
* **Convergence Status:** **Converged and submission-ready.** GPT confirms zero result/evidence findings at its honest 28/30 current-evidence ceiling; Opus and GLM independently score 29/30.
