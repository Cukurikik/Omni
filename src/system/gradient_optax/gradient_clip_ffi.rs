#[no_mangle]
pub extern "C" fn omni_clip_gradients(
    grads: *mut f64,
    length: i32,
    max_norm: f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if grads.is_null() || length <= 0 || max_norm <= 0.0 {
        unsafe { *err_code = -1 };
        return;
    }

    let slice = unsafe { std::slice::from_raw_parts_mut(grads, length as usize) };
    
    // Deterministic mathematical gradient clipping by global norm
    let mut sum_sq = 0.0;
    for &mut g in slice.iter_mut() {
        sum_sq += g * g;
    }
    
    let global_norm = sum_sq.sqrt();
    
    if global_norm > max_norm {
        let clip_coef = max_norm / (global_norm + 1e-6);
        for g in slice.iter_mut() {
            *g *= clip_coef;
        }
    }

    unsafe { *err_code = 0 };
}
