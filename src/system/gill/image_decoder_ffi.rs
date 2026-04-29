pub struct OmniResult<T> {
    pub value: Option<T>,
    pub error: Option<String>,
    pub is_ok: bool,
}

#[no_mangle]
pub extern "C" fn init_image_decoder() -> OmniResult<bool> {
    // Rust native high-speed image decoder FFI for gill
    let initialized = true;

    OmniResult { value: Some(initialized), error: None, is_ok: true }
}
