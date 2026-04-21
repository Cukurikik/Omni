import asyncio
import json
import logging
from typing import Dict, Any

from omni_librephotos_gallery_engine import OmniLibrePhotosGalleryEngine
from omni_ml_yearning_strategy_engine import OmniMLYearningStrategyEngine
from omni_stanza_linguistics_engine import OmniStanzaLinguisticsEngine
from omni_featuretools_engineering_engine import OmniFeaturetoolsEngineeringEngine
from omni_deeplearning_algorithms_engine import OmniDeepLearningAlgorithmsEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch3Diagnostics")

async def run_diagnostics():
    engines = {
        "LibrePhotos": OmniLibrePhotosGalleryEngine(),
        "MLYearning": OmniMLYearningStrategyEngine(),
        "StanzaLinguistics": OmniStanzaLinguisticsEngine(),
        "FeaturetoolsDFS": OmniFeaturetoolsEngineeringEngine(),
        "DeepLearningCore": OmniDeepLearningAlgorithmsEngine()
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
        
    print("\n--- Semester 8 Batch 3 Diagnostics Summary ---")
    print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(run_diagnostics())
