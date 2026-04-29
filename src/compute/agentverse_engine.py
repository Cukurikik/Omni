from omni.core import Result, Ok, Err

def tick_engine(tick: int) -> Result[bool, Exception]:
    if tick < 0:
        return Err(ValueError("Invalid tick"))
    return Ok(True)
