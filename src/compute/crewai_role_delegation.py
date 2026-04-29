class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def delegate(task, crew):
    if not task: return Result(error="err")
    return Result(value="delegated")
