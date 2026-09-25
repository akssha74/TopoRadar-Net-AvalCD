#!/usr/bin/env python3
"""Normalize the separate identified JISRS title-page DOCX."""

from pathlib import Path
import argparse

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    document = Document(args.path)
    for section in document.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(18)
        section.bottom_margin = Mm(18)
        section.left_margin = Mm(20)
        section.right_margin = Mm(20)

    for paragraph_index, paragraph in enumerate(document.paragraphs):
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(1)
        paragraph.paragraph_format.line_spacing = 1.0

        if paragraph_index <= 3:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_after = Pt(2)
        if paragraph_index == 0:
            paragraph.paragraph_format.space_after = Pt(5)
        elif paragraph_index == 4:
            paragraph.paragraph_format.space_before = Pt(5)
            paragraph.paragraph_format.space_after = Pt(5)

        is_heading = paragraph.style.name == "Heading 1"
        if is_heading:
            paragraph.paragraph_format.space_before = Pt(7)
            paragraph.paragraph_format.space_after = Pt(2)
            paragraph.paragraph_format.keep_with_next = True
        if paragraph.text.strip() == "Declarations":
            paragraph.paragraph_format.space_before = Pt(8)
            paragraph.paragraph_format.space_after = Pt(3)

        for run in paragraph.runs:
            run.font.name = "Times New Roman"
            run._element.get_or_add_rPr().get_or_add_rFonts().set(
                qn("w:eastAsia"), "Times New Roman"
            )
            run.font.size = Pt(12)
            if is_heading:
                run.font.bold = True
                run.font.color.rgb = RGBColor(0, 0, 0)
            if paragraph_index == 0:
                run.font.size = Pt(14)
                run.font.bold = True
            elif paragraph_index == 1:
                run.font.bold = True
            if paragraph.text.strip() == "Declarations":
                run.font.size = Pt(13)

    document.core_properties.author = "Akshay Sharma; Lalji Prasad"
    document.core_properties.last_modified_by = "Akshay Sharma"
    document.save(args.path)


if __name__ == "__main__":
    main()
