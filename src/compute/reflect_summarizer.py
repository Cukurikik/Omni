from omni.core import Result, Ok, Err

def summarize_experience(log: str) -> Result[str, Exception]:
    if not log:
        return Err(ValueError("Empty log"))
    return Ok("Summary generated")
