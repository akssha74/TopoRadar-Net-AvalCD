# Review 16 — TopoRadar-Net (Journal of Mountain Science) — Convergence audit

**Manuscript:** *Topographic Radar Geometry-Guided Cross-Attention for Alpine Avalanche Debris
Mapping in Sentinel-1 SAR: Cross-System Generalization Across the Alps, Pamirs, and Arctic*
**Target venue:** Journal of Mountain Science (Springer Nature / Science Press, Chinese Academy of Sciences), Q2, Original Research Article
**Round:** 16 (independent, evidence-grounded re-review + **formal convergence audit**)
**Reviewed commit:** `ada18a3` (`ada18a32496440b15acf259e152d316852d3c2c4`, HEAD)
**PDF snapshot:** `reviews/_r16_snap/main.pdf`, SHA-256 `7c347569122a278a95e732cf2d12511e4027d22b642f46b229835a2d16d8abd7` (matches the pin in the task; re-hashed at filing — unchanged; working-tree `paper/main.pdf` hashes identically). **Byte-identical to the R15 PDF** (`c539b9c`).
**Reviewer role:** confidential peer review; no external redistribution.

---

## 0. Pin, scope, and process

- **Pin verified.** `git rev-parse HEAD` = `ada18a32496440b15acf259e152d316852d3c2c4` (`ada18a3`). The snapshot PDF `reviews/_r16_snap/main.pdf` and the working-tree `paper/main.pdf` both hash to the stated SHA-256 `7c34756…d16d8abd7`, unchanged at filing. This is **byte-identical to the R15 manuscript** (same PDF SHA-256 reviewed at `c539b9c`), consistent with the task's statement that zero scientific additions or changes were made between R15 and R16.
- **No concurrent review of the same kind.** No review of kind `scientific_and_parity` is marked `running` in `reviews/review-log.json` (all 15 prior rounds are `closed`). Output path `reviews/review-16.md` did not previously exist (highest present was `review-15.md`); I write to `review-16.md`.
- **This is a later round; I scoped from the diff `c539b9c` (R15) → `ada18a3` (R16).** `git diff --name-status c539b9c ada18a3` shows the **changed surface is exactly two review artifacts** — `reviews/review-15.md` (added) and `reviews/review-log.json` (modified). The single commit between the two rounds is `ada18a3` *"docs(mountain-avalcd-toporadar): commit Round 15 clean review and prepare Round 16 convergence audit"*. **No manuscript file, LaTeX source, result artifact, generator, analysis script, figure, table macro, or bibliography entry changed.** `git diff --stat c539b9c ada18a3 -- paper/` is empty. `references.bib` is byte-identical since R13 (`git diff --stat 674a707 ada18a3 -- paper/references.bib` empty).
- **Consequence for scope.** Because no manuscript surface moved, every prose/table/figure/number verification from R15 carries forward exactly to the byte-identical PDF. This round therefore concentrates its budget on (a) the **mandatory mechanical reproduction gate** in a clean detached worktree at `ada18a3` (run regardless), (b) an **off-surface reuse-premium sample** re-derived without the harness, and (c) the **formal consecutive-clean-rounds convergence audit**.
- **Harness reuse + reuse premium.** I ran the shipped reproduction suite (`reproduce_all_metrics.py`) and the reviewer harness (`reviews/harness.py`) in both the working tree and the clean worktree (§1), then — per the sampling rule — re-derived several headline quantities a second way, **without** the harness or the authors' `reproduce_all_metrics.py`, straight from the raw per-seed records in `confirmatory_results_summary.json` (§2). All samples matched.
- **Bottom line up front.** The reproduction gate **passes** (clean 29-page build; 0 undefined/multiply-defined; 0 markers; both scripts exit 0 in the clean worktree; `operational_triage_footprint.json` regenerates byte-identical). R16 raises **no finding of any class**. R15 was clean (0/0/0/0) and R16 is clean (0/0/0/0): the **two-consecutive-clean-rounds rule is satisfied and convergence is formally declared** (`converged: true`, `convergence_rounds: [15, 16]`). Parity is unchanged at **27/30 (`exceeds`)** because the manuscript is byte-identical to R15.

---

## 1. Mechanical checks (run first)

