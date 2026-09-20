#!/usr/bin/env python3
"""Normalize the separate identified JISRS title-page DOCX."""

from pathlib import Path
import argparse

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Mm, Pt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    document = Document(args.path)
    for section in document.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(25.4)
        section.bottom_margin = Mm(25.4)
        section.left_margin = Mm(25.4)
        section.right_margin = Mm(25.4)

    for paragraph in document.paragraphs:
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.0
        for run in paragraph.runs:
            run.font.name = "Times New Roman"
            run._element.get_or_add_rPr().get_or_add_rFonts().set(
                qn("w:eastAsia"), "Times New Roman"
            )
            run.font.size = Pt(12)

    document.core_properties.author = "Akshay Sharma; Lalji Prasad"
    document.core_properties.last_modified_by = "Akshay Sharma"
    document.save(args.path)


if __name__ == "__main__":
    main()
