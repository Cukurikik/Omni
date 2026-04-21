import asyncio
import json
import logging
from typing import Dict, Any

from omni_dowhy_causal_engine import OmniDoWhyCausalEngine
from omni_ml_interview_evaluator_engine import OmniMLInterviewEvaluatorEngine
from omni_cortex_model_serving_engine import OmniCortexModelServingEngine
from omni_bertviz_attention_engine import OmniBertVizAttentionEngine
from omni_tensorboardx_logger_engine import OmniTensorboardXLoggerEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sem8Batch2Diagnostics")

async def run_diagnostics():
    engines = {
        "DoWhyCausal": OmniDoWhyCausalEngine(),
        "MLInterviewEval": OmniMLInterviewEvaluatorEngine(),
        "CortexServing": OmniCortexModelServingEngine(),
        "BertVizAttention": OmniBertVizAttentionEngine(),
        "TensorboardXLogger": OmniTensorboardXLoggerEngine()
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
        
    print("\n--- Semester 8 Batch 2 Diagnostics Summary ---")
    print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(run_diagnostics())
