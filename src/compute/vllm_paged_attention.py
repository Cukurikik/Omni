class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def paged_attention(query, key_cache, value_cache, block_tables) -> Result:
    if not block_tables:
        return Result(error="Block tables empty")
    return Result(value="Attention output")