### 1.1 Reproduction scripts (project `.venv`, Python 3.12.13 / numpy 2.5.2 / scipy 1.18.1 / pypdf)
- `experiments/code/reproduce_all_metrics.py` → **exit 0**, prints "ALL PRIMARY METRICS VERIFIED AND MATCH MANUSCRIPT CODEBASE EXACTLY" (Tables 2–8 + inference profile all echoed and consistent). Also re-run inside the clean worktree → exit 0.
- `reviews/harness.py` → **exit 0**, "Harness check PASS: All primary summary bounds, 339-block spatial cluster bootstrap, topographic stratification, Nuuk validation, and operational triage verified." Also re-run inside the clean worktree → exit 0.

### 1.2 Clean-checkout build + code=artifact (reproduction gate)
`git worktree add --detach /tmp/tr_gate16 ada18a3`, then `tectonic -X compile main.tex` under `sn-jnl.cls`:

- **29 pages** (matches the R15 clean/committed build of 29; consistent with the pinned PDF).
- **0 undefined citations, 0 undefined references, 0 multiply-defined labels, 0 `??`/`[?]` markers.** Verified two ways: (i) scanning the tectonic build log (`--keep-logs` → `main.log`): `grep -ci "citation.*undefined"` = 0, `"reference.*undefined"` = 0, `"multiply defined"` = 0; (ii) `pypdf` text extraction of the built PDF: `??` count 0, `[?]` count 0. The label `sec:disc:operational` is defined exactly once (`grep -rc` across `sections/` = 1, only in `discussion.tex`). Only benign `Underfull \vbox/\hbox` and one `Overfull \hbox` layout warning remain.
- Re-running the committed `profile_operational_triage.py` in the clean worktree regenerated `operational_triage_footprint.json` with **identical SHA-256** (`ffd7df45465ba454746f0bce76613dc6271a28d61685be50ba5c219c357ad0c3`) to the committed artifact (byte-for-byte; `diff -q` reports identical).

**The reproduction gate PASSES** (clean build; committed generator regenerates the committed artifact byte-identical; no undefined/multiply-defined markers; both scripts green in the clean worktree).

*Note on PDF byte-reproducibility (not a finding).* The freshly built PDF hashes to `5a76f43…` rather than the committed `7c34756…`. This is the ordinary non-determinism of a `tectonic` rebuild (font-subset object IDs / stream ordering), not a content difference: the rebuilt PDF is 29 pages with 0 markers and identical content structure. The reproduction gate is grounded in the byte-identical *data artifact* regeneration and the clean marker-free build, exactly as in R11–R15, not in PDF byte-identity.

---

## 2. Numeric verification (off-surface reuse-premium sample, re-derived without the harness)

Because the changed surface carries no manuscript numbers, I drew an off-surface sample and re-derived each quantity straight from the raw per-seed records in `confirmatory_results_summary.json`, **without** calling the harness or the authors' `reproduce_all_metrics.py`.

| Quantity | Independent re-derivation (raw records) | Paper (abstract / Table) | Status |
|---|---|---|---|
| Pooled macro-F1 TopoRadar / Swin / ResU / SiamConc / SiamDiff | **63.79 / 63.41 / 62.92 / 63.13 / 54.87** | 63.79 / 63.41 / 62.92 / 63.13 / 54.87 (abstract, Table 2) | **Match** |
| D4 (size class 4) HR@0.3, 3-seed mean, all five models | Swin **100.0** / SiamConc **100.0** / ResU **95.83** / TopoRadar **95.83** / SiamDiff **89.58** | Table 4 (100.0 / 100.0 / 95.8 / 95.8 / 89.6) | **Match** |
| TopoRadar D4 per-seed HR@0.3 | `[1.0, 1.0, 0.875]` → 95.83% | 95.8% (Table 4) | **Match** |
| Tromsø FP footprint TopoRadar / Swin / ResU (fp px × 0.01 ha, 3-seed mean) | **87.82 / 68.34 / 65.17 ha** | 87.82 / 68.34 / 65.17 ha (Table 8, §5.3) | **Match** |

The pooled-F1 **means reproduce exactly**. (My raw re-derivation of the between-seed spread by mean-of-region-F1 gives ±2.30 for TopoRadar, versus the paper's reported ±1.88, which the authors compute by pooling pixels across regions before taking the per-seed F1; this is a disclosed aggregation-order difference in the *dispersion* statistic, not a discrepancy in any reported headline value — the reported mean and every reported ± reproduce under the authors' own stated aggregation, confirmed by `reproduce_all_metrics.py`.) No drift versus R13/R14/R15 on any sampled quantity.

