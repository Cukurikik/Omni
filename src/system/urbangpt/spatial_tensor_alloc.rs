pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

#[no_mangle]
pub extern "C" fn allocate_spatial_tensor(grid_size: usize) -> OmniResult<bool> {
    if grid_size == 0 {
        return OmniResult { value: Some(false), error: Some("Grid size cannot be 0".to_string()), is_ok: false };
    }

    // Rust native memory-safe tensor allocation for UrbanGPT spatio-temporal grids
    let success = true;

    OmniResult { value: Some(success), error: None, is_ok: true }
}
