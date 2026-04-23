import datetime
import hashlib
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMerkleTreeIntegrityEngine:
    """
    OmniMerkleTreeIntegrityEngine
    Batch: 29 (Semester 10)
    
    A zero-mock cryptographic systems engine generating hierarchical 
    binary verification trees to enforce topological immutable constraints.
    """
    
    def __init__(self, raw_blocks: List[str]):
        """
        :param raw_blocks: The initial layer-0 scalar payload arrays.
        """
        self.raw_blocks = raw_blocks
        self.tree_levels: List[List[str]] = []
        self.root_hash: Optional[str] = None

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "block_count": len(self.raw_blocks),
            "tree_depth": len(self.tree_levels),
            "root_hash": self.root_hash,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def _hash_node(self, payload: str) -> str:
        """Deterministic structural cryptographic digest (SHA-256)."""
        m = hashlib.sha256()
        m.update(payload.encode('utf-8'))
        return m.hexdigest()

    def _hash_pair(self, left: str, right: str) -> str:
        """Aggregates logical pairs using deterministic concatenation."""
        return self._hash_node(left + right)

    def build_tree(self) -> Result[str, Exception]:
        """
        Computes the entire mathematical topological map from leaf to root.
        If leaves are odd, duplicates the final scalar tail for boundary padding.
        """
        try:
            if not isinstance(self.raw_blocks, list):
                return Err(TypeError("Raw blocks must be a logical sequence sequence"))
                
            if not self.raw_blocks:
                return Err(ValueError("Cannot construct Merkle map from empty dataset"))
                
            # Base Layer (L0)
            current_level = [self._hash_node(str(block)) for block in self.raw_blocks]
            self.tree_levels = [current_level]
            
            # Recursive pairing progression
            while len(current_level) > 1:
                next_level = []
                for i in range(0, len(current_level), 2):
                    left = current_level[i]
                    # Boundary duplicate wrap padding if odd parity
                    right = current_level[i + 1] if i + 1 < len(current_level) else left
                    
                    parent_hash = self._hash_pair(left, right)
                    next_level.append(parent_hash)
                    
                self.tree_levels.append(next_level)
                current_level = next_level
                
            self.root_hash = self.tree_levels[-1][0]
            return Ok(self.root_hash)
            
        except Exception as e:
            return Err(e)

    def generate_proof(self, target_block_index: int) -> Result[List[Dict[str, str]], Exception]:
        """
        Generates the sparse mathematical trace required to perform a decoupled root verification.
        Returns a list of sibling hashes.
        """
        try:
            if self.root_hash is None:
                return Err(RuntimeError("Tree not generated. Compile the grid space first."))
                
            if target_block_index < 0 or target_block_index >= len(self.raw_blocks):
                return Err(IndexError("Target index boundary variance violation"))
                
            proof = []
            current_index = target_block_index
            
            # Walk up the topological frame bounds
            for level_hashes in self.tree_levels[:-1]:
                # Find sibling structural offset
                is_left_node = (current_index % 2 == 0)
                
                if is_left_node:
                    sibling_index = current_index + 1
                    # Odd parity bounds checking
                    if sibling_index >= len(level_hashes):
                        sibling_index = current_index
                    sibling_hash = level_hashes[sibling_index]
                    proof.append({"position": "right", "hash": sibling_hash})
                else:
                    sibling_index = current_index - 1
                    sibling_hash = level_hashes[sibling_index]
                    proof.append({"position": "left", "hash": sibling_hash})
                    
                current_index //= 2
                
            return Ok(proof)
            
        except Exception as e:
            return Err(e)

    @classmethod
    def verify_proof(cls, target_block: str, proof: List[Dict[str, str]], root_hash: str) -> bool:
        """
        Isolated deterministic function for enforcing trace matching externally.
        Returns pure bool constraint validation.
        """
        m = hashlib.sha256()
        m.update(str(target_block).encode('utf-8'))
        current_hash = m.hexdigest()
        
        for p in proof:
            sibling = p["hash"]
            m_pair = hashlib.sha256()
            if p["position"] == "left":
                m_pair.update((sibling + current_hash).encode('utf-8'))
            else:
                m_pair.update((current_hash + sibling).encode('utf-8'))
                
            current_hash = m_pair.hexdigest()
            
        return current_hash == root_hash
