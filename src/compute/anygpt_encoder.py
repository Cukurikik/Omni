from omni.core import Result, Ok, Err

def encode_audio(pcm_data: list) -> Result[list, Exception]:
    if not pcm_data:
        return Err(ValueError("No pcm data"))
    return Ok([p * 0.1 for p in pcm_data])
