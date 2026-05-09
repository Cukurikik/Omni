"""
moe_sglang_mini_router.py — Compute / Inference
Layer: Compute / AI — Mini-SGLang Fast Prompt Routing

Inspired by `moham94/mini-sglang`. 
To serve MoE models efficiently, we integrate SGLang's RadixAttention to share 
KV caches across identical prompt prefixes. This module handles the mini-SGLang
backend state, allowing the router to skip computing prefixes already present in VRAM.
"""

import hashlib
from typing import List, Dict

class MiniSGLangRouter:
    def __init__(self):
        # Maps SHA-256 hash of a prompt prefix to its physical VRAM block index
        self.radix_tree_cache: Dict[str, int] = {}
        self.next_block_idx = 0
        print("[Mini-SGLang] Initialized RadixAttention prefix caching router.")

    def _hash_prefix(self, tokens: List[int]) -> str:
        # Create a unique signature for the token sequence
        sig = ",".join(map(str, tokens))
        return hashlib.sha256(sig.encode('utf-8')).hexdigest()

    def route_prompt(self, tokens: List[int]) -> dict:
        """
        Analyzes the prompt to find the longest matching prefix in the Radix Tree.
        Returns the VRAM block to reuse and the remaining tokens to compute.
        """
        # Search backwards for the longest matching prefix
        for i in range(len(tokens), 0, -1):
            prefix = tokens[:i]
            prefix_hash = self._hash_prefix(prefix)
            
            if prefix_hash in self.radix_tree_cache:
                match_length = i
                block_idx = self.radix_tree_cache[prefix_hash]
                new_tokens = tokens[i:]
                
                # print(f"[Mini-SGLang] Cache HIT. Reusing {match_length} tokens from Block {block_idx}.")
                return {
                    "cache_hit": True,
                    "matched_length": match_length,
                    "vram_block_idx": block_idx,
                    "new_tokens_to_compute": new_tokens
                }

        # No match found, compute entirely
        # print("[Mini-SGLang] Cache MISS. Computing full prompt.")
        return {
            "cache_hit": False,
            "matched_length": 0,
            "vram_block_idx": -1,
            "new_tokens_to_compute": tokens
        }

    def commit_to_cache(self, tokens: List[int]):
        """
        After computation, stores the prefix in the Radix Tree for future reuse.
        """
        prefix_hash = self._hash_prefix(tokens)
        if prefix_hash not in self.radix_tree_cache:
            self.radix_tree_cache[prefix_hash] = self.next_block_idx
            self.next_block_idx += 1

# Usage:
# router = MiniSGLangRouter()
# # System prompt: "You are a helpful assistant." (Tokens: [1, 5, 10, 12])
# router.commit_to_cache([1, 5, 10, 12])
# # User asks question with same system prompt: (Tokens: [1, 5, 10, 12, 99, 100])
# result = router.route_prompt([1, 5, 10, 12, 99, 100])
