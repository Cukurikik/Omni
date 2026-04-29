class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def quantize_q4(weights):
    if weights is None: return Result(error="No weights")
    return Result(value="Q4_K_M")
