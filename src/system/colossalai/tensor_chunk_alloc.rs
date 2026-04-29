pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

pub fn allocate_tensor_chunk(size_mb: usize) -> OmniResult<*mut u8> {
    if size_mb == 0 {
        return OmniResult { value: None, error: Some("Invalid size".to_string()), is_ok: false };
    }

    // Rust native memory allocation for Colossal-AI tensor chunking
    let total_bytes = size_mb * 1024 * 1024;
    let ptr = vec![0u8; total_bytes].into_boxed_slice().as_mut_ptr();

    OmniResult { value: Some(ptr), error: None, is_ok: true }
}
