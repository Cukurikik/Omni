from omni.core import Result, Ok, Err

class RDDProcessor:
    def map_partitions(self, data: list) -> Result[list, Exception]:
        try:
            res = [x * 2 for x in data]
            return Ok(res)
        except Exception as e:
            return Err(e)
