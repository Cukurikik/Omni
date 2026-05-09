# OMNI MOTHER: PiKV Eviction Policy (LRU)
# Evicts older KV cache blocks when memory is tight

class OmniPiKVEvictionPolicy:
    def __init__(self):
        self.access_history = {} # seq_id -> timestamp
        
    def record_access(self, seq_id: str, timestamp: float):
        self.access_history[seq_id] = timestamp
        
    def find_eviction_target(self) -> str:
        if not self.access_history:
            return None
        # Return oldest accessed seq_id
        target = min(self.access_history, key=self.access_history.get)
        del self.access_history[target]
        return target
