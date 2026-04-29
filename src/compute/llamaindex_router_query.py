class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def route_query(query, indexes):
    if not query: return Result(error="err")
    return Result(value=indexes[0])
