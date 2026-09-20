#!/usr/bin/env python3
"""Run the mechanical JISRS package and scientific reproduction gates."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission-jisrs"
PAPER = ROOT / "paper-jisrs"


def run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        check=True,
        capture_output=True,
    )
    return result.stdout + result.stderr


def main() -> None:
    print(run([sys.executable, "check_compliance.py"], SUBMISSION))
    print(run([sys.executable, "experiments/code/reproduce_all_metrics.py"], ROOT))
    print(run([sys.executable, "reviews/harness.py"], ROOT))

    metadata = json.loads((SUBMISSION / "submission_metadata.json").read_text())
    required = [
        ROOT / metadata["main_document"],
        ROOT / metadata["title_page"],
        ROOT / metadata["supplementary_information"],
        ROOT / metadata["cover_letter"],
        ROOT / metadata["highlights"],
        ROOT / metadata["source_package"],
        PAPER / "main.pdf",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing submission files: {missing}")

    anonymous_text = (PAPER / "main.tex").read_text(encoding="utf-8")
    anonymous_text += (PAPER / "supplementary_information.tex").read_text(
        encoding="utf-8"
    )
    with zipfile.ZipFile(SUBMISSION / "JISRS_Main_Manuscript_Anonymous.docx") as docx:
        anonymous_text += docx.read("word/document.xml").decode("utf-8")
        docx_document_xml = docx.read("word/document.xml").decode("utf-8")
        core = docx.read("docProps/core.xml").decode("utf-8")

    identity_terms = (
        "Akshay",
        "Lalji",
        "SAGE University",
        "akssha74",
        "@gmail",
    )
    leaks = [term for term in identity_terms if term.lower() in anonymous_text.lower()]
    if leaks:
        raise SystemExit(f"Anonymous-package identity leaks: {leaks}")
    if re.search(r"<dc:creator>[^<]+", core):
        raise SystemExit("Anonymous DOCX has a non-empty creator")
    for required_text in (
        "Abstract",
        "Cloud cover",
        "Keywords",
        "Sentinel-1 SAR",
        "snow avalanche mapping",
    ):
        if required_text not in docx_document_xml:
            raise SystemExit(f"Anonymous DOCX missing required text: {required_text}")

    document = Document(SUBMISSION / "JISRS_Main_Manuscript_Anonymous.docx")
    if not document.sections:
        raise SystemExit("DOCX has no section")
    section = document.sections[0]
    if round(section.page_width.mm) != 210 or round(section.page_height.mm) != 297:
        raise SystemExit("DOCX is not A4")
    line_numbers = section._sectPr.find(qn("w:lnNumType"))
    if line_numbers is None or line_numbers.get(qn("w:restart")) != "continuous":
        raise SystemExit("DOCX lacks continuous line numbering")
    if abs(document.styles["Normal"].font.size.pt - 12) > 0.01:
        raise SystemExit("DOCX Normal style is not 12 pt")

    with zipfile.ZipFile(SUBMISSION / "source_package.zip") as source:
        names = set(source.namelist())
        required_members = {
            "TopoRadar-Net-JISRS/main.tex",
            "TopoRadar-Net-JISRS/supplementary_information.tex",
            "TopoRadar-Net-JISRS/references.bib",
            "TopoRadar-Net-JISRS/sn-jnl.cls",
            "TopoRadar-Net-JISRS/sn-apacite.bst",
            "TopoRadar-Net-JISRS/figures/Fig1.eps",
            "TopoRadar-Net-JISRS/figures/Fig2.eps",
            "TopoRadar-Net-JISRS/evidence/event_sensor_manifest.json",
        }
        absent = sorted(required_members - names)
        if absent:
            raise SystemExit(f"Source package missing members: {absent}")

    print("PASS: JISRS package, anonymity, Word, source, and scientific gates")


if __name__ == "__main__":
    main()
