import math

class ColorEmotionError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self):
        if not self.is_ok():
            raise self.error
        return self.value

# OMNI Engine: feeling-blue
# Maps emotional connotation constraints from normalized color contexts (RGB geometry).
class FeelingBlueColorEngine:
    def __init__(self, context_smoothing: float = 0.2):
        self.smoothing = context_smoothing

    def evaluate_rgb_emotion_distance(self, r: int, g: int, b: int) -> Result:
        try:
            if not (0 <= r <= 255) or not (0 <= g <= 255) or not (0 <= b <= 255):
                return Result(error=ColorEmotionError("RGB matrices exceeded physical 8-bit color dimensions"))

            # Calculate "blue-ness" context mapping vs brightness
            brightness = (r + g + b) / (3.0 * 255.0)
            
            blueness = b / max((r + g + b), 1)

            # High blueness + low brightness = high melancholic emotion score
            melancholy_score = blueness * (1.0 - brightness) + self.smoothing

            is_melancholic = melancholy_score > 0.6

            return Result(value={
                "melancholy_score": min(melancholy_score, 1.0),
                "is_melancholic": is_melancholic,
                "brightness": brightness
            })

        except Exception as e:
            return Result(error=ColorEmotionError(f"Emotion geometry collapsed: {str(e)}"))
