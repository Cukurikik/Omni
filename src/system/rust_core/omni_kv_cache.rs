// OMNI System Layer — Rust KV-Cache Manager
// Zero-copy KV cache for efficient autoregressive inference.

use std::alloc::{alloc_zeroed, dealloc, Layout};
use std::ptr;

/// KV Cache entry for a single layer and head
pub struct KVCache {
    key_cache: *mut f32,
    value_cache: *mut f32,
    max_seq_len: usize,
    head_dim: usize,
    num_heads: usize,
    current_len: usize,
    layout: Layout,
}

unsafe impl Send for KVCache {}
unsafe impl Sync for KVCache {}

impl KVCache {
    pub fn new(max_seq_len: usize, num_heads: usize, head_dim: usize) -> Self {
        let total_elements = max_seq_len * num_heads * head_dim;
        let layout = Layout::array::<f32>(total_elements).expect("Invalid layout");

        let key_cache = unsafe { alloc_zeroed(layout) as *mut f32 };
        let value_cache = unsafe { alloc_zeroed(layout) as *mut f32 };

        assert!(!key_cache.is_null(), "Key cache allocation failed");
        assert!(!value_cache.is_null(), "Value cache allocation failed");

        Self { key_cache, value_cache, max_seq_len, head_dim, num_heads, current_len: 0, layout }
    }

    /// Append new key-value pair at current position
    pub fn append(&mut self, keys: &[f32], values: &[f32]) -> Result<(), &'static str> {
        if self.current_len >= self.max_seq_len {
            return Err("KV cache full");
        }
        let expected = self.num_heads * self.head_dim;
        if keys.len() != expected || values.len() != expected {
            return Err("Invalid key/value dimensions");
        }

        let offset = self.current_len * self.num_heads * self.head_dim;
        unsafe {
            ptr::copy_nonoverlapping(keys.as_ptr(), self.key_cache.add(offset), expected);
            ptr::copy_nonoverlapping(values.as_ptr(), self.value_cache.add(offset), expected);
        }
        self.current_len += 1;
        Ok(())
    }

    /// Get all cached keys for a specific head as a slice
    pub fn get_keys(&self, head: usize) -> &[f32] {
        assert!(head < self.num_heads);
        unsafe {
            let base = self.key_cache.add(head * self.head_dim);
            std::slice::from_raw_parts(base, self.current_len * self.head_dim)
        }
    }

    /// Get all cached values for a specific head as a slice
    pub fn get_values(&self, head: usize) -> &[f32] {
        assert!(head < self.num_heads);
        unsafe {
            let base = self.value_cache.add(head * self.head_dim);
            std::slice::from_raw_parts(base, self.current_len * self.head_dim)
        }
    }

    pub fn len(&self) -> usize { self.current_len }
    pub fn is_empty(&self) -> bool { self.current_len == 0 }
    pub fn capacity(&self) -> usize { self.max_seq_len }
    pub fn memory_usage_bytes(&self) -> usize { self.layout.size() * 2 }

    pub fn clear(&mut self) {
        self.current_len = 0;
        let size = self.max_seq_len * self.num_heads * self.head_dim * std::mem::size_of::<f32>();
        unsafe {
            ptr::write_bytes(self.key_cache, 0, size);
            ptr::write_bytes(self.value_cache, 0, size);
        }
    }
}

impl Drop for KVCache {
    fn drop(&mut self) {
        unsafe {
            dealloc(self.key_cache as *mut u8, self.layout);
            dealloc(self.value_cache as *mut u8, self.layout);
        }
    }
}

/// Multi-layer KV cache manager
pub struct KVCacheManager {
    caches: Vec<KVCache>,
    num_layers: usize,
}

impl KVCacheManager {
    pub fn new(num_layers: usize, max_seq_len: usize, num_heads: usize, head_dim: usize) -> Self {
        let caches = (0..num_layers)
            .map(|_| KVCache::new(max_seq_len, num_heads, head_dim))
            .collect();
        Self { caches, num_layers }
    }

    pub fn get_layer(&self, layer: usize) -> &KVCache { &self.caches[layer] }
    pub fn get_layer_mut(&mut self, layer: usize) -> &mut KVCache { &mut self.caches[layer] }
    pub fn current_len(&self) -> usize { self.caches.first().map_or(0, |c| c.len()) }

    pub fn total_memory_bytes(&self) -> usize {
        self.caches.iter().map(|c| c.memory_usage_bytes()).sum()
    }

    pub fn clear_all(&mut self) {
        for cache in &mut self.caches { cache.clear(); }
    }
}
