from omni.core import Result, Ok, Err

class ActorPool:
    def __init__(self, size: int):
        self.size = size
        self.actors = []

    def spawn(self) -> Result[bool, Exception]:
        if len(self.actors) >= self.size:
            return Err(Exception("Pool exhausted"))
        self.actors.append("actor_ref")
        return Ok(True)
