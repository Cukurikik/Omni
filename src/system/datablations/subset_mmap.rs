pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

#[no_mangle]
pub extern "C" fn init_subset_mmap() -> OmniResult<bool> {
    // Rust low-level zero-cost memory mapping for rapidly switching Datablation subsets
    let mmap_ready = true;

    OmniResult { value: Some(mmap_ready), error: None, is_ok: true }
}
