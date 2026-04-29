class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def run_loop(state):
    if state is None: return Result(error="err")
    return Result(value="next_state")
