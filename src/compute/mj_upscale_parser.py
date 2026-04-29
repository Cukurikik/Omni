class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def parse_upscale_options(msg):
    if not msg: return Result(error="No msg")
    return Result(value=["U1", "U2"])
