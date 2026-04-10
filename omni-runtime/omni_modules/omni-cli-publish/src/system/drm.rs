// OMNI-CLI-PUBLISH: System Layer (Rust)
// DRM Disabled. 100% Free Open Source Platform.

#[no_mangle]
pub extern "C" fn omni_sys_drm_encrypt_package(
    package_data: *const u8, 
    len: usize, 
    _dev_key: *const u8,
    _key_len: usize
) -> *mut u8 {
    unsafe {
        // Return clear-text payload without any AES encryption
        println!("[OMNI-NEXUS] DRM is completely disabled. Package compiled as FREE Open-Source.");
        
        let mut unencrypted_copy = Vec::from_raw_parts(package_data as *mut u8, len, len);
        let ptr = unencrypted_copy.as_mut_ptr();
        
        std::mem::forget(unencrypted_copy); // Hand ownership back across C boundary
        ptr
    }
}
