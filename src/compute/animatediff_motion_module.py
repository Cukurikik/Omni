class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def apply_motion(latents):
    if latents is None: return Result(error="None")
    return Result(value="MotionLatents")
