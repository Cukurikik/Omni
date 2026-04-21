# ===========================================================================
# OMNI COMPUTE LAYER — Python Core Package Initializer
# ===========================================================================
# Auto-generated barrel export for all 224 OMNI Compute engines.
# This file makes `src/compute/python_core` a proper Python package,
# enabling `from compute.python_core import OmniXxxEngine` imports.
# ===========================================================================

"""
OMNI Compute Layer — Central Python Package.

This package contains 224+ production-grade compute engines spanning:
  - Machine Learning (CV, NLP, RL, RecSys, AutoML)
  - Speech & Audio Processing
  - Computer Vision & Object Detection
  - Generative AI (Diffusion, GAN, TTS, LLM)
  - MLOps & Distributed Training
  - Data Science & Statistical Computing

All engines follow OMNI Blueprint standards:
  - Monadic error handling (Result pattern)
  - Type hints on all public APIs
  - Docstrings on every class and method
  - evaluate_health() or diagnostics() for observability
"""

import importlib
import os
import re
import logging
from typing import Dict, Any, Optional, Type

logger = logging.getLogger("omni.compute")

# ---------------------------------------------------------------------------
# Dynamic Engine Discovery & Lazy Loading
# ---------------------------------------------------------------------------

_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
_ENGINE_PATTERN = re.compile(r"^omni_[\w]+_engine\.py$")
_CLASS_PATTERN = re.compile(r"class\s+(Omni\w+Engine)\b")

# Registry of discovered module names (populated at import time)
_DISCOVERED_MODULES: list = []

# Cache of loaded classes (populated on first access)
_LOADED_CLASSES: Dict[str, Type] = {}


def _discover_engines() -> list:
    """Scan this directory for all omni_*_engine.py files."""
    modules = []
    for filename in sorted(os.listdir(_ENGINE_DIR)):
        if _ENGINE_PATTERN.match(filename):
            module_name = filename[:-3]  # strip .py
            modules.append(module_name)
    return modules


def get_engine_class(module_name: str) -> Optional[Type]:
    """
    Lazily import and return the main Engine class from a module.

    Args:
        module_name: The module name without .py extension.

    Returns:
        The main Omni*Engine class, or None if not found.
    """
    if module_name in _LOADED_CLASSES:
        return _LOADED_CLASSES[module_name]

    try:
        mod = importlib.import_module(f".{module_name}", package=__name__)
        # Find the main engine class
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name, None)
            if (isinstance(attr, type)
                    and attr_name.startswith("Omni")
                    and attr_name.endswith("Engine")):
                _LOADED_CLASSES[module_name] = attr
                return attr
    except Exception as e:
        logger.debug(f"Failed to load {module_name}: {e}")
    return None


def list_all_engines() -> list:
    """Return a sorted list of all discovered engine module names."""
    return list(_DISCOVERED_MODULES)


def get_engine_count() -> int:
    """Return the total number of discovered compute engines."""
    return len(_DISCOVERED_MODULES)


def instantiate_engine(module_name: str, **kwargs: Any) -> Optional[Any]:
    """
    Lazily import, instantiate, and return an engine instance.

    Args:
        module_name: The engine module name (e.g., 'omni_xlnet_autoregressive_engine').
        **kwargs: Arguments passed to the engine constructor.

    Returns:
        An engine instance, or None on failure.
    """
    cls = get_engine_class(module_name)
    if cls is None:
        return None
    try:
        return cls(**kwargs)
    except Exception as e:
        logger.warning(f"Failed to instantiate {module_name}: {e}")
        return None


# Discover all engines at package import time (lightweight — no imports)
_DISCOVERED_MODULES = _discover_engines()

# Expose count for quick access
ENGINE_COUNT = len(_DISCOVERED_MODULES)

__all__ = [
    "list_all_engines",
    "get_engine_class",
    "get_engine_count",
    "instantiate_engine",
    "ENGINE_COUNT",
]
