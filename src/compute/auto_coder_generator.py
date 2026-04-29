from omni.core import Result, Ok, Err

def generate_code(spec: str) -> Result[str, Exception]:
    if not spec:
        return Err(ValueError("No spec"))
    return Ok("def generated(): pass")
