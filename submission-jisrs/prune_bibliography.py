#!/usr/bin/env python3
"""Retain only bibliography entries cited by the JISRS manuscript."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "paper-jisrs" / "main.tex"
BIB = ROOT / "paper-jisrs" / "references.bib"


def parse_entries(text: str) -> dict[str, str]:
    starts = list(re.finditer(r"(?m)^@\w+\{([^,]+),", text))
    entries: dict[str, str] = {}
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        entries[match.group(1)] = text[match.start() : end].strip()
    return entries


def main() -> None:
    source = MAIN.read_text(encoding="utf-8")
    cited: set[str] = set()
    for match in re.finditer(r"\\cite[pt]?\{([^}]+)\}", source):
        cited.update(key.strip() for key in match.group(1).split(","))

    entries = parse_entries(BIB.read_text(encoding="utf-8"))
    missing = sorted(cited - entries.keys())
    if missing:
        raise SystemExit(f"Missing bibliography entries: {missing}")

    retained = "\n\n".join(entries[key] for key in sorted(cited)) + "\n"
    BIB.write_text(retained, encoding="utf-8")
    print(f"Retained {len(cited)} cited entries; removed {len(entries) - len(cited)}")


if __name__ == "__main__":
    main()
