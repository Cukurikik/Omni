from omni.core import Result, Ok, Err

def execute_prefect_flow(flow_name: str) -> Result[bool, Exception]:
    if not flow_name:
        return Err(ValueError("Missing flow name"))
    return Ok(True)
