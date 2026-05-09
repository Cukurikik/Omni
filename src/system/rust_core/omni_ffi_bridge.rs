// OMNI System — Rust FFI Bridge
// Exposes safe Rust core functions to C and Python via C ABI

use std::os::raw::c_char;
use std::ffi::CStr;

#[no_mangle]
pub extern "C" fn omni_core_init(config_path: *const c_char) -> i32 {
    if config_path.is_null() {
        return -1;
    }

    let c_str = unsafe { CStr::from_ptr(config_path) };
    let path = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return -2,
    };

    println!("OMNI Rust Core: Initializing from {}", path);
    // Simulation of core boot
    0 // Success
}

#[no_mangle]
pub extern "C" fn omni_core_shutdown() {
    println!("OMNI Rust Core: Shutting down gracefully.");
}
