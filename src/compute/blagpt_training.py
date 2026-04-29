from omni.core import Result, Ok, Err

def train_blagpt(epochs: int) -> Result[bool, Exception]:
    if epochs <= 0:
        return Err(ValueError("Epochs must be > 0"))
    return Ok(True)
