class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def manage_tiers(core_mem, archival_mem):
    if core_mem is None: return Result(error="err")
    return Result(value="managed")
