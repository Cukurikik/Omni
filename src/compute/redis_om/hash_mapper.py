from omni.core import Result, Ok, Err

class HashMapper:
    def map_to_hash(self, obj: dict) -> Result[dict, Exception]:
        if not isinstance(obj, dict):
            return Err(TypeError("Object must be a dictionary"))
        return Ok({k: str(v) for k, v in obj.items()})
