from typing import Dict

class OmniMemGPTOS:
    """OMNI Compute Layer: MemGPT OS Memory Manager"""
    
    def __init__(self, core_limit: int = 500):
        self.core_memory = ""
        self.core_limit = core_limit
        self.archival_memory: Dict[str, str] = {}

    def edit_core_memory(self, new_text: str) -> bool:
        if len(new_text) > self.core_limit:
            return False
        self.core_memory = new_text
        return True

    def archive_push(self, key: str, text: str) -> None:
        self.archival_memory[key] = text

    def archive_search(self, query: str) -> str:
        for k, v in self.archival_memory.items():
            if query in k or query in v:
                return v
        return "No results found."
