from omni.core import Result, Ok, Err

def reason_qwq(query: str) -> Result[str, Exception]:
    if not query:
        return Err(ValueError("Empty query"))
    return Ok(query + " reasoned")
