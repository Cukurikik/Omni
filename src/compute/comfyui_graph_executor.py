class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def execute_graph(nodes):
    if not nodes: return Result(error="Empty graph")
    return Result(value="Executed")