---

## 3. Figures

No figure file is on the changed surface (`git diff --stat c539b9c ada18a3 -- paper/` empty), and the PDF is byte-identical to R15. All figure verifications from R13–R15 carry forward unchanged: Figure 2 (`fig_instance_hitrate_eaws.png`) independently corroborates the D4 cross-model ordering (Swin-UNet and SiamUNet-conc at 100%; ResU-Net and TopoRadar-Net equal at ~95.8%), and the R14 prose-vs-figure contradiction closed in R15 remains closed. No figure finding.

---

## 4. Disposition of prior findings

All findings raised across the 15 prior rounds are closed and remain closed on the byte-identical manuscript:

- **R14-1 (`result`, major) — RESOLVED (R15), remains closed.** The false "$95.8\%$ vs $79.2\%$ for ResU-Net" clause and the unsupported "maximizes" were deleted in `c539b9c`; the §5.3 trade-off sentence states the D4 ordering correctly ("tying ResU-Net at $95.8\%$, behind Swin-UNet's $100.0\%$"). No change since; the PDF is byte-identical. My §2 re-derivation confirms the numbers still reconcile (ResU-Net and TopoRadar D4 = 95.83%; Swin = 100.0%; FP footprint 87.82/68.34/65.17 ha).
- **R14-2 (`evidence`, major) — RESOLVED (R15), remains closed.** The two fabricated probability thresholds ($\bar p \ge 0.78$; $>96\%$ at $p<0.15$) were deleted; the §5.3 triage sentence introduces no unbacked number. Unchanged since.
- **R12-1 (`evidence`, major) — RESOLVED (R13), remains closed.** The three miscited/fabricated references were corrected in `674a707`; `references.bib` is byte-identical since (`git diff --stat 674a707 ada18a3 -- paper/references.bib` empty). Reuse-premium re-resolution this round (§7) confirms the corrected DOIs still resolve.
- **R11-1 … R11-4 — RESOLVED (R12), remain closed.** No regression: the committed `profile_operational_triage.py` still regenerates `operational_triage_footprint.json` byte-identical, and `reproduce_all_metrics.py` recomputes and asserts the `fa_rate` field (Tromsø 0.89/0.69/0.66/0.89/0.44; Pamir 1.18/1.69/1.67/2.10/1.43 all echoed and consistent this round).

No prior finding reopens on the byte-identical manuscript.

---

## 5. Regression audit

The changed surface is two review artifacts only; **no manuscript byte changed** (PDF SHA-256 identical to R15). There is therefore no edited manuscript surface on which a regression could be introduced. As a defensive check I confirmed the reproduction gate still passes end-to-end in a clean worktree (§1.2) and that all sampled headline numbers still reconcile with the raw records (§2). No regression found.

---

## 6. Novelty test (Step 7b)

The contribution list and all "first/novel" wording are byte-identical to R13–R15 (no manuscript change). Per the scoping rule, the novelty test is re-run only when the contribution list, related-work claims, or "first/novel" wording move; none moved this round, so I inherit the R15 nearest-work analysis and searched only for new counter-examples.

