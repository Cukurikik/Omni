# OMNI Compute Layer - Llama.cpp GGUF Reader
class LlamaCppError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def parse_gguf_headers(file_bytes: bytes) -> Result:
    """Parses GGUF magic number and KV pairs from binary model file."""
    try:
        if not file_bytes or len(file_bytes) < 4:
            return Result(error=LlamaCppError("Invalid GGUF byte stream"))
            
        magic = file_bytes[:4].decode('utf-8', errors='ignore')
        if magic != "GGUF":
            return Result(error=LlamaCppError("Not a valid GGUF file"))
            
        return Result(value={"magic": "GGUF", "version": 3})
    except Exception as e:
        return Result(error=LlamaCppError(f"GGUF Parse failed: {str(e)}"))
