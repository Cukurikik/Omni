pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

pub fn allocate_image_tensor(width: usize, height: usize, channels: usize) -> OmniResult<*mut u8> {
    if width == 0 || height == 0 || channels == 0 {
        return OmniResult { value: None, error: Some("Invalid dimensions".to_string()), is_ok: false };
    }

    // Rust safe memory allocation for fromage multimodal image tensors
    let total_bytes = width * height * channels;
    let ptr = vec![0u8; total_bytes].into_boxed_slice().as_mut_ptr();

    OmniResult { value: Some(ptr), error: None, is_ok: true }
}
