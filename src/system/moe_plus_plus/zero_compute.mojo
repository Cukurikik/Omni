from omni.core import Result, Ok, Err

fn process_zero_expert(tensor_id: Int) -> Result[Int, String]:
    if tensor_id < 0:
        return Err("Invalid tensor ID")
    return Ok(tensor_id * 2)
