class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def filter_payload(payload, query):
    if not payload: return Result(error="err")
    return Result(value="filtered")
