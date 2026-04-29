from omni.core import Result, Ok, Err

def uot_plan(state: dict) -> Result[str, Exception]:
    if not state:
        return Err(ValueError("State missing"))
    return Ok("optimal_path")
