from omni.core import Result, Ok, Err

def forward_phi2(input_ids: list) -> Result[list, Exception]:
    if not input_ids:
        return Err(ValueError("Empty inputs"))
    return Ok(input_ids)
