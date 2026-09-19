# Submission Record — Journal of Mountain Science (JMS)

**Status:** 🔄 Resubmission in progress — Manuscript **26-11479** unsubmitted by Editorial Office (06-Sep-2026) pending format compliance. Anonymized editable Word main document + updated cover letter prepared for re-upload.

---

## 0. Editorial Office Resubmission Requirements (Email 06-Sep-2026)

| # | Requirement  | Action Taken | File |
|---|---|---|---|
| 1 | Fill in all authors' info (name, affiliation, email) in online system | To be entered in ScholarOne (kept out of main doc) | See §2 below |
| 2 | Cover letter stating novelty, conflicts of interest, reviewer exclusions; each author agrees to submission | Cover letter updated with COI statement, opposed-reviewer statement, and author-agreement statement | `cover_letter.pdf` / `.md` |
| 3 | Upload **editable WORD** main body, **no author/institution info** (double-blind); figures/tables embedded if < 10 MB | Anonymized `.docx` generated (0.86 MB, 4 figures + 8 tables embedded, all identifying info stripped). **v2 fix (06-Sep):** cross-references resolved to real numbers (Table 1–8, Fig. 1–4, Eq. 4/5, Section n) from compiled `.aux`; all 12 float captions restored with bold "Table N."/"Fig. N." prefixes; tables switched to AutoFit-to-window at 9 pt so wide tables no longer fragment/clip in the ScholarOne proof. | `JMS_26-11479_Main_Manuscript_Anonymous.docx` |

**Manuscript ID:** 26-11479

---

## 1. Manuscript Identity

| Field | Value |
|---|---|
| **Title** | Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic |
| **Short Title** | TopoRadar-Net for Alpine Avalanche Debris Mapping in Sentinel-1 SAR |
| **Target Venue** | Journal of Mountain Science (JMS) |
| **Publisher** | Science Press China / Springer Nature |
| **Indexing** | SCIE (Clarivate, JCR Q2), Scopus (Else vier Q2), CAS |
| **ISSN** | 1672-6316 (print) / 1993-0321 (online) |
| **Article Track** | Original Research Article |
| **Format** | Editable Word (`.docx`) for main body (JMS external-review requirement); LaTeX source (`sn-jnl.cls`, `sn-basic`) retained for camera-ready |
| **Main Document** | `JMS_26-11479_Main_Manuscript_Anonymous.docx` and `paper/main_anonymous.pdf` (anonymized, 4 figures + 8 tables embedded, 13 pages) |
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
| **Release v1.0.6 (Weights & Paper)** | [https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.6](https://github.com/akssha74/TopoRadar-Net-AvalCD/releases/tag/v1.0.6) | **200 OK** | Immutable post-freeze package: `main.pdf` (13 pages), `main_anonymous.pdf`, synchronized submission-support sources/PDFs, `publication_checkpoints_3seeds.tar.gz` (TopoRadar-Net + Attention U-Net, 3 seeds), `source_package.zip` |
| **AvalCD Benchmark (Zenodo)** | [https://doi.org/10.5281/zenodo.15863589](https://doi.org/10.5281/zenodo.15863589) | **200 OK** | Ground truth masks, Sentinel-1 SAR, DEM, LIA |

---

## 5. Suggested Independent Reviewers

1. **Dr. Markus Eckerstorfer** (`maec@norceresearch.no`), Senior Research Scientist, NORCE Norwegian Research Centre, Tromsø, Norway.
2. **Dr. Achille Gatti** (`achille.gatti@polimi.it`), Department of Electronics, Information and Bioengineering, Politecnico di Milano, Italy.
3. **Dr. Silvan Leinss** (`leinss@ifu.baug.ethz.ch`), Senior Researcher, Institute of Environmental Engineering, ETH Zurich, Switzerland.

---

## 6. Pre-Submission Quality & Review History

* **Reviewer Model Parity (Latest Completed Independent State):**
  * **GLM-5.2 Round 25:** **28 / 30** — score target achieved; its sole stale-public-support-file blocker is resolved in v1.0.6.
  * **Claude Opus 4.8 Round 24:** **27 / 30 (`accept`)** — 0 result/evidence blockers; Round-25 verification pending.
  * **GPT-5.6 Round 24:** **26 / 30** — all seven findings are resolved in v1.0.5/v1.0.6; Round-25 verification pending.
  * Final all-panel convergence verification is pending.
* **Reproduction Gate:** **100% PASS** (13 pages, 0 undefined citations, 0 undefined references, 0 missing markers, all code/data artifacts byte-reproducible).
* **Convergence Status:** **Pending Round-24 confirmation.**
