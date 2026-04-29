class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def extract(metadata):
    if not metadata: return Result(error="err")
    return Result(value="extracted")
