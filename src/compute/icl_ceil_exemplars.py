from omni.core import Result, Ok, Err

def select_exemplars(pool: list) -> Result[list, Exception]:
    if not pool:
        return Err(ValueError("Pool empty"))
    return Ok(pool[:2])
