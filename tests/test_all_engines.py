#!/usr/bin/env python3
"""
OMNI Batch Unit Test Runner.

Discovers all compute engines, attempts to instantiate each one,
and runs their evaluate_health() or diagnostics() method as a
minimal unit test. Reports pass/fail for every engine.

Usage:
    python tests/test_all_engines.py
    pytest tests/test_all_engines.py -v
"""

import importlib.util
import os
import re
import sys
import pytest
from typing import List, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

ENGINE_DIR = os.path.join(ROOT_DIR, "src", "compute", "python_core")
ENGINE_FILE_PATTERN = re.compile(r"^omni_[\w]+_engine\.py$")
ENGINE_CLASS_PATTERN = re.compile(r"class\s+(Omni\w+Engine)\b")


def discover_engine_params() -> List[Tuple[str, str, str]]:
    """Discover all engine files and return (module_name, class_name, path) tuples."""
    params: List[Tuple[str, str, str]] = []
    if not os.path.isdir(ENGINE_DIR):
        return params

    for filename in sorted(os.listdir(ENGINE_DIR)):
        if not ENGINE_FILE_PATTERN.match(filename):
            continue
        filepath = os.path.join(ENGINE_DIR, filename)
        try:
            source = open(filepath, "r", encoding="utf-8").read()
            match = ENGINE_CLASS_PATTERN.search(source)
            if match:
                params.append((filename[:-3], match.group(1), filepath))
        except Exception:
            pass
    return params


ENGINE_PARAMS = discover_engine_params()


@pytest.mark.parametrize("module_name,class_name,filepath", ENGINE_PARAMS, ids=[p[0] for p in ENGINE_PARAMS])
def test_engine_import(module_name: str, class_name: str, filepath: str) -> None:
    """Test that each engine file can be imported without errors."""
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    assert spec is not None, f"Failed to create spec for {module_name}"
    assert spec.loader is not None, f"No loader for {module_name}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # Required for dataclass on Python 3.10+
    spec.loader.exec_module(mod)
    cls = getattr(mod, class_name, None)
    assert cls is not None, f"Class {class_name} not found in {module_name}"


@pytest.mark.parametrize("module_name,class_name,filepath", ENGINE_PARAMS, ids=[p[0] for p in ENGINE_PARAMS])
def test_engine_instantiate(module_name: str, class_name: str, filepath: str) -> None:
    """Test that each engine can be instantiated with no arguments."""
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # Required for dataclass on Python 3.10+
    spec.loader.exec_module(mod)
    cls = getattr(mod, class_name)
    instance = cls()
    assert instance is not None


@pytest.mark.parametrize("module_name,class_name,filepath", ENGINE_PARAMS, ids=[p[0] for p in ENGINE_PARAMS])
def test_engine_health(module_name: str, class_name: str, filepath: str) -> None:
    """Test that each engine's health check returns valid data."""
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # Required for dataclass on Python 3.10+
    spec.loader.exec_module(mod)
    cls = getattr(mod, class_name)
    instance = cls()

    if hasattr(instance, "evaluate_health"):
        result = instance.evaluate_health()
        assert isinstance(result, dict), f"evaluate_health() must return dict, got {type(result)}"
        assert "status" in result, "evaluate_health() must contain 'status' key"
    elif hasattr(instance, "diagnostics"):
        result = instance.diagnostics()
        assert isinstance(result, dict), f"diagnostics() must return dict, got {type(result)}"
    else:
        # Engine has no health method — pass silently
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-q"])