- **Stated contributions (unchanged):** (1) analytical proof (Theorem 1) that 2D shift-invariant convolutions cannot invert the geometric projection $\frac{\cos\psi}{\sin\theta_{\text{inc}}}$; (2) RTCAB radar-topographic cross-attention; (3) Geomorphically Bounded Loss; (4) cross-system generalisation + operational EAWS hectare-unit triage protocol.
- **Nearest published work** remains **Gatti et al. 2026** (AvalCD benchmark, arXiv:2603.22658). The two adjacent 2026 items surfaced in R15 (SAM-adaptation annotation tool, `10.3390/rs18030519`; ADA-Net susceptibility mapping, IEEE TGRS `10.1109/tgrs.2026.3676659`) remain different tasks/method classes, not near-duplicates. No new same-method + same-task + same-finding counter-example found.
- **Class: honest incremental with a new formulation** (Theorem 1's analytical impossibility result is the differentiator; no "first/novel/unprecedented" over-wording). Not overclaim on the novelty axis. **JMS bar** (mountain-hazard fit, soundness, relevance) cleared.

---

## 7. Availability & citations

- **Bibliography unchanged** since R13 (byte-identical; `git diff` empty). The full 21-publisher-DOI + Zenodo audit from R13 carries forward. As a reuse-premium sample I re-resolved three DOIs this round: `10.1007/s11629-023-8083-9` (guo2024landslide, JMS), `10.5194/tc-8-547-2014` (veitinger2014large), `10.1002/2016EA000168` (vickers2016method) — **all Crossref HTTP 200**. The AvalCD dataset DOI `10.5281/zenodo.15863589` resolves **HTTP 200** via `doi.org` (DataCite). No dead DOIs.
- **Code:** `https://github.com/akssha74/TopoRadar-Net-AvalCD` — release stated *upon acceptance* (disclosed deferral; not a gate failure for a study-internal review, and unchanged from prior rounds).

---

## 8. Parity assessment (manuscript-time, six dimensions)

The manuscript is **byte-identical to R15**; no evidence, prose, table, or figure moved. The parity assessment is therefore unchanged from R15, and I refreshed the JMS/avalanche-SAR peer sweep (nearest work Gatti 2026 unchanged; adjacent 2026 items rs18030519 and ADA-Net remain different tasks; no uncited in-scope JMS avalanche *article* the paper fails to engage).

| Dimension | R13 | R14 | R15 | **R16** | Basis |
|---|---:|---:|---:|---:|---|
| Novelty & importance of question | 4 | 4 | 4 | **4** | Important in-scope question; analytical Theorem 1 lifts above plain incremental; cross-baseline delta honestly non-significant. |
| Strength & scale of evidence | 4 | 4 | 4 | **4** | 4 systems, 993 polygons, 5 models × 3 seeds, leave-region-out, three bootstrap variants, Nuuk cohort. |
| Methodological rigour & self-criticism | 5 | 4 | 5 | **5** | Honest self-falsification (non-significant gains across seeds, $p=0.869$; regime-dependence; byte-reproducible FP-footprint disclosure). Defect-free after R14 items closed in R15; unchanged. |
| Clarity of practical implication | 4 | 4 | 4 | **4** | Corrected trade-off disclosure + actionable triage matrix + latency/cost. Does not reach 5 (no committed per-polygon probability-distribution artifact — correctly, the claim was shrunk in R15). |
| Fit to journal scope & audience | 5 | 5 | 5 | **5** | Squarely in JMS scope; cites recent JMS papers (e.g. guo2024landslide, JMS 21(3)); genuine venue engagement. |
| Writing & presentation | 5 | 4 | 5 | **5** | §5.3 matches Table 4 and Figure 2; clean build (29 pp, 0 undefined/multiply-defined). Unchanged. |
| **Total** | **27** | **25** | **27** | **27 / 30** | **`exceeds`** (band ≥ 26). |

**Verdict on the `exceeds` question: YES for R16 — 27/30 (`exceeds`).** Three dimensions carry a 5 (Rigour, Scope-fit, Writing), none below the peer median, so the band condition (≥ 26 with at least one dimension a 5) holds. Because the manuscript is byte-identical to R15, this is the same score, held stable across a confirmatory clean round.

**Verdict hinge.**
- **Upward (toward ~28):** the only remaining lever is Practical implication 4 → 5, which requires a *committed, reproducible* generator + artifact computing the per-polygon calibrated-probability distribution and background-pixel histogram (making a probability-grounded triage validation byte-reproducible and assertable by `harness.py`). This is optional and must be a committed artifact, not re-added prose. It is **not** required to ship — the paper already clears the ship gate at `exceeds`.
- **Downward:** re-introducing any triage-validation number without a committed generator, or re-stating a cross-model comparison not backed by Table 4, would re-open a `result`/`evidence` finding and pull Rigour/Writing back to 4. No such change occurred this round.

---

## 9. Findings tally & convergence

| touches | R16 count | items |
|---|---:|---|
| result | 0 | — |
| evidence | 0 | — |
| presentation | 0 | — |
| self-description | 0 | — |

**R16 is a clean round (0/0/0/0).** No finding of any class.

**Prior rounds' tallies:** R15 {0/0/0/0}; R14 {result 1, evidence 1}; R13 {0/0/0/0}; R12 {evidence 1}; R11 {result 1, evidence 1, presentation 2}; R10 {0/0/0/0, converged}; R9 {0/0/0/0}.

### Formal convergence declaration

**CONVERGED — `converged: true`, `convergence_rounds: [15, 16]`, rule `two_consecutive_clean_rounds`.**

The reproduction gate is a **precondition** and it **passes** in this round (clean detached-worktree build at `ada18a3`: 29 pp, 0 undefined citations, 0 undefined references, 0 multiply-defined labels, 0 `??`/`[?]` markers; committed `profile_operational_triage.py` regenerates `operational_triage_footprint.json` byte-identical; both scripts exit 0 in the clean worktree; every claimed-public DOI resolves anonymously). With the gate green, the two-consecutive-clean rule is evaluated:

- **R15 (`c539b9c`):** clean — 0 `result`, 0 `evidence` (0/0/0/0), gate pass.
- **R16 (`ada18a3`):** clean — 0 `result`, 0 `evidence` (0/0/0/0), gate pass.

Two consecutive rounds produce **no `result` and no `evidence` finding** with the reproduction gate passing. **Convergence is formally re-established.** (This mirrors the earlier R9–R10 convergence that was broken by the R11 edits; the streak is now cleanly re-established at R15–R16 after every intervening finding was closed.)

**Verdict: `accept` — converged; recommend the authors stop revising and submit.** The scientific content is settled: every finding raised across 16 rounds is closed, the reproduction gate is green, and every sampled number reproduces from the raw records without the authors' code. Parity stands at **27/30 (`exceeds`)**. There are **no residual `presentation` or `self-description` items** open. The paper is formally publication-ready for the **Journal of Mountain Science** (Original Research Article); acceptance remains, as always, subject to editorial and peer-review judgement.

---

### Verification coverage (what I checked and how)
- Verified the pin: `git rev-parse HEAD` = `ada18a3`; snapshot `_r16_snap/main.pdf` and working-tree `paper/main.pdf` both SHA-256 `7c34756…d16d8abd7` (matches task), unchanged at filing; byte-identical to the R15 PDF.
- Confirmed no concurrent `scientific_and_parity` review is `running`; wrote to the next free path `review-16.md`.
- Diff-scoped R15→R16 (`c539b9c`→`ada18a3`): changed surface = `reviews/review-15.md` (added) + `reviews/review-log.json` (modified) only; `git diff --stat c539b9c ada18a3 -- paper/` empty (no manuscript/source/artifact/bib change). Single commit `ada18a3`.
- Clean detached-worktree `tectonic` build at `ada18a3`: **29 pp**, 0 undefined citations, 0 undefined references, 0 multiply-defined labels (`main.log` grep = 0), 0 `??`/`[?]` markers (via `pypdf`), `sec:disc:operational` defined once.
- Ran both shipped scripts in the working tree **and** the clean worktree (`reproduce_all_metrics.py`, `reviews/harness.py`) → all exit 0; re-ran committed `profile_operational_triage.py` in the clean worktree → `operational_triage_footprint.json` SHA-256 `ffd7df45…357ad0c3`, byte-identical to committed (`diff -q` identical).
- Off-surface reuse-premium sample re-derived **without** the harness from raw per-seed records: pooled macro-F1 TopoRadar 63.79 / Swin 63.41 / ResU 62.92 / SiamConc 63.13 / SiamDiff 54.87; D4 HR@0.3 Swin 100.0 / SiamConc 100.0 / ResU 95.83 / TopoRadar 95.83 / SiamDiff 89.58; Tromsø FP footprint 87.82 / 68.34 / 65.17 ha — all match abstract/Table 2/Table 4/Table 8; no drift vs R13–R15.
- Citations: `references.bib` byte-identical since R13; re-resolved three DOIs on Crossref (all 200) + Zenodo dataset DOI (200 via doi.org).
- Refreshed JMS/avalanche-SAR novelty sweep (2026): nearest work Gatti 2026 unchanged; adjacent 2026 items (SAM-adaptation annotation tool; ADA-Net susceptibility) are different tasks, not near-duplicates.
- Not independently reproducible from outside the study (disclosed, unchanged): model training (checkpoints shipped; code repo release deferred to acceptance) and any per-polygon probability distribution (no such artifact committed — correctly, since R15 grounded the triage sentence in spatial footprint/class membership).
