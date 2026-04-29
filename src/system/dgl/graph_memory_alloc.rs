pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

pub fn allocate_graph_memory(node_count: usize, feature_dim: usize) -> OmniResult<*mut u8> {
    if node_count == 0 || feature_dim == 0 {
        return OmniResult { value: None, error: Some("Invalid dimensions".to_string()), is_ok: false };
    }

    // Rust safe memory allocation for Deep Graph Library tensors
    let total_bytes = node_count * feature_dim * 4; // float32
    let ptr = vec![0u8; total_bytes].into_boxed_slice().as_mut_ptr();

    OmniResult { value: Some(ptr), error: None, is_ok: true }
}
