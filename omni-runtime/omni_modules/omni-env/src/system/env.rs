// omni-env/system/env.rs
use std::env;
#[no_mangle]
pub extern "C" fn omni_env_get(key_ptr: *const u8, len: usize) -> *const u8 {
    // unsafe pointer extraction, returns env var
    std::ptr::null()
}
