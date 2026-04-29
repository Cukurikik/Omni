class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def execute_agent(agent, tools):
    if not agent: return Result(error="err")
    return Result(value="done")
