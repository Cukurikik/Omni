import asyncio
import json
import logging
from typing import Dict, Any

from omni_autoscraper_engine import OmniAutoscraperEngine
from omni_pyprobml_engine import OmniPyProbMLEngine
from omni_serpent_ai_engine import OmniSerpentAIEngine
from omni_coreml_models_engine import OmniCoreMLModelsEngine
from omni_fun_rec_engine import OmniFunRecEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch7Diagnostics")

async def run_diagnostics():
    engines = {
        "AutoScraper": OmniAutoscraperEngine(),
        "PyProbML": OmniPyProbMLEngine(),
        "SerpentAI": OmniSerpentAIEngine(),
        "CoreMLModels": OmniCoreMLModelsEngine(),
        "FunRec": OmniFunRecEngine()
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
        
    print("\n--- Semester 8 Batch 7 Diagnostics Summary ---")
    print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(run_diagnostics())
