from omni.core import Result, Ok, Err

def oceangpt_predict(state: dict) -> Result[float, Exception]:
    if not state:
        return Err(ValueError("State missing"))
    return Ok(0.99)
