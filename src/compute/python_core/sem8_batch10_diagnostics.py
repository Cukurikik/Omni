"""
Semester 8 Batch 10 — Diagnostics Runner

Initializes all 5 Batch 10 engines and reports health status.
"""

import asyncio
import json
import logging

from omni_snorkel_engine import OmniSnorkelEngine
from omni_gorgonia_engine import OmniGorgoniaEngine
from omni_river_engine import OmniRiverEngine
from omni_causalml_engine import OmniCausalmlEngine
from omni_nn_svg_engine import OmniNnSvgEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch10Diagnostics")


async def run_diagnostics() -> None:
    """Initializes each engine and prints diagnostics."""
    engines = {
        "Snorkel": OmniSnorkelEngine(),
        "Gorgonia": OmniGorgoniaEngine(),
        "River": OmniRiverEngine(),
        "CausalML": OmniCausalmlEngine(),
        "NN-SVG": OmniNnSvgEngine(),
    }

    results = {}
    for name, engine in engines.items():
        logger.info(f"Initializing {name}...")
        init_res = await engine.initialize()
        diag = engine.diagnostics()
        results[name] = {
            "initialization": init_res,
            "diagnostics": diag,
            "is_healthy": diag.get("status") == "active",
        }

    print("\n--- Semester 8 Batch 10 Diagnostics Summary ---")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(run_diagnostics())
