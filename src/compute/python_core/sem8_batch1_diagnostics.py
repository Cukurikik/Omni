import asyncio
import json
import logging
from typing import Dict, Any

from omni_vowpal_wabbit_engine import OmniVowpalWabbitEngine
from omni_mage_data_pipeline_engine import OmniMageDataPipelineEngine
from omni_embedded_toolchain_engine import OmniEmbeddedToolchainEngine
from omni_bitsandbytes_optimizer_engine import OmniBitsAndBytesOptimizerEngine
from omni_boxmot_engine import OmniBoxMOTEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch1Diagnostics")

async def run_diagnostics():
    engines = {
        "VowpalWabbit": OmniVowpalWabbitEngine({"learning_rate": 0.01}),
        "MageDataPipeline": OmniMageDataPipelineEngine({"project_path": "/omni/data/pipes"}),
        "EmbeddedToolchain": OmniEmbeddedToolchainEngine({"toolchain_path": "/opt/omni/embedded_sdk"}),
        "BitsAndBytesOptimizer": OmniBitsAndBytesOptimizerEngine({"optimizer_type": "Adam8bit"}),
        "BoxMOTTracker": OmniBoxMOTEngine({"tracker": "BoTSORT"})
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
        
    print("\n--- Semester 8 Batch 1 Diagnostics Summary ---")
    print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(run_diagnostics())
