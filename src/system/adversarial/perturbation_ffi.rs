// OMNI SYSTEM LAYER: Adversarial (Rust)
// FFI for high-speed tensor perturbation clipping (L-infinity norm bounding)

#[no_mangle]
pub extern "C" fn omni_clip_perturbation(
    base_ptr: *const f32,
    adv_ptr: *mut f32,
    len: usize,
    epsilon: f32,
) -> i32 {
    if base_ptr.is_null() || adv_ptr.is_null() {
        return -1; // Omni Error Code: Null Pointer
    }

    let base_slice = unsafe { std::slice::from_raw_parts(base_ptr, len) };
    let adv_slice = unsafe { std::slice::from_raw_parts_mut(adv_ptr, len) };

    for i in 0..len {
        let diff = adv_slice[i] - base_slice[i];
        let clipped_diff = diff.clamp(-epsilon, epsilon);
        adv_slice[i] = (base_slice[i] + clipped_diff).clamp(0.0, 1.0);
    }

    0 // Omni Success Code
}

#[no_mangle]
pub extern "C" fn omni_free_perturbation(ptr: *mut f32, len: usize) {
    if !ptr.is_null() {
        unsafe {
            let _ = Vec::from_raw_parts(ptr, len, len);
        }
    }
}
