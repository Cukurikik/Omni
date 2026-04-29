from omni.core import Result, Ok, Err

class AlphaRecModel:
    def predict(self, user_vector: list) -> Result[float, Exception]:
        if not user_vector:
            return Err(ValueError("User vector empty"))
        return Ok(sum(user_vector) * 0.9)
