from omni.core import Result, Ok, Err

class CaptionGenerator:
    def generate(self, image_tensor) -> Result[str, TypeError]:
        if image_tensor is None:
            return Err(TypeError("Null image tensor"))
        return Ok("A highly detailed caption describing the image.")
