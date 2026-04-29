from omni.core import Result, Ok, Err

class CoTInterleaver:
    def interleave(self, thought: str, retrieval: str) -> Result[str, ValueError]:
        if not thought or not retrieval:
            return Err(ValueError("Thought and retrieval must be valid strings"))
        return Ok(f"Thought: {thought}\nContext: {retrieval}")
