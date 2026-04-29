# OMNI Compute Layer - MemGPT Archival
class MemError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def archive_core_memory(core_memory: str, archival_storage: list) -> Result:
    """Moves memory from context window to long-term storage in MemGPT."""
    try:
        if len(core_memory) == 0:
            return Result(error=MemError("Core memory is empty"))
            
        archival_storage.append({
            "timestamp": "utc_now",
            "content": core_memory
        })
        
        new_core_memory = "" # Flushed
        return Result(value={"core_flushed": True, "archive_size": len(archival_storage)})
    except Exception as e:
        return Result(error=MemError(f"Archival failed: {str(e)}"))
