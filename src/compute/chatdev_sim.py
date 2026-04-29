from omni.core import Result, Ok, Err

def sim_chatdev(agents: list) -> Result[str, Exception]:
    if not agents:
        return Err(ValueError("No agents"))
    return Ok("Simulated")
