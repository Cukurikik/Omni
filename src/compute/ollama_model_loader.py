class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def load_model(path: str) -> Result:
    if not path: return Result(error="Empty path")
    return Result(value="ModelLoaded")
