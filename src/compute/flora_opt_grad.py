from omni.core import Result, Ok, Err

def flora_opt_step(gradients: list) -> Result[float, Exception]:
    if not gradients:
        return Err(ValueError("Empty gradients"))
    return Ok(0.01)
