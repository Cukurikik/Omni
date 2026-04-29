class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def parse_tool_call(xml_str):
    if not xml_str: return Result(error="err")
    return Result(value="tool")
