#!/usr/bin/env python3
"""Build the editable JISRS LaTeX source package deterministically."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper-jisrs"
SUBMISSION = ROOT / "submission-jisrs"
OUTPUT = SUBMISSION / "source_package.zip"

FILES = [
    "main.tex",
    "supplementary_information.tex",
    "references.bib",
    "sn-jnl.cls",
    "sn-apacite.bst",
    "README.md",
    "plot_jisrs_figures.py",
    "figures/Fig1.pdf",
    "figures/Fig1.png",
    "figures/Fig1.eps",
    "figures/Fig2.pdf",
    "figures/Fig2.png",
    "figures/Fig2.eps",
]

EXTERNAL_FILES = [
    (
        ROOT / "experiments" / "derived" / "results" / "event_sensor_manifest.json",
        Path("evidence/event_sensor_manifest.json"),
    )
]


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        package_root = Path(temp) / "TopoRadar-Net-JISRS"
        for relative in FILES:
            source = PAPER / relative
            destination = package_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        for source, relative in EXTERNAL_FILES:
            destination = package_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(package_root.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(package_root.parent))

    print(f"Built {OUTPUT} with {len(FILES) + len(EXTERNAL_FILES)} files")


if __name__ == "__main__":
    main()
