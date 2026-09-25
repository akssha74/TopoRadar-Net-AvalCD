#!/usr/bin/env python3
"""Mechanical checks for the JISRS submission package."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "paper-jisrs" / "main.tex"
HIGHLIGHTS = ROOT / "submission-jisrs" / "highlights.txt"
TITLE_PAGE = ROOT / "submission-jisrs" / "title_page.tex"


def extract_braced(text: str, command: str) -> str:
    marker = f"\\{command}"
    start = text.index(marker) + len(marker)
    while start < len(text) and text[start].isspace():
        start += 1
    if text[start] != "{":
        raise ValueError(f"{command} does not use a braced argument")
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start + 1 : index]
    raise ValueError(f"unterminated {command}")


def pandoc_plain(tex: str) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "latex", "-t", "plain"],
        input=tex,
        text=True,
        check=True,
        capture_output=True,
    )
    return result.stdout


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w%]+(?:[-–][\w%]+)*\b", text, flags=re.UNICODE))


def main() -> None:
    source = MAIN.read_text(encoding="utf-8")
    source = re.sub(r"(?m)(?<!\\)%.*$", "", source)
    title_page = TITLE_PAGE.read_text(encoding="utf-8")

    abstract_tex = extract_braced(source, "abstract")
    abstract_words = count_words(pandoc_plain(abstract_tex))

    body = source.split("\\maketitle", 1)[1]
    body = body.rsplit("\\end{document}", 1)[0]
    body = re.sub(
        r"\\begin\{(?:table\*?|figure\*?)\}.*?\\end\{(?:table\*?|figure\*?)\}",
        "",
        body,
        flags=re.DOTALL,
    )
    body = re.sub(r"\\bibliography\{[^}]+\}", "", body)
    main_words = count_words(pandoc_plain(body))

    keywords = [item.strip() for item in extract_braced(source, "keywords").split(",")]
    highlights = [
        line.removeprefix("•").strip()
        for line in HIGHLIGHTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    title_headings = [
        r"\section*{Conflict of Interest}",
        r"\section*{Funding}",
        r"\section*{Author's Contribution}",
        r"\section*{Acknowledgement}",
    ]
    title_heading_positions = [
        title_page.find(heading) for heading in title_headings
    ]

    checks = {
        "main_words_le_4000": main_words <= 4000,
        "abstract_words_le_200": abstract_words <= 200,
        "keywords_4_to_6": 4 <= len(keywords) <= 6,
        "highlights_3_to_5": 3 <= len(highlights) <= 5,
        "highlights_each_le_150_chars": all(len(item) <= 150 for item in highlights),
        "highlights_without_acronyms": all(
            re.search(r"\b[A-Z]{2,}\b", item) is None for item in highlights
        ),
        "heading_depth_le_3": "\\paragraph{" not in source and "\\subparagraph{" not in source,
        "data_availability_present": "Data Availability/Supplementary Information" in source,
        "statements_declarations_absent_from_blinded_manuscript": (
            "Statements and Declarations" not in source
        ),
        "title_page_feedback_headings_present": all(
            position >= 0 for position in title_heading_positions
        ),
        "title_page_feedback_headings_ordered": title_heading_positions == sorted(
            title_heading_positions
        ),
        "title_page_conflict_statement_present": (
            "The authors declare that they have no conflict of interest." in title_page
        ),
        "title_page_funding_statement_present": (
            "No funding was received for conducting this study or preparing this manuscript."
            in title_page
        ),
        "title_page_acknowledgement_not_applicable": (
            r"\section*{Acknowledgement}" in title_page
            and "Not applicable." in title_page.split(
                r"\section*{Acknowledgement}", 1
            )[1]
        ),
        "ai_disclosure_in_method": "AI-assisted research support" in source,
    }

    print(f"Main-text words (journal counting boundary): {main_words}")
    print(f"Abstract words: {abstract_words}")
    print(f"Keywords: {len(keywords)}")
    print("Highlight lengths:", [len(item) for item in highlights])
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit(f"JISRS compliance failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
