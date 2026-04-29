from omni.core import Result, Ok, Err

def process_sops(sop_list: list) -> Result[bool, Exception]:
    if not sop_list:
        return Err(ValueError("Empty SOP list"))
    return Ok(True)
