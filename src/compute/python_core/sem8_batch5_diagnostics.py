import asyncio
import json
import logging
from typing import Dict, Any

from omni_bertopic_engine import OmniBERTopicEngine
from omni_generative_models_engine import OmniGenerativeModelsEngine
from omni_industry_ml_engine import OmniIndustryMLEngine
from omni_elements_of_math_engine import OmniElementsOfMathEngine
from omni_evidently_ai_engine import OmniEvidentlyAIEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch5Diagnostics")

async def run_diagnostics():
    engines = {
        "BERTopic": OmniBERTopicEngine(),
        "GenerativeModels": OmniGenerativeModelsEngine(),
        "IndustryML": OmniIndustryMLEngine(),
        "ElementsOfMath": OmniElementsOfMathEngine(),
        "EvidentlyAI": OmniEvidentlyAIEngine()
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
        
    print("\n--- Semester 8 Batch 5 Diagnostics Summary ---")
    print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(run_diagnostics())
