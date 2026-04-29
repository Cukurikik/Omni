class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def ddim_step(latents, t):
    if latents is None: return Result(error="No latents")
    return Result(value="NextLatents")
