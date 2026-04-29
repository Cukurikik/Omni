from omni.core import Result, Ok, Err

def evolve_context(base_context: str) -> Result[str, Exception]:
    if not base_context:
        return Err(ValueError("Base context missing"))
    return Ok(base_context + " evolved")
