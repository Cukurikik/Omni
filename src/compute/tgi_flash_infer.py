class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def flash_infer(x):
    if x is None: return Result(error="None input")
    return Result(value=x * 2)
