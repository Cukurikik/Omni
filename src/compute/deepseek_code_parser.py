class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def parse_code_snippet(code: str) -> Result:
    if not code:
        return Result(error="Code snippet is empty")
    return Result(value={"ast_nodes": len(code.split())})
