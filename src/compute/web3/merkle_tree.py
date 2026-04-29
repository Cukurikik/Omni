import hashlib
from typing import Any, List, Optional

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class MerkleTree:
    def __init__(self):
        self.leaves: List[str] = []
        self.levels: List[List[str]] = []
        
    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def build_tree(self, transactions: List[str]) -> OmniResult:
        if not transactions:
            return OmniResult.err("Cannot build Merkle tree from empty transaction list")
            
        try:
            self.leaves = [self._hash(tx) for tx in transactions]
            self.levels = [self.leaves]
            
            current_level = self.leaves
            while len(current_level) > 1:
                next_level = []
                # Process in pairs
                for i in range(0, len(current_level), 2):
                    left = current_level[i]
                    # If odd number of nodes, duplicate the last one
                    right = current_level[i + 1] if i + 1 < len(current_level) else left
                    
                    combined_hash = self._hash(left + right)
                    next_level.append(combined_hash)
                    
                self.levels.append(next_level)
                current_level = next_level
                
            return OmniResult.ok(self.get_root())
        except Exception as e:
            return OmniResult.err(f"Merkle tree construction failed: {str(e)}")

    def get_root(self) -> Optional[str]:
        if not self.levels:
            return None
        return self.levels[-1][0]
