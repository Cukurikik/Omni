class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def temporal_attn(x):
    if x is None: return Result(error="err")
    return Result(value="out")
