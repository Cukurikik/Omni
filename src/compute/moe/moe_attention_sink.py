"""
moe_attention_sink.py — Compute / Stability
Layer: Compute / AI — StreamingLLM Attention Sinks

During infinite streaming generation (e.g. 4M+ tokens), the KV cache overflows
and traditional sliding windows cause models to immediately collapse and output 
gibberish. This module implements "Attention Sinks" (keeping the first ~4 tokens 
permanently in cache), stabilizing the MoE experts infinitely.
"""

import torch
import torch.nn as nn

class AttentionSinkManager:
    """
    Manages the KV cache for infinite streaming without memory explosion.
    Preserves the initial "sink" tokens, and applies a rolling window to the rest.
    """
    def __init__(self, sink_size: int = 4, window_size: int = 2048):
        self.sink_size = sink_size
        self.window_size = window_size
        print(f"[Attention Sink] Initialized StreamingLLM stability manager. (Window: {window_size}, Sinks: {sink_size})")

    def update_kv_cache(self, past_key_values: torch.Tensor, new_key_values: torch.Tensor) -> torch.Tensor:
        """
        past_key_values: (Batch, NumHeads, SeqLen, HeadDim)
        new_key_values: (Batch, NumHeads, 1, HeadDim)
        """
        if past_key_values is None:
            return new_key_values
            
        current_seq_len = past_key_values.shape[2]
        
        # If we haven't hit the window limit, just append normally
        if current_seq_len < self.window_size:
            return torch.cat([past_key_values, new_key_values], dim=2)
            
        # We hit the limit. We must evict tokens to prevent OOM, 
        # BUT we must perfectly preserve the first `sink_size` tokens.
        
        # 1. Extract the permanent sink tokens [0 : sink_size]
        sink_tokens = past_key_values[:, :, :self.sink_size, :]
        
        # 2. Extract the sliding window, dropping the oldest non-sink token
        #    We keep [sink_size + 1 : end]
        rolling_tokens = past_key_values[:, :, self.sink_size + 1:, :]
        
        # 3. Concatenate Sink + Rolling Window + New Token
        updated_cache = torch.cat([sink_tokens, rolling_tokens, new_key_values], dim=2)
        
        return updated_cache

# Integration in Transformer Layer:
# k, v = self.qkv_proj(x)
# self.k_cache = self.sink_manager.update_kv_cache(self.k_cache, k)
# self.v_cache = self.sink_manager.update_kv_cache(self.v_cache, v)
# output = standard_attention(q, self.k_cache, self.v_cache)
