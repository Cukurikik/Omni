from omni.core import Result, Ok, Err

def manage_memory(mem: dict) -> Result[bool, Exception]:
    if not mem:
        return Err(ValueError("No memory"))
    return Ok(True)
