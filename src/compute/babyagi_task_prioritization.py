class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def prioritize(tasks):
    if not tasks: return Result(error="err")
    return Result(value=tasks)
