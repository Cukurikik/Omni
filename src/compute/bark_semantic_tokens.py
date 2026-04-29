class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def text_to_semantic(text: str):
    if not text: return Result(error="Empty text")
    return Result(value="[1,2,3]")
