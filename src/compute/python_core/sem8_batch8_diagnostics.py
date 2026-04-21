import asyncio
import json
import logging
from typing import Dict, Any

from omni_feast_engine import OmniFeastEngine
from omni_autoclaude_engine import OmniAutoclaudeEngine
from omni_vespa_engine import OmniVespaEngine
from omni_flyte_engine import OmniFlyteEngine
from omni_multimodal_ml_engine import OmniMultimodalMLEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch8Diagnostics")

async def run_diagnostics():
    engines = {
        "Feast": OmniFeastEngine(),
        "AutoClaude": OmniAutoclaudeEngine(),
        "Vespa": OmniVespaEngine(),
        "Flyte": OmniFlyteEngine(),
        "MultimodalML": OmniMultimodalMLEngine()
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
        
    print("\n--- Semester 8 Batch 8 Diagnostics Summary ---")
    print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(run_diagnostics())
