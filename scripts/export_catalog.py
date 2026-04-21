#!/usr/bin/env python3
"""
OMNI Engine Catalog Export Script.

Scans all engine directories and exports a comprehensive JSON catalog
suitable for LSP, CLI, and dashboard consumption.

Usage:
    python scripts/export_catalog.py
    python scripts/export_catalog.py --output docs/api/engine_catalog.json
"""

import argparse
import json
import os
import re
import sys
import time
from typing import Dict, Any, List

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

SCAN_DIRS = {
    "compute": os.path.join(ROOT_DIR, "src", "compute", "python_core"),
    "ui": os.path.join(ROOT_DIR, "src", "ui", "ts_core"),
    "system": os.path.join(ROOT_DIR, "src", "system"),
    "network": os.path.join(ROOT_DIR, "src", "network"),
    "bridge": os.path.join(ROOT_DIR, "src", "bridge"),
}

PATTERNS = {
    ".py": re.compile(r"^omni_[\w]+_engine\.py$"),
    ".ts": re.compile(r"^omni_[\w]+_engine\.ts$"),
    ".rs": re.compile(r"^omni_[\w]+_engine\.rs$"),
    ".go": re.compile(r"[\w]+_engine\.go$"),
}


def scan_directory(directory: str, layer: str) -> List[Dict[str, Any]]:
    """Scan a directory for engine files."""
    engines: List[Dict[str, Any]] = []
    if not os.path.isdir(directory):
        return engines

    for filename in sorted(os.listdir(directory)):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue

        ext = os.path.splitext(filename)[1]
        pattern = PATTERNS.get(ext)
        if pattern and pattern.match(filename):
            stat = os.stat(filepath)
            engines.append({
                "name": filename,
                "module": os.path.splitext(filename)[0],
                "layer": layer,
                "language": {".py": "Python", ".ts": "TypeScript", ".rs": "Rust", ".go": "Go"}.get(ext, "Unknown"),
                "size_bytes": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 1),
                "path": filepath,
            })
    return engines


def main() -> None:
    """Export the complete engine catalog."""
    parser = argparse.ArgumentParser(description="OMNI Engine Catalog Export")
    parser.add_argument("--output", default=os.path.join(ROOT_DIR, "docs", "api", "engine_catalog.json"))
    args = parser.parse_args()

    start = time.time()

    catalog: Dict[str, Any] = {
        "framework": "OMNI",
        "version": "5.0.0-semester5",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "layers": {},
        "summary": {},
    }

    total = 0
    for layer, directory in SCAN_DIRS.items():
        engines = scan_directory(directory, layer)
        catalog["layers"][layer] = {
            "count": len(engines),
            "engines": engines,
        }
        total += len(engines)

    catalog["summary"] = {
        "total_engines": total,
        "scan_time_ms": round((time.time() - start) * 1000, 1),
        "layers": {k: v["count"] for k, v in catalog["layers"].items()},
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, default=str)

    print(f"✅ Catalog exported to {args.output}")
    print(f"   Total engines: {total}")
    for layer, data in catalog["layers"].items():
        print(f"   {layer}: {data['count']} engines")


if __name__ == "__main__":
    main()
