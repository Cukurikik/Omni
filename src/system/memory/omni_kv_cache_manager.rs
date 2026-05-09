//! Omni Key-Value (KV) Cache Manager
//! Handles the zero-copy, pre-allocated memory buffers for autoregressive
//! generation. Required to prevent reallocation overhead during sequential token decoding.

pub struct KVCache {
    pub max_seq_len: usize,
    pub num_layers: usize,
    pub num_heads: usize,
    pub head_dim: usize,
    pub current_len: usize,
    
    // Contiguous pre-allocated memory blocks
    k_cache: Vec<f32>,
    v_cache: Vec<f32>,
}

impl KVCache {
    pub fn new(max_seq_len: usize, num_layers: usize, num_heads: usize, head_dim: usize) -> Self {
        let size = num_layers * max_seq_len * num_heads * head_dim;
        KVCache {
            max_seq_len,
            num_layers,
            num_heads,
            head_dim,
            current_len: 0,
            k_cache: vec![0.0; size],
            v_cache: vec![0.0; size],
        }
    }

    pub fn append(&mut self, layer: usize, k_tokens: &[f32], v_tokens: &[f32], num_new_tokens: usize) {
        assert!(self.current_len + num_new_tokens <= self.max_seq_len, "KV Cache Overflow");
        
        let layer_offset = layer * self.max_seq_len * self.num_heads * self.head_dim;
        let token_offset = self.current_len * self.num_heads * self.head_dim;
        let start_idx = layer_offset + token_offset;
        let len = num_new_tokens * self.num_heads * self.head_dim;
        
        self.k_cache[start_idx..start_idx + len].copy_from_slice(k_tokens);
        self.v_cache[start_idx..start_idx + len].copy_from_slice(v_tokens);
    }
    
    pub fn increment_len(&mut self, num_new_tokens: usize) {
        self.current_len += num_new_tokens;
    }
    
    pub fn reset(&mut self) {
        self.current_len = 0;
    }
    
    pub fn get_layer_cache(&self, layer: usize) -> (&[f32], &[f32]) {
        let layer_offset = layer * self.max_seq_len * self.num_heads * self.head_dim;
        let active_len = self.current_len * self.num_heads * self.head_dim;
        
        let k = &self.k_cache[layer_offset..layer_offset + active_len];
        let v = &self.v_cache[layer_offset..layer_offset + active_len];
        
        (k, v)
    }
}
