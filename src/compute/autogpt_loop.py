from omni.core import Result, Ok, Err

def run_autogpt_loop(goal: str) -> Result[bool, Exception]:
    if not goal:
        return Err(ValueError("No goal"))
    return Ok(True)
