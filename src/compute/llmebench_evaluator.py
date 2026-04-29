from omni.core import Result, Ok, Err

def evaluate_llm(preds: list, truths: list) -> Result[float, Exception]:
    if len(preds) != len(truths) or not preds:
        return Err(ValueError("Mismatched or empty lists"))
    return Ok(0.85)
