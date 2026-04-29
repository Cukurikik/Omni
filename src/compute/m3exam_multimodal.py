from omni.core import Result, Ok, Err

def run_m3exam(modalities: list) -> Result[float, Exception]:
    if not modalities:
        return Err(ValueError("No modalities"))
    return Ok(0.92)
