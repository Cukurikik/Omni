import asyncio
import json
import logging
from typing import Dict, Any

from omni_deepmind_lab_engine import OmniDeepmindLabEngine
from omni_python_ml_book_engine import OmniPythonMLBookEngine
from omni_ml_specialization_engine import OmniMLSpecializationEngine
from omni_background_matting_v2_engine import OmniBackgroundMattingV2Engine
from omni_guess_js_engine import OmniGuessJSEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch6Diagnostics")

async def run_diagnostics():
    engines = {
        "DeepMindLab": OmniDeepmindLabEngine(),
        "PythonMLBook": OmniPythonMLBookEngine(),
        "MLSpecialization": OmniMLSpecializationEngine(),
        "BackgroundMattingV2": OmniBackgroundMattingV2Engine(),
        "GuessJS": OmniGuessJSEngine()
    }
    
    results = {}
    
    for name, engine in engines.items():
        logger.info(f"Initializing {name}...")
        init_res = await engine.initialize()
        
        diag = engine.diagnostics()
        
        results[name] = {
            "initialization": init_res,
            "diagnostics": diag,
            "is_healthy": diag.get("status") == "active"
        }
        
    print("\n--- Semester 8 Batch 6 Diagnostics Summary ---")
    print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(run_diagnostics())
