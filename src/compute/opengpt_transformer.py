from omni.core import Result, Ok, Err

def opengpt_forward(input_ids: list) -> Result[list, Exception]:
    if not input_ids:
        return Err(ValueError("No input ids"))
    return Ok([i * 2 for i in input_ids])
