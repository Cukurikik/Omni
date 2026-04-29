# Omni LLM4Regression Engine
# Ref: robertvacareanu/llm4regression
from typing import List, Tuple, Dict
import math

def format_regression_prompt(examples: List[Tuple[float, float]], target_x: float) -> str:
    """Format numerical examples as an in-context learning prompt for an LLM."""
    prompt = "Given the following numerical sequence mappings, predict the output for the target input.\n"
    for x, y in examples:
        prompt += f"Input: {round(x, 4)}, Output: {round(y, 4)}\n"
    prompt += f"Input: {round(target_x, 4)}, Output: "
    return prompt

def evaluate_regression_mse(predictions: List[float], ground_truths: List[float]) -> Dict[str, float]:
    """Calculate Mean Squared Error for synthetic LLM regression tasks."""
    if not predictions or len(predictions) != len(ground_truths):
        return {"mse": 0.0, "mae": 0.0, "r_squared": 0.0}
        
    mse = sum((p - g)**2 for p, g in zip(predictions, ground_truths)) / len(predictions)
    mae = sum(abs(p - g) for p, g in zip(predictions, ground_truths)) / len(predictions)
    
    mean_g = sum(ground_truths) / len(ground_truths)
    ss_tot = sum((g - mean_g)**2 for g in ground_truths)
    ss_res = sum((g - p)**2 for p, g in zip(predictions, ground_truths))
    
    r_squared = 1.0 - (ss_res / max(ss_tot, 1e-8))
    
    return {
        "mse": round(mse, 4),
        "mae": round(mae, 4),
        "r_squared": round(r_squared, 4)
    }
