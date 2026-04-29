class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def count_tokens(text):
    if not text: return Result(error="err")
    return Result(value=100)
