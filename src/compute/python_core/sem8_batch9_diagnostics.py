import asyncio
import json
import logging
from typing import Dict, Any

from omni_smile_engine import OmniSmileEngine
from omni_pytorch_metric_learning_engine import OmniPytorchMetricLearningEngine
from omni_lihang_stat_learning_engine import OmniLihangStatLearningEngine
from omni_tensorpack_engine import OmniTensorpackEngine
from omni_swarms_engine import OmniSwarmsEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch9Diagnostics")

async def run_diagnostics():
    engines = {
        "Smile": OmniSmileEngine(),
        "PyTorchMetricLearning": OmniPytorchMetricLearningEngine(),
        "Lihang": OmniLihangStatLearningEngine(),
        "Tensorpack": OmniTensorpackEngine(),
        "Swarms": OmniSwarmsEngine()
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
        
    print("\n--- Semester 8 Batch 9 Diagnostics Summary ---")
    print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(run_diagnostics())
