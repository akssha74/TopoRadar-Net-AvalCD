#!/usr/bin/env python3
"""Acquire a frozen public OSM major-road snapshot for held-out test scenes."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


EXP_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = EXP_DIR / "external"
OUT_PATH = OUT_DIR / "osm_major_roads_20260919.json"

SCENES = {
    "Tromso_Arctic": (69.3883176, 19.0618732, 69.5362063, 19.4312453),
    "Pamir_HighMountain": (37.3271217, 71.3898698, 37.4800751, 71.5817922),
}
HIGHWAY_REGEX = "^(motorway|trunk|primary|secondary|tertiary)$"
ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
)


def fetch_scene(name: str, bbox: tuple[float, float, float, float]) -> dict:
    south, west, north, east = bbox
    query = (
        "[out:json][timeout:90];"
        f'way["highway"~"{HIGHWAY_REGEX}"]'
        f"({south},{west},{north},{east});"
        "out tags geom;"
    )
    headers = {"User-Agent": "TopoRadar-Net-research/1.0 (public-data snapshot)"}
    errors = []
    for attempt in range(4):
        for endpoint in ENDPOINTS:
            try:
                response = requests.get(
                    endpoint,
                    params={"data": query},
                    headers=headers,
                    timeout=120,
                )
                if response.status_code == 200:
                    payload = response.json()
                    return {
                        "scene": name,
                        "bbox_wgs84": list(bbox),
                        "query": query,
                        "endpoint": endpoint,
                        "osm_timestamp": payload.get("osm3s", {}).get(
                            "timestamp_osm_base"
                        ),
                        "copyright": payload.get("osm3s", {}).get("copyright"),
                        "ways": payload.get("elements", []),
                    }
                errors.append(f"{endpoint}: HTTP {response.status_code}")
            except Exception as exc:  # acquisition fallback is recorded below
                errors.append(f"{endpoint}: {type(exc).__name__}: {exc}")
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"OSM acquisition failed for {name}: {' | '.join(errors)}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenes = {name: fetch_scene(name, bbox) for name, bbox in SCENES.items()}
    payload = {
        "source": "OpenStreetMap via Overpass API",
        "license": "ODbL 1.0",
        "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
        "highway_filter": HIGHWAY_REGEX,
        "scenes": scenes,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["content_sha256_without_hash_field"] = hashlib.sha256(canonical).hexdigest()
    with open(OUT_PATH, "w") as handle:
        json.dump(payload, handle, indent=2)
    for name, scene in scenes.items():
        print(f"{name}: {len(scene['ways'])} major-road ways")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
