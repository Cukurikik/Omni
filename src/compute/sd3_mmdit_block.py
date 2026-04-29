class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def mmdit_forward(x, context):
    if x is None: return Result(error="Input none")
    return Result(value="Out")
