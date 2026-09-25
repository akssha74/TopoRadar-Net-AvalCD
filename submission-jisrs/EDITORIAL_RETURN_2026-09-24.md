# Editorial Return Compliance — ISRS-D-26-01429

Editorial return received: 24 September 2026  
Correction package verified: 25 September 2026

## Requirement-by-requirement closure

| Editorial-office requirement | Corrective action | Verification |
|---|---|---|
| Title page must contain a Conflict of Interest statement | Added exact heading `Conflict of Interest` and statement “The authors declare that they have no conflict of interest.” | Present in source, DOCX, and one-page render |
| Title page must contain Funding information | Added exact heading `Funding` and statement that no funding supported the study or manuscript preparation | Present in source, DOCX, and one-page render |
| Author's Contribution must follow Conflict of Interest and Funding | Reordered title-page declarations to Conflict of Interest → Funding → Author's Contribution | Heading-order gate passes |
| Title page must contain Acknowledgement | Added exact heading `Acknowledgement` with `Not applicable.` | Present in source, DOCX, and one-page render |
| Blinded manuscript must use automatic continuous line numbering | Added Word `w:lnNumType` with `countBy=1`, `start=1`, and `restart=continuous` to every section | OOXML gate passes; rendered numbering continues across all 13 pages |
| Remove Statements/Declarations from blinded manuscript | Deleted the complete `Statements and Declarations` section from the anonymous source and regenerated the DOCX | Source, DOCX, and rendered-text absence gates pass |

## Files to replace in Editorial Manager

1. `JISRS_Title_Page.docx` as **Title Page**
2. `JISRS_Main_Manuscript_Anonymous.docx` as **Blinded Manuscript**

`ESM_1.pdf` is unchanged and does not need replacement.

## Regression checks

- Main-text limit: 2,039 / 4,000 words
- Abstract: 199 / 200 words
- Anonymous Word manuscript: 13 A4 pages
- Identified title page: 1 A4 page
- Figures, tables, equations, units, captions, and references render without clipping or missing glyphs
- Anonymous DOCX identity scan: pass
- Metric reproduction and independent reviewer harness: pass
- No method, result, abstract, figure, table, citation, or conclusion changed

## Automated gates

- `check_compliance.py`: pass
- `verify_package.py`: pass
- `experiments/code/reproduce_all_metrics.py`: pass
- `reviews/harness.py`: pass

The correction is administrative only and does not change the manuscript's scientific claims or evidence.
