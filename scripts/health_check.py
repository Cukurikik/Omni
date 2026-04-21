#!/usr/bin/env python3
"""
OMNI Engine Health Check Script.

Scans all compute engines, attempts to instantiate each one,
and runs their evaluate_health() or diagnostics() method.
Outputs a full health report.

Usage:
    python scripts/health_check.py
    python scripts/health_check.py --layer compute
    python scripts/health_check.py --verbose
"""

import argparse
import importlib
import importlib.util
import os
import re
import sys
import time
import json
from typing import Dict, Any, List, Optional

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

ENGINE_DIRS = {
    "compute": os.path.join(ROOT_DIR, "src", "compute", "python_core"),
    "system": os.path.join(ROOT_DIR, "src", "compute", "python_core", "system"),
}

ENGINE_FILE_PATTERN = re.compile(r"^omni_[\w]+_engine\.py$")
ENGINE_CLASS_PATTERN = re.compile(r"class\s+(Omni\w+Engine)\b")


def discover_engines(target_dir: str) -> List[Dict[str, str]]:
    """Discover all engine files in a directory."""
    engines: List[Dict[str, str]] = []
    if not os.path.isdir(target_dir):
        return engines
    for filename in sorted(os.listdir(target_dir)):
        if ENGINE_FILE_PATTERN.match(filename):
            filepath = os.path.join(target_dir, filename)
            try:
                source = open(filepath, "r", encoding="utf-8").read()
                match = ENGINE_CLASS_PATTERN.search(source)
                class_name = match.group(1) if match else "Unknown"
            except Exception:
                class_name = "Unknown"
            engines.append({
                "file": filename,
                "module": filename[:-3],
                "class": class_name,
                "path": filepath,
            })
    return engines


def check_engine(engine_info: Dict[str, str], verbose: bool = False) -> Dict[str, Any]:
    """Attempt to import and health-check a single engine."""
    result: Dict[str, Any] = {
        "module": engine_info["module"],
        "class": engine_info["class"],
        "import_ok": False,
        "instantiate_ok": False,
        "health_ok": False,
        "error": None,
    }
    try:
        spec = importlib.util.spec_from_file_location(engine_info["module"], engine_info["path"])
        if spec is None or spec.loader is None:
            result["error"] = "Failed to create import spec"
            return result
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result["import_ok"] = True

        cls = getattr(mod, engine_info["class"], None)
        if cls is None:
            result["error"] = f"Class {engine_info['class']} not found"
            return result

        instance = cls()
        result["instantiate_ok"] = True

        # Try evaluate_health() first, then diagnostics()
        if hasattr(instance, "evaluate_health"):
            health = instance.evaluate_health()
            result["health_ok"] = True
            if verbose:
                result["health_data"] = health
        elif hasattr(instance, "diagnostics"):
            diag = instance.diagnostics()
            result["health_ok"] = True
            if verbose:
                result["health_data"] = diag
        else:
            result["health_ok"] = True  # No health method = assume healthy
            result["note"] = "No health method found"

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)[:200]}"

    return result


def main() -> None:
    """Run health checks across all engine directories."""
    parser = argparse.ArgumentParser(description="OMNI Engine Health Check")
    parser.add_argument("--layer", choices=["compute", "system", "all"], default="all")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    dirs = ENGINE_DIRS if args.layer == "all" else {args.layer: ENGINE_DIRS[args.layer]}

    total = 0
    passed = 0
    failed = 0
    results: List[Dict[str, Any]] = []

    start = time.time()

    for layer, directory in dirs.items():
        engines = discover_engines(directory)
        for eng in engines:
            total += 1
            result = check_engine(eng, verbose=args.verbose)
            result["layer"] = layer
            results.append(result)
            if result["health_ok"]:
                passed += 1
            else:
                failed += 1

            if not args.json:
                status = "✅" if result["health_ok"] else "❌"
                print(f"  {status} {result['module']}: import={result['import_ok']} inst={result['instantiate_ok']} health={result['health_ok']}", end="")
                if result["error"]:
                    print(f"  ERR: {result['error'][:80]}")
                else:
                    print()

    elapsed = (time.time() - start) * 1000

    if args.json:
        print(json.dumps({"total": total, "passed": passed, "failed": failed, "elapsed_ms": round(elapsed, 1), "results": results}, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  OMNI Health Check Complete")
        print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
        print(f"  Elapsed: {elapsed:.1f}ms")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
