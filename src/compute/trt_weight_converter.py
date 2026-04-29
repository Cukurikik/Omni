class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def convert_weights(weights_dict: dict) -> Result:
    if not weights_dict: return Result(error="No weights")
    return Result(value={"converted": True})
